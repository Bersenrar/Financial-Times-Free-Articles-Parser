# Опис рішення для парсингу новин з Financial Times

## Загальний огляд архітектури

Рішення складається з трьох основних компонентів, оркестрованих за допомогою Docker Compose:

### 1. База даних PostgreSQL (`db`)
- **Контейнер**: `newsdb`
- **Порт**: 5432
- **Призначення**: Зберігання спарсених статей
- **Схема**: Таблиця `article` з полями для URL, заголовка, контенту, автора, дати публікації, тегів та зображень

### 2. Парсер новин (`parser`)
- **Контейнер**: `news-parser`
- **Призначення**: Автоматичне збирання статей з Financial Times
- **Технології**: Python, requests, BeautifulSoup, SQLAlchemy, asyncio

### 3. API сервер (`api`)
- **Контейнер**: `news-api`
- **Порт**: 5000
- **Призначення**: REST API для отримання даних та веб-інтерфейс
- **Технології**: Flask, SQLAlchemy

## Детальний опис процесу парсингу

### Етап 1: Ініціалізація та підключення до бази даних

```python
# app/database.py
async def init_db():
    # Динамічний імпорт моделей для уникнення циклічних залежностей
    from app.models import Article
    
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            # Обробка випадків, коли таблиці вже існують
            if "already exists" in str(e) or "duplicate key" in str(e):
                logger.info("Tables already exist, skipping creation")
            else:
                raise e
```

### Етап 2: Отримання посилань на статті

```python
# app/spider.py
def get_articles_urls(content: Tag) -> list[str]:
    urls = list()
    all_links = content.find_all('a')
    logger.debug(f"Found {len(all_links)} total links on page")
    
    for url in all_links:
        href = url.get("href", "")
        # Фільтрація тільки посилань на статті
        if href.startswith("/content") and href not in urls:
            urls.append(href)
            logger.debug(f"Added article URL: {href}")
    
    logger.info(f"Extracted {len(urls)} unique article URLs from page")
    return urls
```

**Процес:**
1. Відправка GET-запиту до `https://www.ft.com/world?page={номер_сторінки}`
2. Парсинг HTML за допомогою BeautifulSoup
3. Пошук всіх посилань `<a>` на сторінці
4. Фільтрація тільки посилань, що починаються з `/content`
5. Усунення дублікатів
6. Важливим уточненням є те що при отриманні 406 статус коду відбувається очікування 10 хвилин, це зроблено для того
щоб сервер не відбивав запити, також між запитами до сторінок встановленне очікування 5 секунд по тим самим причинам
7. Для запитів використовуються кукі які імітують згоду на викорастання кукі файлів, а також заголовки для імітації
реального веб-клієнта

### Етап 3: Парсинг окремих статей

```python
# app/spider.py
def parse_article(text: str) -> dict[str, str|None|datetime] | None:
    soup = BeautifulSoup(text, "html.parser")
    
    # Перевірка на paywall
    if soup.find("a", {"id": "charge-button"}):
        logger.debug("Found paywall button - skipping article")
        return None
    
    result = {}
    logger.debug("Starting to parse article content")
    
    # Парсинг заголовка
    title_tag = soup.find("span", {"class": "headline__text"})
    result["title"] = title_tag.get_text(strip=True) if title_tag else None
    
    # Парсинг підзаголовка
    subtitle_tag = soup.find("div", {"class": "o-topper__standfirst"})
    result["subtitle"] = subtitle_tag.get_text(strip=True) if subtitle_tag else None
    
    # Парсинг автора
    author_tag = soup.find("a", {"class": "o3-editorial-typography-byline-author"})
    result["author"] = author_tag.get_text(strip=True) if author_tag else None
    
    # Парсинг дати публікації
    time_tag = soup.find("time", {"class": "article-info__timestamp o3-editorial-typography-byline-timestamp o-date"})
    if time_tag:
        try:
            result["published_at"] = datetime.strptime(time_tag.get("datetime"), "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            logger.error(f"Failed to parse date: {time_tag.get('datetime')} - Error: {e}")
            result["published_at"] = None
    
    # Парсинг контенту
    article_tag = soup.find("article", {"id": "article-body"})
    if article_tag:
        result["content"] = article_tag.decode_contents()
    else:
        result["content"] = None
    
    # Парсинг зображення
    picture_tag = soup.find("picture")
    img_tag = picture_tag.find("img") if picture_tag else None
    result["image_url"] = img_tag.get("src") if img_tag else None
    
    # Парсинг тегів
    tag_list = []
    ul_tag = soup.find("ul", {"class": "concept-list__list"})
    if ul_tag:
        for li in ul_tag.find_all("li"):
            a_tag = li.find("a")
            if a_tag:
                tag_list.append(a_tag.get_text(strip=True))
    result["tags"] = tag_list
    
    # Перевірка наявності обов'язкових даних
    if not result.get("title") or not result.get("published_at"):
        logger.warning(f"Article missing essential data - Title: {result.get('title')}, Date: {result.get('published_at')}")
        return None
    
    logger.info(f"Successfully parsed article: {result['title']}")
    return result
```

**Елементи, що парсяться:**
- **Заголовок**: `<span class="headline__text">`
- **Підзаголовок**: `<div class="o-topper__standfirst">`
- **Автор**: `<a class="o3-editorial-typography-byline-author">`
- **Дата**: `<time class="article-info__timestamp o3-editorial-typography-byline-timestamp o-date">`
- **Контент**: `<article id="article-body">`
- **Зображення**: `<picture><img>`
- **Теги**: `<ul class="concept-list__list">`

### Етап 4: Фільтрація за датою

```python
# app/spider.py
def should_parse_article(
    published_at: datetime,
    hours: int = None,
    days: int = None,
    parsing_start_at: datetime = datetime.now()
) -> bool:
    if hours is not None:
        return (parsing_start_at - published_at).total_seconds() <= hours * 3600
    elif days is not None:
        return (parsing_start_at - published_at).days <= days
    return False
```

**Логіка фільтрації:**
- **Перший запуск**: Статті за останні 30 днів
- **Регулярний запуск**: Статті за останню 1 годину

### Етап 5: Збереження в базу даних

```python
# app/database_operations.py
async def insert_article_chunk(articles_list: list[dict[str, str|None|datetime]]) -> None:
    if not articles_list:
        logger.warning("No articles to insert")
        return
        
    logger.info(f"Attempting to insert {len(articles_list)} articles to database")
    
    async with AsyncSessionLocal() as session:
        for i, article_data in enumerate(articles_list, 1):
            logger.debug(f"Inserting article {i}/{len(articles_list)}: {article_data.get('title', 'Unknown')}")
            await insert_article(session, article_data)
    
    logger.info(f"Completed inserting {len(articles_list)} articles to database")
```

**Процес збереження:**
1. Фільтрація полів відповідно до схеми бази даних
2. Використання `INSERT` з обробкою дублікатів
3. Транзакційна безпека з rollback при помилках
4. Логування успішних операцій та помилок

## Модель даних

```python
# app/models.py
class Article(Base):
    __tablename__ = "article"
    
    url: Mapped[str] = mapped_column(String(2048), primary_key=True)
    title: Mapped[str] = mapped_column(String(400), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(400), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)
    image_url: Mapped[str] = mapped_column(String(400), nullable=True)
```

## API для отримання даних

### Ендпоінти:

1. **`GET /`** - Веб-інтерфейс з формою для вибору часового діапазону
2. **`GET /api/articles`** - Отримання статей з фільтрацією за часом
3. **`GET /api/articles/count`** - Кількість статей
4. **`GET /api/articles/stats`** - Статистика по статтях

### Приклад використання API:

```bash
# Отримання всіх статей
curl http://localhost:5000/api/articles

# Отримання статей за часовий діапазон
curl "http://localhost:5000/api/articles?start_date=2025-08-01T00:00:00&end_date=2025-08-03T23:59:59"

# Статистика
curl http://localhost:5000/api/articles/stats
```

## Обробка помилок та логування

### Типи помилок, що обробляються:

1. **Paywall**: Статті з кнопкою "charge-button" пропускаються
2. **Відсутні дані**: Статті без заголовка або дати публікації пропускаються
3. **HTTP помилки**: 406 (Too Many Requests) обробляється з затримкою
4. **Дублікати**: Обробляються через `IntegrityError`
5. **Помилки парсингу**: Логуються з детальною інформацією

### Система логування:

```python
# app/logger.py
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)
```

**Рівні логування:**
- **DEBUG**: Детальна інформація про парсинг
- **INFO**: Основні етапи роботи
- **WARNING**: Пропущені статті
- **ERROR**: Помилки та винятки

## Docker оркестрація

### docker-compose.yml:

```yaml
version: '3.8'
services:
  db:
    build: { context: ., dockerfile: Dockerfile.db }
    environment: { POSTGRES_DB: newsdb, POSTGRES_USER: postgres, POSTGRES_PASSWORD: postgres }
    ports: [ "5432:5432" ]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U postgres -d newsdb"] }
  
  parser:
    build: { context: ., dockerfile: Dockerfile.parser }
    environment: { POSTGRES_HOST: db, POSTGRES_DB: newsdb }
    depends_on: { db: { condition: service_healthy } }
    restart: unless-stopped
  
  api:
    build: { context: ., dockerfile: Dockerfile.api }
    environment: { POSTGRES_HOST: db, POSTGRES_DB: newsdb }
    ports: [ "5000:5000" ]
    depends_on: { db: { condition: service_healthy } }
    restart: unless-stopped
```

## Особливості реалізації

### 1. Асинхронність
- Використання `asyncio` для неблокуючих операцій
- Асинхронні HTTP запити та робота з базою даних
- Правильне управління сесіями SQLAlchemy

### 2. Обробка циклічних імпортів
```python
# Динамічний імпорт для уникнення циклічних залежностей
from app.models import Article
```

### 3. Робастність
- Обробка всіх типів помилок
- Автоматичний перезапуск контейнерів
- Health checks для бази даних

### 4. Масштабованість
- Модульна архітектура
- Незалежні сервіси
- Легке додавання нових джерел даних

## Результат роботи

Парсер автоматично:
1. Збирає статті з Financial Times
2. Фільтрує їх за датою та якістю
3. Зберігає в PostgreSQL
4. Надає API для отримання даних
5. Логує всі операції для моніторингу

Система працює 24/7 з автоматичним перезапуском при помилках та детальним логуванням всіх операцій.