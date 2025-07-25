# Poetry 사용 방법
## Poetry 설치
```bash
# 직접 설치
curl -sSL https://install.python-poetry.org | python3 -

# pip 설치 
pip install poetry 

# 설치 확인
poetry --version
```

## 프로젝트 초기화 
### 새 프로젝트 생성
```bash
# 새 디렉토리와 함께 프로젝트 생성
poetry new my-project
cd my-project

# 기존 디렉토리에서 초기화
poetry init  # 대화형
poetry init --no-interactive  # 기본값으로 빠르게
```

## 패키지 관리 명령어
### 패키지 추가
```bash
# 기본 의존성 추가
poetry add requests
poetry add "fastapi>=0.100.0"  # 버전 지정
poetry add fastapi langchain pandas  # 여러 개 동시

# 개발 의존성 추가
poetry add --group dev pytest black flake8
poetry add --group dev jupyter  # 개발용

# 선택적 의존성 추가
poetry add --optional redis
```
### 패키지 제거
```bash
poetry remove requests
poetry remove --group dev pytest
```
### 패키지 업데이트 
```bash
poetry update  # 모든 패키지 업데이트
poetry update requests  # 특정 패키지만
poetry update --dry-run  # 시뮬레이션 (실제 업데이트 안함)
```

## 환경관리
### 가상 환경 관리
```bash
# 가상환경 생성 (패키지 설치 시 자동 생성됨)
poetry install

# 가상환경 활성화
poetry shell

# 가상환경에서 명령 실행
poetry run python script.py
poetry run pytest
poetry run jupyter notebook

# 가상환경 정보 확인
poetry env info
poetry env info --path  # 경로만 출력

# 가상환경 삭제
poetry env remove python
```
### Python 버전 관리
```bash
# 특정 Python 버전 사용
poetry env use python3.9
poetry env use /usr/bin/python3.8

# 현재 사용 중인 Python 확인
poetry env info
```

## 의존성 확인
### 설치된 패키지 확인
```bash
poetry show  # 모든 패키지 목록
poetry show --tree  # 의존성 트리
poetry show --latest  # 최신 버전과 비교
poetry show requests  # 특정 패키지 상세 정보

# 그룹별 확인
poetry show --only main  # 메인 의존성만
poetry show --only dev   # 개발 의존성만
```
### 의존성 문제 확인
```bash
poetry check  # pyproject.toml 유효성 검사
poetry lock --check  # lock 파일 일치 확인
```

## 스크립트 및 실행
### 스크립트 정의 및 실행
```bash
# pyproject.toml에 스크립트 정의 후
poetry run my-script

# 직접 실행
poetry run python -m my_project
poetry run python my_project/main.py
```

## 빌드 및 배포
### 패키지 빌드
```bash
poetry build  # wheel과 tar.gz 생성
poetry build --format wheel  # wheel만 생성
```
### PyPI에 배포
```bash
# 설정
poetry config pypi-token.pypi your-token

# 배포
poetry publish
poetry publish --build  # 빌드와 동시에 배포

# 테스트 PyPI에 배포
poetry publish --repository testpypi
```

## 실용적인 워크플로우
### 새프로젝트 시작
```bash
# 1. 프로젝트 생성
poetry new my-fastapi-project
cd my-fastapi-project

# 2. 의존성 추가
poetry add fastapi uvicorn
poetry add --group dev pytest black

# 3. 개발 시작
poetry shell
# 또는
poetry run python main.py
```
### 기존 프로젝트 복제
```bash
# 1. 저장소 클론
git clone repo-url
cd project

# 2. 의존성 설치
poetry install

# 3. 개발 환경 활성화
poetry shell
```
### 팀 협업
```bash
# 새 의존성 추가 후 커밋
poetry add new-package
git add pyproject.toml poetry.lock
git commit -m "Add new-package dependency"

# 다른 팀원이 업데이트
git pull
poetry install  # 자동으로 새 의존성 설치
```

## 유용한 방법
### 빠른 의존성 설치
```bash
# requirements.txt가 있는 경우
cat requirements.txt | xargs poetry add

# 개발 의존성 일괄 추가
poetry add --group dev pytest black flake8 mypy isort
```
### 환경 변수 사용
```bash
# .env 파일과 함께 사용
poetry add python-dotenv
poetry run python -c "import os; from dotenv import load_dotenv; load_dotenv()"
```
### VScode 통합
```bash
# Poetry 가상환경 경로 확인
poetry env info --path

# VS Code에서 Python 인터프리터로 설정
# Ctrl+Shift+P → Python: Select Interpreter
```
