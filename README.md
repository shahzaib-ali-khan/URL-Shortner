# FastAPI URL Shortener

A production-ready FastAPI application with JWT authentication and URL shortening capabilities, built with async support and capability to generate user-friendly URLs.

## Features

- ✅ User registration and authentication (JWT)
- ✅ URL shortening with custom short codes
- ✅ Public URL redirection (no auth required)
- ✅ Click tracking and analytics
- ✅ User-specific URL management
- ✅ Pagination support
- ✅ Filtering support
- ✅ Async/await throughout the application
- ✅ SQLite with async support (aiosqlite)
- ✅ Password hashing with bcrypt
- ✅ CORS support

## Quick Start

### Prerequisites
- Python 3.11+
- Poetry

### Installation

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env


# Run the server
poetry run uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Get current user info

### URL Shortening
- `POST /api/v1/urls` - Create shortened URL
- `GET /api/v1/urls` - Get all user URLs (paginated)
- `GET /api/v1/urls/{short_code}` - Get URL details
- `GET /api/v1/urls/{short_code}/resolve` - Get resolved URL
- `GET /api/v1/urls/{short_code}/stats` - Get URL statistics
- `PATCH /api/v1/urls/{short_code}` - Update URL
- `DELETE /api/v1/urls/{short_code}` - Delete URL


## URL Shortening Features

### Custom Short Codes
- Users can specify their preferred short code (e.g., "my-link")
- If available, the custom code is used
- If taken, a random code is generated automatically
- Validation: 3-50 characters, alphanumeric + hyphens/underscores

### Automatic Short Code Generation
- Default: 6-character random alphanumeric
- Excludes confusing characters (0, O, I, l)
- Collision detection with automatic retry

### Click Tracking
- Automatic click counting on each redirect
- View statistics via `/urls/{short_code}/stats`
- Per-user analytics available

### URL Management
- Enable/disable URLs without deletion
- Update titles and metadata
- Pagination for URL lists
- Owner-only modifications

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_auth.py
```

## Development Tools

```bash
# Sort import alphabatically
poetry run isort

# Lint code
poetry run ruff check

# Type checking
poetry run mypy
```

## Docker Deployment

Docker compose is being used for deploying it on Docker. In the root directory run:
```
docker compose up -d
```

> Set the environment variables related to application and database in the `compose.yml` file.

Docker deployment will use PostgreSQL database.
