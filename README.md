# ELK_Stack (logging)
Elastic search, Log stash, Kibana 

1. server 의 log file 을 Beat 로 저장

2. server 의 log 관련 config 가 변경되었을 때 각 서버에 ssh 접속으로 하나하나 config 를 수정하지 않고 log stash 로 파싱 

3. elastic search 에 stack

4. stack 된 data 를 kibina 에서 확인 or dashboard

관련 내용들을 정리합니다. 

docker 환경에서 진행하며 설치는 https://github.com/deviantony/docker-elk 에서 클론하고 내용을 보며 설치.

![스크린샷 2023-09-23 15-03-54](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/36a4964c-b2e0-462f-b60b-c6ba182a28af)

# Postman (api check)

ENV 추가 후 Authorization ApiKey ~ 추가.

basedir 설정 후 원하는 요청 listup

swagger.json 으로 load 가능

# Django REST API (게시판) 개발 
>(기능 구현 끝난 후 spring boot 로 변경 예정) 

Docker : [Zookeeper, kafka(confluent), kafdrop, ELK Stack]

__workflow__ 

1. server log 를 Queue(kafka with zookeeper)

2. kafka 에 저장된 message를 logstash(indexing)[logstash.conf] 로

3. logstash -> elasticsearch 에 stack

4. kibana (dashboard) 로 확인

만약 서버가 커져서 트래픽이 많아지고 서버를 늘림과 동시에 logstash 로 보내는 logfile 들이 많아져 과부화 발생.

ㄴ n * server = n * log

Auto Scaling 시 모든 서버 인스턴스의 로그 파일을 추적/관리 하기 어려워짐. (ssh login 으로 하나하나 확인해야함)

해결책으로 kafka 를 활용해 FT(장애허용), HA(고 가용성) 보장. kafka 에 서버별 토픽을 분리시키고 메세지를 logstash 로 일괄 관리.

날짜별 event log 를 NoSQL(MongoDB) 에 적재 -> 스키마를 재정의 후 DW 에 load

### ISSUE LIST

1. makemigrations 시 권한 오류 해결 (ubuntu 에서 git clone 시 잠김 폴더로 된 경우,chmod -R +w 로 해결 안됨)

ㄴ sudo <which python 으로 출력된 path> manage.py makemigrations 

Settings.py 파일에 LOGGING config 작성

ㄴ Kafka 에 관련된 config 작성했음에도 작동되지 않았음. view 파일에 logging 을 하거나 다른 방법이 있을 듯. (문제 해결 중)

ㄴ Django settings.py 에 Logging 관련 config 로 handler 에 kafka 와 관련된 것을 넣어도 오류는 나지 않았음

```python
(bigdata) owen@happy:~/ELK_Stack/dj4ngo$ python manage.py runserver 1234
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
```

에서 멈추고 더 이상 진행되지 않았음 -> 호환되지 않음

ㄴ view 파일에 하나하나 json schema 로 logging 하기로 결정함 (spring 으로 빨리 넘어가자)

2. 커밋 전 git pull 시 오류

로컬 브랜치와 원격 브랜치가 충돌해서 발생.

```python
(bigdata) owen@happy:~/ELK_Stack/dj4ngo$ git pull origin main
remote: Enumerating objects: 20, done.
remote: Counting objects: 100% (20/20), done.
remote: Compressing objects: 100% (18/18), done.
remote: Total 18 (delta 6), reused 0 (delta 0), pack-reused 0
오브젝트 묶음 푸는 중: 100% (18/18), 4.91 KiB | 1.23 MiB/s, 완료.
https://github.com/OwenKimcertified/ELK_Stack URL에서
 * branch            main       -> FETCH_HEAD
   a95e3f9..e754872  main       -> origin/main
힌트: You have divergent branches and need to specify how to reconcile them.
힌트: You can do so by running one of the following commands sometime before
힌트: your next pull:
힌트: 
힌트:   git config pull.rebase false  # merge (the default strategy)
힌트:   git config pull.rebase true   # rebase
힌트:   git config pull.ff only       # fast-forward only
힌트: 
힌트: You can replace "git config" with "git config --global" to set a default
힌트: preference for all repositories. You can also pass --rebase, --no-rebase,
힌트: or --ff-only on the command line to override the configured default per
힌트: invocation.
fatal: Need to specify how to reconcile divergent branches.
```

위와 같은 오류 발생. 

ㄴ <mark>로컬 브랜치의 커밋을 원격 브랜치 위로 다시 적용하여 히스토리를 정리하고 선형으로 유지.</mark>
```python
(bigdata) owen@happy:~/ELK_Stack/dj4ngo$ git pull --rebase origin main
https://github.com/OwenKimcertified/ELK_Stack URL에서
 * branch            main       -> FETCH_HEAD
Successfully rebased and updated refs/heads/main.

이후 git push 

bigdata) owen@happy:~/ELK_Stack/dj4ngo$ git push origin main
오브젝트 나열하는 중: 76, 완료.
오브젝트 개수 세는 중: 100% (76/76), 완료.
Delta compression using up to 12 threads
오브젝트 압축하는 중: 100% (53/53), 완료.
오브젝트 쓰는 중: 100% (54/54), 22.02 KiB | 4.40 MiB/s, 완료.
Total 54 (delta 16), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (16/16), completed with 7 local objects.
To https://github.com/OwenKimcertified/ELK_Stack.git
   e754872..e3d782f  main -> main
```

# Schedule

2023 / 09 / 26 ~ 09 / 30

~~ELK docker image 경량화~~

- [X] django restAPI 기능 구현 (basic, logging) 

- [X] Server log - Kafka connection, Zookeeper Failover test 

<mark>Kafka(server log) - Logstash server log 인덱싱</mark>
