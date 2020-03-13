#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
# 设置服务器
mail_host = "smtp.qq.com"
# 用户名（实际发送）
mail_user = "875577407@qq.com"
# 口令
mail_pass = "iedfqlvhmxdzbahi"
# 代发
sender = 'yusitong1999@foxmail.com'
# 接收邮件，可设置为你的QQ邮箱或者其他邮箱
receivers = ['875577407@qq.com']

# 邮件内容
message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
# 发送人
message['From'] = Header(mail_user, 'utf-8')
# 收件人
# message['To'] = Header("书店顾客<" + receivers[0] + ">", 'utf-8')

# 标题
subject = 'Python SMTP 邮件测试'
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")