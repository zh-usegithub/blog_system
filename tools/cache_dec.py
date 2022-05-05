"""缓存装饰器,这个装饰器是在常规的装饰器外面再加上了一层函数用于接收过期时间参数，这个是可传参的装饰器写法
带参数的装饰器，参数传递给expire，被装饰的函数传递给func"""
from django.core.cache import cache

from .logging_dec import get_user_by_request
"""使用缓存是对接redis数据库，操作redis对于大量数据反应更快，而不用跟主数据库mysql交互，这样可以减轻mysql数据库负荷，使用高效存取的redis数据库代为响应
对于带参数的装饰器或者不带参数的装饰器，我们首先需要写出装饰器的整体架构，具体的业务逻辑在wrapper()函数中进行编写完成，核心思想是被装饰的函数会被传进装饰器中拓展其功能"""
def cache_set(expire):
    def _cache_set(func):
        def wrapper(request,*args,**kwargs):
            #区分场景-只做列表页
            if 't_id' in request.GET:
                #表示访问的是详情页数据
                return func(request,*args,**kwargs)
            #当代码走到此处证明是获取列表页数据
            #生成出正确的 cache key  [访客访问和博主访问]
            visitor_user = get_user_by_request(request)
            visitor_username = None
            if visitor_user:
                visitor_username = visitor_user.username
            visitor_username = kwargs['author_id']
            author_username = kwargs['author_id']#因为被装饰的函数func中的参数在被装饰的情况下，参数直接传递到了wrapper函数的参数中，参数author_id由**kwargs以键值对的方式接收到，所以根据键取值拿到被访问的博客的username
            print('visitor is %s'%(visitor_username))
            print('author is %s'%(author_username))
            full_path = request.get_full_path()#这个函数可以直接返回request请求中url中的查询字符串的内容
            if visitor_username == author_username:
                cache_key = 'topics_cache_self_%s'%(full_path)
            else:
                cache_key = 'topics_cache_%s'%(full_path)
            print('cache_key is %s'%(cache_key))


            #判断是否有缓存，有缓存则直接返回，代码运行到这里需要缓存服务器redis是开启的状态才行，不然去redis取数据时找不到服务器程序会暂停在这里
            res = cache.get(cache_key)
            if res:
                print('---cache---in---使用缓存')
                return res
            #执行视图
            res = func(request,*args,**kwargs)#无论是在获取列表页数据还是详情页数据都调用被修饰的函数func，因为被修饰的函数中有相应的逻辑进行判断是返回列表页还是详情页
            # 存储缓存 cache对象/set/get，引入from django.core.cache import cache后直接使用set方法即可，在settting配置文件中已经写好了django-cache对接的redis服务器的地址
            cache.set(cache_key,res,expire)#这里设置缓存时间为expire
            #返回响应
            return res


            return func(request,*args,**kwargs)
        return wrapper
    return _cache_set