from datetime import datetime

from app import spider
from app.logger import logger
import asyncio


async def main():
    parser = spider.Spider(first_run=True)
    while True:
        logger.info(f"Start parsing at {datetime.now()}")
        await parser.run()
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())