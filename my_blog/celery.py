from celery import Celery
# from django.conf import settings
from . import settings
import os
import my_blog
"""这个文件是celery配置，worker消费函数在user应用下tasks.py,使用celery的目的是不要让django去向容联云发短信请求，如果容联云卡住了，整个程序就卡住了，我们使用异步的celery来做这件事，容联云出现异常卡顿，不影响主程序运行"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE','my_blog.settings')#告诉celery使用哪个django  setting配置
# app = Celery('zh',broker='redis://:@127.0.0.1:6379/2')#表示任务传输至redis数据库，也可使用下面的方式定义
app = Celery('zh')
app.conf.update(
    BROKER_URL = 'redis://:@127.0.0.1:6379/3'
)
app.autodiscover_tasks(settings.INSTALLED_APPS)#在这个配置下去找有没有worker函数，所以我们的worker函数需要放在已在django的settting配置文件中注册的应用的那个文件夹下面
"""celery 启动方法 celery -A tasks worker --pool=solo -l info，由于对windows的支持不是那么友好，需要添加--pool=solo参数"""