import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

# Dashboard Page Config
st.set_page_config(page_title="Nifty 50 Live", layout="wide")

# Manual Indicator Functions
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
        df = yf.download(tickers="^NSEI", period="2d", interval="5m")
        if not df.empty:
            df['EMA_20'] = calculate_ema(df['Close'], 20)
            df['RSI_14'] = calculate_rsi(df['Close'], 14)
            return df
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
        return None

st.title("📈 Nifty 50 Smart Dashboard")
placeholder = st.empty()

while True:
    df = get_data()
    if df is not None:
        last_row = df.iloc[-1]
        ltp = round(float(last_row['Close']), 2)
        day_high = round(float(df['High'].max()), 2)
        day_low = round(float(df['Low'].min()), 2)
        rsi = round(float(last_row['RSI_14']), 2)
        ema = round(float(last_row['EMA_20']), 2)
        
        with placeholder.container():
            st.write(f"🕒 Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Top row metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP", f"₹{ltp}")
            m2.metric("Day High", f"₹{day_high}")
            m3.metric("Day Low", f"₹{day_low}")
            m4.metric("RSI (14)", f"{rsi}")

            # Signal Logic
            st.divider()
            signal = "WAITING"
            trend = "NEUTRAL"
            color = "white"
            
            if ltp > ema and rsi > 60:
                signal = "BUY CALL"
                trend = "BULLISH"
                color = "#2ecc71" # Green
            elif ltp < ema and rsi < 40:
                signal = "BUY PUT"
                trend = "BEARISH"
                color = "#e74c3c" # Red

            st.markdown(f"### Trend: <span style='color:{color}'>{trend}</span>", unsafe_allow_html=True)

            if signal != "WAITING":
                st.success(f"🔥 Signal: {signal}")
                entry = ltp
                sl = entry - 20 if signal == "BUY CALL" else entry + 20
                target = entry + 40 if signal == "BUY CALL" else entry - 40
                
                t1, t2, t3 = st.columns(3)
                t1.info(f"Entry: {entry}")
                t2.error(f"Stop Loss: {sl}")
                t3.success(f"Target: {target}")
                
                # TSL Levels
                step = 10 if signal == "BUY CALL" else -10
                st.write(f"**TSL Levels:** L1: {entry+step} | L2: {entry+step*2} | L3: {entry+step*3} | L4: {entry+step*4}")
            else:
                st.warning("Market condition not ideal for Entry. Waiting...")

    time.sleep(10)
    st.rerun()
