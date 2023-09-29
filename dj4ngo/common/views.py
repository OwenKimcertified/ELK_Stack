from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from common.forms import UserForm
import logging, datetime, json
from kafka import KafkaProducer

logger = logging.getLogger('server_log')
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
KAFKA_BROKERS = ['localhost:9091', 'localhost:9092', 'localhost:9093']
KAFKA_TOPIC = 'django_SERVER_LOGS_create_account'
producer = KafkaProducer(bootstrap_servers = KAFKA_BROKERS,
                         value_serializer = lambda d: json.dumps(d).encode('utf-8'))


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = raw_password) 
            if user is not None:
                login(request, user)
                success_signup_log = {'log_level' : 'info', 
                                      'category' : 'signup',
                                      'time' : current_time,
                                      'method' : 'POST',
                                      'username': username,
                                      'email' : email,
                                      'status' : 'Success'}                    
                logger.debug(success_signup_log)
                producer.send(KAFKA_TOPIC, value = success_signup_log)
                producer.flush()
                return redirect('index')

            else:
                fail_signup_log = {'log_level' : 'info', 
                                   'category' : 'signup',
                                   'time' : current_time,
                                   'method' : 'POST',
                                   'status' : 'Success'}  
                logger.debug(fail_signup_log) 
                producer.send(KAFKA_TOPIC, value = fail_signup_log)
                producer.flush()              
    else:
        form = UserForm()

    
    return render(request, 'common/signup.html', {'form': form})