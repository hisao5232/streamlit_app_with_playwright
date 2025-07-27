import asyncio
from playwright.async_api import async_playwright

async def scrape_nikkei(page):
    await page.goto("https://business.nikkei.com/ranking/?i_cid=nbpnb_ranking", timeout=60000)
    results = []
    articles = await page.locator('section.p-articleList_item').all()

        # 最大10件までループ
    for article in articles[:10]:

        try:
            title = await article.locator('h3.p-articleList_item_title').inner_text()
            href = await article.locator('a.p-articleList_item_link').get_attribute('href')
            if href and not href.startswith("http"):
                href = "https://business.nikkei.com" + href
            results.append((title.strip(), href))
        except:
            continue

    return results

async def scrape_yahoo(page):
    await page.goto("https://news.yahoo.co.jp/categories/business", timeout=60000)
    results = []
    articles = await page.locator('a.sc-1nhdoj2-1').all()

    for article in articles:
        try:
            title = await article.inner_text()
            url = await article.get_attribute('href')
            if url and title:
                results.append((title.strip(), url))
        except:
            continue

    return results

async def scrape_toyokeizai(page):
    await page.goto("https://toyokeizai.net/list/genre/market", timeout=60000)
    results = []

    # 記事のlocatorをすべて取得
    articles = await page.locator('li.wd217').all()
    # 最大10件までループ
    for article in articles[:10]:
        try:
            title = await article.locator('span.title').inner_text()
            href = await article.locator('span.title > a').get_attribute('href')
            if href and not href.startswith("http"):
                href = "https://toyokeizai.net" + href
            results.append((title.strip(), href))
        except:
            continue

    return results


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        nikkei_page = await browser.new_page()
        yahoo_page = await browser.new_page()
        toyokeizai_page = await browser.new_page()

        # 両方を同時に取得
        nikkei_task = scrape_nikkei(nikkei_page)
        yahoo_task = scrape_yahoo(yahoo_page)
        toyokeizai_task = scrape_toyokeizai(toyokeizai_page)

        nikkei_news, yahoo_news, toyokeizai_news = await asyncio.gather(nikkei_task, yahoo_task, toyokeizai_task)

        await browser.close()

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
