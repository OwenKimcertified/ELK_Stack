from django.contrib import admin
from django.urls import path, include
from main.views import base_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', include('main.urls')),
    path('register/', include('register.urls')),
    path('', base_views.index, name='index'),
    
]
