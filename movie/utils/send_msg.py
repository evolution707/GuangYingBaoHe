# -*- coding:utf-8 -*-


import smtplib
from email.mime.text import MIMEText

#发送方设置
# def send_email(email_list, content):
#     msg = MIMEText(content, 'plain', 'utf-8')
#     msg['From'] = 'lightbox'
#     msg['To'] = email_list
#     msg['Subject'] = "lightbox用户注册"
#
#     server = smtplib.SMTP_SSL("smtp.qq.com", 465)
#     server.login("707177173@qq.com", "nxqdopbdwrsobbgc")
#     server.sendmail('707177173@qq.com', email_list, msg.as_string())
#
#     server.quit()

def send_email(email_list, content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = 'evolution707@163.com'
    msg['To'] = email_list
    msg['Subject'] = "lightbox用户注册"

    server = smtplib.SMTP("smtp.163.com", 25)
    server.login("evolution707@163.com", "evolution707")
    server.sendmail('evolution707@163.com', email_list, msg.as_string())

    server.quit()
# send_email('707177173@qq.com', '这是怎么回事')
