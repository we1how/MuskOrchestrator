#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载模块
负责从本地 DuckDB 数据库加载股票数据
"""

import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List


class StockDataLoader:
    """股票数据加载器"""

    def __init__(self, base_path: str = "~/StockData", read_only: bool = False):
        self.base_path = Path(base_path).expanduser()
        self.parquet_path = self.base_path / "parquet"
        self.db_path = self.base_path / "stock.duckdb"

        # 连接 DuckDB（支持只读模式避免锁定冲突）
        self.conn = duckdb.connect(str(self.db_path), read_only=read_only)
        self._init_views()
    
    def _init_views(self):
        """初始化视图"""
        # 检查是否只读模式（只读模式下视图应已存在）
        try:
            is_readonly = self.conn.execute("PRAGMA database_list").fetchall()
            # 尝试获取当前数据库的只读状态
            readonly_setting = self.conn.execute("SELECT current_setting('access_mode')").fetchone()[0]
            is_readonly_mode = (readonly_setting == 'read_only')
        except:
            is_readonly_mode = False

        # 只读模式下跳过视图创建（视图应已存在）
        if is_readonly_mode:
            return

        # 日线数据视图 - 支持分区路径 (year=*/month=*/data.parquet)
        daily_path = self.parquet_path / "daily"
        try:
            if daily_path.exists():
                # 匹配嵌套分区结构 year=*/month=*/*.parquet
                daily_glob = str(daily_path / "year=*" / "month=*" / "*.parquet")
                self.conn.execute(f"""
                    CREATE OR REPLACE VIEW daily AS
                    SELECT * FROM read_parquet('{daily_glob}', hive_partitioning=1)
                """)
        except Exception as e:
            print(f"Warning: daily view creation failed: {e}")

        # 其他表视图
        tables = ['stock_basic', 'fundamentals', 'income_statement',
                  'balance_sheet', 'cash_flow']
        for table in tables:
            parquet_path = self.parquet_path / f"{table}.parquet"
            if parquet_path.exists():
                try:
                    self.conn.execute(f"""
                        CREATE OR REPLACE VIEW {table} AS
                        SELECT * FROM read_parquet('{parquet_path}')
                    """)
                except Exception as e:
                    print(f"Warning: {table} view creation failed: {e}")
    
    def _normalize_stock_code(self, code: str) -> str:
        """
        将各种格式的股票代码统一转换为 ts_code 格式 (600408.SH)
        支持的输入格式：
        - 600408 (纯数字)
        - 600408.SH (标准格式)
        - sh.600408 / sz.600408 (stock_basic 格式)
        """
        if not code:
            return code

        # 已经是标准格式 (600408.SH)
        if '.' in code and len(code.split('.')) == 2:
            suffix = code.split('.')[1].upper()
            if suffix in ['SH', 'SZ', 'BJ']:
                return code.upper()

        # 处理 sh.600408 / sz.600408 / bj.600408 格式
        if '.' in code and len(code.split('.')) == 2:
            parts = code.split('.')
            prefix = parts[0].lower()
            num = parts[1]
            if prefix == 'sh':
                return f"{num}.SH"
            elif prefix == 'sz':
                return f"{num}.SZ"
            elif prefix == 'bj':
                return f"{num}.BJ"

        # 纯数字，根据前缀判断交易所
        if code.startswith('6'):
            return f"{code}.SH"
        elif code.startswith('0') or code.startswith('3'):
            return f"{code}.SZ"
        elif code.startswith('8') or code.startswith('4'):
            return f"{code}.BJ"

        return code

    def get_stock_data(
        self,
        code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取单只股票的历史数据

        Args:
            code: 股票代码 (如: 000001, 600519, sh.600408)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            DataFrame 包含 OHLCV 数据，格式适配 backtesting.py
        """
        # 标准化股票代码格式
        code = self._normalize_stock_code(code)

        query = f"""
            SELECT
                trade_date as Date,
                open as Open,
                high as High,
                low as Low,
                close as Close,
                vol as Volume
            FROM daily
            WHERE ts_code = '{code}'
              AND trade_date >= '{start_date}'
              AND trade_date <= '{end_date}'
            ORDER BY trade_date ASC
        """

        try:
            df = self.conn.execute(query).fetchdf()
        except Exception as e:
            error_msg = str(e)
            if "No magic bytes found" in error_msg or "parquet" in error_msg.lower():
                print(f"[数据加载] 警告: 数据文件可能损坏，尝试使用备用方法加载: {e}")
                # 尝试直接从 parquet 文件加载，跳过损坏的文件
                df = self._get_stock_data_fallback(code, start_date, end_date)
            else:
                raise
        
        if df.empty:
            return df
        
        # 设置日期索引（backtesting.py 要求）
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # 确保列名首字母大写（backtesting.py 要求）
        df.columns = [col.capitalize() if col.lower() in ['open', 'high', 'low', 'close', 'volume'] 
                      else col for col in df.columns]
        
        return df

    def _get_stock_data_fallback(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        备用方法：当视图查询失败时，尝试直接从 parquet 文件加载数据
        跳过损坏的文件
        """
        import pandas as pd
        from pathlib import Path

        # 标准化代码格式
        if '.' not in code:
            if code.startswith('6'):
                code = f"{code}.SH"
            elif code.startswith('0') or code.startswith('3'):
                code = f"{code}.SZ"
            elif code.startswith('8') or code.startswith('4'):
                code = f"{code}.BJ"

        # 计算需要查询的年月范围
        start_year = int(start_date[:4])
        end_year = int(end_date[:4])
        start_month = int(start_date[5:7])
        end_month = int(end_date[5:7])

        all_data = []
        daily_path = self.parquet_path / "daily"

        # 遍历可能的年月组合
        for year in range(start_year, end_year + 1):
            year_path = daily_path / f"year={year}"
            if not year_path.exists():
                continue

            month_start = start_month if year == start_year else 1
            month_end = end_month if year == end_year else 12

            for month in range(month_start, month_end + 1):
                month_str = f"{month:02d}"
                parquet_file = year_path / f"month={month_str}" / "data.parquet"

                if parquet_file.exists():
                    try:
                        # 尝试读取单个 parquet 文件
                        df = pd.read_parquet(parquet_file)
                        # 筛选特定股票
                        if 'ts_code' in df.columns:
                            df = df[df['ts_code'] == code]
                        elif 'symbol' in df.columns:
                            df = df[df['symbol'] == code]
                        if not df.empty:
                            all_data.append(df)
                    except Exception as e:
                        print(f"[数据加载] 跳过损坏的文件 {parquet_file}: {e}")
                        continue

        if not all_data:
            return pd.DataFrame()

        # 合并所有数据
        combined = pd.concat(all_data, ignore_index=True)

        # 标准化列名
        column_mapping = {
            'trade_date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume',
            'volume': 'Volume'
        }

        # 重命名列
        for old_col, new_col in column_mapping.items():
            if old_col in combined.columns:
                combined = combined.rename(columns={old_col: new_col})

        # 确保必要的列存在
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in combined.columns:
                print(f"[数据加载] 警告: 缺少列 {col}")

        # 按日期排序和筛选
        if 'Date' in combined.columns:
            combined['Date'] = pd.to_datetime(combined['Date'])
            combined = combined[(combined['Date'] >= start_date) & (combined['Date'] <= end_date)]
            combined = combined.sort_values('Date')

        return combined

    def get_available_stocks(self, limit: int = 1000) -> pd.DataFrame:
        """
        获取可用股票列表（去重，只包含当前上市股票）

        Returns:
            DataFrame 包含股票代码和名称
        """
        # 尝试从 stock_basic 表获取
        parquet_path = self.parquet_path / "stock_basic.parquet"

        if parquet_path.exists():
            # 尝试使用兼容的列名（表结构可能不同）
            try:
                # 先查看有哪些列
                schema_query = "DESCRIBE SELECT * FROM stock_basic LIMIT 1"
                schema = self.conn.execute(schema_query).fetchdf()
                available_cols = schema['column_name'].tolist()

                # 构建查询
                select_cols = ['name']
                if 'industry' in available_cols:
                    select_cols.append('industry')
                if 'market' in available_cols:
                    select_cols.append('market')
                if 'total_mv' in available_cols:
                    select_cols.append('total_mv')
                if 'tradeStatus' in available_cols:
                    select_cols.append('tradeStatus')

                query = f"""
                    SELECT DISTINCT
                        CASE
                            WHEN symbol LIKE '%.SZ' OR symbol LIKE '%.SH' OR symbol LIKE '%.BJ'
                            THEN SUBSTRING(symbol, 1, LENGTH(symbol) - 3)
                            ELSE symbol
                        END as code,
                        {', '.join(select_cols)}
                    FROM stock_basic
                    ORDER BY symbol
                    LIMIT {limit}
                """
                df = self.conn.execute(query).fetchdf()
                print(f"[数据加载] 从stock_basic获取到 {len(df)} 只股票")
                return df
            except Exception as e:
                print(f"[数据加载] 从stock_basic获取失败: {e}")

        # 备选：从daily表获取（去重，只取最近30天有交易的股票）
        query = f"""
            SELECT DISTINCT
                CASE
                    WHEN ts_code LIKE '%.SZ' OR ts_code LIKE '%.SH' OR ts_code LIKE '%.BJ'
                    THEN SUBSTRING(ts_code, 1, LENGTH(ts_code) - 3)
                    ELSE ts_code
                END as code
            FROM daily
            WHERE trade_date >= (SELECT MAX(trade_date) FROM daily) - INTERVAL '30 days'
            LIMIT {limit}
        """

        try:
            df = self.conn.execute(query).fetchdf()
            print(f"[数据加载] 从daily表获取到 {len(df)} 只活跃股票")
            return df
        except Exception as e:
            print(f"[数据加载] Error getting stock list: {e}")
            return pd.DataFrame(columns=['code'])
    
    def get_stock_info(self, code: str) -> Optional[pd.Series]:
        """
        获取股票基本信息
        
        Args:
            code: 股票代码
        
        Returns:
            股票信息 Series
        """
        if '.' not in code:
            if code.startswith('6'):
                code = f"{code}.SH"
            elif code.startswith('0') or code.startswith('3'):
                code = f"{code}.SZ"
            elif code.startswith('8') or code.startswith('4'):
                code = f"{code}.BJ"
        
        parquet_path = self.parquet_path / "stock_basic.parquet"
        
        if parquet_path.exists():
            query = f"""
                SELECT *
                FROM stock_basic
                WHERE symbol = '{code}' OR ts_code = '{code}'
                LIMIT 1
            """
            try:
                df = self.conn.execute(query).fetchdf()
                if not df.empty:
                    return df.iloc[0]
            except:
                pass
        
        return None
    
    def get_date_range(self) -> tuple:
        """
        获取数据的日期范围
        
        Returns:
            (最早日期, 最晚日期)
        """
        query = """
            SELECT 
                MIN(trade_date) as min_date,
                MAX(trade_date) as max_date
            FROM daily
        """
        
        try:
            df = self.conn.execute(query).fetchdf()
            if not df.empty:
                return df.iloc[0]['min_date'], df.iloc[0]['max_date']
        except Exception as e:
            print(f"Error getting date range: {e}")
        
        # 默认返回最近一年的范围
        end = datetime.now()
        start = end - timedelta(days=365)
        return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票
        
        Args:
            keyword: 搜索关键词（代码或名称）
        
        Returns:
            匹配的股票列表
        """
        parquet_path = self.parquet_path / "stock_basic.parquet"
        
        if parquet_path.exists():
            query = f"""
                SELECT 
                    symbol as code,
                    name,
                    industry
                FROM stock_basic
                WHERE symbol LIKE '%{keyword}%'
                   OR name LIKE '%{keyword}%'
                   OR cnspell LIKE '%{keyword}%'
                LIMIT 20
            """
            try:
                return self.conn.execute(query).fetchdf()
            except:
                pass
        
        return pd.DataFrame(columns=['code', 'name', 'industry'])
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()


# 便捷函数
def load_stock_data(
    code: str, 
    start_date: str, 
    end_date: str,
    base_path: str = "~/StockData"
) -> pd.DataFrame:
    """
    便捷函数：加载股票数据
    
    Example:
        df = load_stock_data('000001', '2023-01-01', '2023-12-31')
    """
    loader = StockDataLoader(base_path)
    try:
        data = loader.get_stock_data(code, start_date, end_date)
        return data
    finally:
        loader.close()


if __name__ == "__main__":
    # 测试代码
    print("测试数据加载器...")
    
    loader = StockDataLoader()
    
    # 测试获取日期范围
    min_date, max_date = loader.get_date_range()
    print(f"\n数据日期范围: {min_date} ~ {max_date}")
    
    # 测试获取股票数据
    print("\n获取贵州茅台(600519)最近30天数据:")
    df = loader.get_stock_data('600519', '2024-01-01', '2024-12-31')
    print(df.head())
    print(f"\n数据条数: {len(df)}")
    
    # 测试获取股票列表
    print("\n获取股票列表(前10条):")
    stocks = loader.get_available_stocks(10)
    print(stocks)
    
    loader.close()
    print("\n测试完成!")
