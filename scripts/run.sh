#!/bin/bash

# D&D Adventure Game 실행 스크립트

show_help() {
    echo "🎲 D&D Adventure Game 실행 스크립트"
    echo ""
    echo "사용법:"
    echo "  ./scripts/run.sh [옵션]"
    echo ""
    echo "옵션:"
    echo "  --help, -h     이 도움말 표시"
    echo "  --setup        환경 설정 먼저 실행"
    echo "  --python-only  Python 엔진만 실행 (TUI 없이)"
    echo "  --debug        디버그 모드로 실행"
    echo ""
    echo "예시:"
    echo "  ./scripts/run.sh           # 기본 실행"
    echo "  ./scripts/run.sh --setup   # 설정 후 실행"
    echo "  ./scripts/run.sh --debug   # 디버그 모드"
}

# 인수 처리
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --setup)
        echo "🔧 환경 설정을 먼저 실행합니다..."
        ./scripts/setup.sh
        if [ $? -ne 0 ]; then
            echo "❌ 환경 설정 실패"
            exit 1
        fi
        echo ""
        ;;
    --python-only)
        echo "🐍 Python 엔진만 실행합니다..."
        python main.py
        exit $?
        ;;
esac

# 실행 전 검증
echo "🎮 D&D Adventure Game 시작 중..."

# Python 엔진 확인
if [ ! -f "./main.py" ]; then
    echo "❌ Python 게임 엔진을 찾을 수 없습니다."
    echo "📁 python-engine/main.py 파일이 있는지 확인해주세요."
    exit 1
fi

# Rust UI 확인
if [ ! -f "rust-ui/Cargo.toml" ]; then
    echo "❌ Rust UI 프로젝트를 찾을 수 없습니다."
    echo "📁 rust-ui/Cargo.toml 파일이 있는지 확인해주세요."
    exit 1
fi

# Python 실행 가능 확인
if ! command -v python &> /dev/null; then
    echo "가상환경을 먼저 실행시켜 주세요"
    echo "🔧 ./scripts/setup.sh를 먼저 실행해주세요."
    exit 1
fi

# Rust 실행 가능 확인
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust/Cargo를 찾을 수 없습니다."
    echo "🔧 ./scripts/setup.sh를 먼저 실행해주세요."
    exit 1
fi

echo "✅ 모든 요구사항이 충족되었습니다."
echo ""

# 게임 실행
echo "🚀 TUI와 함께 게임을 시작합니다..."
echo "📌 종료하려면 게임 내에서 'q' 또는 'ESC'를 누르세요."
echo ""

cd rust-ui

if [ "$1" = "--debug" ]; then
    echo "🐛 디버그 모드로 실행 중..."
    RUST_LOG=debug cargo run
else
    cargo run --release
fi

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 게임이 정상적으로 종료되었습니다!"
else
    echo "❌ 게임 실행 중 오류가 발생했습니다. (코드: $exit_code)"
    echo "🔧 문제가 지속되면 './scripts/run.sh --setup'을 실행해보세요."
fi

exit $exit_code