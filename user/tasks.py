from my_blog.celery import app
from tools.sms import YunTongXin
"""定义一个worker函数必须使用装饰器，celery会自动寻找到这个worker函数"""
@app.task
def send_sms_celery(phone,code):
    config = {
        'accountSid': '8a216da87e7baef8017f29a965481943',
        'accountToken': '9067cc7dc0a84688870814ca55f98723',
        'appId': '8a216da87e7baef8017f29a96669194a',
        'templateId': '1',

    }
    yun = YunTongXin(**config)  # 拆包操作，把字典拆包进行关键字传参
    res = yun.run(phone, code)
    return res