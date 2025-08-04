#!/usr/bin/env python3
"""
Test database connection and model creation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, engine
from app.logger import logger

async def test_database():
    """Test database connection and model creation"""
    try:
        logger.info("Testing database connection...")
        
        # Test connection
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful!")
        
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialization successful!")
        
        # Test model creation
        logger.info("Testing model creation...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            logger.info(f"Available tables: {[table[0] for table in tables]}")
            
            if 'article' in [table[0] for table in tables]:
                # Test table structure
                result = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'article' ORDER BY ordinal_position"))
                columns = result.fetchall()
                logger.info(f"Article table columns: {columns}")
            else:
                logger.error("Article table not found!")
                
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_database()) 