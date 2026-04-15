import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import os
from datetime import datetime

# --- 🚀 ADVANCED AI TRADING ENGINE ---
def get_advanced_ai_advice(ticker):
    try:
        # 15 മിനിറ്റ് ചാർട്ടിലെ ഡാറ്റ എടുക്കുന്നു
        data = yf.Ticker(ticker).history(period='5d', interval='15m')
        if data.empty: return None

        # 1. RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # 2. 20 EMA
        ema_20 = data['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
        current_price = data['Close'].iloc[-1]

        # 3. VWAP (Volume Weighted Average Price)
        data['tp'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['tpv'] = data['tp'] * data['Volume']
        vwap = data['tpv'].sum() / data['Volume'].sum()

        # 4. MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=9, adjust=False).mean()
        macd_val = macd.iloc[-1]
        sig_val = signal_line.iloc[-1]

        # 5. Supertrend (Simplified Logic)
        data['tr'] = np.maximum(data['High'] - data['Low'], 
                     np.maximum(abs(data['High'] - data['Close'].shift()), 
                     abs(data['Low'] - data['Close'].shift())))
        atr = data['tr'].rolling(window=10).mean().iloc[-1]
        st_val = ((data['High'].iloc[-1] + data['Low'].iloc[-1]) / 2) - (3 * atr)

        # --- AI DECISION LOGIC (SCORING) ---
        score = 0
        details = []

        # RSI Analysis
        if rsi > 70: details.append("⚠️ RSI High (Overbought)"); score -= 1
        elif rsi < 30: details.append("✅ RSI Low (Oversold)"); score += 1
        
        # Trend Analysis (EMA & VWAP)
        if current_price > ema_20 and current_price > vwap:
            details.append("📈 Bullish: Price above EMA & VWAP"); score += 2
        elif current_price < ema_20 and current_price < vwap:
            details.append("📉 Bearish: Price below EMA & VWAP"); score -= 2

        # MACD Analysis
        if macd_val > sig_val: details.append("🚀 MACD: Bullish Crossover"); score += 1
        else: details.append("🔻 MACD: Bearish Crossover"); score -= 1

        # Final Advice Generation
        if score >= 3: advice = "🔥 STRONG BUY: High probability trend!"
        elif score >= 1: advice = "✅ BUY: Market is looking positive."
        elif score <= -3: advice = "🚫 STRONG SELL: High risk, avoid long!"
        elif score <= -1: advice = "❌ SELL: Weakness detected."
        else: advice = "⏳ NEUTRAL: Wait for a clear signal."

        return {"price": current_price, "rsi": rsi, "vwap": vwap, "advice": advice, "details": details}
    except: return None

# --- UI SECTION ---
if st.session_state.get('auth') and st.session_state.role == "admin":
    st.title("🤖 PAICHI AI PRO ADVISOR")
    
    selected_asset = st.selectbox("Analyze Asset", ["^NSEI", "^NSEBANK", "CL=F", "AEDINR=X"])
    ai_res = get_advanced_ai_advice(selected_asset)
    
    if ai_res:
        st.markdown(f"""
        <div style="background: #0f172a; padding: 25px; border-radius: 20px; border: 2px solid #FFD700;">
            <h1 style="color: #FFD700; font-size: 35px;">{ai_res['advice']}</h1>
            <p style="color: #00f2fe; font-size: 20px;">Current Price: {ai_res['price']:,.2f}</p>
            <hr style="border-color: #FFD700;">
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px;"><b>RSI:</b> {ai_res['rsi']:.2f}</div>
                <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px;"><b>VWAP:</b> {ai_res['vwap']:,.2f}</div>
            </div>
            <h4 style="margin-top: 20px; color: #FFD700;">Technical Checklist:</h4>
            <ul style="font-size: 16px;">
                {"".join([f"<li>{d}</li>" for d in ai_res['details']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
