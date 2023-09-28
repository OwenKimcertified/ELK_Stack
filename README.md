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

(기능 구현 끝난 후 spring boot 로 변경 예정) 

Docker : [Zookeeper, kafka(confluent), kafdrop, ELK Stack] 이미지 경량화하기.

__workflow__ 

1. server log 를 Queue(kafka with zookeeper)

2. kafka 에 저장된 message를 logstash(indexing)[logstash.conf] 로

3. logstash -> elasticsearch 에 stack

4. kibana (dashboard) 로 확인

만약 서버가 커졌을 경우 logstash 로 보내는 logfile 들이 많아져 과부화 발생. n * server = (n+@) logs

해결책으로 kafka 를 활용해 FT(장애허용), HA(고 가용성) 보장.

날짜별 event log 를 NoSQL(MongoDB) 에 적재 -> 스키마를 재정의 후 DW 에 load

### ISSUE LIST

makemigrations 시 권한 오류 해결 (ubuntu 에서 git clone 시 잠김 폴더로 된 경우,chmod -R +w 로 해결 안됨)

ㄴ sudo <which python 으로 출력된 path> manage.py makemigrations 


# Schedule

2023 / 09 / 26 ~ 09 / 30

~~ELK docker image 경량화~~

django restAPI 기능 구현 (basic, logging)

Kafka - server log connection, Zookeeper Failover test 

<mark>Kafka(server log) - Logstash server log 인덱싱</mark>
