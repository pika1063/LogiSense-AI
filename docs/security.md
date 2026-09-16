# LogiSense-AI Security Guidelines

## CORS Policy
- CORS is configured dynamically via `CORS_ORIGINS` environment variable.
- In development, localhost origins (5173, 3000, 8000) are allowed.

## Input Validation
- All inference inputs are validated using Pydantic `oodels with boundary constraints.
- SQL database access strictly uses parameterized queries, preventing SQL injection.

## Secrets & Environment
- No private keys, credentials, or tokens are committed to git.
- Gitignore enforces exclusion of `.env` files while sharing `.env.example`.
