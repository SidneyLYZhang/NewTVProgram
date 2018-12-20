#!/usr/bin/python
# -*- coding: utf-8 -*-

# 邮箱配置通过emconfig.toml进行配置，可按需增加需要的邮箱地址。
# 邮件本体通过参数“mail”传入这个脚本;
# mail必须toml文件，主要格式为：
# [to]
#   addr = '邮箱地址'
#   name = '收件人名称'
# [content]
#   title = '邮件标题'
#   text = '邮件正文'
#   type = 'html/plain'
# [appendix]
#   part1 = '本地文件位置'
#   part2 = '本地文件位置'
# 详细mail格式见mail_example.toml。

import os
import sys
import argparse as argset
import smtplib
import toml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# 加载并解析配置文件
def getConfig():
    cf = 'emconfig.toml'
    with open(cf, 'rb') as f:
        content = f.read()
    dic = toml.loads(content.decode('utf8'))
    return(dic)

# 取得本次邮件的主要信息
def getMaininfo(config, mailtype):
    if mailtype not in config['email'].keys():
        raise Exception('Selected WRONG Email-Type!!', mailtype)
    result = {}
    if mailtype == 'work':
        result['name'] = config["user"]["name"]["zh"]