import sqlite3
import os
from pathlib import Path
from typing import List, Tuple, Optional

class DnDDatabaseManager:
    def __init__(self, db_path: str = "DnD.db"):
        """
        D&D 데이터베이스 매니저 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self.db_initialized = False
    
    def initialize_database(self) -> bool:
        """
        데이터베이스 초기화 - 프로젝트 시작 시 한 번만 호출
        
        Returns:
            bool: 초기화 성공 여부
        """
        try:
            # 데이터베이스 디렉토리 생성
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 데이터베이스 연결
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블 생성
                self._create_race_table(cursor)
                self._create_class_table(cursor)
                
                # 변경사항 커밋
                conn.commit()
                
                print(f"✅ D&D 데이터베이스 초기화 완료: {self.db_path}")
                print(f"📁 데이터베이스 크기: {self.db_path.stat().st_size} bytes")
                
                self.db_initialized = True
                return True
                
        except sqlite3.Error as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
            return False
    
    def _create_race_table(self, cursor: sqlite3.Cursor) -> None:
        """Race 테이블 생성"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS race (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                strength INTEGER NOT NULL DEFAULT 0,
                agility INTEGER NOT NULL DEFAULT 0,
                mentality INTEGER NOT NULL DEFAULT 0,
                luck INTEGER NOT NULL DEFAULT 0,
                intelligence INTEGER NOT NULL DEFAULT 0,
                base_hp INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("📋 Race 테이블 생성 완료")
    
    def _create_class_table(self, cursor: sqlite3.Cursor) -> None:
        """Class 테이블 생성"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS class (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                strength INTEGER NOT NULL DEFAULT 0,
                agility INTEGER NOT NULL DEFAULT 0,
                mentality INTEGER NOT NULL DEFAULT 0,
                luck INTEGER NOT NULL DEFAULT 0,
                intelligence INTEGER NOT NULL DEFAULT 0,
                base_hp INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("📋 Class 테이블 생성 완료")
    
    def check_tables_exist(self) -> bool:
        """테이블 존재 여부 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블 목록 조회
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('race', 'class')
                """)
                
                tables = [row[0] for row in cursor.fetchall()]
                return 'race' in tables and 'class' in tables
                
        except sqlite3.Error:
            return False
    
    def add_sample_data(self) -> None:
        """샘플 데이터 추가 (선택사항)"""
        if not self.db_initialized:
            print("❌ 데이터베이스가 초기화되지 않았습니다.")
            return
        
        # 샘플 종족 데이터
        sample_races = [
            ("인간", "균형잡힌 능력치를 가진 인간", 3, 3, 3, 3, 3, 100),
            ("엘프", "민첩하고 지적인 엘프", 2, 5, 3, 2, 3, 80),
            ("늑대인간","혹독한 환경에 적응하는 늑대인간",4,4,2,3,2,150),
            ("드워프", "강하고 튼튼한 드워프", 4,2,3,3,3, 120),
            ("하플링", "작지만 운이 좋은 하플링", 2,2,2,5,3, 70)
        ]
        
        # 샘플 클래스 데이터
        sample_classes = [
            ("Warrior", "근접 전투의 전문가", 5,2,0,0,0, 50),
            ("Mage", "마법의 대가", 0,0,2,0,3, 20),
            ("Rogue", "은밀함과 민첩함의 화신", 1,3,0,2,0,10),
            ("Bard", "노래로 아군은 강화하고 적을 방해는 바드", 0,1,2,0,3, 10)
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Race 데이터 삽입
                cursor.executemany('''
                    INSERT OR IGNORE INTO race 
                    (name, description, strength, agility, mentality, luck, intelligence, base_hp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_races)
                
                # Class 데이터 삽입
                cursor.executemany('''
                    INSERT OR IGNORE INTO class 
                    (name, description, strength, agility, mentality, luck, intelligence, base_hp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_classes)
                
                conn.commit()
                print("✅ 샘플 데이터 추가 완료")
                
        except sqlite3.Error as e:
            print(f"❌ 샘플 데이터 추가 실패: {e}")
    
    def view_tables_info(self) -> None:
        """테이블 정보 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Race 테이블 정보
                cursor.execute("SELECT COUNT(*) FROM race")
                race_count = cursor.fetchone()[0]
                
                # Class 테이블 정보  
                cursor.execute("SELECT COUNT(*) FROM class")
                class_count = cursor.fetchone()[0]
                
                print(f"\n📊 데이터베이스 정보:")
                print(f"  📁 파일 위치: {self.db_path.absolute()}")
                print(f"  🏃 Race 테이블 레코드 수: {race_count}")
                print(f"  ⚔️  Class 테이블 레코드 수: {class_count}")
                
                # 샘플 데이터 조회
                if race_count > 0:
                    print(f"\n🏃 Race 샘플:")
                    cursor.execute("SELECT name, strength, agility, intelligence, base_hp FROM race LIMIT 3")
                    for row in cursor.fetchall():
                        print(f"  - {row[0]}: STR:{row[1]} AGI:{row[2]} INT:{row[3]} HP:{row[4]}")
                
                if class_count > 0:
                    print(f"\n⚔️ Class 샘플:")
                    cursor.execute("SELECT name, strength, agility, intelligence, base_hp FROM class LIMIT 3")
                    for row in cursor.fetchall():
                        print(f"  - {row[0]}: STR:{row[1]} AGI:{row[2]} INT:{row[3]} HP:{row[4]}")
                        
        except sqlite3.Error as e:
            print(f"❌ 테이블 정보 조회 실패: {e}")


def main():
    """메인 함수 - 프로젝트 시작 시 호출"""
    print("🎲 D&D 데이터베이스 초기화 시작...")
    
    # 데이터베이스 매니저 생성
    db_manager = DnDDatabaseManager("../db/DnD.db")  # database 폴더에 생성
    
    # 데이터베이스 초기화
    if db_manager.initialize_database():
        
        # 테이블 존재 확인
        if db_manager.check_tables_exist():
            print("✅ 모든 테이블이 정상적으로 생성되었습니다.")
            
            # 샘플 데이터 추가 (선택사항)
            choice = input("\n샘플 데이터를 추가하시겠습니까? (y/n): ").lower()
            if choice == 'y':
                db_manager.add_sample_data()
            
            # 테이블 정보 출력
            db_manager.view_tables_info()
            
        else:
            print("❌ 테이블 생성에 문제가 있습니다.")
    
    else:
        print("❌ 데이터베이스 초기화에 실패했습니다.")

# 프로젝트 시작 시 자동 실행되도록 하는 함수
def ensure_dnd_database():
    """
    프로젝트의 다른 모듈에서 import하여 사용할 수 있는 함수
    데이터베이스가 없으면 자동으로 생성
    """
    db_manager = DnDDatabaseManager("../db/DnD.db")
    
    if not db_manager.db_path.exists() or not db_manager.check_tables_exist():
        print("🔄 D&D 데이터베이스 자동 초기화 중...")
        db_manager.initialize_database()
        db_manager.add_sample_data()  # 자동으로 샘플 데이터 추가
        return True
    else:
        print("✅ D&D 데이터베이스가 이미 존재합니다.")
        return False


if __name__ == "__main__":
    main()