# 経済ニュース・株価アプリ / Economic News & Stock Price App

[English](#english) | [日本語](#japanese)

---

## English

A web application built with Streamlit that displays economic news and stock price charts.

### Features

- **Economic News Retrieval**: Uses requests and BeautifulSoup to fetch economic news from Nikkei, Reuters, and Bloomberg
- **Stock Price Charts**: Uses yfinance to display real-time stock price data
- **Interactive Charts**: Beautiful stock price charts using Plotly
- **Basic Statistics**: Basic stock price statistics (latest price, daily change, etc.)

### Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Run the Application

```bash
streamlit run main.py
```

### Usage

#### News Feature
1. Select a news source from the sidebar (Nikkei, Reuters, Bloomberg)
2. Click "Update News" button
3. Latest economic news will be displayed

#### Stock Price Feature
1. Enter a stock symbol (e.g., 7203.T, 6758.T, AAPL)
2. Select a time period
3. Click "Get Stock Data" button
4. Stock price chart and basic statistics will be displayed

### Supported Stock Symbols

- **Japanese Stocks**: 7203.T (Toyota), 6758.T (Sony), etc.
- **US Stocks**: AAPL (Apple), GOOGL (Google), etc.
- **Others**: Supports major stock markets worldwide

### Important Notes

- This app is for informational purposes only and does not provide investment advice
- News retrieval may take some time
- Some news sites may have access restrictions

### Tech Stack

- **Streamlit**: Web application framework
- **requests & BeautifulSoup**: Web scraping
- **yfinance**: Stock price data retrieval
- **Plotly**: Interactive charts
- **Pandas**: Data processing

---

## 日本語

Streamlitで作成された経済ニュースと株価チャートを表示するWebアプリケーションです。

### 機能

- **経済ニュース取得**: requestsとBeautifulSoupを使用して日経新聞、ロイター、Bloombergから経済ニュースを取得
- **株価チャート**: yfinanceを使用してリアルタイム株価データを表示
- **インタラクティブチャート**: Plotlyを使用した美しい株価チャート
- **基本統計**: 株価の基本統計情報（最新価格、前日比など）

### セットアップ

#### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

#### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

#### 3. アプリの実行

```bash
streamlit run main.py
```

### 使い方

#### ニュース機能
1. サイドバーからニュースソースを選択（日経新聞、ロイター、Bloomberg）
2. 「ニュースを更新」ボタンをクリック
3. 最新の経済ニュースが表示されます

#### 株価機能
1. 株価シンボルを入力（例：7203.T、6758.T、AAPL）
2. 期間を選択
3. 「株価を取得」ボタンをクリック
4. 株価チャートと基本統計が表示されます

### 対応株価シンボル

- **日本株**: 7203.T（トヨタ）、6758.T（ソニー）など
- **米国株**: AAPL（アップル）、GOOGL（グーグル）など
- **その他**: 世界中の主要株式市場に対応

### 注意事項

- このアプリは情報提供のみを目的としており、投資助言ではありません
- ニュース取得には時間がかかる場合があります
- 一部のニュースサイトではアクセス制限がある場合があります

### 技術スタック

- **Streamlit**: Webアプリケーションフレームワーク
- **requests & BeautifulSoup**: Webスクレイピング
- **yfinance**: 株価データ取得
- **Plotly**: インタラクティブチャート
- **Pandas**: データ処理 