from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase
import app.config as config
import os
from app.logger import logger

# Get database configuration from environment variables or config
POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', config.POSTGRES_USERNAME)
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', config.POSTGRES_PASSWORD)
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'newsdb')

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    # Import models here to avoid circular import
    from app.models import Article
    
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            # If table already exists, that's fine
            if "already exists" in str(e) or "duplicate key" in str(e):
                logger.info("Tables already exist, skipping creation")
            else:
                raise e

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

