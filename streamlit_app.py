# streamlit_app.py

import streamlit as st
import requests
import os
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 日付範囲の設定
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# TOPIX ETF（1475.T）
topix = yf.download("1475.T", start=start_date, end=end_date)

# ドル円レート（JPY=X）
usd_jpy = yf.download("JPY=X", start=start_date, end=end_date)

# グラフ1：TOPIX ETF
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=topix.index, y=topix["Close"],
                          mode='lines',
                          name="TOPIX ETF (1475.T)",
                          line=dict(color='blue')))
fig1.update_layout(title="TOPIX ETF",
                   xaxis_title="日付",
                   yaxis_title="価格（円）")

st.plotly_chart(fig1, use_container_width=True)

# グラフ2：ドル円レート
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=usd_jpy.index, y=usd_jpy["Close"],
                          mode='lines',
                          name="USD/JPY",
                          line=dict(color='green')))
fig2.update_layout(title="ドル円レート",
                   xaxis_title="日付",
                   yaxis_title="為替レート")

st.plotly_chart(fig2, use_container_width=True)

# 日付範囲の設定
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# TOPIX ETF（1475.T）
topix = yf.download("1475.T", start=start_date, end=end_date)

# ドル円レート（JPY=X）
usd_jpy = yf.download("JPY=X", start=start_date, end=end_date)

# グラフ1：TOPIX ETF
fig1, ax1 = plt.subplots()
ax1.plot(topix.index, topix["Close"], label="TOPIX ETF (1475.T)", color="blue")
ax1.set_title("TOPIX ETF")
ax1.set_ylabel("価格（円）")
ax1.legend()
st.pyplot(fig1)

# グラフ2：ドル円レート
fig2, ax2 = plt.subplots()
ax2.plot(usd_jpy.index, usd_jpy["Close"], label="USD/JPY", color="green")
ax2.set_title("ドル円レート")
ax2.set_ylabel("為替レート")
ax2.legend()
st.pyplot(fig2)

API_URL = "http://210.131.217.15:8000/news"  # ← VPSにデプロイ後はIPに置き換える
API_TOKEN = st.secrets["API_TOKEN"]

st.title("📰 最新ニュース一覧")

# 選択肢（APIのsourceに合わせて）
source = st.selectbox("ニュースソースを選んでください", ["nikkei", "yahoo", "toyokeizai"])
limit = st.slider("取得件数", min_value=1, max_value=50, value=10)

params = {
    "source": source,
    "limit": limit
}
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

try:
    response = requests.get(API_URL, params=params, headers=headers)
    response.raise_for_status()
    news_items = response.json()

    if not news_items:
        st.warning("該当するニュースが見つかりませんでした。")
    else:
        for item in news_items:
            st.markdown(f"### [{item['title']}]({item['url']})")
            st.caption(f"出典: {item['source']} ／ 取得日時: {item['scraped_at']}")
            st.divider()
except requests.exceptions.RequestException as e:
    st.error(f"APIリクエストに失敗しました: {e}")






