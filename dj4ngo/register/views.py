from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from register.forms import UserForm
import logging, datetime, json
from kafka import KafkaProducer

logger = logging.getLogger('main_logger')
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
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            if user is not None:
                login(request, user)  # 로그인
                success_signup_logs = {
                    'log_level' : 'info',
                    'category' : 'sign_up',
                    'time' : current_time,
                    'method' : 'POST',
                    'username' : username,
                    'email' : email,
                    'status' : 'Success'
                }
                logger.debug(json.dumps(success_signup_logs))
                producer.send(KAFKA_TOPIC, value = success_signup_logs)
                producer.flush()
            
                return redirect('index')
    else:
        form = UserForm()
    return render(request, 'register/signup.html', {'form': form})