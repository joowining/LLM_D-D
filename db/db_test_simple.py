# connection_test.py
import os
import psycopg
import redis
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL 테스트
try:
    conn_str = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    print("PostgreSQL 연결 문자열:", conn_str)
    conn = psycopg.connect(conn_str)
    print("✅ PostgreSQL 연결 성공!")
    conn.close()
except Exception as e:
    print("❌ PostgreSQL 연결 실패:", e)

# PgVector 테스트
try:
    conn_str = f"postgresql://{os.getenv('PGVECTOR_USER')}:{os.getenv('PGVECTOR_PASSWORD')}@{os.getenv('PGVECTOR_HOST')}:{os.getenv('PGVECTOR_PORT')}/{os.getenv('PGVECTOR_DB')}"
    print("PgVector 연결 문자열:", conn_str)
    conn = psycopg.connect(conn_str)
    print("✅ PgVector 연결 성공!")
    conn.close()
except Exception as e:
    print("❌ PgVector 연결 실패:", e)

# Redis 테스트
try:
    client = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )
    client.ping()
    print("✅ Redis 연결 성공!")
except Exception as e:
    print("❌ Redis 연결 실패:", e)