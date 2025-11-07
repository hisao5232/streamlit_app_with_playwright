import os
from fastapi import FastAPI, Query, Depends, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# .env を読み込む
load_dotenv()

# .envから環境変数取得
API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:your_secure_password@news-db:5432/newsdb")

# Docker環境によっては "postgres://" に変換されることがあるので補正
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL が設定されていません")

# 非同期エンジン作成
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# 非同期セッション
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# メタデータ
metadata = sqlalchemy.MetaData()

# テーブル定義
news = sqlalchemy.Table(
    "news",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("source", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("scraped_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

# FastAPIアプリ作成
app = FastAPI()

# 認証トークン検証
def verify_token(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # "Bearer " を取り除き、前後空白を削除して比較
    token = authorization.replace("Bearer ", "").strip()
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

# CORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 起動時イベント：テーブル自動生成
@app.on_event("startup")
async def on_startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    print("✅ Database and tables are ready.")

# APIエンドポイント
@app.get("/news", response_model=List[dict])
async def get_news(
    source: Optional[str] = Query(None, description="例: 'Yahoo', 'Nikkei', 'Toyokeizai'"),
    limit: int = Query(10, ge=1, le=50, description="取得件数（最大50）"),
    token: None = Depends(verify_token),
):
    async with AsyncSessionLocal() as session:
        query = news.select()
        if source:
            query = query.where(news.c.source == source)
        query = query.order_by(news.c.scraped_at.desc()).limit(limit)
        result = await session.execute(query)
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

@app.post("/news")
async def post_news(
    data: dict = Body(...),
    token: None = Depends(verify_token),
):
    """
    スクレイパーから送信されたニュースをDBに登録する
    """
    source = data.get("source")
    title = data.get("title")
    url = data.get("url")
    scraped_at = data.get("scraped_at")

    if not (source and title and url and scraped_at):
        raise HTTPException(status_code=400, detail="Missing required fields")

    async with AsyncSessionLocal() as session:
        insert_stmt = news.insert().values(
            source=source,
            title=title,
            url=url,
            scraped_at=datetime.fromisoformat(scraped_at),
        )
        await session.execute(insert_stmt)
        await session.commit()

    return {"status": "success", "message": f"Inserted news from {source}"}
