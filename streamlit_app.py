# streamlit_app.py

import streamlit as st
import requests
import os
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# タイトル
st.title("📈 TOPIXとドル円の3カ月推移")

# 日付範囲設定
end_date = datetime.today()
start_date = end_date - timedelta(days=90)

# TOPIXのティッカー
topix = yf.download("1306.T", start=start_date, end=end_date)
usd_jpy = yf.download("JPY=X", start=start_date, end=end_date)

# データが取得できているか確認
if topix.empty or usd_jpy.empty:
    st.error("データ取得に失敗しました。時間をおいて再試行してください。")
else:
    # グラフ描画
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=topix.index,
        y=topix["Close"],
        name="TOPIX",
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=usd_jpy.index,
        y=usd_jpy["Close"],
        name="ドル円 (USD/JPY)",
        yaxis="y2",
        line=dict(color='orange')
    ))

    # レイアウトの調整（2軸表示）
    fig.update_layout(
        title="TOPIXとドル円為替の推移（過去3カ月）",
        xaxis_title="日付",
        yaxis=dict(title="TOPIX", side="left"),
        yaxis2=dict(title="USD/JPY", overlaying="y", side="right"),
        legend=dict(x=0, y=1.1, orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)

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

