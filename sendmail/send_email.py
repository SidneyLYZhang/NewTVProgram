# 初级实验品 #

# 为什么那么多固定类型的邮件呢？就不能好好的开发一个数据展示的系统吗？真的是无语了…… #
# 简单至极的给固定人员发送不同文件的小玩意儿…… #

import smtplib
import argparse
import time
import os
import json
import urllib.request as urlreq
import datetime as dte
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

##  日期部分：主要负责固定日期的文件发送
def getYesterday(): 
    today=dte.date.today()
    oneday=dte.timedelta(days=1) 
    yesterday=today-oneday  
    return(time.strftime('%Y%m%d',time.strptime(str(yesterday),"%Y-%m-%d")))

## 发送的文件其实都不太一样……
def getFiles(marks, start = None, place = None):
	res = "%PATH%/" # 文件目录这是示意地址
	if place :
		res = place
	if not start :
		start = "00000000"
	ffile = (marks == "#0" and "A统计.xls") \
			or (marks == "#1" and "B指标.xls") \
			or (marks == "#2" and "*.*") \
			or (marks)
	prep = (start == "00000000" and "_".join([getYesterday(),getYesterday()])) \
			or (start.replace(",","_"))
	if marks == "#2" or "#" not in marks:
		res  = res + ffile
	else:
		res = res + prep + ffile
	return(res)

# 有趣的结束信息——基于一言API
def getYiyan():
    page = urlreq.urlopen("https://v1.hitokoto.cn/")
    text = page.read()
    text = text.decode("UTF-8")
    text = json.loads(text)
    return(text['hitokoto'] + " —— " + text['from'])

## 主程序：用个参数选择多样一些。。。。
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "发送文件给固定人...")
	parser.add_argument('--start', type = str, help = "输入文件起止日期，以逗号,隔开，例子：20181111,20181119")
	parser.add_argument('--place', type = str, help = "输入目标文件目录，默认windows下载目录")
	parser.add_argument('mark', type = str, help = "输入发送的文件名，固定代码有：#0-A文件数据；#1-B文件数据；#2-文件夹下全部文件")
	### 看看这参数的设计，就知道有多烦每天固定给人发附件邮件的无语了……
	args = parser.parse_args()
	receivers = ["Name Name <name@mail.com>"]
	sender = "sender@mail.com"
	mail_pass = "password"
	filename = getFiles(args.mark,args.start,args.place)
	mail_subject = (args.mark == "#2" and "多文件附件邮件 - " + time.strftime('%Y%m%d',time.localtime(time.time()))) \
					or (filename.split("/")[-1].split(".")[0]) # 邮件的标题
	timenow = dte.datetime.now()
	mail_context = "附件: " + filename.split("/")[-1] + "\n" + timenow.strftime("%Y-%m-%d %H:%M:%S")
	msg = MIMEMultipart()
	msg["From"] = sender  # 发件人
	msg["To"] = ";".join(receivers) # 收件人
	msg["Subject"] = mail_subject   # 邮件标题
	# 邮件正文
	msg.attach(MIMEText(mail_context, 'plain', 'utf-8'))
	#### 不同的目录下要写全文件路径
	#### 构造附件
	if args.mark != "#2" :
		att = MIMEText(open(filename, "rb").read(), "base64", "utf-8")
		att["Content-Type"] = "application/octet-stream"
		att.add_header("Content-Disposition", "attachment", filename=("gbk", "", filename.split("/")[-1]))
		msg.attach(att)
	else :
		filepath = filename[0:-3]
		for alldir in os.listdir(filepath):
			cname = os.path.join(filepath,alldir)
			att = MIMEText(open(cname, "rb").read(), "base64", "utf-8")
			att["Content-Type"] = "application/octet-stream"
			att.add_header("Content-Disposition", "attachment", filename=("gbk", "", cname.split("/")[-1]))
			msg.attach(att)
	try:
	    # 启动SMTP服务，端口多为465
	    smtpObj = smtplib.SMTP_SSL('smtp.mail.com',465)
	    # 登陆账号
	    smtpObj.login(sender, mail_pass)
	    # 发送
	    smtpObj.sendmail(sender, receivers, msg.as_string())
	    print('Success!成功了!还不快欢呼！')
		print(getYiyan())
	    # 退出登录
	    smtpObj.quit()
	except smtplib.SMTPException as e:
	    print(e)


"""
	我是想写点厉害的东西的，但是在现在的工作岗位上有点难……
	希望未来有机会做得更多吧……
"""