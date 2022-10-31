import email
import os

import django
from django.template import loader
from django.conf import settings
from celery import Celery
# 创建Celery实例对象
from django.core.mail import send_mail

# from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
app = Celery('celery_tasks.tasks', broker='redis://localhost:6379/8')

# 内置装饰器
@app.task
def send_register_active_email(to_email, username, token):
    # 发邮件   settings里要配置
    subject = '天天生鲜best'
    message1 = ''
    message = '<h1>%s,欢迎你,请点击下列连接激活账户</h1>点击下列连接激活<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message1, sender, receiver, html_message=message)
@app.task
def generate_static_index_html():
    """产生首页静态页面"""
    # 查询商品的种类信息
    types = GoodsType.objects.all()
    # 获取首页轮播的商品的信息
    index_banner = IndexGoodsBanner.objects.all().order_by('index')
    # 获取首页促销的活动信息
    promotion_banner = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品信息展示
    for type in types:
        # 查询首页显示的type类型的文字商品信息
        title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        # 查询首页显示的图片商品信息
        image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 动态给type对象添加两个属性保存数据
        type.title_banner = title_banner
        type.image_banner = image_banner

    # 组织模板上下文
    context = {
        'types': types,
        'index_banner': index_banner,
        'promotion_banner': promotion_banner,
    }

    # 使用模板exi
    # 1. 加载模板文件，返回模板对象
    temp = loader.get_template('static_index.html')
    print("加载模板文件")
    # 2. 定义模板上下文
    # context = RequestContext(request, context) # 可省
    # 3. 模板渲染

    static_index_html = temp.render(context)
    print("渲染模板")
    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    print("生成静态文件")
    with open(save_path, 'w') as f:
        f.write(static_index_html)

