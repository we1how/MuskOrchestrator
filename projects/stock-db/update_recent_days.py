#!/usr/bin/env python3
"""更新最近几天缺失的股票数据 (2026-03-24, 2026-03-25)"""
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import baostock as bs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class UpdateRecentDays:
    def __init__(self):
        self.parquet_path = Path("~/StockData/parquet").expanduser()
        self.valid_prefixes = ('600', '601', '603', '605', '688', '689', '000', '001', '002', '003', '300', '301')
        self.stock_codes = self._get_stock_list()

    def _get_stock_list(self):
        basic_path = self.parquet_path / "stock_basic.parquet"
        df = pd.read_parquet(basic_path)
        codes = df['symbol'].tolist()
        clean_codes = [str(c).split('.')[1] if '.' in str(c) else str(c) for c in codes]
        return [c for c in clean_codes if len(c) == 6 and c.isdigit() and c.startswith(self.valid_prefixes)]

    def _normalize_code(self, ts_code) -> str:
        """统一代码格式为纯数字6位"""
        code = str(ts_code)
        if '.' in code:
            code = code.split('.')[0]
        return code if len(code) == 6 and code.isdigit() else None

    def _get_completed_stocks_for_date(self, date_str: str) -> set:
        """获取指定日期已完成的A股股票（过滤ETF和指数）"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            year, month = date_obj.year, date_obj.month
            partition_path = self.parquet_path / f"daily/year={year}/month={month:02d}/data.parquet"
            if partition_path.exists():
                df = pd.read_parquet(partition_path)
                date_data = df[df['trade_date'] == date_str]
                # 统一格式并过滤只保留A股代码
                codes = set()
                for ts_code in date_data['ts_code'].unique():
                    code = self._normalize_code(ts_code)
                    if code and code.startswith(self.valid_prefixes):
                        codes.add(code)
                return codes
        except Exception as e:
            logger.warning(f"读取 {date_str} 数据失败: {e}")
        return set()

    def check_date_data(self, date_str: str) -> int:
        """检查指定日期的数据量"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            year, month = date_obj.year, date_obj.month
            partition_path = self.parquet_path / f"daily/year={year}/month={month:02d}/data.parquet"
            if partition_path.exists():
                df = pd.read_parquet(partition_path)
                count = len(df[df['trade_date'] == date_str])
                return count
        except Exception:
            pass
        return 0

    def fill_date(self, date_str: str, target_count: int = 5000):
        """补充指定日期的数据"""
        logger.info(f"=== 补充 {date_str} 数据 ===")

        current_count = self.check_date_data(date_str)
        logger.info(f"当前数据: {current_count} 条")

        if current_count >= target_count:
            logger.info(f"{date_str} 数据已完整 ({current_count} 条)")
            return 0

        completed = self._get_completed_stocks_for_date(date_str)
        remaining = [c for c in self.stock_codes if c not in completed]

        logger.info(f"已完成: {len(completed)} 只, 待补充: {len(remaining)} 只")

        if not remaining:
            logger.info("所有股票数据已存在")
            return 0

        lg = bs.login()
        if lg.error_code != '0':
            logger.error("baostock 登录失败")
            return 0

        success = 0
        total_records = 0

        for i, code in enumerate(remaining):
            try:
                records = self._fetch_one(code, date_str, date_str)
                if records > 0:
                    success += 1
                    total_records += records

                if (i + 1) % 100 == 0:
                    logger.info(f"{date_str} 进度: {i+1}/{len(remaining)}, 成功: {success}, 记录: {total_records}")

                time.sleep(0.03)
            except Exception as e:
                logger.debug(f"{code} 失败: {e}")

        bs.logout()
        logger.info(f"✅ {date_str} 完成: {success}/{len(remaining)} 只成功, {total_records} 条新记录")
        return success

    def _fetch_one(self, code, start, end):
        if code.startswith(('6', '688', '689')):
            bs_code = f"sh.{code}"
        else:
            bs_code = f"sz.{code}"

        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,preclose,volume,amount,turn,pctChg",
            start_date=start, end_date=end,
            frequency="d", adjustflag="2"
        )

        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return 0

        df = pd.DataFrame(data_list, columns=rs.fields)
        df = df.rename(columns={
            'date': 'trade_date', 'open': 'open', 'high': 'high', 'low': 'low',
            'close': 'close', 'preclose': 'pre_close', 'volume': 'vol',
            'amount': 'amount', 'turn': 'turnover_rate', 'pctChg': 'pct_chg',
        })
        for col in ['open', 'high', 'low', 'close', 'pre_close', 'vol', 'amount', 'turnover_rate', 'pct_chg']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['ts_code'] = code
        df['trade_date'] = pd.to_datetime(df['trade_date'])

        df['year'] = df['trade_date'].dt.year
        df['month'] = df['trade_date'].dt.month

        for (year, month), group in df.groupby(['year', 'month']):
            partition_path = self.parquet_path / f"daily/year={year}/month={month:02d}"
            partition_path.mkdir(parents=True, exist_ok=True)
            parquet_file = partition_path / "data.parquet"

            if parquet_file.exists():
                existing = pd.read_parquet(parquet_file)
                combined = pd.concat([existing, group], ignore_index=True)
                combined = combined.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
                combined.to_parquet(parquet_file, index=False, compression='zstd')
            else:
                group.to_parquet(parquet_file, index=False, compression='zstd')

        return len(df)


if __name__ == "__main__":
    updater = UpdateRecentDays()

    # 需要补充的日期列表（基于检查结果：3/30、3/31严重不足，4/1基本无数据）
    dates_to_fill = ['2026-04-02']

    total_success = 0
    for date in dates_to_fill:
        success = updater.fill_date(date)
        total_success += success
        logger.info("")

    logger.info(f"=== 全部完成，共更新 {len(dates_to_fill)} 天 ===")
