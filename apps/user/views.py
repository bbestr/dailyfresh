import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.template import RequestContext
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from user.models import User, Address
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from goods.models import GoodsSKU


from itsdangerous import TimedJSONWebSignatureSerializer as Serailser, \
    SignatureExpired  # 新版itsdangerous不支持该函数  只能下载老版本的  我下的是1.1.0
import re
import time
from django.core.mail import send_mail
#由 RegisterView 类替代
# def register(request):
#     """显示注册页面"""
#     if request.method == 'get':
#         #
#         return render(request,'register.html')
#     else:
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#
#         # 校验数据
#         if not all([username, password, email]):
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式错误'})
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请勾选同意协议'})
#         User1 = get_user_model()
#         User = get_user_model()
#         # 校验 用户名高是否重复
#         try:
#             user_1 = User.objects.get(username=username)
#         except User.DoesNotExist:
#             user_1 = None
#         if user_1:
#             return render(request, 'register.html', {'errmsg': '用户名已经存在'})
#         # 进行用户信息 save   (使用内置的objects.create_user  直接保存)
#
#         user = User1.objects.create_user(username, email, password)
#         # 默认没激活
#         user.is_active = 0
#         user.save()
#         # 返回应答 跳转首页
#         return redirect(reverse('goods:index'))
# def register_handle(request):
#     """处理注册"""
#     #接受数据
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#
#     #校验数据
#     if not all([username,password,email]):
#         return render(request,'register.html',{'errmsg':'数据不完整'})
#     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
#         return render(request, 'register.html', {'errmsg': '邮箱格式错误'})
#     if allow != 'on':
#         return render(request, 'register.html', {'errmsg': '请勾选同意协议'})
#     User1 = get_user_model()
#     User =  get_user_model()
#     #校验 用户名高是否重复
#     try:
#         user_1 = User.objects.get(username=username)
#     except User.DoesNotExist:
#         user_1 = None
#     if user_1:
#         return render(request, 'register.html', {'errmsg': '用户名已经存在'})
#     #进行用户信息 save   (使用内置的objects.create_user  直接保存)
#
#     user = User1.objects.create_user(username, email, password)
#     #默认没激活
#     user.is_active = 0
#     user.save()
#     #返回应答 跳转首页
#     return redirect(reverse('goods:index'))

#类视图  明确post  方法   get方法 分别执行的业务   只需要一个url   即可
class RegisterView(View):
    """注册类视图"""
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
        # 校验 用户名是否重复
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
        # 需要包含每个用户的信息    需要加密处理
        #加密 用户信息  生产token

        serailser = Serailser(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serailser.dumps(info)
        token = token.decode('utf8')
        #发邮件  使用celery+redis
        # subject = '天天生鲜best'
        # message1 = ''
        # message = '<h1>%s,欢迎你,请点击下列连接激活账户</h1>点击下列连接激活<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        #     username, token, token)
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # send_mail(subject, message1, sender, receiver, html_message=message)


        send_register_active_email.delay(email,username,token)  #使用celery 发送邮件
        # 返回应答 跳转首页
        return redirect(reverse('goods:index'))

class ActiveView(View):
    """用户激活"""
    def get(self,request,token):
        #进行解密
        serailser = Serailser(settings.SECRET_KEY,3600)
        try:
            #获取激活用户id URL中通过正则表达式捕获token 进行激活操作
            info = serailser.loads(token)
            user_id = info['confirm']

            #保存数据
            User = get_user_model()
            user = User.objects.get(id = user_id)
            user.is_active = 1
            user.save()
            #跳转登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse("连接过期 请重新注册")

class LoginView(View):
    def get(self,request):
        """登录页面显示"""
        #判断用户名是否被记住了
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            check = 'checked'
        else:
            username = ''
            check = ''
        return render(request,'login.html',{'username':username,'checked':check})
    def post(self,request):
        """登录处理"""
        #接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        #校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'不能为空'})
        #登录校验
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                print('已激活')
                login(request,user)

                #获取登录后所要跳转的地址
                next_url = request.GET.get('next',reverse('goods:index'))
                #判断是否需要记住用户名
                response = redirect(next_url)
                remeber = request.POST.get('remember')
                if remeber == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})

class UserInfoView(LoginRequiredMixin,View):
    """用户中心 信息页"""
    def get(self,request):
        #request.user.is_authenticated
        #除了传给模板文件模板变量外 django框架还会吧request.user传给模板文件
        user = request.user
        print("-------------------------------------------")
        address = Address.objects.get_default_address(user)
        print(user)
        print(address)
        print("-------------------------------------------")

        #获取用户信息

        #获取用户历史浏览记录
        from redis import StrictRedis
        sr = StrictRedis(host='127.0.0.1',port=6379,db=9)

        #取redis中的数据
        history_key = 'history_%d'%user.id
        sku_ids = sr.lrange(history_key,0,4)

        goods_li = []
        # for i in sku_ids:
        #     for good in goods_li:
        #         if i.id == good.id:
        #             goods_res.append(good)
        # goods = GoodsSKU.objects.filter(id__in=sku_idsid)
        # goods_li.append(goods)
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context = {'page':'user','address':address,'goods_li':goods_li}
        print("*--------------------------***********")
        return render(request,'user_center_info.html',context)
class LogoutView(LoginRequiredMixin,View):
    """登出"""
    def get(self,request):
        #清除用户信息
        logout(request)

        return redirect(reverse('goods:index'))

class UserOrderView(View):
    """用户订单页"""

    def get(self, request, page):
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历Order_skus计算商品的小计
            for order_sku in order_skus:
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount,保存订单商品小计
                order_sku.amount = amount

            # 动态给order增加属性, 保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 2)  # 单页显示数目2

        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages or page <= 0:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1. 总数不足5页，显示全部
        # 2. 如当前页是前3页，显示1-5页
        # 3. 如当前页是后3页，显示后5页
        # 4. 其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,  # 页面范围控制
                   'page': 'order'}

        return render(request, 'user_center_order.html', context)


class AddressView(View):
    """用户地址页"""
    def get(self,request):
        # django框架会给request对象添加一个属性user
        # 如果用户已登录，user的类型User
        # 如果用户没登录，user的类型AnonymousUser
        # 除了我们给django传递的模板变量，django还会把user传递给模板文件

        # 获取用户的默认地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None  # 不存在默认地址
        address = Address.objects.get_default_address(user)

        return render(request, 'user_center_site.html',
                      {'title': '用户中心-收货地址', 'page': 'address', 'address': address})
    def post(self,request):
        """地址的添加"""
        #修改地址信息

        #接受数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None  # 不存在默认地址
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 数据校验
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html',
                          {'page': 'address',
                           'address': address,
                           'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1([3-8][0-9]|5[189]|8[6789])[0-9]{8}$', phone):
            return render(request, 'user_center_site.html',
                          {'page': 'address',
                           'address': address,
                           'errmsg': '手机号格式不合法'})

        # 添加
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答
        return redirect(reverse('user:address'))  # get的请求方式
