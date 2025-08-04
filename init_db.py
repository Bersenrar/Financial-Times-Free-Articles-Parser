#!/usr/bin/env python3
"""
Database initialization script
Run this to create tables and set up the database schema
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from app.logger import logger

async def main():
    """Initialize the database"""
    try:
        logger.info("Initializing database...")
        logger.info("Creating database tables...")
        await init_db()
        logger.info("Database initialization completed successfully!")
        logger.info("✓ Database initialization completed!")
                
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 