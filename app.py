import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import time

# Page Settings
st.set_page_config(page_title="Nifty 50 Dashboard", layout="wide")

# Custom Styles
st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

def get_data():
    try:
        # Fetching Nifty 50 data (5-minute interval)
        data = yf.download(tickers="^NSEI", period="2d", interval="5m")
        return data
    except:
        return None

def apply_indicators(df):
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['RSI_14'] = ta.rsi(df['Close'], length=14)
    return df

st.title("📈 Nifty 50 Live Trading Dashboard")

placeholder = st.empty()

while True:
    df = get_data()
    if df is not None and not df.empty:
        df = apply_indicators(df)
        last_row = df.iloc[-1]
        
        ltp = round(float(last_row['Close']), 2)
        day_high = round(float(df['High'].max()), 2)
        day_low = round(float(df['Low'].min()), 2)
        rsi = round(float(last_row['RSI_14']), 2)
        ema = round(float(last_row['EMA_20']), 2)
        f_high = round(float(last_row['High']), 2)
        f_low = round(float(last_row['Low']), 2)

        with placeholder.container():
            # Time and Date
            st.info(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Metrics row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP (Nifty 50)", f"₹{ltp}")
            m2.metric("Day High", f"₹{day_high}")
            m3.metric("Day Low", f"₹{day_low}")
            m4.metric("RSI (14)", rsi)

            # Candle Details
            st.write("---")
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**5m High:** {f_high}")
            c2.markdown(f"**5m Low:** {f_low}")
            c3.markdown(f"**EMA (20):** {ema}")

            # Strategy Logic
            st.write("---")
            signal = "Neutral"
            if ltp > ema and rsi > 60:
                signal = "BUY CALL"
                color = "green"
            elif ltp < ema and rsi < 40:
                signal = "BUY PUT"
                color = "red"
            else:
                color = "gray"

            st.subheader(f"Current Signal: :{color}[{signal}]")

            if signal != "Neutral":
                # Calculations
                entry = ltp
                if signal == "BUY CALL":
                    target = entry + 40
                    sl = entry - 20
                    l1, l2, l3, l4 = entry+10, entry+20, entry+30, entry+40
                else:
                    target = entry - 40
                    sl = entry + 20
                    l1, l2, l3, l4 = entry-10, entry-20, entry-30, entry-40

                t1, t2, t3 = st.columns(3)
                t1.info(f"Entry: {entry}")
                t2.error(f"Stop Loss: {sl}")
                t3.success(f"Target: {target}")

                st.write(f"**TSL Levels:** L1: {l1} | L2: {l2} | L3: {l3} | L4: {l4}")

                # Simple hit check
                if (signal == "BUY CALL" and ltp >= target) or (signal == "BUY PUT" and ltp <= target):
                    st.success("🎯 Target Hit!")
                elif (signal == "BUY CALL" and ltp <= sl) or (signal == "BUY PUT" and ltp >= sl):
                    st.error("❌ Stop Loss Hit!")

    time.sleep(10)
    st.rerun()
