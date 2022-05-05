import json

from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from .models import UserProfile
from tools.logging_dec import logging_check
import hashlib
import random
from django.core.cache import cache
from tools.sms import YunTongXin
from .tasks import send_sms_celery

# CBV模式,更灵活，可继承，对未定义的method请求直接返回405响应
# 定义user应用异常码的范围 10100 - 10199
# 在子路由中使用了path转换器，在这里需要使用形参接收path转换器传递过来的username,传递参数的形式是关键字传参
# users_views视图函数用于修改用户头像，前端选择用户头像传至后端，后端传至数据库并在前端刷新界面
"""对于视图可以有视图函数和视图类，因为使用同一个装饰器去校验普通函数和类中函数（方法）是不允许的，所以django提供了一个装饰器method_decorator,它可以装饰我们写出的函数装饰器，进而将函数装饰器转换成方法装饰器"""


@logging_check
def users_views(request, username):
    if request.method != 'POST':
        result = {'code': 10103, 'error': 'The method is wrong!'}
        return JsonResponse(result)
    else:
        # try:
        #     user = UserProfile.objects.get(username=username)
        # except Exception as e:
        #     #根据前端传递过来的用户名，在数据库中查找是否有此用户存在，若没有查找到此用户抛出错误码
        #     result = {'code':10104,'error':'The username is error，we do not find the match username '}
        #     return JsonResponse(result)
        user = request.myuser
        avatar = request.FILES['avatar']
        user.avatar = avatar
        user.save()  # 修改数据库中的值需要使用save保存,一查二改三更新
        return JsonResponse({'code': 200})  # 修改成功后向前端返回200状态码


class Usereview(View):
    # 有两个类型的url会匹配到这个视图类，一个是带username的url，一个是不带username的url,所以当这两个url都是以get方法进行请求会匹配到函数get，因此需要加上username=None来确保函数在处理这两类请求的时候不会出错
    # 在子路由中是用path转换器匹配的这个视图类，传递过来的参数会进行关键字传参，如果有的url没有传递参数过来也匹配到这个路由，那么username形参没有传参会报错，所以需要使用一个默认值None
    def get(self, request, username=None):
        if username:
            # 如果username 存在，表示需要获取指定用户的数据
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                result = {'code': 10102, 'error': 'The username is wrong!'}
                return JsonResponse(result)
            result = {'code': 200, 'username': username,
                      'data': {'info': user.info, 'sign': user.sign, 'nickname': user.nickname,
                               'avatar': str(user.avatar)}}
            return JsonResponse(result)
        else:
            # 如果username不存在，表示需要获取所有用户的数据
            pass
        return JsonResponse({'code': 200, 'msg': 'test'})

    def post(self, request):
        # request.post是针对表单的post请求提交的数据，可以用这样的方法取数据，对于application/json这样的数据，需要使用下面的方法取数据
        json_str = request.body  # request.body可以直接取出请求体中的数据
        json_str = json.loads(json_str)  # 转换为字典
        username = json_str['username']  # 这里去数据的方式是强取的，可以使用json_str.get('username')的方式温柔的取出数据
        email = json_str['email']
        password_1 = json_str['password_1']
        password_2 = json_str['password_2']
        phone = json_str['phone']
        sms_num = json_str['sms_num']
        # 参数基本检查，检查密码是否一致
        if password_1 != password_2:
            result = {'code': 10100, 'error': 'the password is not same'}
            return JsonResponse(result)
        #比对验证码是否一致
        old_code = cache.get('sms_%s'%(phone))#使用cache.get取redis数据库中的值的时候，由于cache.set在存储值的时候设置了一个有效时间，所以需要在下面校验现在这个值是否在redis数据库中还是存在的
        if not old_code:
            result = {'code':10110,'error':'The code is wrong!'}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {'code': 10110, 'error': 'The code is wrong!'}
            return JsonResponse(result)



        # 检查验证用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10101, 'error': 'The username is already existed'}
            return JsonResponse(result)
        # 向数据库的user_user_profile表插入数据（密码md5存储）
        p_m = hashlib.md5()
        p_m.update(password_1.encode())  # 把字符串使用encode()转化成字节串
        UserProfile.objects.create(username=username, nickname=username, password=p_m.hexdigest(), email=email,
                                   phone=phone)
        result_sucess = {'code': 200, 'username': username, 'data': {}}
        return JsonResponse(result_sucess)

    @method_decorator(logging_check)  # 把函数装饰器转换成方法装饰器
    def put(self, request, username=None):
        # 更新用户数据【昵称，个人信息，个人描述】
        json_str = request.body
        json_obj = json.loads(json_str)  # 转换成字典
        # try:
        #     user = UserProfile.objects.get(username= username)
        # except Exception as e:
        #     result = {'code':10105,'error':'The username is error, please chenk the username '}
        #     return JsonResponse(result)
        user = request.myuser  # 把上面注释的代码用这句进行替代，好处是直接使用浏览器本地存储的token里面保存的username,起到了仅限于当前登录用户的操作权限，即使是在url中传入（http://127.0.0.1:5000/（非当前登录用户的用户名）/change_info）进入修改页面也不会因为这样的访问导致修改到url中传入的用户的信息，因为这里取出的是token中的用户名，即当前登录的用户名，仅限于修改当前用户名的用户信息
        user.sign = json_obj['sign']
        user.info = json_obj['info']
        user.nickname = json_obj['nickname']
        user.save()
        return JsonResponse({'code': 200})
"""把数据存储到redis里面去的两种方式，一种是使用from django.core.cache import cache,cache.get()h/cache.set()的方式，因为在setting文件中配置了cache，所以cache.set()会自动去连接配置中的redis数据库
另一种方式是from django_redis import get_redis_connection,r = get_redis_connection()拿到一个配置文件中的redis地址的连接，然后使用连接对象r进行redis的各种操作"""
def sms_view(request):
    if request.method != 'POST':
        result = {'code':'10108','error':'please use post'}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']
    #生成随机码
    code = random.randint(1000,9999)#生成区间1000-9999之间的int类型的值
    print('phone',phone,'code',code)

    #储存随机码 django_redis，代码运行到此处需要保证redis服务器开启，否则代码运行到此处会因为找不到redis服务器停止
    cache_key = 'sms_%s'%(phone)
    #检查是否已经有发过的且未过期的验证码，有则不再生成验证码，直接使用，没有则再次生成验证码
    old_code = cache.get(cache_key)
    if old_code:
        return JsonResponse({'code': 10111,'error':'此手机号在一分钟内已进行注册操作，验证码在有效期内'})

    cache.set(cache_key,code,60)#把code存进redis并设置只存储60秒

    #发送随机码,不使用celery版本
    # res = send_sms(phone,code)
    try:
        res = send_sms_celery.delay(phone,code)#celery版本的发送随机码,这里需要使用delay()启动celery版本的发送短信验证码功能，这样传输端才能收到这个消费请求,不使用delay()启动只是单纯的调用发送短信验证码的方法，能够达到注册效果但是失去了celery的意义
        return JsonResponse({'code': 200})
    except Exception as e:
        return JsonResponse({'code':201})
    # res = json.dumps(res, default=lambda obj: obj.__dict__)
    # print(type(res))
    # if (res.get('statusCode') =='000000'):
    #     return JsonResponse({'code':200})
    # else:
    #     return JsonResponse({'code':201})
def send_sms(phone,code):
    config = {
        'accountSid': '8a216da87e7baef8017f29a965481943',
        'accountToken': '9067cc7dc0a84688870814ca55f98723',
        'appId': '8a216da87e7baef8017f29a96669194a',
        'templateId': '1',

    }
    yun = YunTongXin(**config)  # 拆包操作，把字典拆包进行关键字传参
    res = yun.run(phone, code)
    return res


