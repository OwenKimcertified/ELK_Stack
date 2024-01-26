## How to handle Event Stream ?
1 차 : 2023 - 09 - 26 ~ 10 - 04 

2 차 : 2023 - 10 - 08 ~ ing 

목차

1. [Workflow](#workflow)

2. [Schedule](#Schedule)

3. [additional](#additional)

3. [Issue-List](#ISSUE-LIST)

# __workflow__ 

Docker : [Zookeeper, Kafka(confluent), Kafdrop, ELK Stack], BigQuery, Airflow


![image](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/7c11b52c-c780-433a-b4fc-fc5c49f4e334)



1. Web 에서 발생하는 Event Stream 에 대해서 카테고리 별로 kafka topic 에 저장

2. kafka 에 저장된 message를 logstash index mapping

3. kibana (dashboard) 로 확인

4. NoSQL(ES) 에 stack 된 날짜별 log 들을 스키마를 재정의 후 DW(Apache-Hive) 에 저장. <수정: Hive -> bigquery>

   ES : 실시간 모니터링, BigQuery : 배치 처리 모니터링 ( airflow 를 통해 매일 오전 6 : 00 배치 처리됨. )


# Schedule

## 2023 / 09 / 26 ~ 10 / 02

~~ELK docker image 경량화~~ 

- [X] django restAPI 기능 구현 (basic, logging) 

- [X] Server log - Kafka connection, Zookeeper Failover test 

kafka broker 의 status, topic 별 message 를 GUI로 확인.
![스크린샷 2023-09-30 00-29-15](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/6023ef98-4b49-4a15-8872-9636b35b68d5)

- [X] <mark>Kafka(server log) - Logstash server log 연동 </mark>
```python
Kafka 관련

kafka1                 | [2023-10-04 18:33:44,318] TRACE [Broker id=1] Cached leader info UpdateMetadataPartitionState(topicName='django_SERVER_LOGS_question_delete_q', partitionIndex=0, controllerEpoch=74, leader=3, leaderEpoch=12, isr=[3], zkVersion=12, replicas=[3], offlineReplicas=[]) for partition django_SERVER_LOGS_question_delete_q-0 in response to UpdateMetadata request sent by controller 3 epoch 74 with correlation id 3 (state.change.logger)

.
.
.
kafka3                 | [2023-10-04 18:33:49,232] INFO [Controller id=3] Processing automatic preferred replica leader election (kafka.controller.KafkaController)
.
.
.
kafka3                 | [2023-10-04 18:33:49,243] DEBUG [Controller id=3] Topics not in preferred replica for broker 3 HashMap() (kafka.controller.KafkaController)
kafka3                 | [2023-10-04 18:33:49,243] TRACE [Controller id=3] Leader imbalance ratio for broker 3 is 0.0 (kafka.controller.KafkaController)
kafka2                 | [2023-10-04 18:34:18,298] INFO [GroupCoordinator 2]: Dynamic member with unknown member id joins group logstash in Empty state. Created a new member id logstash-0-3557231f-a526-4b40-9d93-1c69cb880a90 and request the member to rejoin with this id. (kafka.coordinator.group.GroupCoordinator)
```
ㄴ kafka controller 가 Leader, Follower 파티션을 지정하고 파티션 상태를 update, logstash 그룹에 kafka 코디네이터가 가입.
```python
kafka2                 | [2023-10-05 13:08:29,602] INFO [GroupCoordinator 2]: Dynamic member with unknown member id joins group logstash in Empty state. Created a new member id logstash-0-428700bf-9673-4251-912a-8abd67649bff and request the member to rejoin with this id. (kafka.coordinator.group.GroupCoordinator)
kafka2                 | [2023-10-05 13:08:29,606] INFO [GroupCoordinator 2]: Preparing to rebalance group logstash in state PreparingRebalance with old generation 38 (__consumer_offsets-49) (reason: Adding new member logstash-0-428700bf-9673-4251-912a-8abd67649bff with group instance id None) (kafka.coordinator.group.GroupCoordinator)
kafka2                 | [2023-10-05 13:08:32,608] INFO [GroupCoordinator 2]: Stabilized group logstash generation 39 (__consumer_offsets-49) with 1 members (kafka.coordinator.group.GroupCoordinator)
kafka2                 | [2023-10-05 13:08:32,621] INFO [GroupCoordinator 2]: Assignment received from leader logstash-0-428700bf-9673-4251-912a-8abd67649bff for group logstash for generation 39. The group has 1 members, 0 of which are static. (kafka.coordinator.group.GroupCoordinator)
```
ㄴ kafka  GroupCoordinator 에 의해 consumer group 이 logstash 그룹에 가입, 그룹 안정화, leader 가 follower 들에게 할당량 배포
 
```python
ELK 관련

docker-elk-main-logstash-1       | [2023-09-30T15:55:30,330][INFO ][org.apache.kafka.clients.consumer.KafkaConsumer][main][0fd99696a92c968bccc1713a676feaca61f52661b8896582adbf98c1fe4f8371] [Consumer clientId=logstash-0, groupId=logstash] Subscribed to topic(s): django_SERVER_LOGS_create_account, django_SERVER_LOGS_question, django_SERVER_LOGS_answer

.....

docker-elk-main-logstash-1       | [2023-09-30T16:11:49,168][ERROR][logstash.codecs.json     ][main][62abd92972a6d191c6edf0d14a8a960c3ec54c02effff72cbc49d8ddd8863036] JSON parse error, original data now in message field {:message=>"incompatible json object type=java.lang.String , only hash map or arrays are supported", :exception=>LogStash::Json::ParserError, :data=>"\"{\\\"log_level\\\": \\\"INFO\\\", \\\"category\\\": \\\"Q_create\\\", \\\"method\\\": \\\"POST\\\", \\\"time\\\": \\\"2023-10-01 01:11\\\", \\\"user_id\\\": 19, \\\"status\\\": \\\"Success\\\"}\""}

```

ㄴ 연동 확인. 일부로 타입 오류 내고 로그 확인.
![스크린샷 2023-10-01 00-37-08](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/820eb38d-7e9a-4b6b-863a-cf229c813c19)

- [X] index mapping

kafka 에서 받아온 message 를 index 에 mapping 
![스크린샷 2023-10-05 03-36-24](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/8c66c3f1-3159-4285-9dde-f223a9189b95)

대시보드 기능 

logstash 파이프라인을 통해 처리된 Event stream 은 ES 로 가기 전 샤딩.

Event stream 을 여러 샤드 노드로 분할 저장. ES 는 샤드 노드를 활용해 분산 / 병렬 처리함.

ㄴ 검색, 분석 성능 강화. 서버가 커지면 ES config 를 수정해서 클러스터 구성을 조절하기.

Airflow 를 활용한 DW(BigQuery) 로 데이터 배치처리.

ㄴ 모니터링이 아닌 데이터 분석을 위한 환경을 위해 DW 사용

![스크린샷 2023-10-07 18-59-53](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/5aa2c05e-e4ab-4e99-a9c4-75b4a44eb86b)

## additional

- [X] multiple pipelines. (2023 - 10 - 01)

pipeline.yml 수정 후 config 파일 추가.
![스크린샷 2024-01-25 13-08-25](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/f74acd08-1da2-48a7-9c22-8859d48f4987)

- [X] airflow 로 scheduling (2023 - 10 - 04)

- [X] cron 으로 일, 주, 월 단위의 쿼리를 cron 으로 자동화. 쉘스크립트 작성
      ㄴ 쿼리 튜닝

- [ ] 2023 - 10 - 07 아이디어 기록.  
1. ES 에서 BigQuery 로 Batch 처리 시 중복되는 데이터 문제 알고리즘으로 해결..? 방법 찾기.

   ㄴ 시, 분 단위로 배치 처리를 한다면 데이터 중복 문제를 해결해야함.

 2. 데이터가 많아지면 배치 처리 속도가 느려질 것임.
   
    ㄴ 기존에는 n 개의 데이터를 검색O(n) 후 날짜를 기준으로 배치 처리.

    ㄴ 이진 검색? 

- [ ] 할 일 탐색 중

# Postman (api check)

ENV 추가 후 Authorization ApiKey ~ 추가.

basedir 설정 후 원하는 요청 listup.

swagger.json 으로 load 가능.

### Django REST API 개발 (Web Server)
>(기능 구현 끝난 후 spring boot 로 변경 예정) 

Web 구성은 basic 글,댓글 쓰기, 수정 삭제, 추천, 페이징

ㄴ 각 category 에 대한 Event stream 을 kafka topic 에 logging
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

6. multiple pipelines 관련

docker file, yml volume 에 pipelines.yml 추가. 경로는 logstash.yml 과 동일하게 수정

```python
config
ㄴ logstash.yml, pipelines.yml

pipeline
ㄴ account.conf, question.conf ....etc config file 
```
7. Apache-Hive 설치시 hive-site.xml 문제 

hive-default.xml.template 을 cp 해서 config 를 수정했을 때 3215 줄에 이상한 특수문자가 섞여있음 

for ~ transactional table ... for 과 transactional 사이의 특수 문자를 제거.

혹시 자바의 버전이 2개 설치되어 있다면 한 개를 제거해야 충돌이 발생하지 않음.

$HIVE_HOME/bin/hive run

8. python - bigquery 연동 관련 

google-cloud-sdk 설치. 

pip install google-cloud-bigquery

sdk 를 다운 받고 그 폴더에서 스크립트 실행

지금의 폴더 디렉토리를 생각하며 cli 작성 ./ or ../google-cloud-sdk/install.sh

authorization

/google-cloud-sdk/gcloud auth login 

/google-cloud-sdk/gcloud config set project <project_id>

인증 문제 시 

/google-cloud-sdk/gcloud auth application-default set-quota-project <project_id>

초기화 

/google-cloud-sdk/bin/gcloud init

정상적으로 진행 완료 시 

홈 디렉토리에 .config 숨김 폴더가 생성, .config/gcloud/application_default~.json 파일 생성

application_default~.json 를 cat 시 프로젝트, 클라이언트, 토큰, 권한 등을 확인

# ELK Basic
Elastic search, Log stash, Kibana 

1. server 의 log file 을 Beat 로 저장

2. server 의 log 관련 config 가 변경되었을 때 각 서버에 ssh 접속하지 않고

   각 서버의 log config 들을 수정하지 않고 log stash 로 파싱. 

4. elastic search 에 stack

5. stack 된 data 를 kibina 에서 확인 or dashboard

관련 내용들을 정리합니다. 

docker 환경에서 진행하며 설치는 https://github.com/deviantony/docker-elk 에서 클론하고 내용을 보며 설치.

![스크린샷 2023-09-23 15-03-54](https://github.com/OwenKimcertified/ELK_Stack/assets/99598620/36a4964c-b2e0-462f-b60b-c6ba182a28af)

### 자세한 개념 설명은 ELK_explain.ipynb 파일을 통해 업로드 예정.

ㄴ 업로드 완료.

### App server 에서 발생하는 Event stream 을 kafka 에 logging

### ELK 를 활용해 kafka 에서 Server 의 Event stream log 를 가져오고 처리 / 분석 / 저장.
