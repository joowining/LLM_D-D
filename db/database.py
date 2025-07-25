import os
import psycopg
import redis
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class DatabaseConnections:
    def __init__(self):
        self.postgres_conn = None
        self.pgvector_conn = None
        self.redis_client = None
    
    def connect_postgres(self):
        """PostgreSQL 연결(sync)"""
        try:
            # postgresql://username:password@host:port:dbname
            connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            self.postgres_conn = psycopg.connect(connection_string)
            print("postgres connection complete")
            return self.postgres_conn

        except Exception as e:
            print(f"Fail to connect to PostgreSQL: {e}")
            return None
    
    async def connect_postgres_async(self):
        """PostgreSQL 연결(async)"""
        try:
            connection_string = f"postgresql://{os.getenv('POSTGRES_USER')}:\
                {os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:\
                    {os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            self.postgres_conn = await psycopg.AsyncConnection.connect(connection_string)
            print("postgres async connection complete")
            return self.postgres_conn

        except Exception as e:
            print(f"Fail to async connect to PostgreSQL: {e}")
            return None
    
    def connect_pgvector(self):
        """PgVector 연결 (sync)"""
        try:
            connection_string = f"postgresql://{os.getenv('PGVECTOR_USER')}:{os.getenv('PGVECTOR_PASSWORD')}@{os.getenv('PGVECTOR_HOST')}:{os.getenv('PGVECTOR_PORT')}/{os.getenv('PGVECTOR_DB')}"
            
            self.pgvector_conn = psycopg.connect(connection_string)
            
            # pgvector 확장 활성화
            with self.pgvector_conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                self.pgvector_conn.commit()
            
            print("PgVector 연결 성공!")
            return self.pgvector_conn
        except Exception as e:
            print(f"PgVector 연결 실패: {e}")
            return None

    async def connect_pgvector_async(self):
        """PgVector 비동기 연결"""
        try:
            connection_string = f"postgresql://{os.getenv('PGVECTOR_USER')}:{os.getenv('PGVECTOR_PASSWORD')}@{os.getenv('PGVECTOR_HOST')}:{os.getenv('PGVECTOR_PORT')}/{os.getenv('PGVECTOR_DB')}"
            
            self.pgvector_conn = await psycopg.AsyncConnection.connect(connection_string)
            
            # pgvector 확장 활성화
            async with self.pgvector_conn.cursor() as cur:
                await cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                await self.pgvector_conn.commit()
            
            print("PgVector 비동기 연결 성공!")
            return self.pgvector_conn
        except Exception as e:
            print(f"PgVector 비동기 연결 실패: {e}")
            return None

    def connect_redis(self):
        """Redis 연결"""
        try: 
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True
            )

            self.redis_client.ping()
            print("Redis 연결 성공")
            return self.redis_client
        except Exception as e:
            print(f"Redis 연결 실패: {e}")
            return None

    def close_connections(self):
        """모든 연결 종료 (sync)"""
        if self.postgres_conn:
            self.postgres_conn.close()
        if self.pgvector_conn:
            self.pgvector_conn.close()
        if self.redis_client:
            self.redis_client.close()