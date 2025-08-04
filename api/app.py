import sys
import os

# Add the current directory to Python path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import select, func, create_engine
from sqlalchemy.orm import sessionmaker
import os
import app.config as config
# Create synchronous database engine for API
POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', config.POSTGRES_USERNAME)
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', config.POSTGRES_PASSWORD)
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'newsdb')

DATABASE_URL = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = Flask(__name__)

# HTML template for the form
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Data Retrieval</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="datetime-local"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #0056b3;
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .api-links {
            margin-top: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 5px;
        }
        .api-links h3 {
            margin-top: 0;
            color: #495057;
        }
        .api-links a {
            display: block;
            margin: 10px 0;
            color: #007bff;
            text-decoration: none;
        }
        .api-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Article Data Retrieval</h1>
        
        <form id="timeRangeForm">
            <div class="form-group">
                <label for="start_date">Start Date and Time:</label>
                <input type="datetime-local" id="start_date" name="start_date" required>
            </div>
            
            <div class="form-group">
                <label for="end_date">End Date and Time:</label>
                <input type="datetime-local" id="end_date" name="end_date" required>
            </div>
            
            <button type="submit">Get Articles</button>
        </form>
        
        <div class="api-links">
            <h3>API Endpoints:</h3>
            <a href="/api/articles">Get All Articles</a>
            <a href="/api/articles/count">Get Article Count</a>
            <a href="/api/articles/stats">Get Article Statistics</a>
        </div>
        
        <div id="results" class="results" style="display: none;">
            <h3>Results:</h3>
            <div id="resultsContent"></div>
        </div>
    </div>

    <script>
        // Set default dates (last 7 days)
        const now = new Date();
        const sevenDaysAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
        
        document.getElementById('end_date').value = now.toISOString().slice(0, 16);
        document.getElementById('start_date').value = sevenDaysAgo.toISOString().slice(0, 16);
        
        document.getElementById('timeRangeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            // Fetch articles with time range
            fetch(`/api/articles?start_date=${startDate}&end_date=${endDate}`)
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');
                    const resultsContent = document.getElementById('resultsContent');
                    
                    if (data.articles && data.articles.length > 0) {
                        let html = `<p><strong>Found ${data.articles.length} articles:</strong></p>`;
                        html += '<ul>';
                        data.articles.forEach(article => {
                            html += `<li><strong>${article.title}</strong> - ${article.author} (${article.published_at})</li>`;
                        });
                        html += '</ul>';
                        resultsContent.innerHTML = html;
                    } else {
                        resultsContent.innerHTML = '<p>No articles found for the selected time range.</p>';
                    }
                    
                    resultsDiv.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('resultsContent').innerHTML = '<p>Error fetching data.</p>';
                    document.getElementById('results').style.display = 'block';
                });
        });
    </script>
</body>
</html>
"""

def get_articles_with_filters(start_date=None, end_date=None, limit=100):
    """Get articles from database with optional time filters"""
    # Import Article model here to avoid circular import
    from app.models import Article
    
    with SessionLocal() as session:
        query = select(Article)
        
        if start_date:
            query = query.where(Article.published_at >= start_date)
        if end_date:
            query = query.where(Article.published_at <= end_date)
            
        query = query.order_by(Article.published_at.desc()).limit(limit)
        
        result = session.execute(query)
        articles = result.scalars().all()
        
        return [
            {
                'url': article.url,
                'title': article.title,
                'content': article.content[:200] + '...' if len(article.content) > 200 else article.content,
                'author': article.author,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'scraped_at': article.scraped_at.isoformat() if article.scraped_at else None,
                'subtitle': article.subtitle,
                'tags': article.tags,
                'image_url': article.image_url
            }
            for article in articles
        ]

def get_article_count(start_date=None, end_date=None):
    """Get count of articles with optional time filters"""
    # Import Article model here to avoid circular import
    from app.models import Article
    
    with SessionLocal() as session:
        query = select(func.count(Article.url))
        
        if start_date:
            query = query.where(Article.published_at >= start_date)
        if end_date:
            query = query.where(Article.published_at <= end_date)
            
        result = session.execute(query)
        return result.scalar()

def get_article_stats():
    """Get basic statistics about articles"""
    # Import Article model here to avoid circular import
    from app.models import Article
    
    with SessionLocal() as session:
        # Total count
        total_count = session.execute(select(func.count(Article.url)))
        total_count = total_count.scalar()
        
        # Latest article
        latest_article = session.execute(
            select(Article).order_by(Article.published_at.desc()).limit(1)
        )
        latest_article = latest_article.scalar()
        
        # Oldest article
        oldest_article = session.execute(
            select(Article).order_by(Article.published_at.asc()).limit(1)
        )
        oldest_article = oldest_article.scalar()
        
        # Articles in last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        recent_count = session.execute(
            select(func.count(Article.url)).where(Article.published_at >= yesterday)
        )
        recent_count = recent_count.scalar()
        
        return {
            'total_articles': total_count,
            'articles_last_24h': recent_count,
            'latest_article_date': latest_article.published_at.isoformat() if latest_article else None,
            'oldest_article_date': oldest_article.published_at.isoformat() if oldest_article else None
        }

@app.route('/')
def index():
    """Main page with form for time range selection"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/articles')
def get_articles():
    """Get articles with optional time range filtering"""
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('T', ' '))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('T', ' '))
        
        # Get articles
        articles = get_articles_with_filters(start_date, end_date, limit)
        
        return jsonify({
            'success': True,
            'articles': articles,
            'count': len(articles),
            'filters': {
                'start_date': start_date_str,
                'end_date': end_date_str,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/count')
def get_articles_count():
    """Get count of articles with optional time range filtering"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('T', ' '))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('T', ' '))
        
        count = get_article_count(start_date, end_date)
        
        return jsonify({
            'success': True,
            'count': count,
            'filters': {
                'start_date': start_date_str,
                'end_date': end_date_str
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/articles/stats')
def get_articles_stats():
    """Get basic statistics about articles"""
    try:
        stats = get_article_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting API server...")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    app.run(debug=True, host='0.0.0.0', port=5000)
