from datetime import datetime
from app.database import AsyncSessionLocal
from app.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError


async def insert_article(session: AsyncSession, article_data: dict[str, str|None|datetime])->None:
    try:
        # Import Article model here to avoid circular import
        from app.models import Article
        
        # Filter out any extra fields that don't exist in the model
        model_fields = {column.name for column in Article.__table__.columns}
        filtered_data = {k: v for k, v in article_data.items() if k in model_fields}
        
        stmt = insert(Article).values(**filtered_data)
        await session.execute(stmt)
        await session.commit()
        logger.debug(f"Successfully inserted article: {article_data.get('url', 'unknown')}")
    except IntegrityError as e:
        logger.error(f"Integrity error while inserting article by url='{article_data.get('url', 'unknown')}'. Error: {str(e)}")
        await session.rollback()
    except Exception as e:
        logger.error(f"Error while inserting article by url='{article_data.get('url', 'unknown')}'. Error: {str(e)}")
        await session.rollback()
        raise



async def insert_article_chunk(articles_list: list[dict[str, str|None|datetime]])->None:
    if not articles_list:
        logger.warning("No articles to insert")
        return
        
    logger.info(f"Attempting to insert {len(articles_list)} articles to database")
    
    async with AsyncSessionLocal() as session:
        for i, article_data in enumerate(articles_list, 1):
            logger.debug(f"Inserting article {i}/{len(articles_list)}: {article_data.get('title', 'Unknown')}")
            await insert_article(session, article_data)
    
    logger.info(f"Completed inserting {len(articles_list)} articles to database")