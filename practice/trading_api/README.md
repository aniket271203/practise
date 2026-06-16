
# Trading API

A production-grade trade management system built with FastAPI, SQLAlchemy, and SQLite.

## Architecture

```
app/
├── main.py          # FastAPI app, middleware, exception handlers, lifespan
├── config.py        # Environment-based configuration using Pydantic Settings
├── database.py      # Async SQLAlchemy engine and session management
├── auth.py          # API key authentication
├── rate_limiter.py  # Sliding window rate limiter with per-IP thread locking
├── logger.py        # Structured logging to console and file
├── utils.py         # Retry decorator with exponential backoff
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas with validation
├── routers/         # FastAPI route handlers (HTTP layer only)
├── services/        # Business logic layer
└── repositories/    # Database access layer
```

## Design Decisions

### Layered Architecture
Separated into Router → Service → Repository layers.
Each layer has exactly one responsibility.
Swapping the database only requires changing the repository layer.

### Async Throughout
All endpoints and database operations are async using SQLAlchemy's
async engine with aiosqlite. Non-blocking I/O allows the event loop
to handle concurrent requests efficiently.

### Rate Limiting
Sliding window algorithm using a deque of timestamps per client IP.
Per-IP locks prevent race conditions when multiple threads update
the same client's request history simultaneously.
Configured via environment variable — no hardcoded limits.

### Retry with Exponential Backoff
Database operations wrapped with a retry decorator.
Exponential backoff (delay * attempt) gives failing services
progressively more time to recover between retries.

### Authentication
API key authentication via X-API-Key header.
Key stored in environment variable — never hardcoded or committed.

### Validation
Pydantic V2 field validators on all input schemas.
Validation errors return structured 422 responses.
ValueError objects serialized to strings before JSON encoding.

## Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Create .env file
DATABASE_URL=sqlite+aiosqlite:///./trading.db
API_KEY=your-secret-key
MAX_REQUESTS_PER_MINUTE=10
APP_NAME=Trading API
APP_VERSION=1.0.0
DEBUG=False

### 3. Run server
uvicorn app.main:app --reload

### 4. Access Swagger UI
http://127.0.0.1:8000/docs
Click Authorize and enter your API key.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Health check |
| POST | /trades/ | Create a new trade |
| GET | /trades/ | Get all trades (supports filtering + pagination) |
| GET | /trades/{id} | Get trade by ID |
| GET | /trades/symbol/{symbol} | Get trades by symbol |
| PATCH | /trades/{id}/cancel | Cancel a trade |

## Query Parameters

GET /trades/ supports:
- symbol — filter by stock symbol e.g. ?symbol=AAPL
- status — filter by status e.g. ?status=pending
- skip — pagination offset e.g. ?skip=0
- limit — page size e.g. ?limit=10 (max 100)

## Trade Status Flow

PENDING → FILLED
PENDING → CANCELLED
FILLED → cannot be cancelled
CANCELLED → cannot be cancelled again

## Running Tests
pytest tests/ -v

## Trade-offs

SQLite chosen for simplicity and portability.
For production with concurrent writes, PostgreSQL would be preferred.

Rate limiter uses in-memory storage — resets on server restart.
For distributed systems, Redis-backed rate limiting would be needed.

Background tasks use FastAPI's built-in runner.
For heavy workloads, a dedicated task queue like Celery would be better.
```

---

## Generate requirements.txt

```bash
pip freeze > requirements.txt
```

---

## Final Project Structure Check

Run this and make sure it looks clean:
```bash
find . -type f -name "*.py" | grep -v __pycache__ | sort
```

Should look like:
```
./app/__init__.py
./app/auth.py
./app/config.py
./app/database.py
./app/logger.py
./app/main.py
./app/models/__init__.py
./app/rate_limiter.py
./app/repositories/__init__.py
./app/routers/__init__.py
./app/schemas/__init__.py
./app/services/__init__.py
./app/utils.py
./tests/__init__.py
./tests/conftest.py
./tests/test_trades.py
```

---

## What You've Built — Full Picture

```
┌─────────────────────────────────────┐
│           Client Request            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Middleware Layer            │
│  • Request logging (method, path,   │
│    status, duration)                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Auth + Rate Limit           │
│  • API key validation               │
│  • Sliding window rate limiter      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           Router Layer              │
│  • HTTP concerns only               │
│  • Response models                  │
│  • Status codes                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Service Layer              │
│  • Business logic                   │
│  • HTTPException on violations      │
│  • Logging at every operation       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Repository Layer             │
│  • Database operations only         │
│  • Retry with exponential backoff   │
│  • Async SQLAlchemy                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         SQLite Database             │
│  • Indexed columns                  │
│  • created_at / updated_at          │
└─────────────────────────────────────┘
```

