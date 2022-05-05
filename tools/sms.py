import base64
import datetime
import hashlib
import json

import requests


class YunTongXin():
    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountSid, accountToken,appId,templateId):
        self.accountSid = accountSid  # 账户ID
        self.accountToken = accountToken  # 账户授权令牌
        self.appId = appId #应用ID
        self.templateId = templateId #模板ID

    def get_request_url(self, sig):
        self.url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid,sig)
        return self.url

    def get_timestamp(self):
        # 生成时间戳
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_sig(self, timestamp):
        # 生成业务url中的sig
        s = self.accountSid + self.accountToken + timestamp
        m = hashlib.md5()
        m.update(s.encode())  # 传入的参数是字节串，所以这里需要encode()一下
        return m.hexdigest().upper()  # 返回十六进制数据并且字母全部大写

    def get_request_header(self,timestamp):
        #生成请求头
        s = self.accountSid+':'+timestamp
        auth = base64.b64encode(s.encode()).decode()#encode成字节串，然后decode成字符串
        return {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8',
            'Authorization':auth
        }

    def get_request_body(self,phone,code):

        return {
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,'3']

        }

    def request_api(self,url,header,body):
        res = requests.post(url,headers = header,data=body)#发送post请求,返回的是一个post请求对象
        return res.text#拿到post响应的内容




    def run(self,phone,code):
        timestamp = self.get_timestamp()  # 获取时间戳
        sig = self.get_sig(timestamp)  # 生成签名
        url = self.get_request_url(sig)  # 生成业务url
        # print(url)
        header = self.get_request_header(timestamp)
        # print(header)
        body = self.get_request_body(phone,code)#生成请求体
        data = self.request_api(url,header,json.dumps(body))#需要把字典形式的body转换成具体的json字符串
        return data





if __name__ == '__main__':
    #accountSid, accountToken,appId,templateId
    config = {
        'accountSid':'8a216da87e7baef8017f29a965481943',
        'accountToken':'9067cc7dc0a84688870814ca55f98723',
        'appId':'8a216da87e7baef8017f29a96669194a',
        'templateId':'1',

    }
    yun = YunTongXin(**config)#拆包操作，把字典拆包进行关键字传参
    res = yun.run('18282498593','960206')
    print(res)
