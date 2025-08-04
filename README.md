# News Parser with API

A Docker-based application that parses news articles and provides a REST API for data retrieval.

## Architecture

The application consists of three main components:

1. **Database (PostgreSQL)** - Stores parsed article data
2. **Parser Application** - Scrapes and parses news articles
3. **API Application** - Provides REST API endpoints for data retrieval

## Docker Setup

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. **Clone the repository and navigate to the project directory**

2. **Create environment file (optional)**
   ```bash
   cp env.example .env
   # Edit .env if you want to customize the configuration
   ```

3. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:5000
   - Database: localhost:5432 (postgres/postgres)

### Individual Services

#### Database
```bash
# Start only the database
docker-compose up db

# Connect to database
docker exec -it newsdb psql -U postgres -d newsdb
```

#### Parser
```bash
# Start parser (requires database to be running)
docker-compose up parser

# View parser logs
docker-compose logs -f parser
```

#### API
```bash
# Start API (requires database to be running)
docker-compose up api

# View API logs
docker-compose logs -f api
```

### API Endpoints

- `GET /` - Main page with time range selection form
- `GET /api/articles` - Get articles with optional time filtering
- `GET /api/articles/count` - Get article count
- `GET /api/articles/stats` - Get article statistics

### Environment Variables

The following environment variables can be customized:

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_USERNAME | postgres | Database username |
| POSTGRES_PASSWORD | postgres | Database password |
| POSTGRES_HOST | db | Database host (use 'db' for Docker) |
| POSTGRES_PORT | 5432 | Database port |
| POSTGRES_DB | newsdb | Database name |

### Volumes

- `postgres_data` - Persistent PostgreSQL data
- `./logs` - Application logs (mounted to containers)

### Health Checks

All services include health checks:
- Database: PostgreSQL connection test
- Parser: Database connection test
- API: HTTP endpoint test

### Troubleshooting

1. **Database connection issues**
   ```bash
   # Check database status
   docker-compose ps
   
   # View database logs
   docker-compose logs db
   ```

2. **Parser not working**
   ```bash
   # Check parser logs
   docker-compose logs parser
   
   # Restart parser
   docker-compose restart parser
   ```

3. **API not accessible**
   ```bash
   # Check API logs
   docker-compose logs api
   
   # Test API health
   curl http://localhost:5000/api/articles/stats
   ```

### Development

For development, you can override the default configuration:

```bash
# Use custom environment file
docker-compose --env-file .env.dev up

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production

For production deployment:

1. Change default passwords in `.env` file
2. Use external PostgreSQL database if needed
3. Configure proper logging
4. Set up monitoring and alerting
5. Use reverse proxy (nginx) for API
6. Configure SSL/TLS certificates 