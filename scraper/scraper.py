import asyncio
import os
import requests
from playwright.async_api import async_playwright
from datetime import datetime
from zoneinfo import ZoneInfo

# === 環境変数 ===
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

# === APIへニュースを送信する関数 ===
def save_to_api(source, articles):
    """
    ニュースデータを FastAPI 経由で PostgreSQL に登録する。
    """
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # 日本時間 → UTC → naive（タイムゾーン削除）
    now = datetime.now(ZoneInfo("Asia/Tokyo")).astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    # JSON化できるようにISO8601文字列に変換
    now_str = now.isoformat()

    for title, url in articles:
        payload = {
            "source": source,
            "title": title,
            "url": url,
            "scraped_at": now_str,
        }
        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"✅ 登録成功: {title}")
            else:
                print(f"❌ 登録失敗 ({response.status_code}): {title}")
        except Exception as e:
            print(f"⚠️ 通信エラー: {e}")

# === 各ニュースサイトのスクレイピング関数 ===
async def scrape_nikkei(page):
    await page.goto("https://business.nikkei.com/ranking/?i_cid=nbpnb_ranking", timeout=60000, wait_until="domcontentloaded")
    results = []
    article_list = page.locator('section.p-articleList_item')
    count = await article_list.count()
    for i in range(min(count, 10)):
        try:
            article = article_list.nth(i)
            title = await article.locator('h3.p-articleList_item_title').inner_text()
            href = await article.locator('a.p-articleList_item_link').get_attribute('href')
            if href and not href.startswith("http"):
                href = "https://business.nikkei.com" + href
            results.append((title.strip(), href))
        except:
            continue
    return results

async def scrape_yahoo(page):
    await page.goto("https://news.yahoo.co.jp/categories/business", timeout=60000, wait_until="domcontentloaded")
    results = []
    article_list = page.locator('a.sc-1nhdoj2-1')
    count = await article_list.count()
    for i in range(min(count, 10)):
        try:
            article = article_list.nth(i)
            title = await article.inner_text()
            url = await article.get_attribute('href')
            if url and title:
                results.append((title.strip(), url))
        except:
            continue
    return results

async def scrape_toyokeizai(page):
    await page.goto("https://toyokeizai.net/list/genre/market", timeout=60000, wait_until="domcontentloaded")
    results = []
    article_list = page.locator('li.wd217')
    count = await article_list.count()
    for i in range(min(count, 10)):
        try:
            article = article_list.nth(i)
            title = await article.locator('span.title').inner_text()
            href = await article.locator('span.title > a').get_attribute('href')
            if href and not href.startswith("http"):
                href = "https://toyokeizai.net" + href
            results.append((title.strip(), href))
        except:
            continue
    return results

# === メイン処理 ===
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        nikkei_page = await browser.new_page()
        yahoo_page = await browser.new_page()
        toyokeizai_page = await browser.new_page()

        # 並列スクレイピング
        nikkei_task = scrape_nikkei(nikkei_page)
        yahoo_task = scrape_yahoo(yahoo_page)
        toyokeizai_task = scrape_toyokeizai(toyokeizai_page)

        nikkei_news, yahoo_news, toyokeizai_news = await asyncio.gather(
            nikkei_task, yahoo_task, toyokeizai_task
        )

        await browser.close()

        # === API経由で保存 ===
        save_to_api("nikkei", nikkei_news)
        save_to_api("yahoo", yahoo_news)
        save_to_api("toyokeizai", toyokeizai_news)

        # === 確認用出力 ===
        print("\n📰 日経新聞 経済ニュース")
        for i, (title, url) in enumerate(nikkei_news, 1):
            print(f"{i}. {title}\n   {url}")

        print("\n🗞️ Yahooニュース 経済")
        for i, (title, url) in enumerate(yahoo_news, 1):
            print(f"{i}. {title}\n   {url}")

        print("\n🗞️ 東洋経済ニュース")
        for i, (title, url) in enumerate(toyokeizai_news, 1):
            print(f"{i}. {title}\n   {url}")

# 実行
if __name__ == "__main__":
    asyncio.run(main())
