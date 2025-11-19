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