import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import time

# Page config
st.set_page_config(
    page_title="AI Crypto Trading Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .profit-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .loss-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .trade-log {
        background: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'cash': 10000.0,
        'positions': {},
        'trade_history': [],
        'pnl_history': [],
        'start_value': 10000.0,
        'start_time': datetime.now()
    }

# AI API Call Function
def call_ai_api(prompt, api_key, base_url, model_name):
    """Call AI API with OpenAI-compatible format"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an elite crypto trading AI based on DeepSeek's winning Alpha Arena strategy."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"API Error: {str(e)}"

# Helper functions
def get_crypto_price(symbol):
    """Get real-time crypto price from Binance API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return None

def get_market_data(symbol, interval='1h', limit=100):
    """Get historical market data"""
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={interval}&limit={limit}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                         'close_time', 'quote_volume', 'trades', 'taker_buy_base', 
                                         'taker_buy_quote', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    except:
        return None

def calculate_portfolio_value():
    """Calculate current portfolio value"""
    total = st.session_state.portfolio['cash']
    
    for symbol, position in st.session_state.portfolio['positions'].items():
        current_price = get_crypto_price(symbol)
        if current_price:
            position_value = position['amount'] * current_price
            total += position_value
    
    return total

def execute_trade(action, symbol, amount, leverage=1.0):
    """Execute a trade (paper trading)"""
    current_price = get_crypto_price(symbol)
    if not current_price:
        return False, "Failed to get price"
    
    portfolio = st.session_state.portfolio
    
    if action == "BUY":
        cost = (amount * current_price) / leverage
        if portfolio['cash'] < cost:
            return False, "Insufficient funds"
        
        portfolio['cash'] -= cost
        
        if symbol in portfolio['positions']:
            old_pos = portfolio['positions'][symbol]
            new_amount = old_pos['amount'] + amount
            new_avg_price = ((old_pos['amount'] * old_pos['entry_price']) + (amount * current_price)) / new_amount
            portfolio['positions'][symbol] = {
                'amount': new_amount,
                'entry_price': new_avg_price,
                'leverage': leverage
            }
        else:
            portfolio['positions'][symbol] = {
                'amount': amount,
                'entry_price': current_price,
                'leverage': leverage
            }
        
        trade_log = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'BUY',
            'symbol': symbol,
            'amount': amount,
            'price': current_price,
            'leverage': leverage,
            'cost': cost
        }
        portfolio['trade_history'].append(trade_log)
        return True, f"Bought {amount:.6f} {symbol} at ${current_price:.2f} (Leverage: {leverage}x)"
    
    elif action == "SELL":
        if symbol not in portfolio['positions']:
            return False, "No position to sell"
        
        position = portfolio['positions'][symbol]
        if position['amount'] < amount:
            return False, "Insufficient position size"
        
        proceeds = amount * current_price
        profit = (current_price - position['entry_price']) * amount * position['leverage']
        
        portfolio['cash'] += proceeds
        position['amount'] -= amount
        
        if position['amount'] <= 0:
            del portfolio['positions'][symbol]
        
        trade_log = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'SELL',
            'symbol': symbol,
            'amount': amount,
            'price': current_price,
            'profit': profit,
            'proceeds': proceeds
        }
        portfolio['trade_history'].append(trade_log)
        return True, f"Sold {amount:.6f} {symbol} at ${current_price:.2f} (Profit: ${profit:.2f})"
    
    return False, "Invalid action"

# Header
st.markdown('<h1 class="main-header">🚀 AI Crypto Trading Agent</h1>', unsafe_allow_html=True)
st.markdown("### Alpha Arena Style - DeepSeek Strategy | Paper Trading with Real-Time Prices")

# Sidebar
with st.sidebar:
    st.header("🔐 API Configuration")
    
    api_provider = st.selectbox(
        "AI Model Provider",
        ["Qwen (FREE)", "DeepSeek", "Custom API"],
        help="Qwen is completely FREE!"
    )
    
    if api_provider == "Qwen (FREE)":
        st.success("🎉 Qwen is 100% FREE!")
        st.info("Get your FREE API key at: https://dashscope.aliyun.com")
        api_key = st.text_input("Dashscope API Key", type="password",
                               help="Sign up at dashscope.aliyun.com for free!")
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        model_name = "qwen-plus"
    elif api_provider == "DeepSeek":
        api_key = st.text_input("DeepSeek API Key", type="password", 
                               help="Get from platform.deepseek.com")
        base_url = "https://api.deepseek.com/v1"
        model_name = "deepseek-chat"
    else:
        api_key = st.text_input("API Key", type="password")
        base_url = st.text_input("Base URL", placeholder="https://api.example.com/v1")
        model_name = st.text_input("Model Name", placeholder="model-name")
    
    st.divider()
    st.header("⚙️ Trading Parameters")
    
    trading_symbols = st.multiselect(
        "Trading Pairs",
        ["BTC", "ETH", "SOL", "BNB", "DOGE", "XRP", "ADA", "AVAX"],
        default=["BTC", "ETH"],
        help="Same assets as Alpha Arena"
    )
    
    max_leverage = st.slider("Max Leverage", 1, 20, 5)
    risk_per_trade = st.slider("Risk Per Trade (%)", 1, 20, 5)
    
    trading_strategy = st.selectbox(
        "Strategy Style",
        ["Aggressive (Alpha Arena Winner)", "Balanced", "Conservative"]
    )
    
    st.divider()
    st.header("📊 Portfolio Status")
    
    current_value = calculate_portfolio_value()
    profit_loss = current_value - st.session_state.portfolio['start_value']
    profit_pct = (profit_loss / st.session_state.portfolio['start_value']) * 100
    
    st.metric("Portfolio Value", f"${current_value:.2f}", 
             delta=f"${profit_loss:.2f} ({profit_pct:.2f}%)")
    st.metric("Cash", f"${st.session_state.portfolio['cash']:.2f}")
    st.metric("Open Positions", len(st.session_state.portfolio['positions']))
    
    elapsed = datetime.now() - st.session_state.portfolio['start_time']
    hours = elapsed.total_seconds() / 3600
    st.metric("Trading Hours", f"{hours:.1f}h")
    
    if st.button("🔄 Reset Portfolio", type="secondary"):
        st.session_state.portfolio = {
            'cash': 10000.0,
            'positions': {},
            'trade_history': [],
            'pnl_history': [],
            'start_value': 10000.0,
            'start_time': datetime.now()
        }
        st.rerun()

# Main content
if api_key and trading_symbols and base_url:
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 AI Trading Dashboard",
        "📊 Market Analysis", 
        "💼 Portfolio",
        "📜 Trade History"
    ])
    
    # TAB 1: AI Trading Dashboard
    with tab1:
        st.markdown("## 🤖 AI Agent Trading Console")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 💹 Live Market Prices")
            price_cols = st.columns(len(trading_symbols))
            
            for idx, symbol in enumerate(trading_symbols):
                price = get_crypto_price(symbol)
                if price:
                    with price_cols[idx]:
                        df = get_market_data(symbol, '1h', 24)
                        if df is not None and len(df) > 0:
                            change_24h = ((price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                            st.metric(symbol, f"${price:,.2f}", f"{change_24h:+.2f}%")
                        else:
                            st.metric(symbol, f"${price:,.2f}")
        
        with col2:
            st.markdown("### 🎯 Quick Actions")
            if st.button("🚀 Get AI Trade Recommendation", type="primary", use_container_width=True):
                with st.spinner("AI analyzing markets..."):
                    market_context = "**REAL-TIME MARKET DATA:**\n\n"
                    
                    for symbol in trading_symbols:
                        price = get_crypto_price(symbol)
                        df = get_market_data(symbol, '1h', 24)
                        
                        if price and df is not None:
                            change_24h = ((price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                            volume = df['volume'].sum()
                            high_24h = df['high'].max()
                            low_24h = df['low'].min()
                            
                            market_context += f"""
**{symbol}/USDT:**
- Current: ${price:,.2f}
- 24h Change: {change_24h:+.2f}%
- 24h High: ${high_24h:,.2f}
- 24h Low: ${low_24h:,.2f}
- Volume: {volume:,.0f}

"""
                    
                    prompt = f"""{market_context}

**PORTFOLIO:**
- Cash: ${st.session_state.portfolio['cash']:.2f}
- Positions: {json.dumps(st.session_state.portfolio['positions'], indent=2)}

**MISSION:** Analyze and provide ONE specific trade recommendation that will likely profit in the next 1-6 hours.

Use DeepSeek's winning strategy:
1. Identify strongest momentum
2. Recommend aggressive entry with leverage
3. Set clear profit target (5-20%)
4. Explain why this will profit

**FORMAT:**
TRADE SIGNAL: BUY/SELL
SYMBOL: [crypto]
AMOUNT: $[USD]
LEVERAGE: [1-{max_leverage}]x
ENTRY: $[price]
TARGET: $[price] ([%] profit)
STOP LOSS: $[price]
REASONING: [why this wins]
CONFIDENCE: [1-10]
"""
                    
                    response = call_ai_api(prompt, api_key, base_url, model_name)
                    
                    st.markdown("### 🎯 AI Trade Recommendation")
                    st.markdown(response)
        
        st.divider()
        
        # Manual trading
        st.markdown("### 🎮 Manual Trading Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trade_action = st.selectbox("Action", ["BUY", "SELL"])
        with col2:
            trade_symbol = st.selectbox("Symbol", trading_symbols)
        with col3:
            trade_amount = st.number_input("Amount (USD)", min_value=0.0, value=1000.0, step=100.0)
        with col4:
            trade_leverage = st.slider("Leverage", 1, max_leverage, 1)
        
        if st.button("Execute Trade", type="primary"):
            current_price = get_crypto_price(trade_symbol)
            if current_price:
                coin_amount = trade_amount / current_price
                success, message = execute_trade(trade_action, trade_symbol, coin_amount, trade_leverage)
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Failed to get price")
    
    # TAB 2: Market Analysis
    with tab2:
        st.markdown("## 📊 Technical Analysis")
        
        selected_symbol = st.selectbox("Select Crypto", trading_symbols)
        
        if selected_symbol:
            df = get_market_data(selected_symbol, '1h', 168)
            
            if df is not None:
                fig = make_subplots(
                    rows=2, cols=1,
                    row_heights=[0.7, 0.3],
                    subplot_titles=(f'{selected_symbol}/USDT Price', 'Volume'),
                    vertical_spacing=0.05
                )
                
                fig.add_trace(
                    go.Candlestick(
                        x=df['timestamp'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name='Price'
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker_color='rgba(100,100,250,0.5)'),
                    row=2, col=1
                )
                
                fig.update_layout(
                    height=600,
                    xaxis_rangeslider_visible=False,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                if st.button("🧠 Get AI Analysis"):
                    with st.spinner("AI analyzing..."):
                        current_price = df['close'].iloc[-1]
                        price_change = ((current_price - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
                        
                        prompt = f"""Analyze {selected_symbol}:

Current: ${current_price:.2f}
7d Change: {price_change:+.2f}%
7d High: ${df['high'].max():.2f}
7d Low: ${df['low'].min():.2f}

Provide:
1. Trend (bullish/bearish)
2. Support/resistance levels
3. Entry/exit recommendations
4. Risk/reward ratio
"""
                        
                        response = call_ai_api(prompt, api_key, base_url, model_name)
                        st.markdown(response)
    
    # TAB 3: Portfolio
    with tab3:
        st.markdown("## 💼 Portfolio Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        current_value = calculate_portfolio_value()
        profit_loss = current_value - st.session_state.portfolio['start_value']
        profit_pct = (profit_loss / st.session_state.portfolio['start_value']) * 100
        
        with col1:
            if profit_loss >= 0:
                st.markdown(f'<div class="profit-card"><h2>${current_value:.2f}</h2><p>Total Value</p></div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="loss-card"><h2>${current_value:.2f}</h2><p>Total Value</p></div>', 
                           unsafe_allow_html=True)
        
        with col2:
            st.metric("Profit/Loss", f"${profit_loss:.2f}", f"{profit_pct:.2f}%")
        with col3:
            st.metric("Available Cash", f"${st.session_state.portfolio['cash']:.2f}")
        with col4:
            roi = (current_value / st.session_state.portfolio['start_value'] - 1) * 100
            st.metric("ROI", f"{roi:.2f}%")
        
        st.divider()
        
        st.markdown("### 📈 Open Positions")
        
        if st.session_state.portfolio['positions']:
            positions_data = []
            
            for symbol, position in st.session_state.portfolio['positions'].items():
                current_price = get_crypto_price(symbol)
                if current_price:
                    entry_value = position['amount'] * position['entry_price']
                    current_value_pos = position['amount'] * current_price
                    pnl = (current_value_pos - entry_value) * position['leverage']
                    pnl_pct = ((current_price / position['entry_price']) - 1) * 100 * position['leverage']
                    
                    positions_data.append({
                        'Symbol': symbol,
                        'Amount': f"{position['amount']:.6f}",
                        'Entry': f"${position['entry_price']:.2f}",
                        'Current': f"${current_price:.2f}",
                        'Leverage': f"{position['leverage']:.1f}x",
                        'P&L': f"${pnl:.2f}",
                        'P&L %': f"{pnl_pct:.2f}%"
                    })
            
            st.dataframe(pd.DataFrame(positions_data), use_container_width=True)
        else:
            st.info("No open positions")
    
    # TAB 4: Trade History
    with tab4:
        st.markdown("## 📜 Trade History")
        
        if st.session_state.portfolio['trade_history']:
            df_history = pd.DataFrame(st.session_state.portfolio['trade_history'])
            
            st.markdown("### Recent Trades")
            st.dataframe(df_history.tail(20), use_container_width=True)
            
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            
            total_trades = len(df_history)
            buy_trades = len(df_history[df_history['action'] == 'BUY'])
            sell_trades = len(df_history[df_history['action'] == 'SELL'])
            
            with col1:
                st.metric("Total Trades", total_trades)
            with col2:
                st.metric("Buy Orders", buy_trades)
            with col3:
                st.metric("Sell Orders", sell_trades)
            with col4:
                if sell_trades > 0:
                    avg_profit = df_history[df_history['action'] == 'SELL']['profit'].mean()
                    st.metric("Avg Profit", f"${avg_profit:.2f}")
        else:
            st.info("No trades yet")

else:
    st.markdown("""
        <div style='text-align: center; padding: 3rem;'>
            <h2>🏆 Welcome to AI Trading Agent</h2>
            <p style='font-size: 1.3rem;'>
                Based on <strong>DeepSeek's Winning Alpha Arena Strategy</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Paper Trading")
        st.write("Risk-free with $10,000 virtual capital")
    
    with col2:
        st.markdown("### 📊 Real-Time Data")
        st.write("Live crypto prices from Binance")
    
    with col3:
        st.markdown("### 🤖 AI Strategy")
        st.write("DeepSeek's proven algorithm")

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p>⚠️ Paper Trading Only | Not Financial Advice</p>
    </div>
""", unsafe_allow_html=True)