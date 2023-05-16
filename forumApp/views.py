import json

from django.shortcuts import render

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
            data = {
                'username': obj.username,
                'adminname': obj.user_code,
                'code': "成功",
                'Status Code': 200
            }
            return HttpResponse(json.dumps(data), content_type='application/json')  # 注册成功
            # return HttpResponse(0)
        else:
            data_error = {
                'username': obj.username,
                'adminname': obj.user_code,
                'code': "失败",
                'Status Code': 404
            }
            return HttpResponse(json.dumps(data_error), content_type='application/json')  # 注册失败
            # return HttpResponse(1)
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

    elif change == 'avater':
        # TODO:传图片！
        res = User.objects.filter(UserName=user).update(SelfIntro=content)
    else:
        res = User.objects.filter(UserName=user).update(nickname="William", phone="18010476877",
                                                        sex=True, type="under", LogState=True,
                                                        SelfIntro="我是宁哥",
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
             "follower": res.follower.all().value('UserName'), "following": res.following.all().value('UserName'),
             "brief_intro": res.SelfIntro,
             }


def who_to_follow(request):  # 我关注了谁
    user_code = request.POST.get('user_code', '')
    user = User.objects.filter(User_code=user_code).first()
    following_users = user.following.all()
    res = list(following_users)

    return JsonResponse(res, safe=False)


def who_follow_me(request):  # 我的粉丝有谁
    user_code = request.POST.get('user_code', '')
    user = User.objects.filter(User_code=user_code).first()
    res = user.followers.all().values('UserName')
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
