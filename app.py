import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# Page configuration
st.set_page_config(page_title="Nifty 50 Live Dashboard", layout="wide")

def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_data():
    try:
        # Fetching data and flattening columns to avoid MultiIndex error
        df = yf.download(tickers="^NSEI", period="2d", interval="5m", progress=False)
        if df.empty:
            return None
        
        # Flatten columns if they are multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df['EMA_20'] = calculate_ema(df['Close'], 20)
        df['RSI_14'] = calculate_rsi(df['Close'], 14)
        return df
    except Exception as e:
        return None

st.title("📈 Nifty 50 Smart Dashboard")

# UI Logic
placeholder = st.empty()

while True:
    df = get_data()
    
    with placeholder.container():
        if df is not None and len(df) > 0:
            last_row = df.iloc[-1]
            
            # Safe conversion to float
            ltp = round(float(last_row['Close']), 2)
            day_high = round(float(df['High'].max()), 2)
            day_low = round(float(df['Low'].min()), 2)
            rsi = round(float(last_row['RSI_14']), 2)
            ema = round(float(last_row['EMA_20']), 2)
            five_m_high = round(float(last_row['High']), 2)
            five_m_low = round(float(last_row['Low']), 2)

            st.write(f"🕒 Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP (Nifty 50)", f"₹{ltp}")
            m2.metric("Day High", f"₹{day_high}")
            m3.metric("Day Low", f"₹{day_low}")
            m4.metric("RSI (14)", rsi)

            # Candle Details
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.info(f"**5m High:** {five_m_high}")
            c2.info(f"**5m Low:** {five_m_low}")
            c3.info(f"**EMA (20):** {ema}")

            # Trading Signal Logic
            signal = "WAITING"
            trend = "NEUTRAL"
            color = "white"
            
            if ltp > ema and rsi > 60:
                signal = "BUY CALL"
                trend = "BULLISH"
                color = "#2ecc71"
            elif ltp < ema and rsi < 40:
                signal = "BUY PUT"
                trend = "BEARISH"
                color = "#e74c3c"

            st.markdown(f"### Market Trend: <span style='color:{color}'>{trend}</span>", unsafe_allow_html=True)

            if signal != "WAITING":
                st.success(f"🎯 SIGNAL FOUND: {signal}")
                entry = ltp
                sl = entry - 20 if signal == "BUY CALL" else entry + 20
                target = entry + 40 if signal == "BUY CALL" else entry - 40
                
                t1, t2, t3 = st.columns(3)
                t1.metric("Entry Price", entry)
                t2.error(f"Stop Loss: {sl}")
                t3.success(f"Target: {target}")
                
                # TSL Levels
                step = 10 if signal == "BUY CALL" else -10
                st.write(f"**TSL Levels:** L1: {round(entry+step,2)} | L2: {round(entry+step*2,2)} | L3: {round(entry+step*3,2)} | L4: {round(entry+step*4,2)}")
            else:
                st.warning("No clear signal. Scanning markets...")
        else:
            st.error("Market Data is currently unavailable. (Market might be closed or API limit reached)")

    time.sleep(15) # Refresh every 15 seconds
    st.rerun()
