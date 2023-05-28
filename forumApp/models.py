import os

from django.db import models
from django.utils import timezone


# Create your models here.


def user_directory_path(instance, filename):
    ext = filename.split('.').pop()
    filename = '{0}{1}.{2}'.format(instance.name, instance.identity_card, ext)
    return os.path.join(instance.major.name, filename)  # 系统路径分隔符差异，增强代码重用性


class Login(models.Model):
    objects = models.Manager()
    username = models.CharField(max_length=15, unique=True, blank=False, null=False)
    password = models.CharField(max_length=20, blank=False, null=False, default="")
    user_code = models.CharField(max_length=10, blank=False, null=False, default="")

    def __str__(self):
        return self.username


class User(models.Model):
    nickname = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    UserName = models.OneToOneField(Login, on_delete=models.CASCADE, related_name='login_name')
    Email = models.CharField(max_length=30)
    birthday = models.CharField(max_length=20, blank=False, null=False, default="2000-00-00")
    sex = models.BooleanField(default=True)  # True表示男性，False表示女性
    Follower = models.IntegerField(blank=True, null=True)  # 仅关注我的人数
    SelfIntro = models.CharField(max_length=255, blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by')
    imageSrc = models.ImageField(upload_to='photos', default="avatar.jpg")

    def __str__(self):
        return self.UserName


class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_user')
    type = models.CharField(max_length=30, blank=True, null=True, default="校园新闻")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=False, null=False)
    picSrc1 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc2 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc3 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc4 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc5 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc6 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc7 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc8 = models.ImageField(upload_to='photos', blank=True, null=True)
    picSrc9 = models.ImageField(upload_to='photos', blank=True, null=True)
    datetime = models.DateTimeField(default=timezone.now)
    like = models.IntegerField(blank=False, null=False, default=0)  # 点赞
    who_favorite = models.ManyToManyField(to=User, related_name="favorite_posts")  # 收藏
    comment_num = models.IntegerField(blank=False, null=False, default=0)  # 评论数
    location = models.CharField(max_length=255, blank=True, null=True)  # 位置
    # 富文本
    size = models.IntegerField(blank=False, null=False, default=0)
    color = models.CharField(max_length=30, blank=True, null=True)
    thick = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        return self.id


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Conversation(models.Model):  # 一个对话，有两个参与者
    participant1 = models.ForeignKey(User, related_name="conversations1", on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name="conversations2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

