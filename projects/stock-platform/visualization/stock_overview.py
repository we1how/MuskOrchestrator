"""
股票数据可视化展示界面
提供全市场股票概览、筛选、统计分析和个股预览功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from data_loader import StockDataLoader


# ============== 缓存函数 ==============

@st.cache_data(ttl=300)
def get_all_stocks_cached(_loader) -> pd.DataFrame:
    """缓存获取所有股票列表"""
    try:
        # 获取股票基本信息
        stocks = _loader.get_available_stocks(limit=5000)
        return stocks
    except Exception as e:
        st.error(f"获取股票列表失败: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def get_latest_market_data(_loader) -> pd.DataFrame:
    """获取最新市场数据（最近交易日）"""
    try:
        query = """
            SELECT
                ts_code,
                close,
                open,
                high,
                low,
                vol as volume,
                amount,
                trade_date,
                (close - LAG(close, 1) OVER (PARTITION BY ts_code ORDER BY trade_date)) / LAG(close, 1) OVER (PARTITION BY ts_code ORDER BY trade_date) * 100 as change_pct
            FROM daily
            WHERE trade_date >= (SELECT MAX(trade_date) - INTERVAL '5 days' FROM daily)
            ORDER BY ts_code, trade_date DESC
        """
        df = _loader.conn.execute(query).fetchdf()

        # 只保留每个股票的最新记录
        df = df.drop_duplicates(subset=['ts_code'], keep='first')
        return df
    except Exception as e:
        st.error(f"获取市场数据失败: {e}")
        return pd.DataFrame()


# ============== 辅助函数 ==============

def format_market_cap(value: float) -> str:
    """格式化市值显示"""
    if pd.isna(value):
        return "-"
    if value >= 1e12:
        return f"{value/1e12:.2f}万亿"
    elif value >= 1e8:
        return f"{value/1e8:.0f}亿"
    else:
        return f"{value/1e4:.0f}万"


def format_volume(value: float) -> str:
    """格式化成交量显示"""
    if pd.isna(value):
        return "-"
    if value >= 1e8:
        return f"{value/1e8:.2f}亿"
    elif value >= 1e4:
        return f"{value/1e4:.0f}万"
    else:
        return f"{value:.0f}"


def get_color_by_change(change_pct: float) -> str:
    """根据涨跌幅返回颜色"""
    if change_pct > 0:
        return "#EF4444"  # 红色（A股上涨）
    elif change_pct < 0:
        return "#10B981"  # 绿色（A股下跌）
    else:
        return "#9CA3AF"  # 灰色


# ============== 渲染函数 ==============

def render_header():
    """渲染页面标题"""
    st.markdown("""
    <style>
    .viz-header {
        font-size: 2rem;
        font-weight: bold;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-muted);
    }
    </style>
    <div class="viz-header">📊 股票数据可视化展示</div>
    """, unsafe_allow_html=True)


def render_market_summary(market_data: pd.DataFrame):
    """渲染市场概览统计"""
    if market_data.empty:
        st.info("暂无市场数据")
        return

    # 计算统计指标
    total_stocks = len(market_data)
    up_stocks = len(market_data[market_data['change_pct'] > 0])
    down_stocks = len(market_data[market_data['change_pct'] < 0])
    flat_stocks = total_stocks - up_stocks - down_stocks

    # 涨跌家数
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #3B82F6;">{total_stocks}</div>
            <div class="metric-label">总股票数</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #EF4444;">{up_stocks}</div>
            <div class="metric-label">上涨 📈</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #10B981;">{down_stocks}</div>
            <div class="metric-label">下跌 📉</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #9CA3AF;">{flat_stocks}</div>
            <div class="metric-label">平盘 ➖</div>
        </div>
        """, unsafe_allow_html=True)


def render_charts(stocks_df: pd.DataFrame, market_data: pd.DataFrame, loader: StockDataLoader):
    """渲染统计图表"""
    # 涨跌幅分布直方图
    st.subheader("📊 涨跌幅分布")
    if not market_data.empty and 'change_pct' in market_data.columns:
        fig = px.histogram(
            market_data,
            x='change_pct',
            nbins=30,
            color_discrete_sequence=['#3B82F6'],
            labels={'change_pct': '涨跌幅 (%)', 'count': '股票数量'}
        )
        fig.update_layout(
            xaxis_title="涨跌幅 (%)",
            yaxis_title="股票数量",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=50),
            height=350
        )
        # 添加零线
        fig.add_vline(x=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("暂无涨跌幅数据")


def render_filters(stocks_df: pd.DataFrame) -> Dict:
    """渲染筛选面板，返回筛选条件"""
    st.subheader("🔍 筛选条件")

    filters = {}

    # 关键字搜索
    filters['search'] = st.text_input("搜索股票（代码/名称）", placeholder="输入股票代码或名称...")

    # 行业筛选
    if 'industry' in stocks_df.columns and not stocks_df.empty:
        industries = ['全部'] + sorted(stocks_df['industry'].dropna().unique().tolist())
        filters['industry'] = st.selectbox("行业", industries)
    else:
        filters['industry'] = '全部'

    # 市值筛选
    market_cap_options = {
        '全部': (0, float('inf')),
        '超大盘 (>5000亿)': (5000e8, float('inf')),
        '大盘 (1000-5000亿)': (1000e8, 5000e8),
        '中盘 (200-1000亿)': (200e8, 1000e8),
        '小盘 (50-200亿)': (50e8, 200e8),
        '微盘 (<50亿)': (0, 50e8)
    }
    filters['market_cap'] = st.selectbox("市值范围", list(market_cap_options.keys()))
    filters['market_cap_range'] = market_cap_options[filters['market_cap']]

    # 涨跌幅筛选
    change_options = ['全部', '涨停 (≥10%)', '大幅上涨 (5-10%)', '上涨 (0-5%)', '下跌 (-5-0%)', '大幅下跌 (-10--5%)', '跌停 (≤-10%)']
    filters['change'] = st.selectbox("涨跌幅", change_options)

    return filters


def apply_filters(stocks_df: pd.DataFrame, market_data: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """应用筛选条件"""
    # 合并股票基本信息和市场数据
    if not market_data.empty and not stocks_df.empty:
        # 标准化股票代码格式
        stocks_df_copy = stocks_df.copy()
        market_data_copy = market_data.copy()

        # 确保代码格式一致
        if 'code' in stocks_df_copy.columns:
            stocks_df_copy['code_std'] = stocks_df_copy['code'].astype(str).str.replace(r'\.(SH|SZ|BJ)$', '', regex=True)
        if 'ts_code' in market_data_copy.columns:
            market_data_copy['code_std'] = market_data_copy['ts_code'].astype(str).str.replace(r'\.(SH|SZ|BJ)$', '', regex=True)

        df = stocks_df_copy.merge(market_data_copy, on='code_std', how='left')
    else:
        df = stocks_df.copy()

    # 应用搜索筛选
    if filters.get('search'):
        search = filters['search'].lower()
        mask = (
            df['code'].astype(str).str.lower().str.contains(search, na=False) |
            df['name'].astype(str).str.lower().str.contains(search, na=False)
        )
        df = df[mask]

    # 应用行业筛选
    if filters.get('industry') and filters['industry'] != '全部' and 'industry' in df.columns:
        df = df[df['industry'] == filters['industry']]

    # 应用市值筛选
    if filters.get('market_cap_range') and 'total_mv' in df.columns:
        min_cap, max_cap = filters['market_cap_range']
        df = df[(df['total_mv'] >= min_cap) & (df['total_mv'] <= max_cap)]

    # 应用涨跌幅筛选
    if filters.get('change') and filters['change'] != '全部' and 'change_pct' in df.columns:
        change = filters['change']
        if change == '涨停 (≥10%)':
            df = df[df['change_pct'] >= 10]
        elif change == '大幅上涨 (5-10%)':
            df = df[(df['change_pct'] >= 5) & (df['change_pct'] < 10)]
        elif change == '上涨 (0-5%)':
            df = df[(df['change_pct'] >= 0) & (df['change_pct'] < 5)]
        elif change == '下跌 (-5-0%)':
            df = df[(df['change_pct'] >= -5) & (df['change_pct'] < 0)]
        elif change == '大幅下跌 (-10--5%)':
            df = df[(df['change_pct'] >= -10) & (df['change_pct'] < -5)]
        elif change == '跌停 (≤-10%)':
            df = df[df['change_pct'] <= -10]

    return df


def render_stock_table(df: pd.DataFrame, loader: StockDataLoader):
    """渲染股票列表表格"""
    st.subheader(f"📋 股票列表 (共 {len(df)} 只)")

    if df.empty:
        st.info("没有符合条件的股票")
        return

    # 分页
    page_size = 50
    total_pages = max(1, (len(df) + page_size - 1) // page_size)

    if 'page' not in st.session_state:
        st.session_state.page = 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ 上一页") and st.session_state.page > 1:
            st.session_state.page -= 1
            st.rerun()

    with col2:
        st.markdown(f"<div style='text-align: center;'>第 {st.session_state.page} / {total_pages} 页</div>", unsafe_allow_html=True)

    with col3:
        if st.button("下一页 ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1
            st.rerun()

    # 计算当前页数据
    start_idx = (st.session_state.page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    page_df = df.iloc[start_idx:end_idx]

    # 显示表格
    display_data = []
    for _, row in page_df.iterrows():
        code = row.get('code', row.get('symbol', '-'))
        name = row.get('name', '-')
        industry = row.get('industry', '-')

        # 价格和涨跌幅
        close = row.get('close', None)
        change_pct = row.get('change_pct', None)

        if close is not None and not pd.isna(close):
            price_str = f"{close:.2f}"
        else:
            price_str = "-"

        if change_pct is not None and not pd.isna(change_pct):
            change_str = f"{change_pct:+.2f}%"
            change_color = get_color_by_change(change_pct)
        else:
            change_str = "-"
            change_color = "#9CA3AF"

        # 成交量
        volume = row.get('volume', None)
        volume_str = format_volume(volume) if volume is not None else "-"

        # 市值
        market_cap = row.get('total_mv', None)
        market_cap_str = format_market_cap(market_cap)

        display_data.append({
            '代码': code,
            '名称': name,
            '行业': industry,
            '最新价': price_str,
            '涨跌幅': change_str,
            '涨跌颜色': change_color,
            '成交量': volume_str,
            '市值': market_cap_str
        })

    display_df = pd.DataFrame(display_data)

    # 使用自定义样式显示表格
    st.dataframe(
        display_df[['代码', '名称', '行业', '最新价', '涨跌幅', '成交量', '市值']],
        width='stretch',
        height=500,
        column_config={
            '代码': st.column_config.TextColumn('代码', width='small'),
            '名称': st.column_config.TextColumn('名称', width='small'),
            '行业': st.column_config.TextColumn('行业', width='medium'),
            '最新价': st.column_config.TextColumn('最新价', width='small'),
            '涨跌幅': st.column_config.TextColumn('涨跌幅', width='small'),
            '成交量': st.column_config.TextColumn('成交量', width='small'),
            '市值': st.column_config.TextColumn('市值', width='small'),
        }
    )

    # ========== 使用 Tabs 分隔不同板块 ==========
    st.markdown("---")

    tab1, tab2 = st.tabs(["📈 个股分析", "⭐ 自选对比"])

    # ===== Tab 1: 个股分析 =====
    with tab1:
        st.subheader("个股详细分析")

        # 初始化 session state
        if 'chart_start_date' not in st.session_state:
            st.session_state.chart_start_date = (datetime.now() - timedelta(days=90)).date()
        if 'chart_end_date' not in st.session_state:
            st.session_state.chart_end_date = datetime.now().date()
        if 'chart_selected_code' not in st.session_state:
            st.session_state.chart_selected_code = None
        if 'chart_time_range' not in st.session_state:
            st.session_state.chart_time_range = "近3月"

        # 股票选择
        available_codes = df['code'].tolist() if 'code' in df.columns else []

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            selected_code = st.selectbox(
                "选择股票",
                options=available_codes,
                format_func=lambda x: f"{x} - {df[df['code']==x]['name'].iloc[0] if 'name' in df.columns and not df[df['code']==x].empty else ''}",
                key="single_stock_select"
            )

        with col2:
            time_range = st.selectbox(
                "时间范围",
                ["近1月", "近3月", "近6月", "近1年", "自定义"],
                index=1,
                key="single_time_range"
            )

        # 根据选择更新日期
        end_date_default = datetime.now()
        if time_range == "近1月":
            start_date_default = end_date_default - timedelta(days=30)
        elif time_range == "近3月":
            start_date_default = end_date_default - timedelta(days=90)
        elif time_range == "近6月":
            start_date_default = end_date_default - timedelta(days=180)
        elif time_range == "近1年":
            start_date_default = end_date_default - timedelta(days=365)
        else:  # 自定义
            start_date_default = end_date_default - timedelta(days=90)

        # 自定义日期选择
        if time_range == "自定义":
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                start_date = st.date_input(
                    "开始日期",
                    value=start_date_default.date(),
                    key="custom_start_date"
                )
            with col_date2:
                end_date = st.date_input(
                    "结束日期",
                    value=end_date_default.date(),
                    key="custom_end_date"
                )
        else:
            start_date = start_date_default.date()
            end_date = end_date_default.date()

        # 按钮行
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

        with col_btn1:
            if st.button("🔍 查询图表", use_container_width=True, type="primary", key="btn_query_single"):
                st.session_state.chart_selected_code = selected_code
                st.session_state.chart_start_date = start_date
                st.session_state.chart_end_date = end_date
                st.session_state.chart_time_range = time_range
                st.session_state.show_single_chart = True

        with col_btn2:
            if selected_code and selected_code not in st.session_state.watchlist:
                if st.button(f"⭐ 添加到自选", use_container_width=True, key="btn_add_watch"):
                    add_to_watchlist(selected_code, df)
                    st.rerun()
            elif selected_code:
                st.success(f"✅ {selected_code} 已在自选")

        # 显示图表
        if st.session_state.get('show_single_chart') and st.session_state.chart_selected_code:
            render_mini_chart(
                st.session_state.chart_selected_code,
                loader,
                st.session_state.chart_start_date,
                st.session_state.chart_end_date
            )
        else:
            st.info("👆 请选择股票并点击「查询图表」按钮")

    # ===== Tab 2: 自选对比 =====
    with tab2:
        render_multi_stock_chart_tab(df, loader)


def render_mini_chart(stock_code: str, loader: StockDataLoader, start_date, end_date):
    """渲染个股K线图"""
    try:
        # 将 date 对象转换为 datetime 以便兼容
        if hasattr(start_date, 'strftime'):
            start_str = start_date.strftime('%Y-%m-%d')
        else:
            start_str = start_date
        if hasattr(end_date, 'strftime'):
            end_str = end_date.strftime('%Y-%m-%d')
        else:
            end_str = end_date

        # 首先尝试获取用户选择的时间范围数据
        data = loader.get_stock_data(stock_code, start_str, end_str)

        # 如果数据不足，尝试获取更长时间范围的数据
        if data.empty or len(data) < 5:
            st.info(f"选定时间段 ({start_str} ~ {end_str}) 数据不足，尝试获取历史数据...")

            # 尝试获取最近2年的数据
            extended_end = datetime.now()
            extended_start = extended_end - timedelta(days=730)
            data = loader.get_stock_data(
                stock_code,
                extended_start.strftime('%Y-%m-%d'),
                extended_end.strftime('%Y-%m-%d')
            )

            if data.empty or len(data) < 5:
                st.warning(f"⚠️ 该股票数据不足（仅 {len(data)} 条），可能已退市或停牌")
                return

            st.success(f"✅ 已获取到历史数据：{data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}，共 {len(data)} 个交易日")
        else:
            st.info(f"📊 数据范围：{data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}，共 {len(data)} 个交易日")

        # 使用全部获取到的数据，不限于20个交易日

        # 计算均线
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA10'] = data['Close'].rolling(window=10).mean()
        data['MA20'] = data['Close'].rolling(window=20).mean()

        # 创建K线图
        fig = go.Figure()

        # K线
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='K线',
            increasing_line_color='#EF4444',
            decreasing_line_color='#10B981'
        ))

        # 均线
        fig.add_trace(go.Scatter(
            x=data.index, y=data['MA5'],
            mode='lines',
            name='MA5',
            line=dict(color='#F59E0B', width=1)
        ))

        if len(data) >= 10:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MA10'],
                mode='lines',
                name='MA10',
                line=dict(color='#3B82F6', width=1)
            ))

        # 布局 - 使用 category 类型跳过非交易日
        date_range_str = f"{data.index[0].strftime('%Y-%m-%d')} ~ {data.index[-1].strftime('%Y-%m-%d')}"
        fig.update_layout(
            title=f"{stock_code} - {date_range_str} ({len(data)}个交易日)",
            xaxis_title="日期",
            yaxis_title="价格",
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis_rangeslider_visible=False,
            xaxis=dict(
                type='category',  # 按数据点显示，跳过非交易日
                tickmode='auto',
                nticks=10,
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=30)
        )

        st.plotly_chart(fig, width='stretch')

        # 显示关键指标
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest

        change = latest['Close'] - prev['Close']
        change_pct = (change / prev['Close']) * 100 if prev['Close'] != 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("最新价", f"{latest['Close']:.2f}", f"{change:+.2f}")

        with col2:
            st.metric("涨跌幅", f"{change_pct:+.2f}%")

        with col3:
            period_high = data['High'].max()
            st.metric(f"期间最高", f"{period_high:.2f}")

        with col4:
            period_low = data['Low'].min()
            st.metric(f"期间最低", f"{period_low:.2f}")

    except Exception as e:
        error_msg = str(e)
        if "No magic bytes found" in error_msg or "parquet" in error_msg.lower():
            st.error("📁 数据文件损坏或缺失")
            st.info("""
            可能原因：
            1. 该时间段的数据文件损坏
            2. 数据尚未同步到本地

            建议：尝试选择其他时间段，或检查数据同步状态
            """)
        else:
            st.error(f"加载图表失败: {e}")
            st.info("建议：尝试选择其他股票或时间段")


def init_watchlist_state():
    """初始化自选股票相关 session state"""
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    if 'watchlist_colors' not in st.session_state:
        # 预定义一些颜色用于区分不同股票
        st.session_state.watchlist_colors = [
            '#EF4444', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6',
            '#EC4899', '#06B6D4', '#F97316', '#84CC16', '#6366F1'
        ]


def add_to_watchlist(stock_code: str, stocks_df: pd.DataFrame):
    """添加股票到自选列表"""
    if stock_code not in st.session_state.watchlist:
        st.session_state.watchlist.append(stock_code)
        # 获取股票名称
        stock_name = ""
        if not stocks_df.empty and 'code' in stocks_df.columns:
            stock_info = stocks_df[stocks_df['code'] == stock_code]
            if not stock_info.empty and 'name' in stock_info.columns:
                stock_name = stock_info.iloc[0]['name']
        st.success(f"✅ 已添加 {stock_code} {stock_name} 到自选")
    else:
        st.info("该股票已在自选列表中")


def remove_from_watchlist(stock_code: str):
    """从自选列表移除股票"""
    if stock_code in st.session_state.watchlist:
        st.session_state.watchlist.remove(stock_code)
        st.success(f"✅ 已从自选列表移除 {stock_code}")


def render_watchlist_manager(stocks_df: pd.DataFrame):
    """渲染自选股票管理面板"""
    st.subheader("⭐ 自选股票")

    # 添加自选股票
    col1, col2 = st.columns([3, 1])
    with col1:
        if not stocks_df.empty and 'code' in stocks_df.columns:
            new_stock = st.selectbox(
                "添加股票到自选",
                options=stocks_df['code'].tolist(),
                format_func=lambda x: f"{x} - {stocks_df[stocks_df['code']==x]['name'].iloc[0] if 'name' in stocks_df.columns and not stocks_df[stocks_df['code']==x].empty else ''}",
                key="watchlist_add"
            )
        else:
            new_stock = st.text_input("输入股票代码")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ 添加", use_container_width=True):
            if new_stock:
                add_to_watchlist(new_stock, stocks_df)
                st.rerun()

    # 显示自选列表
    if st.session_state.watchlist:
        st.markdown("**当前自选：**")
        for i, code in enumerate(st.session_state.watchlist):
            col1, col2 = st.columns([3, 1])
            with col1:
                # 获取股票名称
                stock_name = ""
                if not stocks_df.empty and 'code' in stocks_df.columns:
                    stock_info = stocks_df[stocks_df['code'] == code]
                    if not stock_info.empty and 'name' in stock_info.columns:
                        stock_name = stock_info.iloc[0]['name']
                color = st.session_state.watchlist_colors[i % len(st.session_state.watchlist_colors)]
                st.markdown(f"<span style='color: {color};'>●</span> **{code}** {stock_name}", unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"remove_{code}"):
                    remove_from_watchlist(code)
                    st.rerun()
    else:
        st.info("暂无自选股票，请添加")


def render_multi_stock_chart_tab(stocks_df: pd.DataFrame, loader: StockDataLoader):
    """渲染多股票走势对比图 (Tab版本)"""
    if not st.session_state.watchlist:
        st.info("⭐ 请在左侧添加股票到自选列表")
        return

    st.subheader("自选股票走势对比")

    # 初始化 session state
    if 'multi_chart_start_date' not in st.session_state:
        st.session_state.multi_chart_start_date = (datetime.now() - timedelta(days=90)).date()
    if 'multi_chart_end_date' not in st.session_state:
        st.session_state.multi_chart_end_date = datetime.now().date()
    if 'multi_chart_time_range' not in st.session_state:
        st.session_state.multi_chart_time_range = "近3月"

    # 时间范围选择
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        time_range = st.selectbox(
            "时间范围",
            ["近1月", "近3月", "近6月", "近1年"],
            index=1,
            key="multi_time_range_tab"
        )

    # 根据选择设置日期
    end_date_default = datetime.now()
    if time_range == "近1月":
        start_date_default = end_date_default - timedelta(days=30)
    elif time_range == "近3月":
        start_date_default = end_date_default - timedelta(days=90)
    elif time_range == "近6月":
        start_date_default = end_date_default - timedelta(days=180)
    else:  # 近1年
        start_date_default = end_date_default - timedelta(days=365)

    start_date = start_date_default.date()
    end_date = end_date_default.date()

    with col3:
        st.markdown(f"**{start_date} ~ {end_date}**")

    # 查询按钮
    if st.button("🔍 查询对比图", use_container_width=True, type="primary", key="btn_query_multi"):
        st.session_state.multi_chart_start_date = start_date
        st.session_state.multi_chart_end_date = end_date
        st.session_state.multi_chart_time_range = time_range
        st.session_state.show_multi_chart = True

    # 显示对比图
    if st.session_state.get('show_multi_chart'):
        with st.spinner("正在加载自选股票数据..."):
            fig = go.Figure()
            valid_stocks = []

            for i, stock_code in enumerate(st.session_state.watchlist):
                try:
                    data = loader.get_stock_data(
                        stock_code,
                        st.session_state.multi_chart_start_date.strftime('%Y-%m-%d'),
                        st.session_state.multi_chart_end_date.strftime('%Y-%m-%d')
                    )

                    if not data.empty and len(data) >= 2:
                        valid_stocks.append(stock_code)
                        # 获取股票名称
                        stock_name = stock_code
                        if not stocks_df.empty and 'code' in stocks_df.columns:
                            stock_info = stocks_df[stocks_df['code'] == stock_code]
                            if not stock_info.empty and 'name' in stock_info.columns:
                                stock_name = f"{stock_code} {stock_info.iloc[0]['name']}"

                        # 标准化价格（以第一天为基准100）
                        normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100

                        color = st.session_state.watchlist_colors[i % len(st.session_state.watchlist_colors)]

                        fig.add_trace(go.Scatter(
                            x=data.index,
                            y=normalized_price,
                            mode='lines',
                            name=stock_name,
                            line=dict(color=color, width=2)
                        ))

                except Exception as e:
                    st.warning(f"加载 {stock_code} 失败: {e}")

            if len(fig.data) > 0:
                fig.update_layout(
                    title=f"自选股票走势对比 (标准化，基准=100) - {st.session_state.multi_chart_time_range}",
                    xaxis_title="日期",
                    yaxis_title="相对涨幅 (%)",
                    height=450,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                    xaxis=dict(
                        type='category',  # 按数据点显示，跳过非交易日
                        tickmode='auto',
                        nticks=10,
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    hovermode='x unified'
                )

                # 添加基准线
                fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)

                st.plotly_chart(fig, width='stretch')

                # 显示统计信息
                st.markdown("**📊 涨跌幅统计**")
                stats_data = []
                for i, stock_code in enumerate(valid_stocks):
                    try:
                        data = loader.get_stock_data(
                            stock_code,
                            st.session_state.multi_chart_start_date.strftime('%Y-%m-%d'),
                            st.session_state.multi_chart_end_date.strftime('%Y-%m-%d')
                        )
                        if not data.empty and len(data) >= 2:
                            start_price = data['Close'].iloc[0]
                            end_price = data['Close'].iloc[-1]
                            change_pct = ((end_price - start_price) / start_price) * 100

                            stock_name = stock_code
                            if not stocks_df.empty and 'code' in stocks_df.columns:
                                stock_info = stocks_df[stocks_df['code'] == stock_code]
                                if not stock_info.empty and 'name' in stock_info.columns:
                                    stock_name = stock_info.iloc[0]['name']

                            stats_data.append({
                                '股票': f"{stock_code} {stock_name}",
                                '起始价': f"{start_price:.2f}",
                                '最新价': f"{end_price:.2f}",
                                '涨跌幅': f"{change_pct:+.2f}%",
                                '涨跌额': f"{end_price - start_price:+.2f}"
                            })
                    except:
                        continue

                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    st.dataframe(stats_df, width='stretch', hide_index=True)
            else:
                st.warning("⚠️ 所选时间段内暂无有效的自选股票数据")
    else:
        st.info("👆 请选择时间范围并点击「查询对比图」按钮")


def render_stock_overview():
    """主渲染函数 - 股票数据可视化展示界面"""
    render_header()

    # 获取数据加载器
    if 'data_loader' not in st.session_state:
        st.error("数据加载器未初始化")
        return

    loader = st.session_state.data_loader

    # 初始化自选股票状态
    init_watchlist_state()

    # 加载数据
    with st.spinner("📥 正在加载股票数据..."):
        stocks_df = get_all_stocks_cached(loader)
        market_data = get_latest_market_data(loader)

    if stocks_df.empty:
        st.error("无法获取股票列表，请检查数据库连接")
        return

    # 布局：左侧筛选面板，右侧内容
    left_col, right_col = st.columns([1, 3])

    with left_col:
        # 添加自选股票管理面板
        render_watchlist_manager(stocks_df)

        st.markdown("---")

        filters = render_filters(stocks_df)

    with right_col:
        # 应用筛选
        filtered_df = apply_filters(stocks_df, market_data, filters)

        # 市场概览
        render_market_summary(market_data)

        st.markdown("---")

        # 图表统计
        render_charts(filtered_df, market_data, loader)

        st.markdown("---")

        # 股票列表和个股分析/自选对比 (在Tabs中)
        render_stock_table(filtered_df, loader)


if __name__ == "__main__":
    # 测试用
    st.set_page_config(page_title="股票数据可视化", layout="wide")
    render_stock_overview()
