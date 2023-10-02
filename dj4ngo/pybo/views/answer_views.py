from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from common.forms import UserForm
from ..forms import AnswerForm
from ..models import Question, Answer
import logging, datetime, json
from kafka import KafkaProducer

logger = logging.getLogger('server_log')
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
KAFKA_BROKERS = ['localhost:9091', 'localhost:9092', 'localhost:9093']
KAFKA_TOPIC = 'django_SERVER_LOGS_answer'
producer = KafkaProducer(bootstrap_servers = KAFKA_BROKERS,
                         value_serializer = lambda d: json.dumps(d).encode('utf-8'))

@login_required(login_url = 'common:login')
def answer_create(request, question_id):
    question = get_object_or_404(Question, pk = question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit = False)
            answer.author = request.user  
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
  
            success_create_A = {
                'log_level' : 'INFO',
                'category' : 'A_create',
                'method' : 'POST',
                'time' : current_time,
                'user_id' : request.user.id,
                'answer_id' : answer.id,
                'status' : 'Success'
            }    
            logger.debug(json.dumps(success_create_A))
            producer.send(KAFKA_TOPIC + '_create_a', value = json.dumps(success_create_A))
            producer.flush()        
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:detail', question_id = question.id), answer.id))

    else:
        form = AnswerForm()
    
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)

@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=answer.question.id)
    
    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify_date = timezone.now()
            answer.save()
            success_modify_A = {
                'log_level' : 'INFO',
                'category' : 'A_modify',
                'method' : 'POST',
                'time' : current_time,
                'user_id' : request.user.id,
                'answer_id' : answer.id,
                'status' : 'Success'
            }    
            logger.debug(json.dumps(success_modify_A))
            producer.send(KAFKA_TOPIC + '_modify_a', value = json.dumps(success_modify_A))
            producer.flush()  
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:detail', question_id = answer.question.id), answer.id))
        
    else:
        form = AnswerForm(instance = answer)
    
    context = {'answer': answer, 'form': form}
    return render(request, 'pybo/answer_form.html', context)

@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    
    if request.user != answer.author:
        messages.error(request, '삭제권한이 없습니다')
    
    else:
        answer.delete()
        success_delete_A = {
                'log_level' : 'INFO',
                'category' : 'A_delete',
                'method' : 'POST',
                'time' : current_time,
                'user_id' : request.user.id,
                'answer_id' : answer.id,
                'status' : 'Success'
            }    
        logger.debug(json.dumps(success_delete_A))
        producer.send(KAFKA_TOPIC + '_delete_a', value = json.dumps(success_delete_A))
        producer.flush()          
    return redirect('pybo:detail', question_id=answer.question.id)

@login_required(login_url='common:login')
def answer_vote(request, answer_id):
    answer = get_object_or_404(Answer, pk = answer_id)
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    
    else:
        answer.voter.add(request.user)
        success_vote_A = {
                'log_level' : 'INFO',
                'category' : 'A_vote',
                'method' : 'POST',
                'time' : current_time,
                'answer_id' : answer.id,
                'voter_id' : request.user.id,
                'status' : 'Success'
            }    
        logger.debug(json.dumps(success_vote_A))
        producer.send(KAFKA_TOPIC + '_voter_a', value = json.dumps(success_vote_A))
        producer.flush()         
    return redirect('{}#answer_{}'.format(
                resolve_url('pybo:detail', question_id = answer.question.id), answer.id))