import email
import os

from celery import Celery


#创建Celery实例对象
from django.conf import settings
from django.core.mail import send_mail
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'dailyfresh.settings')
django.setup()
app = Celery('celery_tasks.tasks',backend='redis://localhost:6379/1',broker='redis://localhost:6379/8')

#内置装饰器
@app.task
def send_register_active_email(to_email,username,token):
    # 发邮件   settings里要配置
    subject = '天天生鲜best'
    message1 = ''
    message = '<h1>%s,欢迎你,请点击下列连接激活账户</h1>点击下列连接激活<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message1, sender, receiver, html_message=message)
