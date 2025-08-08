#!/bin/bash

echo "🎮 D&D Adventure Game 환경 설정 시작..."

# 스크립트 실행 위치를 프로젝트 루트로 변경
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📁 프로젝트 루트: $PROJECT_ROOT"
echo "📂 현재 디렉토리 구조:"

# 1. Python 환경 확인 및 설정
echo "🐍 Python 환경 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다. Python3를 먼저 설치해주세요."
    exit 1
fi

echo "✅ Python3 발견: $(python3 --version)"


# 3. requirements.txt가 없다면 기본값 생성
if [ ! -f "./requirements.txt" ]; then
    echo "📝 기본 requirements.txt를 생성합니다..."
    cat > ./requirements.txt << EOF
langchain-core>=0.3.70
langgraph
langchain
langchain-ollama
langchain-text-splitters
python-dotenv
numpy
huggingface-hub
EOF
fi

# 4. Python 가상환경 생성 및 활성화 (선택적)
if [ "$1" = "--venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m .venv venv
    source .venv/bin/activate
    echo "✅ 가상환경 활성화됨"
    cd "$PROJECT_ROOT"
fi

# 5. Python 의존성 설치
echo "📦 Python 의존성 설치 중..."
if [ -f "requirements.txt" ]; then
    # 기존 langchain-core 업그레이드
    pip3 install --upgrade langchain-core
    pip3 install -r requirements.txt --upgrade
    echo "✅ Python 의존성 설치 완료"
else
    echo "⚠️  requirements.txt를 찾을 수 없습니다."
fi
cd "$PROJECT_ROOT"

# 6. Rust 환경 확인
echo "🦀 Rust 환경 확인 중..."
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust가 설치되지 않았습니다."
    echo "📌 https://rustup.rs/ 에서 Rust를 설치해주세요."
    exit 1
fi

echo "✅ Rust 발견: $(rustc --version)"

# 7. Rust 프로젝트 디렉토리 확인 및 생성
if [ ! -d "rust-ui" ]; then
    echo "📁 rust-ui 디렉토리를 생성합니다..."
    mkdir -p rust-ui
    
    # 기존 Cargo.toml이 현재 디렉토리에 있다면 이동
    if [ -f "Cargo.toml" ]; then
        echo "📦 기존 Rust 프로젝트를 rust-ui로 이동합니다..."
        mv Cargo.toml rust-ui/
        mv Cargo.lock rust-ui/ 2>/dev/null || true
        mv src rust-ui/ 2>/dev/null || true
    fi
fi

# 8. Rust 프로젝트가 없다면 기본 프로젝트 생성
if [ ! -f "rust-ui/Cargo.toml" ]; then
    echo "🔧 새 Rust 프로젝트를 생성합니다..."
    cd rust-ui
    cargo init --name dnd-game
    
    # 기본 의존성 추가
    cat >> Cargo.toml << EOF

[dependencies]
crossterm = "0.27"
ratatui = "0.26"
EOF
    cd "$PROJECT_ROOT"
fi

# 9. Rust 의존성 빌드
echo "🔨 Rust 프로젝트 빌드 중..."
cd rust-ui
cargo build
if [ $? -eq 0 ]; then
    echo "✅ Rust 프로젝트 빌드 완료"
else
    echo "❌ Rust 프로젝트 빌드 실패"
    exit 1
fi
cd "$PROJECT_ROOT"

# 10. Python main.py가 없다면 기본값 생성
if [ ! -f "./main.py" ]; then
    echo "📝 기본 Python main.py를 생성합니다..."
    cat > ./main.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 현재 스크립트의 src 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
if (current_dir / "src").exists():
    sys.path.insert(0, str(current_dir / "src"))

def main():
    print("🎲 D&D 어드벤처 게임에 오신 것을 환영합니다!", flush=True)
    print("게임 시스템을 초기화 중입니다...", flush=True)
    
    try:
        # intro.py가 있는지 확인하고 실행
        if (current_dir / "src" / "graphs" / "intro.py").exists():
            from graphs.intro import test_intro
            result = test_intro()
            if result:
                print("🎉 게임이 성공적으로 완료되었습니다!", flush=True)
        else:
            print("게임 모듈을 찾을 수 없습니다. 기본 데모를 실행합니다.", flush=True)
            demo_game()
    except Exception as e:
        print(f"게임 실행 중 오류: {e}", flush=True)

def demo_game():
    print("=== 데모 게임 모드 ===", flush=True)
    print("실제 게임 파일이 준비되면 여기서 실행됩니다.", flush=True)
    while True:
        try:
            user_input = input("명령어를 입력하세요 (quit으로 종료): ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            print(f"입력받음: {user_input}", flush=True)
        except (EOFError, KeyboardInterrupt):
            break
    print("게임을 종료합니다.", flush=True)

if __name__ == "__main__":
    main()
EOF
fi

# 11. 실행 권한 부여
chmod +x scripts/run.sh 2>/dev/null || true
chmod +x ./main.py

echo ""
echo "🎉 설정 완료!"
echo "📁 최종 프로젝트 구조:"
echo "🚀 게임을 실행하려면: ./scripts/run.sh"
echo "📚 도움말을 보려면: ./scripts/run.sh --help"