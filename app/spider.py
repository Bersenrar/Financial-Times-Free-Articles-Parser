from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
import asyncio

import app.database_operations as db_services
from app.logger import logger
import app.config as config


def get_articles_urls(content: Tag)->list[str]:
    urls = list()
    all_links = content.find_all('a')
    logger.debug(f"Found {len(all_links)} total links on page")
    
    for url in all_links:
        href = url.get("href", "")
        if href.startswith("/content") and href not in urls:
            urls.append(href)
            logger.debug(f"Added article URL: {href}")
    
    logger.info(f"Extracted {len(urls)} unique article URLs from page")
    return urls

def should_parse_article(
    published_at: datetime,
    hours: int = None,
    days: int = None,
    parsing_start_at: datetime=datetime.now()
) -> bool:
    if hours is not None:
        return (parsing_start_at - published_at).total_seconds() <= hours * 3600
    elif days is not None:
        return (parsing_start_at - published_at).days <= days
    return False

def parse_article(text: str)->dict[str, str|None|datetime] | None:
    soup = BeautifulSoup(text, "html.parser")
    
    # Check for paywall
    if soup.find("a", {"id": "charge-button"}):
        logger.debug("Found paywall button - skipping article")
        return None
    
    result = {}
    logger.debug("Starting to parse article content")

    # Parse title
    title_tag = soup.find("span", {"class": "headline__text"})
    result["title"] = title_tag.get_text(strip=True) if title_tag else None
    logger.debug(f"Title: {result['title']}")

    # Parse subtitle
    subtitle_tag = soup.find("div", {"class": "o-topper__standfirst"})
    result["subtitle"] = subtitle_tag.get_text(strip=True) if subtitle_tag else None
    logger.debug(f"Subtitle: {result['subtitle']}")

    # Parse author
    author_tag = soup.find("a", {"class": "o3-editorial-typography-byline-author"})
    result["author"] = author_tag.get_text(strip=True) if author_tag else None
    logger.debug(f"Author: {result['author']}")

    # Parse published date
    time_tag = soup.find("time", {"class": "article-info__timestamp o3-editorial-typography-byline-timestamp o-date"})
    if time_tag:
        try:
            result["published_at"] = datetime.strptime(time_tag.get("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
            logger.debug(f"Published at: {result['published_at']}")
        except Exception as e:
            logger.error(f"Failed to parse date: {time_tag.get('datetime')} - Error: {e}")
            result["published_at"] = None
    else:
        result["published_at"] = None
        logger.debug("No published date found")

    # Parse content
    article_tag = soup.find("article", {"id": "article-body"})
    if article_tag:
        result["content"] = article_tag.decode_contents()
        logger.debug(f"Content length: {len(result['content'])} characters")
    else:
        result["content"] = None
        logger.debug("No article content found")

    # Parse image
    picture_tag = soup.find("picture")
    img_tag = picture_tag.find("img") if picture_tag else None
    result["image_url"] = img_tag.get("src") if img_tag else None
    logger.debug(f"Image URL: {result['image_url']}")

    # Parse tags
    tag_list = []
    ul_tag = soup.find("ul", {"class": "concept-list__list"})
    if ul_tag:
        for li in ul_tag.find_all("li"):
            a_tag = li.find("a")
            if a_tag:
                tag_list.append(a_tag.get_text(strip=True))
    result["tags"] = tag_list
    logger.debug(f"Tags: {tag_list}")

    # Check if we have essential data
    if not result.get("title") or not result.get("published_at"):
        logger.warning(f"Article missing essential data - Title: {result.get('title')}, Date: {result.get('published_at')}")
        return None

    logger.info(f"Successfully parsed article: {result['title']}")
    return result

class Spider:
    first_run = None
    start_time = None
    require_subscription = 0
    requested_articles = 0
    parsed_articles = 0
    base_url = "https://www.ft.com{}"
    main_page_url = "https://www.ft.com".format("/world?page={}")

    def __init__(self, first_run: bool = False):
        self.first_run = first_run

    async def run(self):
        page_counter = 1
        bad_requests_counter = 0
        self.start_time = datetime.now()
        stop_parsing = False
        
        logger.info(f"Starting spider run - First run: {self.first_run}")
        logger.info(f"Start time: {self.start_time}")
        
        while bad_requests_counter < 5 and not stop_parsing:
            logger.info(f"Processing page {page_counter}")
            
            try:
                response = requests.get(self.main_page_url.format(page_counter))
                self.requested_articles += 1
                logger.info(f"Page {page_counter} response status: {response.status_code}")
                
                if response.status_code != 200:
                    bad_requests_counter += 1
                    logger.warning(f"Bad response from page {page_counter}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                urls = get_articles_urls(soup)
                
                if not urls:
                    logger.warning(f"No article URLs found on page {page_counter}")
                    bad_requests_counter += 1
                    page_counter += 1
                    continue
                
                logger.info(f"Processing {len(urls)} articles from page {page_counter}")
                result, stop_parsing = await self.process_articles(urls)
                
                logger.info(f"From page {page_counter} retrieved {len(result)} articles")
                if result:
                    logger.debug(f"Sample article data: {result[0] if result else 'No articles'}")
                
                if result:
                    await db_services.insert_article_chunk(result)
                    logger.info(f"Successfully inserted {len(result)} articles to database")
                else:
                    logger.warning(f"No articles to insert from page {page_counter}")
                
                page_counter += 1
                
            except Exception as e:
                logger.error(f"Error processing page {page_counter}: {e}")
                bad_requests_counter += 1
                page_counter += 1
        
        logger.info(f"Spider run completed:")
        logger.info(f"  - Requested articles: {self.requested_articles}")
        logger.info(f"  - Parsed articles: {self.parsed_articles}")
        logger.info(f"  - Required subscription: {self.require_subscription}")
        logger.info(f"  - Bad requests count: {bad_requests_counter}")
        logger.info(f"  - Processed pages: {page_counter}")
        self.first_run = False


    async def process_articles(self, urls: list[str]) -> tuple[list[dict[str, str | None | datetime]], bool]:
        result = []
        stop_parsing = False
        
        logger.info(f"Processing {len(urls)} article URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing article {i}/{len(urls)}: {url}")
            
            try:
                response = requests.get(
                    self.base_url.format(url),
                    cookies=config.coockies,
                    headers=config.headers
                )
                logger.debug(f"Status code of request to url='{url}' is {response.status_code}")
                
                if response.status_code != 200:
                    logger.warning(f"Bad response for {url}: {response.status_code}")
                    continue
                    
                if response.status_code == 406:
                    logger.info("Too many requests waiting 10 minutes before parsing will continued")
                    await asyncio.sleep(360)
                    
            except Exception as e:
                logger.error(f"Error occurred while fetching url='{url}'. Exception={e}")
                continue
                
            await asyncio.sleep(5)
            logger.debug(f"Sleeping 5 seconds after processing {url}")

            article_dict = parse_article(response.text)
            
            if not article_dict:
                logger.warning(f"Failed to parse article: {url}")
                self.require_subscription += 1
                continue
                
            if not article_dict.get("published_at"):
                logger.warning(f"Article missing published date: {url}")
                self.require_subscription += 1
                continue

            published_at = article_dict["published_at"]
            logger.info(f"Article published at: {published_at}")
            
            self.parsed_articles += 1
            
            # Check if we should continue parsing based on date
            if self.first_run:
                if not should_parse_article(published_at, days=30, parsing_start_at=self.start_time):
                    logger.info(f"Article too old for first run (30 days limit): {published_at}")
                    stop_parsing = True
                    break
            else:
                if not should_parse_article(published_at, hours=1, parsing_start_at=self.start_time):
                    logger.info(f"Article too old for regular run (1 hour limit): {published_at}")
                    stop_parsing = True
                    break

            article_dict["url"] = url
            article_dict["scraped_at"] = datetime.now()
            result.append(article_dict)
            logger.info(f"Successfully processed article: {article_dict.get('title', 'Unknown')}")

        logger.info(f"Processed {len(urls)} articles, got {len(result)} valid articles")
        return result, stop_parsing




if __name__ == '__main__':
    # Spider().parse_main_page()
    s = Spider()
    print(s.process_articles(["/content/2baeefcc-aa1d-419e-beb3-c5c1f0326d09", "/content/e31b6693-2849-49d1-84cb-912a8ba11b5c"]))
