from django.db import models
import random

def default_sign():
    signs = ['数据库标志1','数据库标志2','数据库标志3','数据库标志4','数据库标志5','数据库标志6']
    return random.choice(signs)

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=11,verbose_name='用户名',primary_key=True)
    nickname = models.CharField(max_length=30,verbose_name='昵称')
    password = models.CharField(max_length=32,verbose_name='密码')
    email = models.EmailField()
    phone = models.CharField(max_length=11,verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatar',null=True)
    sign = models.CharField(max_length=50,verbose_name='个人签名',default=default_sign)#这里调用的函数不加括号
    info = models.CharField(max_length=150,verbose_name='个人简介',default='')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'user_user_profile'






