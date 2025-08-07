import sqlite3
from pathlib import Path
from typing import List, Optional, Dict 


class DnDDatabase:
    def __init__(self, db_path: str = "./DnD.db"):
        self.db_path = Path(db_path)
    
    def get_connection(self):
        """데이터베이스 연결"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 반환
        return conn
    
    def get_race_by_name(self, race_name: str) -> Optional[Dict]:
        """종족 정보 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM race WHERE name = ? COLLATE NOCASE", (race_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_status_by_race(self, race_name: str) -> Optional[Dict]:
        """특정한 종족의 스테이터스를 가져오기"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT strength, agility, mentality, luck, intelligence, base_hp FROM race WHERE name = ? COLLATE NOCASE",(race_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    
    def get_class_by_name(self, class_name: str) -> Optional[Dict]:
        """직업 정보 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM class WHERE name = ? COLLATE NOCASE", (class_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_races(self) -> List[Dict]:
        """모든 종족 목록 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM race ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_race_names(self) -> List[Dict]:
        """모든 종족 이름 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM race ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_classes(self) -> List[Dict]:
        """모든 직업 목록 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM class ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_class_names(self) -> List[Dict]:
        """모든 직업 이름 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM class ORDER BY name ")

    def get_status_by_class(self, class_name) -> Optional[Dict]: 
        """특정 직업에 따라 스텟 가져오기"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT strength, agility, mentality, luck, intelligence, base_hp FROM class WHERE name = ? COLLATE NOCASE",(class_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def calculate_total_stats(self, race_name: str, class_name: str) -> Optional[Dict]:
        """종족 + 직업 합산 능력치 계산"""
        race_data = self.get_race_by_name(race_name)
        class_data = self.get_class_by_name(class_name)
        
        if not race_data or not class_data:
            return None
        
        return {
            "race": race_data["name"],
            "class": class_data["name"],
            "total_strength": race_data["strength"] + class_data["strength"],
            "total_agility": race_data["agility"] + class_data["agility"],
            "total_mentality": race_data["mentality"] + class_data["mentality"],
            "total_luck": race_data["luck"] + class_data["luck"],
            "total_intelligence": race_data["intelligence"] + class_data["intelligence"],
            "total_hp": race_data["base_hp"] + class_data["base_hp"],
            "race_bonuses": {
                "strength": race_data["strength"],
                "agility": race_data["agility"],
                "mentality": race_data["mentality"],
                "luck": race_data["luck"],
                "intelligence": race_data["intelligence"],
                "base_hp": race_data["base_hp"]
            },
            "class_bonuses": {
                "strength": class_data["strength"],
                "agility": class_data["agility"],
                "mentality": class_data["mentality"],
                "luck": class_data["luck"],
                "intelligence": class_data["intelligence"],
                "base_hp": class_data["base_hp"]
            }
        }

if __name__=="__main__":
    db = DnDDatabase()
    try:
        db.get_all_class_names()
        db.get_all_classes()
        db.get_all_race_names()
        print(db.get_all_races())
        db.get_class_by_name("Warrior")
        db.get_race_by_name("인간")
        db.get_status_by_race("Warrior")
        db.get_status_by_class("인간")
    
    except Exception as e:
        print(f"DB테스트 오류 : {e}")