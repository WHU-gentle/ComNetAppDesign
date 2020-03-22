
from django.shortcuts import render, redirect, reverse
from django.http import Http404, HttpResponse, JsonResponse

from .models import User


# Create your views here.


def login(request):
    '''显示登录页面'''
    if request.COOKIES.get("user_name"):
        user_name = request.COOKIES.get("user_name")
        checked = 'checked'
    else:
        user_name = ''
        checked = ''
    context = {
        'user_name': user_name,
        'checked': checked,
    }
    return render(request, 'user/login.html', context)


def login_check(request):
    '''进行用户登录校验'''
    # 1.获取数据
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    remember = request.POST.get('remember')
    verifycode = request.POST.get('verifycode')

    # 2.数据校验
    if not all([user_name, password, remember, verifycode]):
        # 有数据为空
        return JsonResponse({'res': 0, 'errmsg': '不能为空'})

    if verifycode.upper() != request.session['verifycode'].upper():
        return JsonResponse({'res': 0, 'errmsg': '验证码错误'})

    # 3.进行处理:根据用户名和密码查找账户信息
    try:
        user = User.objects.get(pk=request.POST['user_name'])
    except User.DoesNotExist:
        return JsonResponse({'res': 0, 'errmsg': '用户不存在'})
    else:
        if user.password != request.POST['password']:
            return JsonResponse({'res': 0, 'errmsg': '密码错误'})
    print('ok')
    next_url = '../../'
    jres = JsonResponse({'res': 1, 'next_url': next_url})

    # 判断是否需要记住用户名
    if remember == 'true':
        # 记住用户名
        jres.set_cookie('user_name', user_name, max_age=7 * 24 * 3600)
    else:
        # 不要记住用户名
        jres.delete_cookie('user_name')

    # 记住用户的登录状态
    request.session['islogin'] = True
    request.session['user'] = {
        'user_name': user.user_name,
        'phone_number': user.phone_number,
        'address': user.address,
        'email': user.email,
    }
    cache_clean()
    return jres


def detail(request):
    if request.session.get('islogin', False):
        context = {
            'user': {
                'user_name': request.session['user']['user_name'],
                'phone_number': request.session['user']['phone_number'],
                'address': request.session['user']['address'],
                'email': request.session['user']['email'],
            }
        }
        return render(request, 'user/detail.html', context)
    else:
        raise Http404


def cache_clean():
    pass


def logout(request):
    request.session.flush()
    cache_clean()
    # 跳转到首页
    return redirect(reverse('index'))


def register(request):
    return render(request, 'user/register.html')


def result(request):
    if request.method == 'POST':
        if request.POST['verify_code'] != request.session['verifyemail']:
            return render(request, 'user/result.html', {'error_message': '验证码错误！'})
        if request.POST['password'] != request.POST['repeat_password']:
            return render(request, 'user/result.html', {'error_message': '两次输入密码不一致！'})
        user = User(user_name=request.POST['user_name'], password=request.POST['password'],
                    phone_number=request.POST['phone_number'], address=request.POST['address'],
                    email=request.POST['email'], )
        user.save()
        return render(request, 'user/result.html', {'message': '注册成功！', 'user_name': request.POST['user_name']})


def cart(request):
    return render(request, 'user/cart.html')


def order(request):
    return render(request, 'user/order.html')


# 引入绘图模块
from PIL import Image, ImageDraw, ImageFont
# 引入随机函数模块
import random
# 内存文件操作
import io


def verifycode(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    # 除去大写I 小写L 字母O 数字0 1
    str1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    # font = ImageFont.truetype(os.path.join(settings.BASE_DIR, "Ubuntu-RI.ttf"), 15)
    font = ImageFont.truetype("courbd.ttf", 15)

    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    print(rand_str)

    buf = io.BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')
    # with open('tmp.png', 'wb') as f:
    #     f.write(buf.getvalue())


import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import time
import re


def verifyemail(request):
    email = request.POST.get('email')
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):  # TODO 电子邮箱格式
        # 邮箱不合法
        return JsonResponse({'res': 0, 'errmsg': '地址格式错误'})
    try:
        smtpObj = smtplib.SMTP()
        # 设置服务器
        mail_host = "smtp.qq.com"
        server = smtplib.SMTP_SSL(mail_host, 465)  # 25 为 SMTP 端口号

        # 登录服务器
        # 用户名
        mail_user = "875577407@qq.com"
        # 口令
        mail_pass = "iedfqlvhmxdzbahi"
        server.login(mail_user, mail_pass)

        # 发送邮件
        # 代发
        # sender = 'yusitong1999@foxmail.com'
        sender = mail_user
        # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        # receivers = ['875577407@qq.com']
        receivers = [email]

        # 邮件内容
        # message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
        random.seed(time.time())
        code = '%d%d%d%d%d%d' % ( random.randint(0,9), random.randint(0,9), random.randint(0,9),
                                 random.randint(0,9), random.randint(0,9), random.randint(0,9) )
        html = '验证码<br><big><strong>' + code + '</strong></big>'
        message = MIMEText(html, 'html', 'utf-8')
        # 发送人
        message['From'] = formataddr(["珞珈网上书店", sender])
        # 收件人
        message['To'] = formataddr(["书店用户", receivers[0]])
        # 标题
        message['Subject'] = '珞珈网上书店 验证码'
        server.sendmail(sender, receivers, message.as_string())
        server.quit()
        print("邮件发送成功")
        request.session['verifyemail'] = code
        return JsonResponse({'res': 1})
    except Exception:
        return JsonResponse({'res': 0, 'errmsg': '邮件发送失败'})
