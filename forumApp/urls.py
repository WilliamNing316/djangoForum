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
    path('change/', views.change_password),
    path('user_info/', views.user_info),
    path('user_query/', views.user_query),
    path('who_to_follow/', views.who_to_follow),
    path('who_follow_me/', views.who_follow_me),
    path('blocked/', views.blocked),
    path('follow/', views.follow),
    path('unfollow/', views.unfollow),
    path('unblocked/', views.unblocked),
    path('post/', views.post),
    path('collect/', views.collect),
    path('de_collect/', views.de_collect),
    path('like/', views.like),
    path('de_like/', views.de_like),
    path('my_post/', views.my_post),
    path('all_post/', views.all_post),
    path('create_comment/', views.create_comment),
    path('get_comments/', views.get_comments),
    path('send_message/', views.send_message),
    path('get_messages/', views.get_messages),
    path('search/', views.search),
    path('notify/', views.notify),
    path('change_avatar/', views.change_avatar),
    path('avatar/', views.avatar),
    path('post_photo/', views.post_photo),
    path('notify_num/', views.notify_num)
]
