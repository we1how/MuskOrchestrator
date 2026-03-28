#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股本地数据库 - 每日增量更新脚本

功能:
- 只拉取新数据
- 合并到现有 Parquet
- 更新 DuckDB 视图
- 生成更新报告
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import pandas as pd
import duckdb

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path('~/StockData/logs/daily_update.log').expanduser()),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyUpdater:
    """每日数据更新器"""
    
    def __init__(self, base_path: str = "~/StockData"):
        self.base_path = Path(base_path).expanduser()
        self.parquet_path = self.base_path / "parquet"
        self.meta_path = self.base_path / "meta"
        self.log_path = self.base_path / "logs"
        self.db_path = self.base_path / "stock.duckdb"
        self.update_log = self.meta_path / "daily_update_log.json"
        self.progress_file = self.meta_path / "daily_update_progress.json"

        # 创建目录
        for path in [self.parquet_path, self.meta_path, self.log_path]:
            path.mkdir(parents=True, exist_ok=True)

        # 加载更新记录和进度
        self.update_history = self._load_update_history()
        self.progress = self._load_progress()

        # 线程锁（用于并发保存进度）
        self._progress_lock = Lock()

        # 初始化数据源
        self._init_data_sources()
    
    def _init_data_sources(self):
        """初始化数据源（仅使用baostock，更稳定可靠）"""
        self.ak = None  # 不再使用akshare（连接不稳定）
        self.bs = None
        self.ts = None
        self.bs_logged_in = False

        # 只使用 baostock（主数据源，更稳定）
        try:
            import baostock as bs
            self.bs = bs
            # 只登录一次
            lg = self.bs.login()
            if lg.error_code == '0':
                self.bs_logged_in = True
                logger.info("✅ baostock 已登录")
            else:
                logger.warning(f"⚠️ baostock 登录失败: {lg.error_msg}")
        except ImportError:
            logger.warning("⚠️ baostock 未安装，请运行: pip install baostock")
        except Exception as e:
            logger.warning(f"⚠️ baostock 登录异常: {e}")

        # Tushare (可选，作为补充)
        token_path = Path("~/.openclaw/credentials/tushare.json").expanduser()
        if token_path.exists():
            try:
                with open(token_path) as f:
                    config = json.load(f)
                    token = config.get("token")
                    if token:
                        import tushare as ts
                        ts.set_token(token)
                        self.ts = ts.pro_api()
                        logger.info("✅ Tushare 已加载")
            except Exception as e:
                logger.debug(f"Tushare 加载失败: {e}")

        # 检查baostock是否可用
        if self.bs is None or not self.bs_logged_in:
            logger.error("❌ baostock 是必需的数据源，请确保已安装并能正常登录")
            sys.exit(1)

    def _ensure_bs_login(self):
        """确保 baostock 已登录"""
        if self.bs and not self.bs_logged_in:
            try:
                lg = self.bs.login()
                if lg.error_code == '0':
                    self.bs_logged_in = True
                    logger.debug("baostock 重新登录成功")
                else:
                    logger.warning(f"baostock 重新登录失败: {lg.error_msg}")
            except Exception as e:
                logger.warning(f"baostock 重新登录异常: {e}")

    def bs_logout(self):
        """登出 baostock"""
        if self.bs and self.bs_logged_in:
            try:
                self.bs.logout()
                self.bs_logged_in = False
                logger.info("✅ baostock 已登出")
            except Exception as e:
                logger.warning(f"baostock 登出异常: {e}")

    def _fetch_worker_batch(self, codes_batch: List[str], start_date: str, end_date: str) -> Tuple[List[Tuple[str, int]], int]:
        """
        工作线程 - 批量获取股票数据
        批次开始时登录一次，批次结束后登出一次

        Returns:
            List[Tuple[code, count]]: 每只股票的获取结果
            int: 批次中的总记录数
        """
        results = []
        batch_records = 0

        try:
            import baostock as bs

            # 批次开始时登录一次
            lg = bs.login()
            if lg.error_code != '0':
                logger.error(f"批次登录失败: {lg.error_msg}")
                return [(code, -1) for code in codes_batch], 0

            try:
                for code in codes_batch:
                    try:
                        # 获取数据（使用传入的baostock实例）
                        df = self._fetch_daily_baostock_with_session(bs, code, start_date, end_date)

                        if df is not None and len(df) > 0:
                            df['ts_code'] = code
                            df['trade_date'] = pd.to_datetime(df['trade_date'])
                            self._save_daily_partition(df, code)
                            results.append((code, len(df)))
                            batch_records += len(df)
                        else:
                            results.append((code, 0))

                        # 单只延时
                        time.sleep(0.03)

                    except Exception as e:
                        logger.debug(f"获取 {code} 失败: {e}")
                        results.append((code, -1))

            finally:
                # 批次结束时登出一次
                bs.logout()

        except Exception as e:
            logger.error(f"批次处理异常: {e}")
            # 如果整个批次失败，标记所有股票为失败
            if not results:
                results = [(code, -1) for code in codes_batch]

        return results, batch_records

    def _fetch_daily_baostock_with_session(self, bs, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """使用传入的baostock session获取数据"""
        try:
            # 转换代码格式
            if code.startswith(('6', '688', '689')):
                bs_code = f"sh.{code}"
            elif code.startswith(('8', '4')):
                bs_code = f"bj.{code}"
            else:
                bs_code = f"sz.{code}"

            # 转换日期格式
            start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,preclose,volume,amount,turn,pctChg",
                start_date=start, end_date=end, frequency="d", adjustflag="2"
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                return None

            df = pd.DataFrame(data_list, columns=rs.fields)
            df = df.rename(columns={
                'date': 'trade_date', 'open': 'open', 'high': 'high', 'low': 'low',
                'close': 'close', 'preclose': 'pre_close', 'volume': 'vol',
                'amount': 'amount', 'turn': 'turnover_rate', 'pctChg': 'pct_chg',
            })
            for col in ['open', 'high', 'low', 'close', 'pre_close', 'vol', 'amount', 'turnover_rate', 'pct_chg']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df

        except Exception as e:
            logger.debug(f"baostock获取 {code} 失败: {e}")
        return None

    def update_daily_data_multithread(self, lookback_days: int = 5, max_workers: int = 4, batch_size: int = 100):
        """
        多线程版本 - 用于快速填充历史数据
        每个线程批量处理多只股票，批次内复用baostock连接

        Args:
            lookback_days: 回溯天数
            max_workers: 线程数（建议4-8）
            batch_size: 每批处理的股票数（默认100）
        """
        today = datetime.now()
        start_date = (today - timedelta(days=lookback_days)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

        logger.info(f"📈 [多线程] 更新日线数据 ({start_date} ~ {end_date}), {max_workers}线程, 每批{batch_size}只...")

        # 获取股票列表
        stock_codes = self._get_stock_list()
        if not stock_codes:
            logger.error("❌ 无法获取股票列表")
            return 0

        total = len(stock_codes)

        # 检查哪些已有数据
        target_dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(lookback_days + 1)]
        processed_set = self._get_completed_for_dates(target_dates)
        valid_processed = processed_set.intersection(set(stock_codes))

        if len(valid_processed) > 0:
            logger.info(f"🔄 发现已完成 {len(valid_processed)}/{total}, 补充剩余...")
            stock_codes = [c for c in stock_codes if c not in valid_processed]
        else:
            logger.info(f"🆕 共 {total} 只股票")

        # 将股票列表分成批次
        batches = [stock_codes[i:i+batch_size] for i in range(0, len(stock_codes), batch_size)]
        logger.info(f"📦 分成 {len(batches)} 个批次，每批最多{batch_size}只")

        # 多线程获取
        new_records = 0
        updated_stocks = 0
        failed_codes = []
        start_time = time.time()
        processed_count = 0
        lock = Lock()

        def process_batch_with_delay(batch, batch_idx):
            """处理单个批次，批次间添加延时"""
            # 批次间延时（除第一个批次外）
            if batch_idx > 0:
                time.sleep(2)
            return self._fetch_worker_batch(batch, start_date, end_date)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有批次任务
            futures = {executor.submit(process_batch_with_delay, batch, i): batch for i, batch in enumerate(batches)}

            for future in as_completed(futures):
                batch = futures[future]
                try:
                    results, _ = future.result()

                    with lock:
                        for code, count in results:
                            processed_count += 1
                            if count > 0:
                                updated_stocks += 1
                                new_records += count
                            elif count == -1:
                                failed_codes.append(code)

                        # 每100只报告进度
                        if processed_count % 100 == 0 or processed_count >= len(stock_codes):
                            elapsed = time.time() - start_time
                            speed = processed_count / elapsed * 60
                            remaining = (len(stock_codes) - processed_count) / (processed_count / elapsed) if processed_count > 0 else 0
                            logger.info(f"进度: {processed_count}/{len(stock_codes)}, "
                                      f"成功: {updated_stocks}, 记录: {new_records}, "
                                      f"速度: {speed:.0f}只/分钟, 剩余: {remaining/60:.1f}分钟")

                except Exception as e:
                    logger.error(f"处理批次时出错: {e}")
                    # 标记整个批次为失败
                    with lock:
                        for code in batch:
                            failed_codes.append(code)
                            processed_count += 1

        if failed_codes:
            logger.warning(f"⚠️ {len(failed_codes)} 只股票更新失败")

        elapsed = time.time() - start_time
        speed = updated_stocks / (elapsed/60) if elapsed > 0 else 0
        logger.info(f"✅ [多线程] 完成: {updated_stocks} 只股票, {new_records} 条记录, "
                   f"耗时 {elapsed/60:.1f} 分钟, 速度: {speed:.0f}只/分钟")

        # 更新历史
        self.update_history["daily"]["last_date"] = end_date
        self.update_history["daily"]["record_count"] += new_records
        self._save_update_history()

        return new_records
    
    def _load_update_history(self) -> Dict:
        """加载更新历史"""
        if self.update_log.exists():
            with open(self.update_log) as f:
                return json.load(f)
        return {
            "last_update": None,
            "daily": {"last_date": None, "record_count": 0},
            "fundamentals": {"last_date": None, "record_count": 0},
        }
    
    def _save_update_history(self):
        """保存更新历史"""
        self.update_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.update_log, 'w') as f:
            json.dump(self.update_history, f, indent=2, default=str)

    def _load_progress(self) -> Dict:
        """加载断点续传进度"""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {
            "in_progress": False,
            "processed_codes": [],
            "failed_codes": [],
            "start_time": None,
            "total": 0
        }

    def _save_progress(self):
        """保存断点续传进度"""
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2, default=str)

    def _clear_progress(self):
        """清除进度（完成时调用）"""
        self.progress = {
            "in_progress": False,
            "processed_codes": [],
            "failed_codes": [],
            "start_time": None,
            "total": 0
        }
        self._save_progress()
        if self.progress_file.exists():
            self.progress_file.unlink()

    def _smart_sleep(self, base_delay: float = 0.3):
        """智能延时"""
        import random
        delay = base_delay + random.uniform(0, 0.2)
        time.sleep(delay)
    
    def _get_last_trading_day(self, max_lookback: int = 5) -> str:
        """获取最近交易日（处理周末/节假日）"""
        for days_back in range(max_lookback + 1):
            date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            if self.bs is not None and self.bs_logged_in:
                try:
                    rs = self.bs.query_all_stock(day=date)
                    stock_list = []
                    while rs.error_code == '0' and rs.next():
                        stock_list.append(rs.get_row_data())
                    if len(stock_list) > 100:  # 确认有数据（至少100只股票）
                        if days_back > 0:
                            logger.info(f"📅 回退到最近交易日: {date} (今天为非交易日)")
                        return date
                except:
                    continue
        return datetime.now().strftime("%Y-%m-%d")  # 默认返回今天

    def update_stock_basic(self):
        """更新股票基本信息（仅使用baostock，更稳定）"""
        logger.info("📊 更新股票基本信息...")

        df = None

        # 只使用 baostock（避免akshare连接不稳定问题）
        if self.bs is not None and self.bs_logged_in:
            try:
                self._ensure_bs_login()
                trading_day = self._get_last_trading_day()
                rs = self.bs.query_all_stock(day=trading_day)
                stock_list = []
                while (rs.error_code == '0') & rs.next():
                    stock_list.append(rs.get_row_data())

                df = pd.DataFrame(stock_list, columns=rs.fields)
                df = df.rename(columns={'code': 'symbol', 'code_name': 'name'})
                logger.info(f"✅ 使用 baostock 获取股票列表: {len(df)} 只")
            except Exception as e:
                logger.error(f"❌ baostock 获取失败: {e}")
        else:
            logger.error("❌ baostock 未登录，无法获取股票列表")

        if df is None:
            logger.error("❌ 数据源获取失败")
            return 0
        
        try:
            # 标准化列名（akshare格式）
            if '代码' in df.columns:
                df = df.rename(columns={
                    '代码': 'symbol',
                    '名称': 'name',
                    '最新价': 'close',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '最高': 'high',
                    '最低': 'low',
                    '今开': 'open',
                    '昨收': 'pre_close',
                    '量比': 'volume_ratio',
                    '换手率': 'turnover_rate',
                    '市盈率-动态': 'pe',
                    '市净率': 'pb',
                    '总市值': 'total_mv',
                    '流通市值': 'circ_mv',
                })
            
            df['update_time'] = datetime.now()
            
            # 保存
            output_path = self.parquet_path / "stock_basic.parquet"
            df.to_parquet(output_path, index=False, compression='zstd')
            
            logger.info(f"✅ 股票基本信息已更新: {len(df)} 只股票")
            return len(df)
            
        except Exception as e:
            logger.error(f"❌ 处理股票基本信息失败: {e}")
            return 0
    
    def update_daily_data_singlethread(self, lookback_days: int = 5):
        """
        更新日线数据（单线程+低延时，baostock不支持高并发）

        Args:
            lookback_days: 回溯天数，用于补全可能缺失的数据
        """
        today = datetime.now()
        start_date = (today - timedelta(days=lookback_days)).strftime("%Y%m%d")
        end_date = today.strftime("%Y%m%d")

        logger.info(f"📈 更新日线数据 ({start_date} ~ {end_date})，单线程模式...")

        # 获取股票列表
        stock_codes = self._get_stock_list()
        if not stock_codes:
            logger.error("❌ 无法获取股票列表")
            return 0

        total = len(stock_codes)

        # 计算需要检查的目标日期（从start_date到end_date的所有交易日）
        target_dates = []
        for i in range(lookback_days + 1):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            target_dates.append(d)

        # 检查这些日期是否已有数据
        processed_set = self._get_completed_for_dates(target_dates)
        # 只保留在当前股票列表中的已完成代码（排除已退市/过滤掉的）
        valid_processed = processed_set.intersection(set(stock_codes))
        failed_codes = []

        if len(valid_processed) > 0:
            progress_pct = len(valid_processed) / total * 100
            logger.info(f"🔄 发现已完成的股票 {len(valid_processed)}/{total} ({progress_pct:.1f}%)，继续补充剩余...")
            stock_codes = [c for c in stock_codes if c not in valid_processed]
        else:
            logger.info(f"🆕 新任务，共 {total} 只股票")

        # 只使用baostock（单连接复用）
        if self.bs is None or not self.bs_logged_in:
            logger.error("❌ baostock未登录")
            return 0

        new_records = 0
        updated_stocks = 0
        start_time = time.time()

        for i, code in enumerate(stock_codes):
            try:
                # 获取数据（只使用baostock，单连接复用）
                df = self._fetch_daily_baostock(code, start_date, end_date)

                if df is not None and len(df) > 0:
                    df['ts_code'] = code
                    df['trade_date'] = pd.to_datetime(df['trade_date'])
                    self._save_daily_partition(df, code)
                    new_records += len(df)
                    updated_stocks += 1

                # 低延时（参考efficient_fill.py的0.05秒）
                time.sleep(0.03)

                # 每100只报告进度
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    speed = (i + 1) / elapsed * 60  # 只/分钟
                    logger.info(f"进度: {i+1}/{len(stock_codes)}, 成功: {updated_stocks}, 记录: {new_records}, 速度: {speed:.0f}只/分钟")

            except Exception as e:
                logger.error(f"{code} 失败: {e}")
                failed_codes.append(code)

        if failed_codes:
            logger.warning(f"⚠️ {len(failed_codes)} 只股票更新失败")

        elapsed = time.time() - start_time
        logger.info(f"✅ 日线数据更新完成: {updated_stocks} 只股票, {new_records} 条新记录, 耗时 {elapsed/60:.1f} 分钟")

        # 更新历史记录
        self.update_history["daily"]["last_date"] = end_date
        self.update_history["daily"]["record_count"] += new_records
        self._save_update_history()

        return new_records
    
    def _get_stock_list(self) -> List[str]:
        """获取股票代码列表（仅使用baostock，更稳定）"""
        # A股有效代码前缀（主板、科创板、创业板、北交所）
        valid_prefixes = ('600', '601', '603', '605', '688', '689',
                          '000', '001', '002', '003', '300', '301',
                          '430', '830', '870', '889')  # 北交所

        all_codes = []

        # 只使用 baostock（更稳定，避免akshare连接问题）
        if self.bs is not None and self.bs_logged_in:
            try:
                self._ensure_bs_login()
                trading_day = self._get_last_trading_day()
                rs = self.bs.query_all_stock(day=trading_day)
                codes = []
                while (rs.error_code == '0') & rs.next():
                    code = rs.get_row_data()[0]
                    # baostock格式: sh.600000 -> 600000
                    if '.' in code:
                        code = code.split('.')[1]
                    codes.append(code)
                all_codes = codes
                logger.info(f"✅ 从baostock获取股票列表: {len(all_codes)} 只")
            except Exception as e:
                logger.error(f"❌ baostock 获取股票列表失败: {e}")
        else:
            logger.error("❌ baostock 未登录，无法获取股票列表")

        # 过滤只保留A股股票（排除ETF、指数等）
        filtered_codes = [
            c for c in all_codes
            if len(str(c)) == 6 and str(c).isdigit() and str(c).startswith(valid_prefixes)
        ]

        excluded_count = len(all_codes) - len(filtered_codes)
        if excluded_count > 0:
            logger.info(f"📊 过滤后股票数量: {len(filtered_codes)}/{len(all_codes)} (排除 {excluded_count} 只ETF/指数/其他)")

        return filtered_codes
    
    def _fetch_daily_akshare(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """使用 akshare 获取日线数据"""
        if self.ak is None:
            return None
        
        try:
            df = self.ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if df is not None and len(df) > 0:
                return df.rename(columns={
                    '日期': 'trade_date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '换手率': 'turnover_rate',
                })
        except Exception as e:
            logger.debug(f"akshare 获取 {code} 失败: {e}")
        
        return None
    
    def _fetch_daily_baostock(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """使用 baostock 获取日线数据（备用）- 使用已登录的session"""
        if self.bs is None or not self.bs_logged_in:
            return None

        try:
            # 转换代码格式: 600000 -> sh.600000
            if code.startswith(('6', '688', '689')):
                bs_code = f"sh.{code}"
            elif code.startswith(('8', '4')):
                bs_code = f"bj.{code}"
            else:
                bs_code = f"sz.{code}"

            # 转换日期格式: 20240301 -> 2024-03-01
            start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

            rs = self.bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,preclose,volume,amount,turn,pctChg",
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag="2"  # 前复权
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if data_list:
                df = pd.DataFrame(data_list, columns=rs.fields)
                df = df.rename(columns={
                    'date': 'trade_date',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'preclose': 'pre_close',
                    'volume': 'vol',
                    'amount': 'amount',
                    'turn': 'turnover_rate',
                    'pctChg': 'pct_chg',
                })
                # 转换数值类型
                for col in ['open', 'high', 'low', 'close', 'pre_close', 'vol', 'amount', 'turnover_rate', 'pct_chg']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                return df

        except Exception as e:
            logger.debug(f"baostock 获取 {code} 失败: {e}")

        return None

    def _fetch_daily_baostock_threadsafe(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """线程安全版baostock获取（每个线程独立登录）"""
        try:
            import baostock as bs

            # 转换代码格式
            if code.startswith(('6', '688', '689')):
                bs_code = f"sh.{code}"
            elif code.startswith(('8', '4')):
                bs_code = f"bj.{code}"
            else:
                bs_code = f"sz.{code}"

            # 转换日期格式
            start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
            end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"

            # 每个线程独立登录
            lg = bs.login()
            if lg.error_code != '0':
                return None

            try:
                rs = bs.query_history_k_data_plus(
                    bs_code,
                    "date,open,high,low,close,preclose,volume,amount,turn,pctChg",
                    start_date=start, end_date=end, frequency="d", adjustflag="2"
                )

                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())

                if not data_list:
                    return None

                df = pd.DataFrame(data_list, columns=rs.fields)
                df = df.rename(columns={
                    'date': 'trade_date', 'open': 'open', 'high': 'high', 'low': 'low',
                    'close': 'close', 'preclose': 'pre_close', 'volume': 'vol',
                    'amount': 'amount', 'turn': 'turnover_rate', 'pctChg': 'pct_chg',
                })
                for col in ['open', 'high', 'low', 'close', 'pre_close', 'vol', 'amount', 'turnover_rate', 'pct_chg']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                return df
            finally:
                bs.logout()

        except Exception as e:
            logger.debug(f"baostock线程安全获取 {code} 失败: {e}")
        return None

    def _get_completed_for_dates(self, dates: List[str]) -> set:
        """
        检查指定日期中最新一天的数据是否已存在
        对于增量更新，只关心最新日期是否有数据

        Args:
            dates: 日期列表，格式 ['2025-03-24', '2025-03-25']

        Returns:
            在最新日期有数据的股票代码集合
        """
        completed = set()
        if not dates:
            return completed

        try:
            # 找出最新的日期
            target_dates = sorted([pd.to_datetime(d).date() for d in dates])
            latest_date = target_dates[-1]  # 只检查最新日期

            partition_path = self.parquet_path / f"daily/year={latest_date.year}/month={latest_date.month:02d}/data.parquet"
            if not partition_path.exists():
                logger.debug(f"分区不存在: {partition_path}")
                return set()

            df = pd.read_parquet(partition_path)
            if 'ts_code' not in df.columns or 'trade_date' not in df.columns:
                return set()

            # 只检查最新日期的数据
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.date
            day_data = df[df['trade_date'] == latest_date]
            codes = day_data['ts_code'].unique()

            # 统一格式为无后缀
            for c in codes:
                c = str(c)
                if '.' in c:
                    completed.add(c.split('.')[0])
                else:
                    completed.add(c)

            logger.info(f"📊 最新日期 {latest_date} 已有数据: {len(completed)} 只股票")

        except Exception as e:
            logger.warning(f"读取已完成股票失败: {e}")
            return set()

        return completed

    def _get_completed_from_parquet(self, lookback_days: int = 7) -> set:
        """
        【已废弃】请使用 _get_completed_for_dates()
        原方法有Bug：会将最近7天有任何数据的股票都标记为已完成
        """
        logger.warning("⚠️ _get_completed_from_parquet() 已废弃，请使用 _get_completed_for_dates()")
        return set()

    def _save_daily_partition(self, df: pd.DataFrame, code: str):
        """保存日线数据到分区"""
        # 确保 ts_code 格式统一（带交易所后缀）
        def normalize_code(ts_code):
            if pd.isna(ts_code):
                return ts_code
            ts_code = str(ts_code)
            # 如果已经有后缀，直接返回
            if ts_code.endswith(('.SH', '.SZ', '.BJ')):
                return ts_code
            # 根据前缀添加后缀
            if ts_code.startswith(('6', '688', '689')):
                return f"{ts_code}.SH"
            elif ts_code.startswith(('0', '3', '1', '2')):
                return f"{ts_code}.SZ"
            elif ts_code.startswith(('8', '4')):
                return f"{ts_code}.BJ"
            return ts_code

        df['ts_code'] = df['ts_code'].apply(normalize_code)

        df['year'] = df['trade_date'].dt.year
        df['month'] = df['trade_date'].dt.month

        for (year, month), group in df.groupby(['year', 'month']):
            partition_path = self.parquet_path / "daily" / f"year={year}" / f"month={month:02d}"
            partition_path.mkdir(parents=True, exist_ok=True)
            
            parquet_file = partition_path / "data.parquet"
            
            if parquet_file.exists():
                # 读取现有数据，合并，去重
                existing = pd.read_parquet(parquet_file)
                combined = pd.concat([existing, group], ignore_index=True)
                combined = combined.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
                combined.to_parquet(parquet_file, index=False, compression='zstd')
            else:
                group.to_parquet(parquet_file, index=False, compression='zstd')
    
    def update_fundamentals(self):
        """更新基本面数据（仅使用baostock，更稳定）"""
        logger.info("📊 更新基本面数据...")

        df = None

        # 只使用 baostock（避免akshare连接问题）
        if self.bs is not None and self.bs_logged_in:
            try:
                df = self._fetch_fundamentals_baostock()
                if df is not None:
                    logger.info(f"✅ 使用 baostock 获取基本面数据: {len(df)} 条")
            except Exception as e:
                logger.error(f"❌ baostock 获取基本面失败: {e}")
        else:
            logger.error("❌ baostock 未登录，无法获取基本面数据")

        if df is None:
            logger.error("❌ 数据源获取失败")
            return 0
        
        try:
            df['trade_date'] = datetime.now().date()
            
            output_path = self.parquet_path / "fundamentals.parquet"
            df.to_parquet(output_path, index=False, compression='zstd')
            
            logger.info(f"✅ 基本面数据已更新: {len(df)} 条记录")
            
            self.update_history["fundamentals"]["last_date"] = datetime.now().isoformat()
            self.update_history["fundamentals"]["record_count"] = len(df)
            self._save_update_history()
            
            return len(df)
            
        except Exception as e:
            logger.error(f"❌ 处理基本面数据失败: {e}")
            return 0
    
    def _fetch_fundamentals_baostock(self) -> Optional[pd.DataFrame]:
        """使用 baostock 获取基本面数据 - 使用已登录的session"""
        if self.bs is None or not self.bs_logged_in:
            return None

        try:
            self._ensure_bs_login()

            # 获取当前所有股票的基本面数据
            today = datetime.now().strftime("%Y-%m-%d")

            # 获取股票列表
            rs = self.bs.query_all_stock(day=today)
            stock_list = []
            while (rs.error_code == '0') & rs.next():
                stock_list.append(rs.get_row_data()[0])

            # 批量查询基本面（这里简化处理，实际可以优化为批量查询）
            fundamentals = []
            for code in stock_list[:100]:  # 限制数量避免超时
                try:
                    rs = self.bs.query_stock_basic(code)
                    if rs.error_code == '0':
                        data = rs.get_row_data()
                        fundamentals.append({
                            'ts_code': code.split('.')[1] if '.' in code else code,
                            'name': data[1] if len(data) > 1 else '',
                            'pe': None,  # baostock 实时PE需要额外查询
                            'pb': None,
                            'total_mv': None,
                            'circ_mv': None,
                        })
                except:
                    continue

            if fundamentals:
                return pd.DataFrame(fundamentals)

        except Exception as e:
            logger.warning(f"baostock 获取基本面失败: {e}")

        return None
    
    def refresh_duckdb_views(self):
        """刷新 Duck DB 视图（支持并发访问）"""
        logger.info("🦆 刷新 DuckDB 视图...")

        # 尝试终止可能持有锁的僵尸进程
        self._kill_stale_duckdb_processes()

        try:
            # 使用连接池配置避免锁冲突
            conn = duckdb.connect(str(self.db_path))

            # 刷新各表视图
            tables = ['stock_basic', 'fundamentals', 'income_statement',
                      'balance_sheet', 'cash_flow']

            for table in tables:
                parquet_path = self.parquet_path / f"{table}.parquet"
                if parquet_path.exists():
                    conn.execute(f"""
                        CREATE OR REPLACE VIEW {table} AS
                        SELECT * FROM read_parquet('{parquet_path}')
                    """)

            # 日线数据视图 - 使用Hive分区格式（兼容DuckDB）
            daily_path = self.parquet_path / "daily" / "year=*" / "month=*" / "data.parquet"
            conn.execute(f"""
                CREATE OR REPLACE VIEW daily AS
                SELECT * FROM read_parquet('{daily_path}', hive_partitioning=1)
            """)

            conn.close()
            logger.info("✅ DuckDB 视图已刷新")

        except Exception as e:
            logger.warning(f"⚠️ 刷新 DuckDB 视图失败: {e}")
            logger.info("💡 提示: 可能有其他程序正在使用数据库，视图将在下次运行时刷新")

    def _kill_stale_duckdb_processes(self):
        """终止可能持有 DuckDB 锁的僵尸进程"""
        try:
            import psutil
            current_pid = os.getpid()
            killed = 0

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # 检查是否是 Python 进程且访问了 stock.duckdb
                    if proc.info['pid'] != current_pid and 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'stock.duckdb' in cmdline or 'daily_update' in cmdline:
                            logger.info(f"🔪 终止僵尸进程 PID {proc.info['pid']}")
                            proc.terminate()
                            killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if killed > 0:
                time.sleep(0.5)  # 等待进程终止
                logger.info(f"✅ 已清理 {killed} 个僵尸进程")

        except ImportError:
            pass  # psutil 未安装，跳过
        except Exception as e:
            logger.debug(f"清理进程失败: {e}")
    
    def generate_report(self) -> Dict:
        """生成更新报告"""
        report = {
            "update_time": datetime.now().isoformat(),
            "stocks_updated": 0,
            "new_records": 0,
            "storage_used_gb": 0,
            "stock_count": 0,
            "daily_records": 0,
        }

        # 计算存储使用量
        total_size = 0
        for parquet_file in self.parquet_path.rglob("*.parquet"):
            total_size += parquet_file.stat().st_size

        report["storage_used_gb"] = round(total_size / (1024**3), 2)

        # 统计记录数（使用只读模式避免锁冲突）
        try:
            conn = duckdb.connect(str(self.db_path), read_only=True)

            # 日线数据数量
            result = conn.execute("SELECT COUNT(*) FROM daily").fetchone()
            report["daily_records"] = result[0] if result else 0

            # 股票数量
            result = conn.execute("SELECT COUNT(*) FROM stock_basic").fetchone()
            report["stock_count"] = result[0] if result else 0

            conn.close()
        except Exception as e:
            logger.warning(f"统计记录数失败: {e}")
            # 从 parquet 文件直接读取作为备选
            try:
                basic_path = self.parquet_path / "stock_basic.parquet"
                if basic_path.exists():
                    df = pd.read_parquet(basic_path)
                    report["stock_count"] = len(df)
            except Exception as e2:
                logger.debug(f"备选统计也失败: {e2}")

        return report
    
    def run_daily_update(self):
        """执行每日更新"""
        logger.info("=" * 60)
        logger.info("🚀 开始每日数据更新")
        logger.info("=" * 60)

        start_time = time.time()
        stock_count = 0
        new_records = 0

        try:
            # 1. 更新股票基本信息
            stock_count = self.update_stock_basic()

            # 2. 更新日线数据（单线程+低延时，避免baostock并发限制）
            new_records = self.update_daily_data_singlethread(lookback_days=10)

            # 3. 更新基本面数据
            fundamentals_count = self.update_fundamentals()

            # 4. 刷新 DuckDB 视图
            self.refresh_duckdb_views()

            # 5. 成功完成，清除进度
            self._clear_progress()
            logger.info("✅ 更新成功完成，清除进度记录")

        except Exception as e:
            logger.error(f"❌ 更新过程中断: {e}")
            logger.info("💾 进度已保存，下次运行将继续")
            raise

        # 6. 生成报告
        report = self.generate_report()
        report["stocks_updated"] = stock_count
        report["new_records"] = new_records

        elapsed = time.time() - start_time
        
        # 保存报告
        report_path = self.log_path / f"update_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("=" * 60)
        logger.info(f"✅ 每日更新完成！耗时: {elapsed/60:.1f} 分钟")
        logger.info(f"📊 更新统计:")
        logger.info(f"   - 股票数: {report['stock_count']}")
        logger.info(f"   - 日线记录: {report['daily_records']}")
        logger.info(f"   - 存储占用: {report['storage_used_gb']} GB")
        logger.info("=" * 60)
        
        # 更新最后更新时间
        self.update_history["last_update"] = datetime.now().isoformat()
        self._save_update_history()

        # 登出 baostock
        self.bs_logout()

        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description='A股本地数据库每日更新')
    parser.add_argument('--base-path', default='~/StockData', help='数据存储路径')
    parser.add_argument('--multithread', '-m', action='store_true', help='使用多线程模式（更快，适合首次填充）')
    parser.add_argument('--workers', '-w', type=int, default=4, help='多线程工作数（默认4）')
    parser.add_argument('--fill-missing', type=str, metavar='DATE', help='补充指定日期的缺失数据（格式: YYYY-MM-DD）')
    args = parser.parse_args()

    updater = DailyUpdater(base_path=args.base_path)

    # 补充特定日期数据
    if args.fill_missing:
        logger.info(f"🔄 补充模式: 填充 {args.fill_missing} 的缺失数据")
        # 计算从该日期到今天的天数
        target = datetime.strptime(args.fill_missing, "%Y-%m-%d")
        today = datetime.now()
        days_diff = (today - target).days

        if args.multithread:
            updater.update_daily_data_multithread(lookback_days=days_diff, max_workers=args.workers)
        else:
            updater.update_daily_data_singlethread(lookback_days=days_diff)
        updater.bs_logout()
        return

    # 正常每日更新
    if args.multithread:
        logger.info(f"🚀 使用多线程模式 ({args.workers} 线程)")
        updater.update_daily_data_multithread(lookback_days=10, max_workers=args.workers)
        updater.bs_logout()
    else:
        report = updater.run_daily_update()

        # 输出 JSON 报告（方便自动化脚本解析）
        print("\n" + "=" * 60)
        print("更新报告 JSON:")
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
