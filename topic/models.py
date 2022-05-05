from django.db import models
from user.models import UserProfile
# Create your models here.
"""列表页简介处理：
1.后端给前端，文章全部内容，前端自己截取
2.后端从数据库中获取全部内容，截取好后响应给前端
3.数据库冗余一个字段【简介】，后端只取简介字段内容"""
class Topic(models.Model):
    title = models.CharField(max_length=50,verbose_name='文章标题')
    category = models.CharField(max_length=20,verbose_name='文章分类')#tec & no-tec
    limit = models.CharField(max_length=20,verbose_name='文章权限')#public & private
    introduce = models.CharField(max_length=90,verbose_name='文章简介')
    content = models.TextField(verbose_name='文章内容')
    created_time= models.DateTimeField(auto_now_add=True)#自动添加创建时的当前时间
    update_time = models.DateTimeField(auto_now=True)#每次更新的时候把时间更新一下
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE)#定义外键，关联另外一张表UserProfile,on_delete=models.CASCADE的意思是在删除的时候，关联的表的数据一起删除
    """author这个外键属性在同步至数据中的时候，会自动变成外键字段名author_id，当在使用这个属性或者字段进行数据创建的时候会有细微差别，使用
    author_id进行数据的创建绑定时，对应的是这个外键字段关联的模型类的字段值，使用属性author进行创建绑定时，对应的是这个外键属性关联的模型类的object，
    在过滤查询的时候不需要遵循这个规则"""




