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