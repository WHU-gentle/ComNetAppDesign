#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import random
import time

def send_email():
    try:
        smtpObj = smtplib.SMTP()
        # 设置服务器
        mail_host = "smtp.qq.com"
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 25 为 SMTP 端口号

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
        receivers = ['13503202005@163.com']

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
        return code
    except Exception:
        return False


code = send_email()
if code:
    print(code)
else:
    print('失败')