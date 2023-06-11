import json
from mimetypes import guess_type

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

# Create your views here.

from django.http import HttpResponse, JsonResponse, HttpResponseNotFound

from djangoForum import settings
from .models import *


def index(request):
    return HttpResponse("请求路径:{}".format(request.path))


@transaction.atomic
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
            User.objects.get_or_create(UserName=obj)
            return JsonResponse(1, safe=False)  # 注册成功
        else:
            return JsonResponse(2, safe=False)  # 注册失败
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def login(request):  # 登录
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        res = Login.objects.filter(username=username, password=password).first()  # TODO:从前端接数据

        if res:
            print(res.user_code)
            print(type(res.user_code))
            return JsonResponse(res.user_code+" "+res.password, safe=False)  # 登陆成功
        else:
            user_res = Login.objects.filter(username=username)
            if user_res:
                return JsonResponse(2, safe=False)  # 密码错误
            else:
                return JsonResponse(3, safe=False)  # 用户名不存在

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def change_password(request):  # 修改密码
    if request.method == 'POST':
        # 此时已经登陆
        user_code = request.POST.get('user_code', '')
        new_password = request.POST.get('new_password', '')
        # print("这是新密码:"+new_password)
        # print("这是ID："+user_code)
        res = Login.objects.filter(user_code=user_code).update(password=new_password)
        if res:
            return JsonResponse(1, safe=False)
        return JsonResponse(2, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def user_info(request):  # 更改用户数据
    #  前端传修改的数据
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        change = request.POST.get('change', '')  # 修改的部分
        content = request.POST.get('content', '')  # 修改内容
        user = Login.objects.filter(user_code=user_code.strip('"')).first()
        print(change)
        if change == 'nickname':

            res = User.objects.filter(UserName=user).update(nickname=content)

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

        if res:
            return JsonResponse(res, safe=False)

        return HttpResponse("更改失败！")

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def change_avatar(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        content = request.FILES['content']  # 修改内容
        user = Login.objects.filter(user_code=user_code).first()
        res = User.objects.filter(UserName=user).first()

        file_content = ContentFile(content.read())
        res.imageSrc.save(content.name, file_content)

        if res:
            return JsonResponse(1, safe=False)
        return HttpResponse("更改失败！")
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def user_query(request):  # 查询用户数据
    # 前端只需要传一个用户序号，或者登陆时的用户名
    if request.method == 'POST':
        query = request.POST.get('user_code', '')
        print(query)
        user = Login.objects.filter(user_code=query.strip('"')).first()

        res = User.objects.filter(UserName=user).first()
        if res:
            if res.sex:
                gender = "男"
            else:
                gender = "女"
            dict_ = {"account": res.UserName.username, "ID": res.UserName.user_code,
                     "username": res.nickname, "gender": gender,
                     "intro": res.SelfIntro, "image_url": res.imageSrc.name
                     }
            return JsonResponse(dict_, safe=False)
        else:
            dict_ = {"account": "", "ID": "",
                     "username": "", "gender": "",
                     "intro": "res.SelfIntro", "image_url": ""
                     }
            return JsonResponse(dict_, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def avatar(request):  # 返回对应用户的头像
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = Login.objects.filter(user_code=user_code.strip('"')).first()
        ava = User.objects.filter(UserName=user).values('imageSrc')

        full_path = settings.MEDIA_ROOT + '/' + ava[0]['imageSrc']
        print(full_path)
        content_type, _ = guess_type(full_path)
        try:
            with open(full_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=content_type)
                response['Content-Encoding'] = 'utf-8'

                return response
        except FileNotFoundError:
            return HttpResponseNotFound('图片未找到')

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def who_to_follow(request):  # 我关注了谁
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code.strip('"')).first()).first()
        following_users = user.following.all().values_list('UserName__user_code', flat=True)
        if following_users:
            res = list(following_users)
            print(res)
            return JsonResponse(res, safe=False)
        else:
            return JsonResponse([], safe=False)

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def who_follow_me(request):  # 我的粉丝有谁
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code.strip('"')).first()).first()
        follower_users = user.followers.all().values_list('UserName__user_code', flat=True)
        res = list(follower_users)
        print(res)

        return JsonResponse(res, safe=False)

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def blocked(request):  # 进行屏蔽操作
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        blocked_code = request.POST.get('other_code', '')
        user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        user2 = User.objects.filter(UserName=Login.objects.filter(user_code=blocked_code).first()).first()
        user1.blocked_users.add(user2)  # 用户1屏蔽用户2

        blocked_users = user1.blocked_users.filter(id=user2.id)
        if blocked_users.exists():
            return HttpResponse("更改成功")
        else:
            return HttpResponse("更改失败")

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def unblocked(request):  # 进行屏蔽操作
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        blocked_code = request.POST.get('other_code', '')
        user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        user2 = User.objects.filter(UserName=Login.objects.filter(user_code=blocked_code).first()).first()
        user1.blocked_users.remove(user2)  # 用户1屏蔽用户2

        blocked_users = user1.blocked_users.filter(id=user2.id)
        if not blocked_users.exists():
            return HttpResponse("更改成功")
        else:
            return HttpResponse("更改失败")
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def follow(request):  # 关注他人
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        followed_code = request.POST.get('other_code', '')
        print(user_code + "---" + followed_code)
        user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        user2 = User.objects.filter(UserName=Login.objects.filter(user_code=followed_code).first()).first()
        user1.following.add(user2)
        if user1.following.filter(id=user2.id):
            return HttpResponse("更改成功")
        else:
            return HttpResponse("更改失败")
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def unfollow(request):  # 取消关注
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        followed_code = request.POST.get('other_code', '')
        user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        user2 = User.objects.filter(UserName=Login.objects.filter(user_code=followed_code).first()).first()
        user1.following.remove(user2)
        if not user1.following.filter(id=user2.id).exists():
            return HttpResponse("更改成功")
        else:
            return HttpResponse("更改失败")

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def post(request):  # 发布动态
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        mtype = request.POST.get('type', '')
        title = request.POST.get('title', '')
        text = request.POST.get('text', '')
        pic1 = request.FILES.get('pic1', '')
        pic2 = request.FILES.get('pic2', '')
        pic3 = request.FILES.get('pic3', '')
        pic4 = request.FILES.get('pic4', '')
        pic5 = request.FILES.get('pic5', '')
        pic6 = request.FILES.get('pic6', '')
        pic7 = request.FILES.get('pic7', '')
        pic8 = request.FILES.get('pic8', '')
        pic9 = request.FILES.get('pic9', '')
        video = request.FILES.get('video', '')
        location = request.POST.get('location', '')

        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()

        res, create = Post.objects.get_or_create(user_id=user, type=mtype, title=title, text=text, location=location)
        if pic1 != '':
            file_content = ContentFile(pic1.read())
            res.picSrc1.save(pic1.name, file_content)
        if pic2 != '':
            file_content = ContentFile(pic2.read())
            res.picSrc2.save(pic2.name, file_content)
        if pic3 != '':
            file_content = ContentFile(pic3.read())
            res.picSrc3.save(pic3.name, file_content)
        if pic4 != '':
            file_content = ContentFile(pic4.read())
            res.picSrc4.save(pic4.name, file_content)
        if pic5 != '':
            file_content = ContentFile(pic5.read())
            res.picSrc5.save(pic5.name, file_content)
        if pic6 != '':
            file_content = ContentFile(pic6.read())
            res.picSrc6.save(pic6.name, file_content)
        if pic7 != '':
            file_content = ContentFile(pic7.read())
            res.picSrc7.save(pic7.name, file_content)
        if pic8 != '':
            file_content = ContentFile(pic8.read())
            res.picSrc8.save(pic8.name, file_content)
        if pic9 != '':
            file_content = ContentFile(pic9.read())
            res.picSrc9.save(pic9.name, file_content)
        if video != '':
            file_content = ContentFile(video.read())
            res.video.save(video.name, file_content)

        if create:
            post_id = res.id
            fans = user.followers.all().values('UserName__user_code')
            for fan in fans:
                types = "post"
                sender = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
                recipient = User.objects.filter(
                    UserName=Login.objects.filter(user_code=fan['UserName__user_code']).first()).first()
                Notification.objects.get_or_create(sender=sender, recipient=recipient, detail=str(post_id), type=types)
            return JsonResponse(res.id, safe=False)
        else:
            return JsonResponse("创建失败", safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def collect(request):  # 收藏操作
    if request.method == 'POST':
        # 传两个，分别是用户，和这个动态的序号
        user_code = request.POST.get('user_code', '')
        post_id = request.POST.get('id', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        post_ = Post.objects.filter(id=post_id).first()
        if user and post_:
            post_.who_favorite.add(user)
            post_.favorite_num += 1
            post_.save()
            return HttpResponse("收藏成功")
        else:
            return HttpResponse("收藏失败")
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def de_collect(request):  # 传两个，分别是用户，和这个动态的序号
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        post_id = request.POST.get('id', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        post_ = Post.objects.filter(id=post_id).first()
        if user and post_:
            post_.who_favorite.remove(user)
            if post_.favorite_num > 0:
                post_.favorite_num -= 1
                post_.save()
            return HttpResponse("收藏取消")
        else:
            return HttpResponse("收藏未取消")
    else:
        return HttpResponse('GET请求无效')


def collection(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        posts = user.favorite_posts.all().order_by('-datetime')
        post_all = []
        for post_ in posts:
            uni_post = {"type": post_.type, "title": post_.title, "text": post_.text,
                        "datetime": post_.datetime, "like": post_.like, "location": post_.location,
                        "id": post_.id, "favorite": post_.favorite_num
                        }
            post_all.append(uni_post)

        return JsonResponse(post_all, safe=False)

    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def like(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        post_id = request.POST.get('id', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        post_ = Post.objects.filter(id=post_id).first()
        if user and post_:
            post_.like += 1
            post_.who_like.add(user)
            post_.save()

        receiver = post_.user_id.UserName.user_code
        print(user_code)
        sender = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        recipient = User.objects.filter(UserName=Login.objects.filter(user_code=receiver).first()).first()
        types = "like"
        Notification.objects.get_or_create(sender=sender, recipient=recipient, detail=str(post_id), type=types)

        return JsonResponse(post_.user_id.UserName.user_code, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def de_like(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        post_id = request.POST.get('id', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        post_ = Post.objects.filter(id=post_id).first()
        if user and post_:
            if post_.like > 0:
                post_.like -= 1
                post_.who_like.remove(user)
                post_.save()

                return JsonResponse("成功", safe=False)
        return JsonResponse("失败", safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def my_post(request):  # 返回自己（别人的也可以）的所有的动态
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code.strip('"')).first()).first()
        posts = Post.objects.filter(user_id=user).order_by('-datetime')  # 按照发布时间，反序排序
        post_all = []
        for post_ in posts:
            liked = user in post_.who_like.all()
            collected = user in post_.who_favorite.all()
            if post_.video:
                print(post_.video)
                video_path = post_.video.name + ""
            else:
                video_path = None

            # 初始化一个空列表来保存所有图片的路径
            image_paths = []

            # 创建一个包含所有图片字段的列表
            image_fields = [post_.picSrc1, post_.picSrc2, post_.picSrc3, post_.picSrc4, post_.picSrc5, post_.picSrc6,
                            post_.picSrc7, post_.picSrc8, post_.picSrc9]

            # 遍历图片字段
            for image in image_fields:
                # 如果图片存在
                if image:
                    # 获取图片的路径，并添加到图片路径列表中
                    image_paths.append(image.name + "")
                else:
                    # 如果图片不存在，添加 None 到图片路径列表中
                    image_paths.append(None)

            uni_post = {"mTag": post_.type, "mTitle": post_.title, "mContent": post_.text,
                        "mDate": post_.datetime, "mPraise": post_.like, "mPosition": post_.location,
                        "id": post_.id, "mCollect": post_.favorite_num, "mComment": post_.comment_num,
                        "mAuthor": post_.user_id.nickname, "up_not": liked,
                        "collect_not": collected, "mVideo": video_path, "mImageList": image_paths,
                        "userID": post_.user_id.UserName.user_code
                        }
            post_all.append(uni_post)
        print(post_all)

        return JsonResponse(post_all, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def all_post(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        # 注意！！！order只有三种取值，datetime、like、comment_num
        order = request.POST.get('order', '')  # 按照什么排序
        msg_type = request.POST.get('type', '')  # 展示哪个类型
        other = request.POST.get('other', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code.strip('"')).first()).first()
        following_users = user.following.all().values_list('UserName__user_code', flat=True)

        if msg_type == 'all':
            if other == 'all':
                posts = Post.objects.all().order_by("-" + order)
            elif other == "我的关注":
                posts = Post.objects.all().filter(Q(user_id__in=following_users)).order_by("-" + order)
            elif other == "最近热度":
                posts = Post.objects.all().filter(Q(comment_num__gt=1) | Q(like__gt=1)).order_by("-" + order)
            else:
                posts = Post.objects.all().order_by("-" + order)
        else:
            if other == 'all':
                posts = Post.objects.filter(type=msg_type).order_by("-" + order)
            elif other == "我的关注":
                posts = Post.objects.filter(type=msg_type).filter(Q(user_id__in=following_users)).order_by("-" + order)
            elif other == "最近热度":
                posts = Post.objects.all().filter(Q(comment_num__gt=1) | Q(like__gt=1)).order_by("-" + order)
            else:
                posts = Post.objects.all().order_by("-" + order)
        if posts is not None:
            post_all = []
            print("不为空！")
            for post_ in posts:
                if not user.blocked_users.filter(id=post_.user_id.id).exists():  # 发布者不是被屏蔽的
                    liked = user in post_.who_like.all()
                    collected = user in post_.who_favorite.all()
                    if post_.video:
                        video_path = post_.video.name + ""
                    else:
                        video_path = None

                    # 初始化一个空列表来保存所有图片的路径
                    image_paths = []

                    # 创建一个包含所有图片字段的列表
                    image_fields = [post_.picSrc1, post_.picSrc2, post_.picSrc3, post_.picSrc4, post_.picSrc5,
                                    post_.picSrc6,
                                    post_.picSrc7, post_.picSrc8, post_.picSrc9]

                    # 遍历图片字段
                    for image in image_fields:
                        # 如果图片存在
                        if image:
                            # 获取图片的路径，并添加到图片路径列表中
                            image_paths.append(image.name + "")
                        else:
                            # 如果图片不存在，添加 None 到图片路径列表中
                            image_paths.append(None)

                    uni_post = {"mTag": post_.type, "mTitle": post_.title, "mContent": post_.text,
                                "mDate": post_.datetime, "mPraise": post_.like, "mPosition": post_.location,
                                "id": post_.id, "mCollect": post_.favorite_num, "mComment": post_.comment_num,
                                "mAuthor": post_.user_id.nickname, "up_not": liked,
                                "collect_not": collected, "mVideo": video_path, "mImageList": image_paths,
                                "userID": post_.user_id.UserName.user_code
                                }
                    post_all.append(uni_post)
            return JsonResponse(post_all, safe=False)

        return JsonResponse("None", safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def uni_post(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        post_id = request.POST.get('post_id', '')
        post_ = Post.objects.filter(id=post_id).first()
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code.strip('"')).first()).first()

        if post_ is not None:
            liked = user in post_.who_like.all()
            collected = user in post_.who_favorite.all()
            if post_.video:
                video_path = post_.video.name + ""
            else:
                video_path = None

            # 初始化一个空列表来保存所有图片的路径
            image_paths = []

            # 创建一个包含所有图片字段的列表
            image_fields = [post_.picSrc1, post_.picSrc2, post_.picSrc3, post_.picSrc4, post_.picSrc5,
                            post_.picSrc6,
                            post_.picSrc7, post_.picSrc8, post_.picSrc9]

            # 遍历图片字段
            for image in image_fields:
                # 如果图片存在
                if image:
                    # 获取图片的路径，并添加到图片路径列表中
                    image_paths.append(image.name + "")
                else:
                    # 如果图片不存在，添加 None 到图片路径列表中
                    image_paths.append(None)

            uni_post = {"mTag": post_.type, "mTitle": post_.title, "mContent": post_.text,
                        "mDate": post_.datetime, "mPraise": post_.like, "mPosition": post_.location,
                        "id": post_.id, "mCollect": post_.favorite_num, "mComment": post_.comment_num,
                        "mAuthor": post_.user_id.nickname, "up_not": liked,
                        "collect_not": collected, "mVideo": video_path, "mImageList": image_paths,
                        "userID": post_.user_id.UserName.user_code
                        }

            return JsonResponse(uni_post, safe=False)

        return JsonResponse("None", safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def post_photo(request):  # 返回一个动态对应的一张照片
    if request.method == 'POST':
        post_id = request.POST.get('id', '')
        i = request.POST.get('i', '')
        print(post_id)
        print(i)

        pic_fields = [f'picSrc{i}' for i in range(1, 10)]
        post_ = Post.objects.filter(id=post_id).values(pic_fields[int(i)])

        if post_[0][pic_fields[int(i)]] != '':
            full_path = settings.MEDIA_ROOT + '/' + post_[0][pic_fields[int(i)]]
            content_type, _ = guess_type(full_path)
            try:
                with open(full_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type=content_type)
                    response['Content-Encoding'] = 'utf-8'
                    return response
            except FileNotFoundError:
                return HttpResponseNotFound('图片未找到')
        else:
            return HttpResponseNotFound('图片未找到')
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def post_video(request):
    if request.method == 'POST':
        post_id = request.POST.get('id', '')
        print(post_id)
        post_ = Post.objects.filter(id=post_id).values('video')
        if post_[0]['video'] != '':
            full_path = settings.MEDIA_ROOT + '/' + post_[0]['video']
            content_type, _ = guess_type(full_path)
            try:
                with open(full_path, 'rb') as file:
                    response = HttpResponse(file.read(), content_type=content_type)
                    response['Content-Encoding'] = 'utf-8'
                    return response
            except FileNotFoundError:
                return HttpResponseNotFound('视频未找到')
        else:
            return HttpResponseNotFound('视频未找到')
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def create_comment(request):  # 写评论
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        content = request.POST.get('content', '')
        post_id = request.POST.get('post_id', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        tmp_post = Post.objects.filter(id=post_id).first()
        tmp_post.comment_num += 1
        tmp_post.save()

        comment = Comment.objects.create(
            user=user,
            post=tmp_post,
            content=content,
            created_at=timezone.now()
        )

        receiver = tmp_post.user_id.UserName.user_code
        types = "comment"
        sender = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        recipient = User.objects.filter(UserName=Login.objects.filter(user_code=receiver).first()).first()
        Notification.objects.get_or_create(sender=sender, recipient=recipient, detail=post_id, type=types)

        return JsonResponse({
            'message': 'Comment created successfully.',
            'comment_id': comment.id,
        })
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def get_comments(request):  # 获取帖子的所有评论
    if request.method == 'POST':
        post_id = request.POST.get('post_id', '')
        print(post_id)
        comments = Comment.objects.filter(post_id=post_id.strip('"')).order_by('-created_at')
        all_comment = []
        if comments:
            for comment in comments:
                uni_comment = {"mImageResource": comment.user.imageSrc.name, "nick_name": comment.user.nickname,
                               "mAccount": comment.user.UserName.user_code, "comment_content": comment.content,
                               "mDate": comment.created_at
                               }
                all_comment.append(uni_comment)

            print(all_comment)
            return JsonResponse(all_comment, safe=False)
        else:
            return JsonResponse(all_comment, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def start_conversation(request):  # 发起对话，需要指定发送者和接收者
    if request.method == 'POST':
        # 获取输入参数
        sender_id = request.POST.get('sender_id', '')
        recipient_id = request.POST.get('recipient_id', '')

        # 获取用户对象
        sender = User.objects.filter(UserName=Login.objects.filter(user_code=sender_id).first()).first()
        recipient = User.objects.filter(UserName=Login.objects.filter(user_code=recipient_id).first()).first()

        # 获取或创建对话对象
        participants = [sender, recipient]
        participants.sort(key=lambda participant: participant.id)
        conversation, created = Conversation.objects.get_or_create(
            participant1=participants[0],
            participant2=participants[1]
        )

        if created:
            return JsonResponse("创建成功", safe=False)
        else:
            return JsonResponse("已有会话", safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def send_message(request):  # 发送消息，需要指定发送者和接收者
    if request.method == 'POST':
        # 获取输入参数
        sender_id = request.POST.get('sender_id', '')
        recipient_id = request.POST.get('recipient_id', '')
        content = request.POST.get('content', '')

        # 获取用户对象
        sender = User.objects.filter(UserName=Login.objects.filter(user_code=sender_id).first()).first()
        recipient = User.objects.filter(UserName=Login.objects.filter(user_code=recipient_id).first()).first()

        # 获取或创建对话对象
        participants = [sender, recipient]
        participants.sort(key=lambda participant: participant.id)
        conversation, created = Conversation.objects.get_or_create(
            participant1=participants[0],
            participant2=participants[1]
        )

        # 创建消息对象
        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            content=content
        )

        # 返回成功响应
        return JsonResponse({'message': 'Message sent successfully.'})
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def get_messages(request):  # 获取两个用户全部聊天记录
    if request.method == 'POST':
        # 获取输入参数
        user1_id = request.POST.get('user1_id')
        user2_id = request.POST.get('user2_id')

        # 获取用户对象
        user1 = User.objects.filter(UserName=Login.objects.filter(user_code=user1_id).first()).first()
        user2 = User.objects.filter(UserName=Login.objects.filter(user_code=user2_id).first()).first()

        # 获取对话对象
        participants = [user1, user2]
        participants.sort(key=lambda participant: participant.id)
        conversation = get_object_or_404(Conversation, participant1=participants[0], participant2=participants[1])

        # 获取消息对象
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')

        # 将消息对象转化为字典列表
        messages_list = []
        for message in messages:
            messages_list.append({
                'sender_id': message.sender.UserName.user_code,
                'content': message.content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # 返回消息列表
        return JsonResponse(messages_list)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def search(request):  # 用空格分割联合查询
    if request.method == 'POST':
        query = request.POST.get('q', '')
        search_type = request.POST.get('type', '')
        if len(query) > 100:
            return JsonResponse({"error": "Search query is too long."}, status=400)
        keywords = query.split()

        if keywords:
            print("接收到查询！")
            username_query = Q()
            title_query = Q()
            text_query = Q()


            for keyword in keywords:
                print(keyword)
                username_query &= Q(nickname__icontains=keyword)
                title_query &= Q(title__icontains=keyword)
                text_query &= Q(text__icontains=keyword)

            user_results = User.objects.filter(username_query)
            title_results = Post.objects.filter(title_query)
            text_results = Post.objects.filter(text_query)


        else:
            user_results = []
            title_results = []
            text_results = []

        user_result = []
        title_result = []
        text_result = []
        context = []

        if search_type == "用户":
            print("查用户")
            for user_ in user_results:
                uni = {"id": user_.UserName.user_code, "nickname": user_.nickname, "image": user_.imageSrc.name}
                user_result.append(uni)

            context = user_result

        elif search_type == "内容":
            print("查内容")
            for post_ in text_results:
                if post_ is not None:
                    if post_.video:
                        video_path = post_.video.name + ""
                    else:
                        video_path = None

                    # 初始化一个空列表来保存所有图片的路径
                    image_paths = []

                    # 创建一个包含所有图片字段的列表
                    image_fields = [post_.picSrc1, post_.picSrc2, post_.picSrc3, post_.picSrc4, post_.picSrc5,
                                    post_.picSrc6,
                                    post_.picSrc7, post_.picSrc8, post_.picSrc9]

                    # 遍历图片字段
                    for image in image_fields:
                        # 如果图片存在
                        if image:
                            # 获取图片的路径，并添加到图片路径列表中
                            image_paths.append(image.name + "")
                        else:
                            # 如果图片不存在，添加 None 到图片路径列表中
                            image_paths.append(None)

                    uni_post = {"mTag": post_.type, "mTitle": post_.title, "mContent": post_.text,
                                "mDate": post_.datetime, "mPraise": post_.like, "mPosition": post_.location,
                                "id": post_.id, "mCollect": post_.favorite_num, "mComment": post_.comment_num,
                                "mAuthor": post_.user_id.nickname, "mVideo": video_path, "mImageList": image_paths,
                                "userID": post_.user_id.UserName.user_code
                                }
                    text_result.append(uni_post)

                    context = text_result
        elif search_type == "标题":
            print("查标题")
            for post_ in title_results:
                if post_ is not None:
                    if post_.video:
                        video_path = post_.video.name + ""
                    else:
                        video_path = None

                    # 初始化一个空列表来保存所有图片的路径
                    image_paths = []

                    # 创建一个包含所有图片字段的列表
                    image_fields = [post_.picSrc1, post_.picSrc2, post_.picSrc3, post_.picSrc4, post_.picSrc5,
                                    post_.picSrc6,
                                    post_.picSrc7, post_.picSrc8, post_.picSrc9]

                    # 遍历图片字段
                    for image in image_fields:
                        # 如果图片存在
                        if image:
                            # 获取图片的路径，并添加到图片路径列表中
                            image_paths.append(image.name + "")
                        else:
                            # 如果图片不存在，添加 None 到图片路径列表中
                            image_paths.append(None)

                    uni_post = {"mTag": post_.type, "mTitle": post_.title, "mContent": post_.text,
                                "mDate": post_.datetime, "mPraise": post_.like, "mPosition": post_.location,
                                "id": post_.id, "mCollect": post_.favorite_num, "mComment": post_.comment_num,
                                "mAuthor": post_.user_id.nickname, "mVideo": video_path, "mImageList": image_paths,
                                "userID": post_.user_id.UserName.user_code
                                }
                    title_result.append(uni_post)

                    context = title_result
        else:
            context = []

        return JsonResponse(context, safe=False)
    else:
        return HttpResponse('GET请求无效')


@transaction.atomic
def notify(request):  # 按照点赞、回复、关注人发布新消息分别返回
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        res = Notification.objects.filter(recipient=user).order_by('-created_at')
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
            elif item.type == 'comment':
                replies.append(tmp)
            elif item.type == 'post':
                new_posts.append(tmp)

        context = {
            'likes': likes,
            'replies': replies,
            'new_posts': new_posts,
        }

        return JsonResponse(context)
    else:
        return HttpResponse('GET请求无效')


def notify_num(request):
    if request.method == 'POST':
        user_code = request.POST.get('user_code', '')
        number = request.POST.get('number', '')  # 旧信息个数
        user = User.objects.filter(UserName=Login.objects.filter(user_code=user_code).first()).first()
        res = Notification.objects.filter(recipient=user).count()
        num = res - int(number)

        return JsonResponse(num, safe=False)  # 返回新信息个数
    else:
        return HttpResponse('GET请求无效')
