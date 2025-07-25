# Docker사용법
## 기본적인 Docker 명령어
### Docker 상태 확인
```bash
sudo docker --version
sudo systemctl status docker
```
### 이미지 관리
```bash
# 이미지 검색
sudo docker search ubuntu

# 이미지 다운로드
sudo docker pull ubuntu:20.04

# 로컬 이미지 목록 보기
sudo docker images

# 이미지 삭제
sudo docker rmi 이미지이름:태그
```
### 컨테이너 실행
```bash
# 기본 실행 (일회성)
sudo docker run ubuntu:20.04

# 인터랙티브 모드로 실행
sudo docker run -it ubuntu:20.04 /bin/bash

# 백그라운드 실행
sudo docker run -d --name my-container ubuntu:20.04 sleep 3600

# 포트 매핑하여 실행
sudo docker run -d -p 8080:80 nginx
```
### 컨테이너 관리
```bash
# 실행 중인 컨테이너 보기
sudo docker ps

# 모든 컨테이너 보기 (중지된 것 포함)
sudo docker ps -a

# 컨테이너 중지
sudo docker stop 컨테이너이름[컨테이너ID]

# 컨테이너 시작
sudo docker start 컨테이너이름[컨테이너ID]

# 컨테이너 삭제
sudo docker rm 컨테이너이름[컨테이너ID]

# 실행 중인 컨테이너에 접속
sudo docker exec -it 컨테이너이름[컨테이너ID] /bin/bash
```
### 실행 예시
```bash
# 컨테이너 내부 접속
sudo docker exec -it postgres-db psql -U myuser -d myproject
sudo docker exec -it pgvector-db psql -U vectoruser -d vectordb
sudo docker exec -it redis-cache redis-cli -a myredispass

# 컨테이너 중지/시작
sudo docker stop postgres-db pgvector-db redis-cache
sudo docker start postgres-db pgvector-db redis-cache

# 데이터 볼륨 확인
sudo docker volume ls
```