import asyncio
import aiosqlite
from playwright.async_api import async_playwright
from datetime import datetime
from zoneinfo import ZoneInfo

DB_PATH = "news.db"

# ニュース記事をDBに保存する関数
async def save_to_db(source, articles):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                title TEXT,
                url TEXT,
                scraped_at TEXT
            )
        ''')
        await db.commit()

        now = datetime.now(ZoneInfo("Asia/Tokyo")).isoformat()

        for title, url in articles:
            await db.execute('''
                INSERT INTO news (source, title, url, scraped_at)
                VALUES (?, ?, ?, ?)
            ''', (source, title, url, now))
        await db.commit()

# スクレイピング関数（3サイト）
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

# メイン処理
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        nikkei_page = await browser.new_page()
        yahoo_page = await browser.new_page()
        toyokeizai_page = await browser.new_page()

        nikkei_task = scrape_nikkei(nikkei_page)
        yahoo_task = scrape_yahoo(yahoo_page)
        toyokeizai_task = scrape_toyokeizai(toyokeizai_page)

        nikkei_news, yahoo_news, toyokeizai_news = await asyncio.gather(nikkei_task, yahoo_task, toyokeizai_task)

        await browser.close()

        # DBに保存
        await save_to_db("nikkei", nikkei_news)
        await save_to_db("yahoo", yahoo_news)
        await save_to_db("toyokeizai", toyokeizai_news)

        # 表示（確認用）
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
asyncio.run(main())
