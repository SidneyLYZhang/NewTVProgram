#!/usr/bin/python
# -*- coding: utf-8 -*-
# 脚本配置与email撰写格式请见对应文件，或阅读README.md

import os
import sys
import argparse
import smtplib
import toml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr

# 定义一个主函数异常
class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

# 加载并解析配置文件
def getConfig():
    cf = 'emconfig.toml'
    with open(cf, 'rb') as f:
        content = f.read()
    dic = toml.loads(content.decode('utf8'))
    typeloc = list(dic['email'].keys())
    return(dic,typeloc)

# 取得本次邮件的主要服务器信息以及签名信息
def getServer(config, mailtype):
    result = {}
    result['user'] = config["user"]["name"]
    result['sender'] = config["email"][mailtype]["addr"]
    result['host'] = config["email"][mailtype]["host"]
    result['port'] = config["email"][mailtype]["port"]
    result['password'] = config["email"][mailtype]["password"]
    result['signature'] = config["email"][mailtype]["tail"]
    return(result)

# 标准化用户邮件地址的格式
def standardAddr(addr, name):
    sd_add = []
    if isinstance(addr,list):
        for i in range(0,len(addr)-1):
            sd_add.insert(len(sd_add),)

# 解析邮件主体内容
def getContents(mailfile):
    with open(mailfile, 'rb') as f:
        txtmail = f.read()
    dic = toml.loads(txtmail.decode('utf8'))
    result = {}
    result['To'] = 
    return(result)
    
# 邮件发送主体
def main(argv = None, cog)：
    if argv.type :
        emtype = argv.type
    else:
        emtype = list(cog['email'].keys())[0]
    maildict = getServer(cog, emtype)
    mailtxt = getContents(argv.mail)

# 主函数入口
if __name__ == '__main__':
    # 加载配置文件
    conf, emloc = getConfig()
    # 设定参数 mail 与 type
    parser = argparse.ArgumentParser()
    parser.add_argument('mail', type=str, help='Provide a toml file storage address')
    shtext = "Select the mailbox you want to use, the type name, mainly:" + ','.join(emloc) + ".\nThe default choice is " + emloc[0] + "."
    parser.add_argument("--type", help=shtext, type=str)
    # 解析参数
    args = parser.parse_args()
    # 运行程序
    sys.exit(main(args, conf))