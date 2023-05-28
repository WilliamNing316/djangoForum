import json

from django.db.models import Q
from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse, JsonResponse

from .models import *


def index(request):
    return HttpResponse("请求路径:{}".format(request.path))


def register(request):  # 上传用户名和密码
    print(request.method)
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if len(Login.objects.all()) == 0:
            userCode = 1353232311
        else:
            last_user = Login.objects.last()
            userCode = 1 + int(last_user.user_code)

        user_code = str(userCode)
        obj, created = Login.objects.get_or_create(username=username)

        if created:
            Login.objects.filter(username=username).update(password=password, user_code=user_code)
            User.objects.get_or_create(UserName=obj, PassWord=password)
            return JsonResponse(1, safe=False)  # 注册成功
        else:
            return JsonResponse(2, safe=False)  # 注册失败
    else:
        return HttpResponse('GET请求无效')


def login(request):  # 登录
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        res = Login.objects.filter(username=username, password=password).first()  # TODO:从前端接数据
        if res:
            data = {
                'username': res.username,
                'adminname': res.user_code,
                'code': "成功",
                'Status Code': 200
            }
            return HttpResponse(json.dumps(data), content_type='application/json')  # 登陆成功
        else:
            user_res = Login.objects.filter(username=username)
            if user_res:
                data = {
                    'username': "",
                    'adminname': "",
                    'code': "失败",
                    'Status Code': 500
                }
                return HttpResponse(json.dumps(data), content_type='application/json')  # 密码错误
            else:
                data = {
                    'username': "",
                    'adminname': "",
                    'code': "失败",
                    'Status Code': 404
                }
                return HttpResponse(json.dumps(data), content_type='application/json')  # 用户名不存在

    else:
        return HttpResponse('GET请求无效')


def change_password(request):  # 修改密码
    # 此时已经登陆
    user_code = request.POST.get('user_code', '')
    new_password = request.POST.get('new_password', '')
    res = Login.objects.filter(user_code=user_code).update(password=new_password)
    if res:
        return HttpResponse("更改成功")
    return HttpResponse("更改失败！")


def user_info(request):  # 更改用户数据
    #  前端传修改的数据
    user_code = request.POST.get('user_code', '')
    change = request.POST.get('change', '')  # 修改的部分
    content = request.POST.get('content', '')  # 修改内容
    user = Login.objects.filter(user_code=user_code).first()

    if change == 'nickname':

        res = User.objects.filter(UserName=user).update(nickname=content)

        '''
        print("---------更改了nickname---------")
        print(content)
        print(user_code)
        print(res)
        '''

    elif change == 'gender':
        if content == '男':
            sex = True
        else:
            sex = False
        res = User.objects.filter(UserName=user).update(sex=sex)

    elif change == 'phone':
        res = User.objects.filter(UserName=user).update(phone=content)

    elif change == 'email':
        res = User.objects.filter(UserName=user).update(Email=content)

    elif change == 'birthday':
        res = User.objects.filter(UserName=user).update(birthday=content)

    elif change == 'introduction':
        res = User.objects.filter(UserName=user).update(SelfIntro=content)

    elif change == 'avatar':
        res = User.objects.filter(UserName=user).update(SelfIntro=content)
    else:
        res = User.objects.filter(UserName=user).update(nickname="William", phone="18010476877",
                                                        sex=True, SelfIntro="我是宁哥",
                                                        imageSrc=request.FILES.get('photo'))  # 最后这里是个图片文件

    if res:
        return JsonResponse(res, safe=False)
    return HttpResponse("更改失败！")


def user_query(request):  # 查询用户数据
    # 前端只需要传一个用户序号，或者登陆时的用户名
    query = request.POST.get('queryName', '')
    user = Login.objects.filter(username=query).first()
    res = User.objects.filter(UserName=user).first()

    if res.sex:
        gender = "男"
    else:
        gender = "女"
    dict_ = {"username": res.UserName.username, "user_code": res.UserName.user_code,
             "nickname": res.nickname, "gender": gender, "phone": res.phone,
             "birthday": res.birthday, "email": res.Email,
             "brief_intro": res.SelfIntro,
             }
    # TODO:返回！


def avatar(request):  # 返回对应用户的头像
    user_code = request.POST.get('user_code', '')
    ava = Login.objects.filter(user_code=user_code).first().values('imageSrc')
    # TODO:传图片回前端
    return JsonResponse(ava, safe=False)


def who_to_follow(request):  # 我关注了谁
    user_code = request.POST.get('user_code', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    following_users = user.following.all().values('UserName__user_code')
    res = list(following_users)

    return JsonResponse(res, safe=False)


def who_follow_me(request):  # 我的粉丝有谁
    user_code = request.POST.get('user_code', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    res = user.followers.all().values('UserName__user_code')
    print(res)

    return JsonResponse(res, safe=False)


def blocked(request):  # 进行屏蔽操作
    user_code = request.POST.get('user_code', '')
    blocked_code = request.POST.get('user_code', '')
    user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    user2 = User.objects.filter(UserName=Login.objects.filter(user_code=blocked_code).first()).first()
    user1.blocked_users.add(user2)  # 用户1屏蔽用户2

    blocked_users = user1.blocked_users.filter(id=user2.id)
    if blocked_users.exists():
        return HttpResponse("更改成功")
    else:
        return HttpResponse("更改失败")


def follow(request):  # 关注他人
    user_code = request.POST.get('user_code', '')
    followed_code = request.POST.get('user_code', '')
    user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    user2 = User.objects.filter(UserName=Login.objects.filter(user_code=followed_code).first()).first()
    user1.following.add(user2)


def unfollow(request):  # 取消关注
    user_code = request.POST.get('user_code', '')
    followed_code = request.POST.get('user_code', '')
    user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    user2 = User.objects.filter(UserName=Login.objects.filter(user_code=followed_code).first()).first()
    user1.following.remove(user2)


def post(request):  # 发布动态
    # TODO:传照片！
    user_code = request.POST.get('user_code', '')
    type = request.POST.get('type', '')
    title = request.POST.get('title', '')
    text = request.POST.get('text', '')
    pic1 = request.POST.get('pic1', '')
    pic2 = request.POST.get('pic2', '')
    pic3 = request.POST.get('pic3', '')
    pic4 = request.POST.get('pic4', '')
    pic5 = request.POST.get('pic5', '')
    pic6 = request.POST.get('pic6', '')
    pic7 = request.POST.get('pic7', '')
    pic8 = request.POST.get('pic8', '')
    pic9 = request.POST.get('pic9', '')
    location = request.POST.get('location', '')
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    thick = request.POST.get('thick', '')

    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()

    res, create = Post.objects.get_or_create(user_id=user, type=type, title=title, text=text, picSrc1=pic1,
                                             picSrc2=pic2,
                                             picSrc3=pic3, picSrc4=pic4, picSrc5=pic5, picSrc6=pic6, picSrc7=pic7,
                                             picSrc8=pic8,
                                             picSrc9=pic9, location=location, size=size, color=color, thick=thick)
    if create:
        post_id = res.id
        fans = user.followers.all().values('UserName__user_code')
        for fan in fans:
            types = "post"
            Notification.objects.get_or_create(sender=user_code, recipient=fan, detail=post_id, type=types)
        return JsonResponse(1, safe=False)


def collect(request):  # 收藏操作
    # 传两个，分别是用户，和这个动态的序号
    user_code = request.POST.get('user_code', '')
    post_id = request.POST.get('id', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    post_ = Post.objects.filter(id=post_id).first()
    post_.who_favorite.add(user)


def de_collect(request):  # 传两个，分别是用户，和这个动态的序号
    user_code = request.POST.get('user_code', '')
    post_id = request.POST.get('id', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    post_ = Post.objects.filter(id=post_id).first()
    post_.who_favorite.remove(user)


def like(request):
    user_code = request.POST.get('user_code', '')
    post_id = request.POST.get('id', '')
    post_ = Post.objects.filter(id=post_id).first()
    post_.like += 1
    post_.save()

    receiver = post_.user_id.UserName.user_code
    types = "like"
    Notification.objects.get_or_create(sender=user_code, recipient=receiver, detail=post_id, type=types)

    return JsonResponse(post_.user_id.UserName.user_code, safe=False)


def de_like(request):
    post_id = request.POST.get('id', '')
    post_ = Post.objects.filter(id=post_id).first()
    post_.like -= 1
    post_.save()


def my_post(request):  # 返回自己（别人的也可以）的所有的动态
    user_code = request.POST.get('user_code', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    posts = Post.objects.filter(user_id=user).order_by('datetime')  # 按照发布时间排序
    post_all = []
    for post_ in posts:
        uni_post = {"type": post_.type, "title": post_.title, "text": post_.text,
                    "datetime": post_.datetime, "like": post_.like, "location": post_.location,
                    "size": post_.size, "color": post_.color, "thick": post_.thick, "id": post_.id
                    }
        post_all.append(uni_post)

    #  图片肯定不能跟着一起传，如何传呢


def all_post(request):
    user_code = request.POST.get('user_code', '')
    # 注意！！！order只有三种取值，datetime、like、comment_num
    order = request.POST.get('order', '')  # 按照什么排序
    msg_type = request.POST.get('type', '')  # 展示哪个类型
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()

    if msg_type == 'all':
        posts = Post.objects.all().order_by(order)
    else:
        posts = Post.objects.filter(type=msg_type).order_by(order)

    post_all = []
    for post_ in posts:
        if post_.user_id not in user.blocked_users:  # 发布者不是被屏蔽的
            uni_post = {"type": post_.type, "title": post_.title, "text": post_.text,
                        "datetime": post_.datetime, "like": post_.like, "location": post_.location,
                        "size": post_.size, "color": post_.color, "thick": post_.thick, "id": post_.id
                        }
            post_all.append(uni_post)


def create_comment(request):  # 写评论
    user_code = request.POST.get('user_code', '')
    content = request.POST.get('content', '')
    post_id = request.POST.get('post_id', '')
    user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
    tmp_post = Post.objects.filter(id=post_id).first
    tmp_post.comment_num += 1
    tmp_post.save()

    comment = Comment.objects.create(
        user=user,
        post=tmp_post,
        content=content,
    )

    receiver = tmp_post.user_id.UserName.user_code
    types = "comment"
    Notification.objects.get_or_create(sender=user_code, recipient=receiver, detail=post_id, type=types)

    return JsonResponse({
        'message': 'Comment created successfully.',
        'comment_id': comment.id,
    })


def get_comments(request):  # 获取帖子的所有评论
    post_id = request.POST.get('post_id', '')
    comments = Comment.objects.filter(post_id=post_id).values('user__user_id__UserName__user_code', 'content',
                                                              'created_at')

    return JsonResponse(list(comments), safe=False)


def send_message(request):  # 发送消息，需要指定发送者和接收者
    # TODO:发送之后通知接收者更新会话
    # 获取输入参数
    sender_id = request.POST.get('sender_id', '')
    recipient_id = request.POST.get('recipient_id', '')
    content = request.POST.get('content', '')

    # 获取用户对象
    sender = User.objects.filter(UserName=Login.objects.filter(user_code=sender_id).first()).first()
    recipient = User.objects.filter(UserName=Login.objects.filter(user_code=recipient_id).first()).first()

    # 获取或创建对话对象
    conversation, created = Conversation.objects.get_or_create(
        participant1=sender,
        participant2=recipient
    )

    # 创建消息对象
    message = Message.objects.create(
        sender=sender,
        conversation=conversation,
        content=content
    )

    # 返回成功响应
    return JsonResponse({'message': 'Message sent successfully.'})


def get_messages(request):  # 获取两个用户全部聊天记录
    # 获取输入参数
    user1_id = request.GET.get('user1_id')
    user2_id = request.GET.get('user2_id')

    # 获取用户对象
    user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user1_id).first()).first()
    user2 = User.objects.filter(UserName=Login.objects.filter(user_code=user2_id).first()).first()

    # 获取对话对象
    conversation = get_object_or_404(Conversation, participant1=user1, participant2=user2)

    # 获取消息对象
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')

    # 将消息对象转化为字典列表
    messages_list = []
    for message in messages:
        messages_list.append({
            'sender_id': message.sender.id,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    # 返回消息列表
    return JsonResponse({'messages': messages_list})


def search(request):  # 用空格分割联合查询
    query = request.GET.get('q', '')
    if len(query) > 100:
        return JsonResponse({"error": "Search query is too long."}, status=400)
    keywords = query.split()

    if keywords:
        username_query = Q()
        post_query = Q()
        comment_query = Q()

        for keyword in keywords:
            username_query |= Q(nickname__icontains=keyword)
            post_query |= Q(title__icontains=keyword)
            post_query |= Q(text__icontains=keyword)
            comment_query |= Q(content__icontains=keyword)

        user_results = User.objects.filter(username_query)
        post_results = Post.objects.filter(post_query)
        comment_results = Comment.objects.filter(comment_query)
    else:
        user_results = []
        post_results = []
        comment_results = []
    context = {
        'user_results': user_results,
        'post_results': post_results,
        'comment_result': comment_results,
        'query': query,
    }

    return JsonResponse(context)


def notify(request):
    user_code = request.POST.get('user_code', '')
    res = Notification.objects.filter(recipient=user_code).order_by('-created_at')
    likes = []
    replies = []
    new_posts = []
    for item in res:
        tmp = {"sender": item.sender.UserName.user_code,
               "recipient": item.recipient.UserName.user_code,
               "created_at": item.created_at,
               "detail": item.detail
               }

        if item.type == 'like':
            likes.append(tmp)
        elif item.type == 'reply':
            replies.append(tmp)
        elif item.type == 'new_post':
            new_posts.append(tmp)

        context = {
            'likes': likes,
            'replies': replies,
            'new_posts': new_posts,
        }

        return JsonResponse(context)
