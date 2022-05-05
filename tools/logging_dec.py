import jwt
from django.http import JsonResponse
# from django.conf import settings
from my_blog import settings
from user.models import UserProfile
# 装饰器修饰函数的过程中需要传递参数进来，被装饰的函数会作为实参传递给形式参数func，被修饰函数中的参数request同时也会传递进装饰器，进而可以对request对象进行自定义修改（request是一个对象）
def logging_check(func):
    def wrap(request, *args, **kwargs):
        # 获取token  request.META.get('HTTP_AUTHORIZATION'),这里有一个命名规范，HTTP_加上请求头这个字段键的大写
        # 校验token
        # 失败code 403 error:Please login
        token = request.META.get('HTTP_AUTHORIZATION')  # 取出请求头中的token,Authorization
        if not token:
            result = {'code': 403, 'error': 'Please login'}
            return JsonResponse(result)
        # 校验jwt
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
        except Exception as e:
            print('jwt decode error is %s' % (e))
            result = {'code': 403, 'error': 'Please login'}
            return JsonResponse(result)
        # 获取登录用户
        username = res['username']
        user = UserProfile.objects.get(username=username)#这里的查询返回的结果类型是模型类的实例化对象，一个模型类可以实例化出很多的对象，符合这个查询条件的对象只有一个
        request.myuser = user  # user是user应用下的model模型类实例化的类对象，把它传递给request.myuser，那么request.myuser也是模型类的实例化对象，return func(request,*args,**kwargs)把request中的username传递回视图函数
        #request.myuser是动态的添加对象属性的方式，request是一直传递到视图函数的，这里使用request.myuser = user把符合查询条件的模型类对象赋值给request对象的myuser属性，那么这个属性值即代表一个对象
        return func(request, *args, **kwargs)

    return wrap

def get_user_by_request(request):
    #尝试性获取登录用户,根据获取情况返回不同结果
    #return UserProfile_obj or None
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    #如果取到了token，那么需要decode一下看看里面的数据，获取具体的用户信息
    try:
        res = jwt.decode(token,settings.JWT_TOKEN_KEY)#如果这里的decode出现了报错，那么捕获异常并且温柔的返回None
    except Exception as e:
        return None
    username= res['username']
    user = UserProfile.objects.get(username = username)#更具token里面解析出来的username,去数据库中get这个用户,返回一个对象，根据对象.字段名的方式可以获取这个对象的其他信息
    return user








