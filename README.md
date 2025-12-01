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

## Redis Integration

**Dependencies:**
- Added `redis>=7.1.0` to project dependencies

```sh
uv add redis
```

**Infrastructure Layer:**
- Created `app/infrastructure/storage/redis.py` with `RedisClient` class for Redis connection management
- Implemented async `init()` method for Redis client initialization with connection testing via `ping()`
- Implemented async `shutdown()` method for graceful Redis client closure
- Created `get_redis()` function with `@lru_cache()` decorator to implement singleton pattern for Redis client instance
- Redis client configured with `decode_responses=True` for automatic string decoding

**Features:**
- Integrated Redis client initialization in `app/main.py` lifespan startup context via `await get_redis().init()`
- Integrated Redis client shutdown in `app/main.py` lifespan shutdown context via `await get_redis().shutdown()`
- Redis client instance accessible through `get_redis().client` property with validation to ensure initialization
- Automatic connection health check during initialization
- Comprehensive error handling and logging for Redis operations

## Postgres Integration

**Dependencies:**
- Added `asyncpg>=0.31.0` for async PostgreSQL support
- Added `sqlalchemy[asyncio]>=2.0.44` for ORM with async support

```sh
uv add asyncpg "sqlalchemy[asyncio]"
```

**Infrastructure Layer:**
- Created `app/infrastructure/storage/postgres.py` with `Postgres` class for database connection management
- Implemented `init()` method to initialize async engine and session factory, ensuring `uuid-ossp` extension exists
- Implemented `shutdown()` method for graceful resource cleanup
- Created `get_db_session()` FastAPI dependency for managing transaction scopes and async sessions

**Features:**
- Integrated Postgres initialization in `app/main.py` via `await get_postgres().init()` at startup
- Integrated Postgres shutdown in `app/main.py` via `await get_postgres().shutdown()` on app exit

**Configuration:**
- Added `sqlalchemy_database_uri` to `core/config.py` (default: `"postgresql+asyncpg://springer:postgres@localhost:5432/manus"`)

## Tencent Cloud COS Integration

**Dependencies:**
- Added `cos-python-sdk-v5>=1.9.39` for Tencent Cloud Object Storage support

```sh
uv add cos-python-sdk-v5
```

**Infrastructure Layer:**
- Created `app/infrastructure/storage/cos.py` with `Cos` class for COS client management
- Implemented async `init()` method to create `CosS3Client` with region, credentials, and scheme configuration
- Implemented async `shutdown()` method for graceful COS client cleanup and cache clearing
- Created `get_cos()` function with `@lru_cache()` decorator to implement singleton pattern for COS client instance
- COS client configured with `Token=None` for standard authentication mode

**Features:**
- Integrated COS client initialization in `app/main.py` lifespan startup context via `await get_cos().init()`
- Integrated COS client shutdown in `app/main.py` lifespan shutdown context via `await get_cos().shutdown()`
- COS client instance accessible through `get_cos().client` property with validation to ensure initialization
- Comprehensive error handling and logging for COS operations

**Configuration:**
- Added COS settings to `core/config.py`: `cos_secret_id`, `cos_secret_key`, `cos_region`, `cos_scheme` (default: `"https"`), `cos_bucket`, and `cos_domain`

## Alembic

- demo model in `app/infrastructure/model/demo.py`

```sh
# install dependencies
uv add alembic psycopg2-binary
```

```sh
# initiate alembic
source .venv/bin/activate
alembic init alembic
```

- update `sqlalchemy.url` in alembic.ini
- update `target_metadata` in alembic/env.py

```sh
# revision with comment of current changes
alembic revision --autogenerate -m "create demos table"
```

```sh
# upgrade database
alembic upgrade <revision_id>
alembic upgrade head
```

```sh
# downgrade database
alembic downgrade <revision_id>
alembic downgrade -1
alembic downgrade base
```

- clean up: remove demo.py and its versions file

## Pytest Integration

**Dependencies:**
- Added `pytest>=9.0.1` and `httpx>=0.28.1` to development dependencies

```sh
uv add pytest httpx --dev
```

**Configuration:**
- Created `pytest.ini` configuring `testpaths = test` and `cache_dir = tmp/.pytest_cache`
- Updated `.gitignore` to exclude `tmp/` directory

**Features:**
- Created `test/conftest.py` with `client` fixture using `TestClient` for integration testing
- Created `test/app/interface/endpoint/test_status_route.py` with `test_get_status()` to verify health check endpoint
- Established test directory structure mirroring the application layout

```sh
pytest
```

## App Config Management

```mermaid
classDiagram
    direction TB

    namespace Interface_Layer {
        class AppConfigRoute {
            +get_llm_config()
            +update_llm_config()
        }
    }

    namespace Domain_Layer {
        class AppConfig {
            +llm_config: LLMConfig
        }
        class LLMConfig {
            +base_url: HttpUrl
            +api_key: str
        }
        class AppConfigRepository {
            <<interface>>
            +load()
            +save()
        }
        class AppConfigService {
            +get_llm_config()
            +update_llm_config()
        }
    }

    namespace Infrastructure_Layer {
        class FileAppConfigRepository {
            +load()
            +save()
        }
    }

    AppConfigRoute ..> AppConfigService : uses
    AppConfigService ..> AppConfigRepository : uses
    AppConfigService ..> AppConfig : manages
    AppConfigRepository ..> AppConfig : persists
    FileAppConfigRepository ..|> AppConfigRepository : implements
    AppConfig *-- LLMConfig : contains
```

**Dependencies:**
- Added `filelock>=3.20.0` for safe concurrent file writes

```sh
uv add filelock
```

**Domain Layer:**
- Created `app/domain/model/app_config.py` defining `AppConfig` and `LLMConfig` domain entities
- Created `app/domain/repository/app_config_repository.py` with `AppConfigRepository` protocol definition
- Created `app/domain/service/app_config_service.py` with `AppConfigService` for configuration business logic

**Infrastructure Layer:**
- Created `app/infrastructure/repository/file_app_config_repository.py` implementing `FileAppConfigRepository` with YAML storage

**Interface Layer:**
- Created `app/interface/endpoint/app_config_route.py` with `get_llm_config()` and `update_llm_config()` endpoints
- Created `app/interface/service_dependency.py` with `get_app_config_service()` dependency provider
- Updated `app/interface/endpoint/route.py` to register `app_config_route` in the API router

**Configuration:**
- Added `app_config_filepath` setting to `core/config.py`

## LLM Integration

**Domain Layer:**
- Created `app/domain/external/llm.py` defining `LLM` protocol with `invoke` method and properties (`model_name`, `temperature`, `max_tokens`)

**Infrastructure Layer:**
- Created `app/infrastructure/external/llm/openai_llm.py` implementing `OpenAILLM` class using `AsyncOpenAI` client
- Implemented `invoke` method handling message invocation with optional tools and response format support
- Added local debug support for single-file testing

```sh
# Test OpenAI LLM implementation
uv run -m app.infrastructure.external.llm.openai_llm
```