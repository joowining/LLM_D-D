#!/usr/bin/env python3
"""
D&D 게임 메인 진입점
Rust UI와 연동을 위해 stdout/stdin을 통한 통신 지원
"""

import sys
import os
from pathlib import Path

# 현재 스크립트의 부모 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """메인 게임 실행 함수"""
    try:
        # intro.py에서 게임 시작
        from graphs.intro import test_intro
        
        print("🎲 D&D 어드벤처 게임에 오신 것을 환영합니다!", flush=True)
        print("게임을 시작하겠습니다...", flush=True)
        print("", flush=True)  # 빈 줄
        
        # 게임 실행
        result = test_intro()
        
        if result:
            print("🎉 게임이 성공적으로 완료되었습니다!", flush=True)
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