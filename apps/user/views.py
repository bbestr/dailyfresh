import re

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
# Create your views here.
from django.urls import reverse

#由 RegisterView 类替代
def register(request):
    """显示注册页面"""
    if request.method == 'get':
        #
        return render(request,'register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验数据
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式错误'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选同意协议'})
        User1 = get_user_model()
        User = get_user_model()
        # 校验 用户名高是否重复
        try:
            user_1 = User.objects.get(username=username)
        except User.DoesNotExist:
            user_1 = None
        if user_1:
            return render(request, 'register.html', {'errmsg': '用户名已经存在'})
        # 进行用户信息 save   (使用内置的objects.create_user  直接保存)

        user = User1.objects.create_user(username, email, password)
        # 默认没激活
        user.is_active = 0
        user.save()
        # 返回应答 跳转首页
        return redirect(reverse('goods:index'))
def register_handle(request):
    """处理注册"""
    #接受数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')

    #校验数据
    if not all([username,password,email]):
        return render(request,'register.html',{'errmsg':'数据不完整'})
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
        return render(request, 'register.html', {'errmsg': '邮箱格式错误'})
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请勾选同意协议'})
    User1 = get_user_model()
    User =  get_user_model()
    #校验 用户名高是否重复
    try:
        user_1 = User.objects.get(username=username)
    except User.DoesNotExist:
        user_1 = None
    if user_1:
        return render(request, 'register.html', {'errmsg': '用户名已经存在'})
    #进行用户信息 save   (使用内置的objects.create_user  直接保存)

    user = User1.objects.create_user(username, email, password)
    #默认没激活
    user.is_active = 0
    user.save()
    #返回应答 跳转首页
    return redirect(reverse('goods:index'))

#类视图  明确post  方法   get方法 分别执行的业务   只需要一个url   即可
class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验数据
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式错误'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选同意协议'})
        User1 = get_user_model()
        User = get_user_model()
        # 校验 用户名高是否重复
        try:
            user_1 = User.objects.get(username=username)
        except User.DoesNotExist:
            user_1 = None
        if user_1:
            return render(request, 'register.html', {'errmsg': '用户名已经存在'})
        # 进行用户信息 save   (使用内置的objects.create_user  直接保存)

        user = User1.objects.create_user(username, email, password)
        # 默认没激活
        user.is_active = 0
        user.save()


        #发送激活邮件  把包含激活连接: http:127.0.0.1:8000/user/active(userid)
        # 需要包含每个用户的信息
        # 返回应答 跳转首页
        return redirect(reverse('goods:index'))

