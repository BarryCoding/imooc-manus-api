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
        class ServiceDependency {
            +get_app_config_service()
        }
    }

    namespace Application_Layer {
        class AppConfigService {
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
    }

    namespace Infrastructure_Layer {
        class FileAppConfigRepository {
            +load()
            +save()
        }
    }

    AppConfigRoute ..> ServiceDependency : uses (Depends)
    AppConfigRoute ..> AppConfigService : uses
    ServiceDependency ..> AppConfigService : creates
    ServiceDependency ..> FileAppConfigRepository : creates
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

**Application Layer:**
- Created `app/application/service/app_config_service.py` with `AppConfigService` for configuration business logic

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

## System Status & Health Checks

```mermaid
classDiagram
    direction TB

    namespace Interface_Layer {
        class StatusRoute {
            +get_status()
        }
        class ServiceDependency {
            +get_status_service()
        }
    }

    namespace Application_Layer {
        class StatusService {
            +check_all()
        }
    }

    namespace Domain_Layer {
        class HealthChecker {
            <<interface>>
            +check()
        }
        class HealthStatus {
            +service: str
            +status: str
            +details: str
        }
    }

    namespace Infrastructure_Layer {
        class PostgresHealthChecker {
            +check()
        }
        class RedisHealthChecker {
            +check()
        }
    }

    StatusRoute ..> ServiceDependency : uses (Depends)
    StatusRoute ..> StatusService : uses
    ServiceDependency ..> StatusService : creates
    ServiceDependency ..> PostgresHealthChecker : creates
    ServiceDependency ..> RedisHealthChecker : creates
    StatusService ..> HealthChecker : uses
    StatusService ..> HealthStatus : returns
    PostgresHealthChecker ..|> HealthChecker : implements
    RedisHealthChecker ..|> HealthChecker : implements
    PostgresHealthChecker ..> HealthStatus : creates
    RedisHealthChecker ..> HealthStatus : creates
```

**Domain Layer:**
- Created `app/domain/model/health_status.py` defining `HealthStatus` model for standardized status reporting
- Created `app/domain/external/health_checker.py` defining `HealthChecker` protocol for health check implementations

**Application Layer:**
- Created `app/application/service/status_service.py` with `StatusService` to orchestrate parallel health checks

**Infrastructure Layer:**
- Created `app/infrastructure/external/health_checker/postgres_health_checker.py` implementing `PostgresHealthChecker`
- Created `app/infrastructure/external/health_checker/redis_health_checker.py` implementing `RedisHealthChecker`

**Interface Layer:**
- Updated `app/interface/endpoint/status_route.py` to use `StatusService` for the `/status` endpoint
- Updated `app/interface/service_dependency.py` to provide `StatusService` with configured health checkers

## Task & Message Queue Protocols

**Domain Layer:**
- Created `app/domain/external/message_queue.py` defining `MessageQueue` protocol
- Created `app/domain/external/task.py` defining `Task` protocol and `TaskRunner` abstract base class

## Redis Message Queue

**Domain Layer:**
- Updated `app/domain/external/message_queue.py` expanding `MessageQueue` protocol with comprehensive queue operations (`put`, `get`, `pop`, `clear`, etc.)

**Infrastructure Layer:**
- Created `app/infrastructure/external/message_queue/redis_stream_message_queue.py` implementing `RedisStreamMessageQueue` class
- Implemented Redis Stream-based queuing using `xadd`, `xread`, `xrange`, and `xdel` operations
- Implemented distributed locking mechanism with `_acquire_lock()` and `_release_lock()` for safe concurrent `pop` operations

## Redis Stream Task

**Infrastructure Layer:**
- Created `app/infrastructure/external/task/redis_stream_task.py` implementing `RedisStreamTask` class
- Implemented `invoke()` method to execute tasks asynchronously using `TaskRunner`
- Implemented `cancel()` method to stop running tasks and clean up resources
- Implemented in-memory task registry `_task_registry` to track and retrieve active tasks by ID
- Integrated `RedisStreamMessageQueue` for task input and output streams (`task:input:{id}`, `task:output:{id}`)

## Memory & Plan Model

**Domain Layer:**
- Created `app/domain/model/memory.py` defining `Memory` class for managing agent message history with support for rollback and compaction
- Created `app/domain/model/plan.py` defining `Plan` and `Step` models for task orchestration
- Defined `ExecutionStatus` enum in `app/domain/model/plan.py` to track task/step states (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`)

## Event Model

**Domain Layer:**
- Created `app/domain/model/event.py` defining `BaseEvent` class with common event attributes (`id`, `type`, `created_at`)
- Created `PlanEvent` class with `PlanEventStatus` enum (`CREATED`, `UPDATED`, `COMPLETED`) for tracking plan lifecycle events
- Created `TitleEvent` class for title update events
- Created `StepEvent` class with `StepEventStatus` enum (`STARTED`, `COMPLETED`, `FAILED`) for tracking step execution events
- Created `MessageEvent` class for user and assistant message events with attachment support
- Created `ToolEvent` class for tracking tool invocation events
- Created `WaitEvent` class for user input confirmation events
- Created `ErrorEvent` class for error notification events
- Created `DoneEvent` class for task completion events
- Defined `Event` union type combining all event types for type-safe event handling

## JSON Parser with Repair

**Dependencies:**
- Added `json-repair>=0.54.2` for robust JSON parsing with automatic repair capabilities

```sh
uv add json-repair
```

**Domain Layer:**
- Created `app/domain/external/json_parser.py` defining `JSONParser` protocol with `invoke()` method for parsing and repairing JSON strings

**Infrastructure Layer:**
- Created `app/infrastructure/json_parser/repair_json_parser.py` implementing `RepairJSONParser` class using `json_repair` library
- Implemented `invoke()` method with text validation, default value support, and automatic JSON repair via `json_repair.repair_json()` with `ensure_ascii=False`

## Tool System

**Domain Layer:**
- Created `app/domain/model/tool_result.py` defining `ToolResult[T]` generic model for standardized tool execution results with `success`, `message`, and `data` fields
- Created `app/domain/service/tool/base.py` with `BaseTool` class providing unified tool management and invocation interface
  - Implemented `tool()` decorator for registering methods as tools with `name`, `description`, `parameters`, and `required` fields
  - Implemented `has_tool()` method in `BaseTool` class to check tool existence by name
  - Implemented `get_tools()` method in `BaseTool` class with caching to retrieve tool schemas for LLM integration
  - Implemented `_filter_parameters()` class method in `BaseTool` to validate and filter kwargs against method signatures
  - Implemented `invoke()` method in `BaseTool` class for dynamic tool execution with automatic parameter filtering to handle LLM hallucinations

## File Model & Enhanced Event System

**Domain Layer:**
- Created `app/domain/model/file.py` defining `File` model for tracking uploaded or generated files with attributes (`id`, `filename`, `filepath`, `key`, `extension`, `mime_type`, `size`)
- Updated `app/domain/model/event.py` to import `File` and `ToolResult` models for type-safe event handling
- Updated `MessageEvent.attachments` in `app/domain/model/event.py` from `list[Any]` to `list[File]` for strongly-typed attachment support
- Created `BrowserToolContent` model in `app/domain/model/event.py` with `screenshot` field for browser tool results
- Created `MCPToolContent` model in `app/domain/model/event.py` with generic `result` field for MCP tool results
- Defined `ToolContent` union type in `app/domain/model/event.py` combining `BrowserToolContent` and `MCPToolContent`
- Created `ToolEventStatus` enum in `app/domain/model/event.py` with states (`CALLING`, `CALLED`) for tracking tool execution lifecycle
- Completed `ToolEvent` class implementation in `app/domain/model/event.py` with fields (`status`, `tool_call_id`, `tool_name`, `tool_content`, `tool_result`, `function_name`, `function_args`) for comprehensive tool invocation tracking

## Agent Configuration Management

**Domain Layer:**
- Created `AgentConfig` model in `app/domain/model/app_config.py` with configurable fields for `max_iterations` (default: 100, range: 1-999), `max_retries` (default: 3, range: 2-9), and `max_search_results` (default: 10, range: 2-29)
- Updated `AppConfig` model in `app/domain/model/app_config.py` to include `agent_config: AgentConfig` field

**Application Layer:**
- Converted `_load_app_config()`, `get_llm_config()`, and `update_llm_config()` methods in `app/application/service/app_config_service.py` to async functions
- Added `get_agent_config()` method in `app/application/service/app_config_service.py` to retrieve agent configuration
- Added `update_agent_config()` method in `app/application/service/app_config_service.py` to update agent configuration with validation and persistence

**Interface Layer:**
- Updated `get_llm_config()` and `update_llm_config()` endpoints in `app/interface/endpoint/app_config_route.py` to use `await` for async service calls
- Created `get_agent_config()` endpoint in `app/interface/endpoint/app_config_route.py` at `/api/app-config/agent` (GET) to retrieve agent configuration
- Created `update_agent_config()` endpoint in `app/interface/endpoint/app_config_route.py` at `/api/app-config/agent` (POST) to update agent configuration

## Base Agent Implementation

**Domain Layer:**
- Created `app/domain/model/message.py` defining `Message` model with `message` (str) and `attachments` (list[str]) fields for user input handling
- Created `app/domain/service/agent/base.py` implementing `BaseAgent` abstract class for agent orchestration
- Implemented `BaseAgent.__init__()` accepting `AgentConfig`, `LLM`, `Memory`, `JSONParser`, and `tools` (list[BaseTool]) for agent initialization
- Implemented `BaseAgent.invoke()` async generator method yielding `Event` objects for streaming agent responses with tool execution
- Implemented `BaseAgent._invoke_llm()` method for LLM invocation with automatic memory management, retry logic, and empty response handling
- Implemented `BaseAgent._invoke_tool()` method with retry mechanism using `AgentConfig.max_retries` for resilient tool execution
- Implemented `BaseAgent._get_available_tools()` method to aggregate tool schemas from all registered `BaseTool` instances
- Implemented `BaseAgent._get_tool()` method to locate tool packages by tool name
- Implemented `BaseAgent._add_to_memory()` method for automatic system prompt injection and message history management
- Implemented `BaseAgent.compact_memory()` method delegating to `Memory.compact()` for memory optimization
- Implemented `BaseAgent.roll_back()` method for state recovery handling user messages and tool call interruptions
- Agent supports configurable `name`, `_system_prompt`, `_format`, `_retry_interval` (default: 1.0s), and `_tool_choice` class attributes
- Agent enforces single tool call per LLM response by slicing `tool_calls[:1]` to prevent parallel tool execution
- Agent uses `AgentConfig.max_iterations` to limit execution loops and prevent infinite agent cycles

**Infrastructure Layer:**
- Updated `app/infrastructure/external/llm/openai_llm.py` to accept `**kwargs` in `OpenAILLM.__init__()` for flexible `AsyncOpenAI` client configuration

## System Prompt Preparation