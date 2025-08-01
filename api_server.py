from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import aiosqlite
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# 任意でCORS許可（例：Streamlit Cloudからアクセスされる前提）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 適宜制限可能
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "news.db"

@app.get("/news", response_model=List[dict])
async def get_news(
    source: Optional[str] = Query(None, description="例: 'Yahoo', 'Nikkei', 'Toyokeizai'"),
    limit: int = Query(10, ge=1, le=50, description="取得件数（最大50）")
):
    """
    SQLiteに保存されたニュースを取得するAPIエンドポイント。
    クエリ例:
      /news?source=Nikkei&limit=5
    """
    query = "SELECT source, title, url, scraped_at FROM news"
    params = []

    if source:
        query += " WHERE source = ?"
        params.append(source)

    query += " ORDER BY scraped_at DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
