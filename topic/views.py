import json

from django.shortcuts import render

# Create your views here.
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from tools.cache_dec import cache_set
from tools.logging_dec import logging_check,get_user_by_request
from topic.models import Topic
from django.core.cache import cache
#异常码使用范围10300-10399
from user.models import UserProfile
from message.models import Message

#这个视图是删除文章的视图
def delete_topic(request,author_name):
    full_path = request.get_full_path()  # 这个函数可以直接返回request请求中url中带查询字符串的内容
    # full_path1 = request.path_info  #这是获取request传递过来的不带查询字符串的url信息，只获取url中的查询字符串使用request.get_full_path()
    print('查询字符串中的内容',full_path)
    t_id = full_path.split('=')[1]
    t_id = int(t_id)
    print('t_id is',t_id)
    delete_topic = Topic.objects.filter(author_id = author_name,id = t_id)#查询符合删除条件的文章
    if delete_topic:
        delete_topic.delete()#删除文章
        topic_user = TopicViews()#创建对象
        topic_user.clear_topics_caches(request)#调用对象的删除缓存方法
        return JsonResponse({'code':'200'})
    else:
        return JsonResponse({'code': '10305'})



class TopicViews(View):
    #删除缓存的方法，在发表文章和更新文章的时候调用这个方法，保证用户拿到的是最新的数据而不是缓存中旧的数据
    def clear_topics_caches(self,request):
        path = request.path_info#这是获取request传递过来的不带查询字符串的url信息，只获取url中的查询字符串使用request.get_full_path()
        cache_key_p = ['topics_cache_self_','topics_cache_']#cache_key前缀
        cache_key_h = ['','?category=tec','?category=no-tec']
        all_keys = []
        for key_p in cache_key_p:
            for key_h in cache_key_h:
                all_keys.append(key_p+path+key_h)#拼接处完成的url
        print('clear_caches is%s'%(all_keys))
        cache.delete_many(all_keys)#这是cache自带的批量删除方法






    #获取列表页方法
    def make_topics_res(self,author,author_topics):
        res = {'code':200,'data':{}}
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['introduce'] = topic.introduce
            d['author'] = author.nickname
            topics_res.append(d)
        res['data']['topics'] = topics_res#res字典中的键data存放的是字典，在data字典中存放一个键topics,值是topics_res
        res['data']['nickname'] = author.nickname
        return res
    #获取详情页方法
    def make_topic_res(self,author,author_topic,is_self):
        if is_self:
            #表示博主访问自己
            #下面语句相当于sql语句 select * from topic where topic.id>author_topic.id and topic.author = author order by topic.id ASC limit 1
            next_topic= Topic.objects.filter(id__gt=author_topic.id,author=author).first()#id__gt=author_topic.id相当于id>author_topic.id,first()的意思是取排序后的第一个
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author,limit = 'public').first()  # id__gt=author_topic.id相当于id>author_topic.id,first()的意思是取排序后的第一个
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author,limit = 'public').last()
        next_id = next_topic.id if next_topic else None
        next_title = next_topic.title if next_topic else ''
        last_id = last_topic.id if last_topic else None
        last_title = last_topic.title if last_topic else ''
        #关联留言和回复
        all_messages = Message.objects.filter(topic = author_topic).order_by('created_time')
        msg_list = []
        rep_dic = {}
        m_count = 0
        for msg in all_messages:
            if msg.parent_message:
                #回复
                rep_dic.setdefault(msg.parent_message,[])
                rep_dic[msg.parent_message].append({'msg_id':msg.id,'publisher':msg.publisher.nickname,'publisher_avatr':str(msg.publisher.avatar),'content':msg.content,'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})

            else:
                #留言
                m_count +=1
                msg_list.append({'id':msg.id,'publisher':msg.publisher.nickname,'publisher_avatr':str(msg.publisher.avatar),'content':msg.content,'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),'reply':[]})
        for m in msg_list:
            if m['id'] in rep_dic:
                m['reply'] = rep_dic[m['id']]







        res = {'code':200,'data':{}}
        res['data']['nickname'] = author.nickname
        res['data']['title'] = author_topic.title
        res['data']['category'] = author_topic.category
        res['data']['content'] = author_topic.content
        res['data']['introduce'] = author_topic.introduce
        res['data']['author'] = author.nickname
        res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        res['data']['last_id'] = last_id#上一篇
        res['data']['last_title'] = last_title
        res['data']['next_id'] = next_id#下一篇
        res['data']['next_title'] = next_title
        res['data']['messages'] = msg_list
        res['data']['messages_count'] = m_count
        return res



    @method_decorator(logging_check)#因为是要修饰类中的方法，所以需要把普通函数装饰器转换成方法装饰器
    def post(self,request,author_id):
        author = request.myuser#在装饰器logging_check中动态给request添加了一个myuser属性，而且这个属性对应的值是user应用下model模型类实例化对象，用它赋值给下面的外键属性，外键属性对应的值正是模型类的实例化对象
        #取出前端数据
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj['title']
        content = json_obj['content']
        content_text = json_obj['content_text']
        introduce = content_text[:30]
        limit = json_obj['limit']
        category = json_obj['category']
        if limit not in ['public','private']:
            result = {'code':10300,'error':'The limit error~'}
            return JsonResponse(result)
        if category not in ['tec','no-tec']:
            result = {'code': 10301, 'error': 'The limit error~'}
            return JsonResponse(result)
        #创建topic数据，使用下面的这种方式往mysql数据库中写入数据的时候不需要使用save提交
        Topic.objects.create(title = title,content = content,limit = limit,category = category,introduce = introduce,author = author)#author = author这条语句是外键关联的那张表，author在数据库的具体体现是：author会对应表中的author_id字段，author_id字段的值是关联的那个表的主键的值

        self.clear_topics_caches(request)#发表文章后删除缓存
        return JsonResponse({'code':200})
    @method_decorator(cache_set(30))#缓存装饰器,使用缓存装饰器的时候需要打开redis服务，因为cache.get()是直接去redis里面读取数据，相关配置在redis里面已经配置完成
    def get(self,request,author_id):
        print('------view------in------数据库取数据')
        #v1/topics/<username>
        #访问者visitor
        #当前被访问的博客的博主 author
        """在对比访问者与被访问者信息时，访问者的信息是从request中获取的，通过request请求传递过来的请求头，从中取出token并解析token中的内容获得访问者信息，被访问者的信息是从path转换器传递过来的author_id中获取的，因为我们要访问谁的博客，那么路由中会传递该博主的username,在这里是author_id"""
        try:
            author = UserProfile.objects.get(username = author_id)#根据get请求，路由中的path转换器传递过来的author_id查询数据库中是否有这样的一个博主，若没有则返回异常状态码
        except Exception as e:
            result = {'code':10302,'error':'The author is not existed'}
            return JsonResponse(result)
        #获取访问者信息有以下三种情况：1.访问者没有登录2.访问者登录且是博主3.访问者登录不是博主
        #思路：根据token来校验，如果有token，则根据token确定登录用户信息，如果没有token，表示是游客，在获取token的时候还需要校验token
        visitor = get_user_by_request(request)#根据request获取登录者的信息
        visitor_username = None
        if visitor:
            visitor_username = visitor.username#把访客信息赋值给visitor_username
        """在访问博客列表页的时候，可能出现两种url去获取博客列表页内容
        1./v1/topics/zh
        2./v1/topics/zh?category=tec或者/v1/topics/zh?category=no-tec
        需要对这两种请求判断一下给出相应的响应结果"""
        category = request.GET.get('category')#这个方法可以取出GET请求中url的参数category的值，从而判断出是在请求技术类tec还是非技术类no-tec的博客列表信息
        """这个路由对应的视图函数可能会接收到类似这样url的get请求
        1./v1/topics/zh?t_id=1,这个请求是在请求文章的详情页数据，所以需要对这样的请求进行判断辨别"""
        t_id = request.GET.get('t_id')
        if t_id:
            #获取指定文章数据
            t_id = int(t_id)
            is_self = False
            #如果是博主在访问自己的文章则全部显示出来，不需要加上过滤查询条件
            if visitor_username == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id = t_id,author_id = author_id)
                except Exception as e:
                    result = {'code':10302,'error':'The topic is not found'}
                    return JsonResponse(result)
            # else表示不是博主在访问自己的文章，是游客在访问博主的文章，这时候需要加上过滤条件只get获取public的文章
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id,limit = 'public')
                except Exception as e:
                    result = {'code': 10303, 'error': 'The topic is not found'}
                    return JsonResponse(result)
            res = self.make_topic_res(author,author_topic,is_self)
            return JsonResponse(res)



        else:
            if category in ['tec','no-tec']:
                if visitor_username == author_id:
                    #意味着博主在访问自己的博客，把博主的所有文章取出来
                    author_topics = Topic.objects.filter(author_id = author_id,category = category)#author_id是外键在数据库中对应的外键字段，也可以使用author = author_id进行过滤查询
                else:
                    #意味着是访客（非博主自己）在访问博主的博客
                    author_topics = Topic.objects.filter(author_id=author_id,limit = 'public',category = category)#过滤查询出公开的博客文章，私有的则不进行展示
                    # res = self.make_topics_res(author,author_topics)
                    # return JsonResponse(res)
            else:
                if visitor_username == author_id:
                    #意味着博主在访问自己的博客，把博主的所有文章取出来
                    author_topics = Topic.objects.filter(author_id = author_id)#author_id是外键在数据库中对应的外键字段，也可以使用author = author_id进行过滤查询
                else:
                    #意味着是访客（非博主自己）在访问博主的博客
                    author_topics = Topic.objects.filter(author_id=author_id,limit = 'public')#过滤查询出公开的博客文章，私有的则不进行展示
                    # res = self.make_topics_res(author,author_topics)
                    # return JsonResponse(res)
            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)












