from database import DatabaseConnections
import json

def main():
    # 데이터베이스 연결지점 객체
    db = DatabaseConnections()

    # DB를 실제로 연결 시도
    postgres_conn = db.connect_postgres()
    pgvector_conn = db.connect_pgvector()
    redis_client = db.connect_redis()

    # PostgreSQL 사용 예시 
    ## 임시 테이블 test를 만들고 쿼리 실행
    if postgres_conn:
        with postgres_conn.cursor() as cur:
            # 테이블 생성
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS test (
                            id INT NOT NULL PRIMARY KEY,
                            name VARCHAR(100),
                            value INT
                        );
                        """)
            
            cur.execute("""
                        INSERT INTO test ( id, name, value) VALUES (%s, %s, %s); 
                        """, (1, "홍길동", 100))
            postgres_conn.commit()

            # 데이터 삭제
            value_id = 1
            cur.execute("DELETE FROM test WHERE id = %s;", (value_id,))
            postgres_conn.commit()
            print(f"임의의 값 삭제 완료 (ID : {value_id})")

            # 데이터 삭제 확인
            cur.execute("SELECT * FROM test WHERE id = %s;", (value_id,))
            print("=== PostgreSQL 테스트 완료 ===")

    # pgvector 사용 예시 
    if pgvector_conn:
        with pgvector_conn.cursor() as cur:
            # 벡터 테이블 생성 
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS documents (
                            id SERIAL PRIMARY KEY,
                            content TEXT,
                            embedding vector(3)
                        );
                        """)
            # 벡터 데이터 삽입
            cur.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s);",
                ("샘플 문서", "[1,2,3]")
            )
            pgvector_conn.commit()

            # 벡터 유사도 검색
            cur.execute("""
                SELECT content, embedding <-> '[1,2,4]' AS distance 
                FROM documents
                ORDER BY distance LIMIT 5; 
            """)
            results = cur.fetchall()
            print("PgVector 유사도 검색: ", results)

            #벡터 데이터 삭제
            doc_id = 1
            cur.execute("DELETE FROM documents WHERE id = %s;",  (doc_id,))
            pgvector_conn.commit()
            print(f"문서 삭제 완료(ID: {doc_id})")

            #삭제 확인
            cur.execute("SELECT COUNT(*) FROM documents WHERE id = %s;",(doc_id,))
            count = cur.fetchone()[0]
            print(f"삭제 확인: {count}개 (0이면 정상 삭제)")
            print("===PgVector테스트 완료===")

    # Redis 사용 예시  
    if redis_client:
        # 단순 키 -값 저장
        redis_client.set("user:1000", "홍길동")
        user = redis_client.get("user:1000")
        print("Redis User: ", user)

        # JSON데이터 저장
        user_data = {"name":"김철수","age":30, "city":"서울"}
        redis_client.set("user:1001", json.dumps(user_data))
        stored_data = json.loads(redis_client.get("user:1001"))
        print("Redis JSON data : ", stored_data)

        # 리스트 사용
        redis_client.lpush("messages", "first message")
        redis_client.lpush("messages", "second mesage")
        messages = redis_client.lrange("messages",0,-1)
        print("Redis 메세지 목록: " ,messages)

        # 데이터 삭제
        redis_client.delete("user:1000")
        redis_client.delete("user:1001")
        redis_client.delete("messages")
        print("Redis 데이터 삭제 완료 ")

        # 삭제 확인
        deleted_keys = ["user:1000", "user:1001", "messages"]
        for key in deleted_keys:
            exists = redis_client.exists(key)
            print(f"키 '{key}' 존재 여부 : {bool(exists)} (False면 정상)")

        print("===Redis 테스트 완료 === \n")

    #연결 종료
    db.close_connections()

if __name__ == "__main__":
    #동기 실행
    main()