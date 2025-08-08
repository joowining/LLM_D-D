@echo off
title D&D Adventure Game

echo 🎮 D&D Adventure Game 시작 중...

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python을 찾을 수 없습니다.
    echo 📌 https://python.org에서 Python을 설치해주세요.
    pause
    exit /b 1
)

REM Rust 확인
cargo --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Rust/Cargo를 찾을 수 없습니다.
    echo 📌 https://rustup.rs에서 Rust를 설치해주세요.
    pause
    exit /b 1
)

REM 파일 존재 확인
if not exist "python-engine\main.py" (
    echo ❌ Python 게임 엔진을 찾을 수 없습니다.
    pause
    exit /b 1
)

if not exist "rust-ui\Cargo.toml" (
    echo ❌ Rust UI 프로젝트를 찾을 수 없습니다.
    pause
    exit /b 1
)

echo ✅ 모든 요구사항이 충족되었습니다.
echo.
echo 🚀 TUI와 함께 게임을 시작합니다...
echo 📌 종료하려면 게임 내에서 'q' 또는 'ESC'를 누르세요.
echo.

cd rust-ui
cargo run --release

if %errorlevel% equ 0 (
    echo.
    echo 🎉 게임이 정상적으로 종료되었습니다!
) else (
    echo.
    echo ❌ 게임 실행 중 오류가 발생했습니다.
    echo 🔧 환경 설정을 확인해보세요.
)

pause