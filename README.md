# solutis-sync

Microsserviço de sincronização TOTVS → MySQL extraído do monólito `solutis_manager_back`.

## Stack

| Ferramenta | Versão |
|---|---|
| Python | 3.13+ |
| Gerenciador | uv |
| API | FastAPI |
| Scheduler | APScheduler (async) |
| ORM (MySQL) | SQLModel (async) |
| Driver SQL Server | aioodbc |
| Validação | Pydantic 2 |

## Estrutura

```
solutis-sync/
├── pyproject.toml
├── .env.example
└── src/
    ├── main.py                          # FastAPI + lifespan
    ├── domain/
    │   ├── entities.py                  # Entidades puras (Pydantic)
    │   ├── protocols.py                 # ReaderRepository[T], WriterRepository[T]
    │   └── checksums.py                 # SHA-256 para idempotência
    ├── application/
    │   ├── sync_use_case.py             # Orquestração com TaskGroup
    │   ├── delete_orphan_assets.py      # Remoção de ativos órfãos
    │   └── container.py                 # Composição / DI
    └── infrastructure/
        ├── settings.py                  # Pydantic Settings (.env)
        ├── database.py                  # Engines assíncronos
        ├── mysql_models.py              # ORM SQLModel (MySQL)
        ├── totvs_queries.py             # SQL bruto (SQL Server)
        ├── totvs_readers.py             # ReaderRepository impls
        ├── mysql_writers.py             # WriterRepository impls
        └── scheduler.py                 # APScheduler cron
```

## Executar

```bash
cp .env.example .env          # editar com credenciais reais
uv sync                       # instalar dependências
uv run uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/fetch-totvs` | Dispara sync manual (background) |
