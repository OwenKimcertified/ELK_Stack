# ELK_Stack (logging)
Elastic search, Log stash, Kibana 

1. server 의 log file 을 Beat 로 저장

2. server 의 log 관련 config 가 변경되었을 때 각 서버에 ssh 접속하지 않고

   각 서버의 log config 들을 수정하지 않고 log stash 로 파싱. 

4. elastic search 에 stack

5. stack 된 data 를 kibina 에서 확인 or dashboard

관련 내용들을 정리합니다. 

docker 환경에서 진행하며 설치는 https://github.com/deviantony/docker-elk 에서 클론하고 내용을 보며 설치.

![스크린샷 2023-09-23 15-03-54](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/36a4964c-b2e0-462f-b60b-c6ba182a28af)

### 자세한 개념 설명은 ela.ipynb 파일을 통해 업로드 예정.

### App server 에서 발생하는 Event stream 을 kafka 에 logging

### ELK 를 활용해 kafka 에서 Server 의 Event stream log 를 가져오고 처리 / 분석 / 저장.

# __workflow__ 

Docker : [Zookeeper, kafka(confluent), kafdrop, ELK Stack]

ㄴ docker network connect 활용

1. server log 를 Queue(kafka with zookeeper)

2. kafka 에 저장된 message를 logstash index mapping

3. 날짜별 event log 를 NoSQL(ES) 에 stack -> 스키마를 재정의 후 DW(MySQL) 에 load

4. kibana (dashboard) 로 확인

# Schedule

## 2023 / 09 / 26 ~ 10 / 02

~~ELK docker image 경량화~~

- [X] django restAPI 기능 구현 (basic, logging) 

- [X] Server log - Kafka connection, Zookeeper Failover test 

kafka broker 의 status, topic 별 message 를 GUI로 확인.
![스크린샷 2023-09-30 00-29-15](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/6023ef98-4b49-4a15-8872-9636b35b68d5)

- [X] <mark>Kafka(server log) - Logstash server log 연동 </mark>

```python
docker-elk-main-logstash-1       | [2023-09-30T15:55:30,330][INFO ][org.apache.kafka.clients.consumer.KafkaConsumer][main][0fd99696a92c968bccc1713a676feaca61f52661b8896582adbf98c1fe4f8371] [Consumer clientId=logstash-0, groupId=logstash] Subscribed to topic(s): django_SERVER_LOGS_create_account, django_SERVER_LOGS_question, django_SERVER_LOGS_answer

.....

docker-elk-main-logstash-1       | [2023-09-30T16:11:49,168][ERROR][logstash.codecs.json     ][main][62abd92972a6d191c6edf0d14a8a960c3ec54c02effff72cbc49d8ddd8863036] JSON parse error, original data now in message field {:message=>"incompatible json object type=java.lang.String , only hash map or arrays are supported", :exception=>LogStash::Json::ParserError, :data=>"\"{\\\"log_level\\\": \\\"INFO\\\", \\\"category\\\": \\\"Q_create\\\", \\\"method\\\": \\\"POST\\\", \\\"time\\\": \\\"2023-10-01 01:11\\\", \\\"user_id\\\": 19, \\\"status\\\": \\\"Success\\\"}\""}

```

ㄴ 연동 확인. 일부로 타입 오류 내고 로그 확인.
![스크린샷 2023-10-01 00-37-08](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/820eb38d-7e9a-4b6b-863a-cf229c813c19)

- [X] index mapping

kafka 에서 받아온 message 를 index mapping 
![스크린샷 2023-10-02 02-13-00](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/02f53511-1099-4550-ac8f-84cda138a8b8)

대시보드화 가능. 

logstash 파이프라인을 통해 처리된 Event stream 은 ES 로 가기 전 샤딩.

Event stream 을 여러 샤드 노드로 분할 저장. ES 는 샤드 노드를 활용해 분산 / 병렬 처리함.

ㄴ 검색, 분석 성능 강화. 서버가 커지면 ES config 를 수정해서 클러스터 구성을 조절하기.

## 2023 / 10 / 02 ~ 10 / 03

- [ ] airflow 로 scheduling  

- [ ] 할 일 탐색 중

# Postman (api check)

ENV 추가 후 Authorization ApiKey ~ 추가.

basedir 설정 후 원하는 요청 listup.

swagger.json 으로 load 가능.

### Django REST API 개발 (Web Server)
>(기능 구현 끝난 후 spring boot 로 변경 예정) 

Web 구성은 basic 글,댓글 쓰기, 수정 삭제, 추천, 페이징

# ISSUE LIST

1. makemigrations 시 권한 오류 해결 (ubuntu 에서 git clone 시 잠김 폴더로 된 경우,chmod -R +w 로 해결 안됨)

 - sudo <which python 으로 출력된 path> manage.py makemigrations 

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
3. docker 에서 elk, kafka 연동 시 네트워크 통신 문제 ★

ㄴ 만약 kafka 에 해당하는 docker-compose.yml 파일을 compose up 하고

ㄴ ELK 에 해당하는 docker-compose.yml 파일을 compose up 했다면 

ㄴ 도커의 컨테이너는 기본적으로 격리되어 있어 서로 통신할 수 없다. 

ㄴ 따라서 새로운 네트워크를 생성하고 통신시킬 컨테이너들을 모아야한다. 

ㄴ docker network connect <network-name> <img_id>

ㄴ 이게 싫으면 한 개의 docker-compose.yml 에 모아서 compose up 해도 되지만 권장하지 않음.

4. 각종 logstash 오류들

not eligible, 401(authorization) ... etc 

공식 문서를 활용  
### [ELK stack 공식문서](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html)

5. Scale out 시 문제 

만약 서버가 커져서 트래픽이 많아져 서버를 늘리면 logstash 로 보내는 log 가 많아져 과부화 발생.

ㄴ n * server = n * log 

ㄴ 해결책으로 kafka 를 활용해 FT(장애허용), HA(고 가용성) 보장.

ㄴ kafka 에 SERVER LOG 들을 구분하고 해당하는 topic 들을 생성. 

서버가 늘어나도 SERVER.log 는 logstash 로 일괄 관리.

Auto Scaling 시 모든 서버 인스턴스의 로그 파일을 추적/관리가 매우 힘들어짐. (ssh login 으로 하나 하나 확인해야함)

ㄴ logstash 로 일괄 관리함

