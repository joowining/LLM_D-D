#!/usr/bin/env python3
"""
D&D 게임 메인 진입점
Rust UI와 연동을 위해 stdout/stdin을 통한 통신 지원
"""

import sys
import os
from pathlib import Path
from enums.phase import GamePhase

# 현재 스크립트의 부모 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """메인 게임 실행 함수"""
    try:
        # intro.py에서 게임 시작
        from graphs.intro import test_intro
        from graphs.village_graph import village_graph
        
        print("🎲 D&D 어드벤처 게임에 오신 것을 환영합니다!", flush=True)
        print("게임을 시작하겠습니다...", flush=True)
        print("", flush=True)  # 빈 줄

        ### Final Result
        #     # 초기 state 준비
        # initial_state = {
        #     "messages": [],
        #     "system_messages": [],
        #     "character_state": {
        #         "name": "",
        #         "race": "",
        #         "profession": "",
        #         "status": {},
        #         "location_type": "",
        #         "location": "",
        #         "attack_item": "",
        #         "defense_item": ""
        #     },
        #     "game_phase": GamePhase.introduction,
        #     "game_context": [],
        #     "story_summary": "",
        #     "question_time": 0,
        #     "cache_box": {}
        # } 
        # # 게임 실행

        # result = test_intro(initial_state)
        # result = village_graph(initial_state) 

        sample_state = {
            "messages": [],
            "system_messages": [],
            "character_state": {
                "name": "Paul",
                "race": "인간",
                "profession": "Warrior",
                "status": {
                    "strength": 5,
                    "agility": 5, 
                    "mentality": 5,
                    "luck": 5,
                    "intelligence": 5,
                    "base_hp": 100,
                    "current_hp": 100
                },
                "location_type": "village",
                "location": "스톤브릿지",
                "attack_item": "long_sowrd",
                "defense_item": "leather_jacket"
            },
            "game_phase": GamePhase.introduction,
            "game_context": [],
            "story_summary": """여러 종족들이 평화롭게 공존하던 에더리아 대륙에 
                흑마법사의 사악한 마법으로 인해 어둠의 던전이 곳곳에 생겨나고 
                모험가는 이를 클리어함으로써 던전을 정화하고 에더리아 대륙의 평화를 되찾아야 한다.
                """,
            "question_time": 0,
            "cache_box": {}
        }
        result = village_graph(sample_state)
        
        if result:
            print("🎉 게임을 성공적으로 클리어 하였습니다!", flush=True)
        else:
            print("❌ 게임 실행 중 오류가 발생했습니다.", flush=True)
            
    except KeyboardInterrupt:
        print("\n🛑 게임이 사용자에 의해 중단되었습니다.", flush=True)
    except Exception as e:
        print(f"💥 게임 실행 중 예기치 못한 오류: {e}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        print("🏁 게임을 종료합니다. 감사합니다!", flush=True)

if __name__ == "__main__":
    main()