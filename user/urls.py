from django.urls import path
from . import views

urlpatterns = [
    path('sms/codeinfo', views.sms_view),
    path('<str:username>', views.Usereview.as_view()),#这里使用path转换器，如果url传入了一个str类型的值，会自动匹配到这个路由地址，并把这个变量username传递给视图函数，在视图函数中也需要定义形式参数来接收这个参数，并且是使用的关键字传参的方式接收这个参数
    path('<str:username>/avatar', views.users_views),#这里使用path转换器，如果url传入了一个str类型的值，会自动匹配到这个路由地址，并把这个变量username传递给视图函数，在视图函数中也需要定义形式参数来接收这个参数，并且是使用的关键字传参的方式接收这个参数
]