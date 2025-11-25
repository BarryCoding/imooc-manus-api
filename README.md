# API

## Initialization

```sh
cd api
uv init --python 3.12
uv venv
```

## Core Dependencies

```sh
uv add pydantic fastapi openai 'uvicorn[standard]'
```

## Project Structure

```
app/
├── domain/          # Domain Layer (Core Business Logic)
│   ├── model/       # Domain entities/value objects
│   ├── repository/  # Repository interfaces (ports)
│   ├── service/     # Domain services
│   └── external/    # External service interfaces (ports)
│
├── application/     # Application Layer (Use Cases/Orchestration)
│   ├── service/     # Application services
│   └── error/       # Application-level errors
│
├── infrastructure/  # Infrastructure Layer (Technical Details)
│   ├── repository/  # Repository implementations (adapters)
│   ├── model/       # Data models/DTOs
│   ├── storage/     # Database/external storage
│   ├── external/    # External service implementations
│   └── logging/     # Logging infrastructure
│
└── interface/       # Interface Layer (API/Presentation)
    ├── endpoint/    # API endpoints (FastAPI routes)
    ├── schema/      # Request/response schemas
    ├── middleware/  # HTTP middleware
    └── error/       # HTTP error handlers
```

## 接口响应约定

1. code: 业务状态码, 和HTTP状态码保持一致, 默认`200`
2. msg: 响应消息提示, 默认`"success"`
3. data: 响应数据, 默认为`{}`

## Pydantic-settings

**Dependencies:**
- Added `pydantic-settings>=2.12.0` to project dependencies

```sh
uv add pydantic-settings
```

**Configuration Management:**
- Created `core/config.py` with `Settings` class using `BaseSettings` from `pydantic-settings`
- Configured environment variable loading from `.env` file with UTF-8 encoding
- Added settings for environment, logging, database, Redis, and cloud storage
- Implemented cached `get_settings()` function to avoid repeated configuration reads

**Project Structure:**
- Moved application entry point from root `main.py` to `app/main.py`
- Updated FastAPI app initialization to load and use centralized settings

```sh
uv run uvicorn app.main:app --reload
```

## Logging

**Infrastructure:**
- Created `app/infrastructure/logging/logging.py` with `setup_logging()` function
- Integrated logging initialization in `app/main.py` at application startup

**Configuration:**
- Log level controlled by `log_level` setting in `core/config.py` (default: `"INFO"`)
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s` with date format `%Y-%m-%d %H:%M:%S`

## Lifespan CORS Router

**Interface Layer:**
- Created `app/interface/endpoint/route.py` with `create_api_routes()` function to centralize API route management
- Created `app/interface/endpoint/status_route.py` with health check endpoint at `/api/status`

**Features:**
- Added lifespan context manager in `app/main.py` using `@asynccontextmanager` for application lifecycle management
- Implemented CORS middleware configuration in `app/main.py` with permissive settings (allow all origins, methods, and headers)
- Integrated router system with `/api` prefix in `app/main.py`
- Added OpenAPI tags configuration for API documentation organization
- Created status health check endpoint that returns `Response` schema with success message

**Project Structure:**
- Router modules organized under `app/interface/endpoint/` directory
- Status route uses prefix `/status` and tag `"状态模块"` for API documentation grouping

## Handle Exception

**Application Layer:**
- Created `app/application/error/exception.py` with `AppException` base class inheriting from `RuntimeError` with customizable attributes (`code`, `status_code`, `msg`, `data`)
- Created exception classes in `app/application/error/exception.py`: `BadRequestError` (400), `NotFoundError` (404), `ValidationError` (422), `TooManusRequestsError` (429), `ServerRequestsError` (500)

**Interface Layer:**
- Created `app/interface/error/exception_handler.py` with `register_exception_handler()` function
- Implemented `app_exception_handler()` to handle `AppException` and all subclasses, returning responses in unified `Response` schema format
- Implemented `http_exception_handler()` to handle FastAPI `HTTPException`, converting to unified response format
- Implemented `exception_handler()` to catch all unhandled exceptions, returning 500 status with default error message

**Features:**
- Integrated exception handler registration in `app/main.py` via `register_exception_handler(app)` at application startup
- All exception handlers log errors using the application logger and return responses following the unified `Response` schema (code, msg, data) as JSON with appropriate HTTP status codes

## Docker Run

```sh
docker run --detach \
--name manus-postgres \
--publish 5432:5432 \
--env POSTGRES_USER=springer \
--env POSTGRES_PASSWORD=postgres \
--env POSTGRES_DB=manus \
--volume manus_postgres_data:/var/lib/postgresql \
postgres:latest

docker ps
```

```sh
docker run --detach \
--name manus-redis \
--publish 6379:6379 \
--volume manus_redis_data:/data \
redis:latest

docker ps
```
