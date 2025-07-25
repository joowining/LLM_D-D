# Docker명령어로 DB구성하기 
## PostgreSQL
```bash
docker run -d \
--name postgres-db \
-e POSTGRES_DB=llm_dnd \
-e POSTGRES_USER=gm \
-e POSTGRES_PASSWORD={password} \
-p 5432:5432 \
postgres:15
```

## PgVectorDB
```bash
docker run -d \
--name pgvector-db \
-e POSTGRES_DB=vector_llm_dnd \\
-e POSTGRES_USER=vector_gm \
-e POSTGRES_PASSWORD={password} \
-p 5433:5432 \
pgvector/pgvector:pg15
```

## Redis
```bash
docker run -d \
--name redis-cache \
-p 6379:6379 \
redis:7-alpine redis-server --requirepass {password}
```