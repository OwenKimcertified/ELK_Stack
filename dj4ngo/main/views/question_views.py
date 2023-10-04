from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from ..forms import QuestionForm
from ..models import Question
from register.forms import UserForm
from django.contrib.auth import get_user_model
import logging, datetime, json
from kafka import KafkaProducer

logger = logging.getLogger('main_logger')
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
KAFKA_BROKERS = ['localhost:9091', 'localhost:9092', 'localhost:9093']
KAFKA_TOPIC = 'django_SERVER_LOGS_question'
producer = KafkaProducer(bootstrap_servers = KAFKA_BROKERS,
                         value_serializer = lambda d: json.dumps(d).encode('utf-8'))

UserModel = get_user_model()

@login_required(login_url='register:login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit = False)
            question.author = request.user
            question.create_date = timezone.now()
            question.save()
            return redirect('main:index')
    else:
        form = QuestionForm()
    context = {'form': form}

    username = request.user.username
    db_user = UserModel.objects.get(username = username)    
    success_create_Q = {
        'log_level' : 'INFO',
        'category' : 'Q_create',
        'method' : 'POST',
        'time' : current_time,
        'user_id' : db_user.id,
        'status' : 'Success'
    }    
    logger.debug(json.dumps(success_create_Q))
    producer.send(KAFKA_TOPIC + '_create_q', value = json.dumps(success_create_Q))
    producer.flush()    
    return render(request, 'main/question_form.html', context)

@login_required(login_url = 'register:login')
def question_modify(request, question_id):
    question = get_object_or_404(Question, pk = question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('main:detail', question_id = question.id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance = question)
        if form.is_valid():
            question = form.save(commit = False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()

            username = request.user.username
            db_user = UserModel.objects.get(username = username)    
            success_modify_Q = {
                'log_level' : 'INFO',
                'category' : 'Q_modify',
                'method' : 'POST',
                'time' : current_time,
                'user_id' : db_user.id,
                'question_id' : question.id,
                'status' : 'Success'
            }    
            logger.debug(json.dumps(success_modify_Q))
            producer.send(KAFKA_TOPIC + '_modify_q', value = json.dumps(success_modify_Q))
            producer.flush()                  
            return redirect('main:detail', question_id = question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'main/question_form.html', context)

@login_required(login_url = 'register:login')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk = question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('main:detail', question_id = question.id)
    question.delete()

    username = request.user.username
    db_user = UserModel.objects.get(username = username)    
    success_modify_Q = {
        'log_level' : 'INFO',
        'category' : 'Q_delete',
        'method' : 'POST',
        'time' : current_time,
        'user_id' : db_user.id,
        'question_id' : question.id,
        'status' : 'Success'
    }    

    logger.debug(json.dumps(success_modify_Q))
    producer.send(KAFKA_TOPIC + '_delete_q', value = json.dumps(success_modify_Q))
    producer.flush()     
    return redirect('main:index')

@login_required(login_url = 'register:login')
def question_vote(request, question_id):
    question = get_object_or_404(Question, pk = question_id)
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        question.voter.add(request.user)

        success_vote_Q = {
            'log_level' : 'INFO',
            'category' : 'Q_vote',
            'method' : 'POST',
            'time' : current_time,
            'voter' : request.user.id,
            'question_id' : question.id,
            'status' : 'Success'
        }    
        logger.debug(json.dumps(success_vote_Q))
        producer.send(KAFKA_TOPIC + '_voter_q', value = json.dumps(success_vote_Q))
        producer.flush()      
    return redirect('main:detail', question_id = question.id)