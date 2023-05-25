# demo/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = "demo"
urlpatterns = [
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('change', views.change_password),
    path('user_info', views.user_info),
    path('user_query', views.user_query),
    path('who_to_follow', views.who_to_follow),
    path('who_to_follow', views.who_to_follow),
    path('blocked', views.blocked),
    path('follow', views.follow),
    path('unfollow', views.unfollow),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
