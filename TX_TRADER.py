import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# --- Config & State ---
st.set_page_config(page_title="TX TRADER", page_icon="logo.png", layout="wide")

# --- Custom CSS Injection ---
st.markdown("""
<style>
/* Base dark mode */
.stApp {
    background-color: #0b0e14;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0b0e14 !important;
}

/* Header/Toolbar styling */
header[data-testid="stHeader"] {
    background-color: #0b0e14 !important;
}

/* Typography styles */
[data-testid="stMetricLabel"] {
    color: #8b9bb4;
    font-size: 14px;
    font-weight: 500;
}

[data-testid="stMetricValue"] {
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
}

[data-testid="stMetricDelta"] {
    color: #00ff88 !important;
}

/* Glassmorphic Metric Cards */
[data-testid="metric-container"] {
    background: rgba(25, 30, 41, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 240, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.1);
}

/* Form and Trade Panel */
div[data-testid="stForm"] {
    background: rgba(25, 30, 41, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
}

/* Base Button Style (Main Area) */
.stButton>button {
    background: rgba(25, 30, 41, 0.8);
    color: white;
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 500;
    transition: 0.3s all ease;
    width: 100%;
}

.stButton>button:hover {
    border-color: #00f0ff;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
    transform: translateY(-1px);
}

/* Sidebar Navigation Buttons Specific Styling */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    color: #8b9bb4 !important;
    text-align: left !important;
    padding: 12px 16px !important;
    margin-bottom: 5px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(0, 240, 255, 0.3) !important;
    color: #00f0ff !important;
}

/* Primary/Active Navigation Button */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00f0ff 0%, #7000ff 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 240, 255, 0.3) !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

if 'balance' not in st.session_state:
    st.session_state.balance = 124563.00
if 'positions' not in st.session_state:
    st.session_state.positions = {
        "AAPL": 100, "MSFT": 50, "NVDA": 10,
        "RELIANCE.NS": 500, "TCS.NS": 250, "ABCAPITAL.NS": 1000, "INFY.NS": 300,
        "TSCO.L": 2000, "BP.L": 1500, "VOD.L": 4000, "HSBA.L": 800
    }
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {"name": "Vijay Odedara", "email": "vijay.odedara@tradex.pro", "tier": "Pro (Active)"}
if 'market' not in st.session_state:
    st.session_state.market = "USA"

# --- Shared UI ---
html_profile = f"""
<div style="display:flex; align-items:center; margin-bottom:10px;">
    <img src="https://ui-avatars.com/api/?name={st.session_state.user_profile['name'].replace(' ', '+')}&background=00f0ff&color=000" style="border-radius:50%; width:40px; height:40px; margin-right:10px;">
    <div>
        <h4 style="margin:0; padding:0; color:#fff; font-size:16px;">{st.session_state.user_profile['name']}</h4>
        <p style="margin:0; padding:0; color:#00ff88; font-size:12px;">{st.session_state.user_profile['tier']}</p>
    </div>
</div>
<hr>
"""
st.sidebar.markdown(html_profile, unsafe_allow_html=True)

try:
    st.logo("logo.png")
except AttributeError:
    st.sidebar.image("logo.png", width=100)

# --- Navigation ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

nav_options = {
    "Dashboard": "Dashboard📊",
    "Portfolio": "Portfolio💼",
    "Trading": "Trading💹",
    "Analytics": "Analytics📈",
    "Profile": "Profile👤"
}

for label, icon in nav_options.items():
    is_active = st.session_state.page == label
    if st.sidebar.button(icon, key=f"nav_{label}", width='stretch', type="primary" if is_active else "secondary"):
        st.session_state.page = label
        st.rerun()

page = st.session_state.page


st.sidebar.markdown("---")
# Market Selector
selected_market = st.sidebar.selectbox("Select Market", ["USA", "INDIA", "UK"], index=["USA", "INDIA", "UK"].index(st.session_state.market))
if selected_market != st.session_state.market:
    st.session_state.market = selected_market
    st.rerun()

market_currency_map = {"USA": "$", "INDIA": "₹", "UK": "£"}
currency_symbol = market_currency_map.get(st.session_state.market, "$")

st.sidebar.markdown("---")
st.sidebar.write(f"**Total Balance:** {currency_symbol}{st.session_state.balance:,.2f}")

# --- Helper Functions ---
@st.cache_data(ttl=10)
def fetch_stock_data(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if hist.empty:
            return None, None
            
        info = stock.fast_info
        current_price = info.last_price
        prev_close = info.previous_close
        
        return hist, {"price": current_price, "prev": prev_close}
    except Exception:
        # Retry with suffix if it's Indian or UK market and not already suffixed
        suffix = None
        if st.session_state.market == "INDIA" and not (ticker.endswith(".NS") or ticker.endswith(".BO")):
            suffix = ".NS"
        elif st.session_state.market == "UK" and not ticker.endswith(".L"):
            suffix = ".L"
            
        if suffix:
            try:
                stock_suffixed = yf.Ticker(f"{ticker}{suffix}")
                hist = stock_suffixed.history(period=period)
                if not hist.empty:
                    info = stock_suffixed.fast_info
                    return hist, {"price": info.last_price, "prev": info.previous_close, "ticker": f"{ticker}{suffix}"}
            except:
                pass
        return None, None

@st.fragment(run_every="2m")
def display_dashboard_chart(ticker, period):
    hist, stats = fetch_stock_data(ticker, period)
    if hist is not None:
        # Create subplots for Price and Volume
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, subplot_titles=(f'{ticker} Price', 'Volume'), 
                            row_width=[0.2, 0.7])

        # Candlestick chart for Price
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="Price"
        ), row=1, col=1)

        # Bar chart for Volume
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name="Volume",
            marker_color='rgba(0, 240, 255, 0.3)'
        ), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            title=f"{ticker} - Current: {currency_symbol}{stats['price']:.2f}",
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=50, b=0),
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(showgrid=False, color="#8b9bb4"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#8b9bb4"),
            xaxis2=dict(showgrid=False, color="#8b9bb4"),
            yaxis2=dict(showgrid=False, color="#8b9bb4")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to fetch data.")

@st.fragment(run_every="2m")
def render_dashboard_kpis():
    # Top KPI Row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Balance", f"{currency_symbol}{st.session_state.balance:,.2f}", "+2.4% Today")
    col2.metric("Monthly Profit", f"+{currency_symbol}8,240.50", "+12% vs last month")
    col3.metric("Active Positions", str(sum(st.session_state.positions.values())), "No change", delta_color="off")

@st.fragment(run_every="2m")
def render_dashboard_watchlist(selected_ticker, tickers):
    st.subheader("Watchlist")
    # Display small watchlist
    for t in tickers:
        col_t1, col_t2 = st.columns([2, 1])
        col_t1.write(f"**{t}**")
        with st.spinner(""):
            _, t_stats = fetch_stock_data(t, "1d")
            if t_stats and t_stats['price']:
                price = t_stats['price']
                prev = t_stats['prev']
                change = ((price - prev) / prev * 100) if prev else 0
                color = "#00ff88" if change >= 0 else "#ff4b4b"
                col_t2.markdown(f"<span style='color:{color}; font-weight:bold;'>{currency_symbol}{price:.2f} ({'+' if change >= 0 else ''}{change:.2f}%)</span>", unsafe_allow_html=True)
            else:
                col_t2.write("N/A")

def render_dashboard():
    st.title("Dashboard")
    
    render_dashboard_kpis()
    st.markdown("---")
    
    # Main Content Area
    main_col, side_col = st.columns([3, 1])
    
    with side_col:
        # We handle selectbox outside the fragment to avoid losing state while typing/selecting
        if st.session_state.market == "INDIA":
            tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ADANIENT.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "ABCAPITAL.NS"]
        elif st.session_state.market == "UK":
            tickers = ["TSCO.L", "HSBA.L", "BP.L", "VOD.L", "GSK.L", "AZN.L", "SHEL.L", "ULVR.L"]
        else:
            tickers = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]
            
        selected_ticker = st.selectbox("Select Asset to view:", tickers)
        render_dashboard_watchlist(selected_ticker, tickers)

    with main_col:
        st.subheader("Portfolio Performance")
        period_map = {"1D": "1d", "1W": "5d", "1M": "1mo", "6M": "6mo", "1Y": "1y", "ALL": "max"}
        period_key = st.select_slider("Timeframe", options=list(period_map.keys()), value="1M")

        # Display Live Chart Fragment
        display_dashboard_chart(selected_ticker, period_map[period_key])
            
    # Trade Panel below
    st.markdown("---")
    st.subheader("Quick Trade")
    with st.form("trade_form"):
        trade_action = st.radio("Action", ["Buy", "Sell"], horizontal=True)
        trade_ticker = st.selectbox("Asset", [selected_ticker, "RELIANCE.NS", "TCS.NS", "INFY.NS", "TSCO.L", "HSBA.L", "BP.L", "AAPL", "MSFT", "NVDA", "TSLA"])
        trade_amount = st.number_input(f"Amount ({'INR' if st.session_state.market == 'INDIA' else ('GBP' if st.session_state.market == 'UK' else 'USD')})", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("Place Order")
        
        if submitted:
            if trade_amount <= 0:
                st.error("Enter a valid amount.")
            else:
                # Fetch price for the selected ticker to calculate shares
                _, trade_stats = fetch_stock_data(trade_ticker, "1d")
                price = trade_stats['price'] if trade_stats and trade_stats['price'] else 0
                
                if price <= 0:
                    st.error("Could not determine current price for trade.")
                else:
                    qty = trade_amount / price
                    ticker_upper = trade_ticker.upper()
                    
                    if trade_action == "Buy":
                        if trade_amount > st.session_state.balance:
                            st.error("Insufficient funds!")
                        else:
                            st.session_state.balance -= trade_amount
                            st.session_state.positions[ticker_upper] = st.session_state.positions.get(ticker_upper, 0) + qty
                            st.success(f"Successfully bought {qty:.4f} shares of {ticker_upper}")
                            st.rerun()
                    elif trade_action == "Sell":
                        # Check if user has enough position to sell (allowing short selling for now if you want, 
                        # but usually better to check)
                        st.session_state.balance += trade_amount
                        st.session_state.positions[ticker_upper] = st.session_state.positions.get(ticker_upper, 0) - qty
                        st.success(f"Successfully sold {qty:.4f} shares of {ticker_upper}")
                        st.rerun()

def render_portfolio():
    st.title("Portfolio Allocation")
    
    # Check if there are any positions
    if not st.session_state.positions:
        st.info("You currently do not hold any assets. Head to the Trading tab to buy some!")
        return

    # Process live data for portfolio
    portfolio_data = []
    total_asset_value = 0.0
    
    with st.spinner("Fetching live portfolio valuation..."):
        for ticker, qty in st.session_state.positions.items():
            if qty > 0:
                hist, stats = fetch_stock_data(ticker, "1d")
                price = stats['price'] if stats['price'] else 0.0
                value = qty * price
                total_asset_value += value
                
                # Determine localized currency for this ticker
                t_currency = "₹" if ticker.endswith(".NS") or ticker.endswith(".BO") else ("£" if ticker.endswith(".L") else "$")
                
                portfolio_data.append({
                    "Asset": ticker,
                    "Shares": round(qty, 4),
                    "Price": price,
                    "Current Price": f"{t_currency}{price:,.2f}",
                    "Total Value": value,
                    "Currency": t_currency
                })
    
    # Display top level stats
    col1, col2 = st.columns(2)
    col1.metric("Total Asset Value", f"{currency_symbol}{total_asset_value:,.2f}")
    col2.metric("Total Account Value (Cash + Assets)", f"{currency_symbol}{(st.session_state.balance + total_asset_value):,.2f}")
    
    st.markdown("---")
    
    # Visualizations and Data Table
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        st.subheader("Allocation Map")
        if total_asset_value > 0:
            df_portfolio = pd.DataFrame(portfolio_data)
            
            # Pie Chart
            fig = go.Figure(data=[go.Pie(
                labels=df_portfolio['Asset'], 
                values=df_portfolio['Total Value'],
                hole=.4,
                marker=dict(colors=["#00f0ff", "#7000ff", "#ff007f", "#00ff88", "#f7931a"])
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                font=dict(color="#ffffff")
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.write("No active allocations to display.")
            
    with col_table:
        st.subheader("Holdings")
        if len(portfolio_data) > 0:
            # Format dataframe for display
            df_display = pd.DataFrame(portfolio_data)
            df_display['Total Value'] = df_display.apply(lambda x: f"{x['Currency']}{x['Total Value']:,.2f}", axis=1)
            st.dataframe(df_display[['Asset', 'Shares', 'Current Price', 'Total Value']], hide_index=True, width='stretch')
        else:
            st.write("No active holdings.")

@st.fragment(run_every="2m")
def display_trading_chart(ticker, period):
    hist, stats = fetch_stock_data(ticker, period)
    if hist is not None:
        # Create subplots for Price and Volume
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_width=[0.2, 0.7])

        # Candlestick chart for Price
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name="Price"
        ), row=1, col=1)

        # Bar chart for Volume
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name="Volume",
            marker_color='rgba(0, 240, 255, 0.3)'
        ), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            title=f"{ticker} Real-time Chart - Current: {currency_symbol}{stats['price']:.2f}",
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=0, t=50, b=0),
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(showgrid=False, color="#8b9bb4"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color="#8b9bb4"),
            xaxis2=dict(showgrid=False, color="#8b9bb4"),
            yaxis2=dict(showgrid=False, color="#8b9bb4")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Invalid ticker or failed to fetch data.")

def render_trading():
    st.title("Advanced Trading Terminal")
    
    col_chart, col_form = st.columns([3, 1])
    
    with col_chart:
        st.subheader("Market Data")
        if st.session_state.market == "INDIA":
            default_ticker = "RELIANCE.NS"
        elif st.session_state.market == "UK":
            default_ticker = "TSCO.L"
        else:
            default_ticker = "AAPL"
            
        trade_ticker_main = st.text_input(f"Enter Ticker Symbol (e.g. {default_ticker})", value=default_ticker)
        period_map = {"1D": "1d", "1W": "5d", "1M": "1mo", "3M": "3mo", "1Y": "1y", "ALL": "max"}
        period_key = st.select_slider("Select Timeframe", options=list(period_map.keys()), value="1M", key="trade_timeframe")
        
        # Display Live Candlestick Fragment
        display_trading_chart(trade_ticker_main.upper(), period_map[period_key])
            
    with col_form:
        # Fetch stats again locally for the trade form so it always has the current price
        _, form_stats = fetch_stock_data(trade_ticker_main.upper(), "1d")
        recent_price = form_stats['price'] if form_stats and 'price' in form_stats else 0.0
        
        st.subheader("Order Execution")
        st.write(f"**Available Buying Power:** {currency_symbol}{st.session_state.balance:,.2f}")
        
        with st.form("advanced_trade_form"):
            trade_action = st.radio("Side", ["Buy", "Sell"], horizontal=True)
            order_type = st.selectbox("Order Type", ["Market", "Limit", "Stop"])
            
            if order_type != "Market":
                st.number_input("Trigger Price", min_value=0.0, value=float(recent_price))
                
            trade_amount = st.number_input(f"Amount ({'INR' if st.session_state.market == 'INDIA' else ('GBP' if st.session_state.market == 'UK' else 'USD')})", min_value=0.0, step=100.0)
            submitted = st.form_submit_button("Submit Order")
            
            if submitted:
                if trade_amount <= 0:
                    st.error("Please enter a valid amount.")
                elif recent_price <= 0:
                    st.error("Could not determine the current market price for this ticker.")
                else:
                    ticker_upper = trade_ticker_main.upper()
                    qty = trade_amount / recent_price
                    
                    if trade_action == "Buy":
                        if trade_amount > st.session_state.balance:
                            st.error(f"Insufficient buying power! Needed: {trade_amount:,.2f}, Available: {st.session_state.balance:,.2f}")
                        else:
                            st.session_state.balance -= trade_amount
                            st.session_state.positions[ticker_upper] = st.session_state.positions.get(ticker_upper, 0) + qty
                            st.success(f"SUCCESS: Order Filled! Bought {qty:.4f} shares of {ticker_upper} at {recent_price:,.2f}")
                            st.balloons()
                            st.rerun()
                            
                    elif trade_action == "Sell":
                        # Check if they have the asset (allowing some margin for float errors)
                        current_holding = st.session_state.positions.get(ticker_upper, 0)
                        if current_holding < (qty * 0.99) and st.session_state.user_profile['tier'] != "Pro (Active)":
                            st.error(f"Insufficient holdings! You own {current_holding:.4f} shares but trying to sell ~{qty:.4f}")
                        else:
                            st.session_state.balance += trade_amount
                            st.session_state.positions[ticker_upper] = current_holding - qty
                            st.success(f"SUCCESS: Order Filled! Sold {qty:.4f} shares of {ticker_upper} at {recent_price:,.2f}")
                            st.info(f"Updated Balance: {st.session_state.balance:,.2f}")
                            st.rerun()

def render_analytics():
    st.title("Deep Analytics")
    st.markdown("Explore fundamental data models and core financial metrics.")
    
    ticker = st.text_input("Enter Ticker for Deep Analysis", value="AAPL")
    
    with st.spinner(f"Analyzing {ticker.upper()}..."):
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            if not info or 'shortName' not in info:
                st.error("No data found for this ticker.")
                return
                
            st.subheader(f"{info.get('shortName', ticker.upper())} ({ticker.upper()})")
            
            st.markdown("### Fundamentals")
            col1, col2, col3, col4 = st.columns(4)
            market_cap = info.get('marketCap', 0)
            col1.metric("Market Cap", f"{currency_symbol}{market_cap:,.0f}" if market_cap else "N/A")
            
            pe = info.get('trailingPE')
            col2.metric("P/E Ratio", f"{pe:.2f}" if pe else "N/A")
            
            high52 = info.get('fiftyTwoWeekHigh')
            col3.metric("52 Wk High", f"{currency_symbol}{high52:.2f}" if high52 else "N/A")
            
            low52 = info.get('fiftyTwoWeekLow')
            col4.metric("52 Wk Low", f"{currency_symbol}{low52:.2f}" if low52 else "N/A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col5, col6, col7, col8 = st.columns(4)
            div = info.get('dividendYield')
            col5.metric("Div Yield", f"{div*100:.2f}%" if div else "N/A")
            
            beta = info.get('beta')
            col6.metric("Beta", f"{beta:.2f}" if beta else "N/A")
            
            margin = info.get('profitMargins')
            col7.metric("Profit Margin", f"{margin*100:.2f}%" if margin else "N/A")
            
            vol = info.get('averageVolume')
            col8.metric("Vol (Avg)", f"{vol:,.0f}" if vol else "N/A")
            
            st.markdown("---")
            st.markdown("### Company Profile")
            st.write(f"**Sector:** {info.get('sector', 'N/A')} | **Industry:** {info.get('industry', 'N/A')}")
            
            with st.expander("Read Full Business Summary"):
                st.write(info.get('longBusinessSummary', 'No summary available.'))
                
        except Exception as e:
            st.error("Error fetching analytics data. Please ensure the ticker is valid.")
            
    st.markdown("---")
    st.markdown("## Company Profiles")
    st.write("Quickly view the business summaries for all assets currently in your portfolio:")
    
    if st.session_state.positions:
        for pos_ticker in st.session_state.positions.keys():
            with st.expander(f"{pos_ticker} - Company Profile"):
                try:
                    pos_info = yf.Ticker(pos_ticker).info
                    st.write(f"**Sector:** {pos_info.get('sector', 'N/A')} | **Industry:** {pos_info.get('industry', 'N/A')}")
                    st.write(pos_info.get('longBusinessSummary', 'No summary available.'))
                except:
                    st.write("Could not load profile for this asset.")
    else:
        st.info("You do not hold any assets in your portfolio to display here.")


def render_profile():
    st.title("User Profile")
    st.markdown("Manage your account settings and preferences here.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Account Details")
        with st.form("profile_form"):
            new_name = st.text_input("Full Name", value=st.session_state.user_profile['name'])
            new_email = st.text_input("Email", value=st.session_state.user_profile['email'])
            
            # Map tier list handling
            tier_options = ["Basic", "Pro (Active)", "Institutional"]
            current_tier_idx = tier_options.index(st.session_state.user_profile['tier']) if st.session_state.user_profile['tier'] in tier_options else 1
            new_tier = st.selectbox("Account Tier", tier_options, index=current_tier_idx)
            
            currency_options = ["USD", "INR", "GBP", "EUR", "JPY"]
            currency_idx = currency_options.index("GBP") if st.session_state.market == "UK" else (1 if st.session_state.market == "INDIA" else 0)
            st.selectbox("Default Currency", currency_options, index=currency_idx)
            
            submitted_profile = st.form_submit_button("Save Changes")
            if submitted_profile:
                if not new_name.strip():
                    st.error("Name cannot be blank.")
                else:
                    st.session_state.user_profile['name'] = new_name
                    st.session_state.user_profile['email'] = new_email
                    st.session_state.user_profile['tier'] = new_tier
                    st.success("Account Details updated successfully!")
                    st.rerun()
        
    with col2:
        st.subheader("Security & API")
        st.markdown("**Member Since:** January 12th, 2026")
        st.markdown("**Last Login:** *Just now* from Seattle, WA")
        with st.form("security_form"):
            st.text_input("Brokerage API Key", type="password", value="TRADEX_API_DEMO_KEY")
            st.checkbox("Enable Two-Factor Authentication (2FA)", value=True)
            st.checkbox("Email me Trade Confirmations")
            submitted_security = st.form_submit_button("Update Security")
            if submitted_security:
                st.success("Security settings and API keys updated successfully!")

# --- Router ---
if page == "Dashboard":
    render_dashboard()
elif page == "Portfolio":
    render_portfolio()
elif page == "Trading":
    render_trading()
elif page == "Analytics":
    render_analytics()
elif page == "Profile":
    render_profile()
