
#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse as argset
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

#设置登录及服务器信息,并设置email信息
def get_email(tips,titles,password):
    #基础信息
    mail_host = 'smtp.exmail.qq.com'
    mail_user = '张良益'
    mail_pass = password
    sender = 'zhang.liangyi@chinaott.net'
    toADDR = ['hu.ping@chinaott.net', 'li.qingfeng@chinaott.net']
    ccADDR = ['jin.ze@chinaott.net', 'sjglb@chinaott.net']
    
    #添加一个MIMEmultipart类，处理正文及附件
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    if tips == 'h':
        msg['To'] = [toADDR[0]]
        msg['Cc'] = ccADDR + [toADDR[1]]
    elif tips == 'q':
        msg['To'] = [toADDR[1]]
        msg['Cc'] = ccADDR + [toADDR[0]]
    else :
        msg['To'] = toADDR
        msg['Cc'] = ccADDR
    msg['Subject'] = titles
    #推荐使用html格式的正文内容，这样比较灵活，可以附加图片地址，调整格式等



with open('abc.html','r') as f:
    content = f.read()
#设置html格式参数
part1 = MIMEText(content,'html','utf-8')
#添加一个txt文本附件
with open('abc.txt','r')as h:
    content2 = h.read()
#设置txt参数
part2 = MIMEText(content2,'plain','utf-8')
#附件设置内容类型，方便起见，设置为二进制流
part2['Content-Type'] = 'application/octet-stream'
#设置附件头，添加文件名
part2['Content-Disposition'] = 'attachment;filename="abc.txt"'
#添加照片附件
with open('1.png','rb')as fp:
    picture = MIMEImage(fp.read())
    #与txt文件设置相似
    picture['Content-Type'] = 'application/octet-stream'
    picture['Content-Disposition'] = 'attachment;filename="1.png"'
#将内容附加到邮件主体中
message.attach(part1)
message.attach(part2)
message.attach(picture)

#登录并发送
try:
    smtpObj = smtplib.SMTP()
    smtpObj.set_debuglevel(1)
    smtpObj.connect(mail_host,25)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(
        sender,receivers,message.as_string())
    print('success')
    smtpObj.quit()
except smtplib.SMTPException as e:
    print('error',e)