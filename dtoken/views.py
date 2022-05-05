import json
import time
import jwt
from django.shortcuts import render
from django.http import JsonResponse
from user.models import UserProfile
import hashlib
from my_blog import settings


# 异常码：10200-10299
# Create your views here.
def tokens(request):
    if request.method != 'POST':
        result = {'code': 10200, 'error': 'Please use method post to update data!'}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str)
    username = json_obj['username']
    password = json_obj['password']
    # 校验用户名和密码
    try:
        user = UserProfile.objects.get(username=username)
    except Exception as e:
        print('捕获到一个异常登录信息')
        result = {'code': 10201, 'error': 'The username or password is wrong'}
        return JsonResponse(result)
    # 若用户名查询过程中没有出现报错，说明数据库中存在此用户，接下来开始校验密码是否正确
    p_m = hashlib.md5()
    p_m.update(password.encode())  # 转化成字节串
    if p_m.hexdigest() != user.password:
        result = {'code': 10202, 'error': 'The username or password is wrong'}
        return JsonResponse(result)
    # 记录会话状态,若以上的分支都没有进入，则说明用户名和密码是正确的，这里返回登录成功的状态返回
    token = make_token(username)
    result = {'code': 200, 'username': username, 'data': {
        'token': token}}  # 这里直接把生成的token放在字典里面进行返回，由于jwt.encode()返回的是字节串，所以需要decode一下变成字节串,在登录成功的响应里面会有生成的token字符串
    return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'username': username, 'exp': now_t + expire}
    return jwt.encode(payload_data, key, algorithm='HS256')
