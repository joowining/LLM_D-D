# Docker로 DB서버를 로컬에서 시작할 때 주의점 
## Docker 명령어로 현재 켜져있는 내용 찾아보기
```bash
# 현재 켜져 있는 컨테이너만 확인
docker ps 

# 종료된 컨테이너 까지 포함하여 확인
docker ps -a
```
docker ps -a 로 실행했어도 만약 DB와 관련된 컨테이너가 없을 경우 docker pull or 문서내용처럼 docker run으로 이미지를 땡겨온다. 

## Docker 로 실행시키기
```bash
docker start postgres-db pgvector-db redis-cache 
```
이 내용으로 DB를 실행했을 때 
실행이 안된다면 다음으로 확인

## Docker가 사용할 수 없는 이유 
### 1. Docker로 사용한 DB서버가 사용하길 원하는 포트가 이미 점유중일 때
Reids나 Postgres는 PC가 켜지면 자동으로 같이 켜지게 된다.
각 DB가 도커에서 사용하고자 하는 포트를 이미 가지고 있기에 문제가 생긴다. 
```bash
# 해당 포트를 어떤 프로그램이 차지하고 있는지 확인
sudo lsof -i :portnumber

# 포트를 차지하는 프로세스를 죽이려 시도
sudo kill -9 <PID>

# 그래도 안되면 시스템에서 해당 프로그램을 종료
sudo systemctl stop <PROGGRAM>

# redis와 postgres
sudo systemctl stop redis
sudo systemctl stop postgresql
```

위 과정이 마무리되면 다시 docker start로 컨테이너 시작