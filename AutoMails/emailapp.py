'''
    这是一个Email Sender CLI工具，只实现发送这个功能。
    因为是为了更容易的工作准备的，所以，也要做的有意思才好。

    可以选择两种使用模式，一种是直接加载的配置文件的模式，一种是普通登录模式。
    通过一些方式实现命令行交互，并在这个交互下，生成邮件，并最终发送出去。
    
    为实现这么一个模式，需要实现以下内容：
    1. 加密保存登录信息，并使用独立密码保护这些登录信息，同时登陆信息保存在data文件夹内
    2. 首次登陆某个账号，需要逐步输入对应的smtp服务器信息
    3. 可使用toml明文快速直发邮件，只有信息输出，没有交互
    
    即，包含以下关键模块：
    a. 针对性的RC4密码器
    b. 登录信息保存于读取模块
    c. 邮件内容构造模块
    d. 邮件发送模块
'''

# AUTHOR    : Liangyi ZHang <zly@lyzhang.me>
# LICENSE   :
#    Email-Sender CLI with python
#    Copyright (C) 2019  Liangyi Zhang
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    For more information on this, and how to apply and follow the GNU
#    GPL, see https://www.gnu.org/licenses/.

#!/usr/bin/python
# -*- coding: utf-8 -*-

# 脚本配置与email撰写格式请见对应文件，或阅读README.md

# PACKAGES

import os
import sys
import click
import smtplib
import toml
import colorama
import base64
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import parseaddr, formataddr

# CLASSES

# File Cryptor
class fileCryptor(object):
    def __init__(self, address, Keys):
        self.crukey = Keys
        self.sirkey = address
    
    def fileEncryptor(self, strText):
        enkey = base64.encodestring(bytes(self.crukey, 'utf-8'))
        encryText = [hashlib.md5(enkey).hexdigest()]
        filename = hashlib.md5(bytes(self.sirkey, 'utf-8')).hexdigest()
        encryText = encryText + list(map(lambda x : rc4(self.crukey, x).encrypt() , strText))
        filewritor = open('data/' + filename + '.databox', 'w')
        for i in encryText:
            filewritor.write(i)
            filewritor.write('\n')
        filewritor.close()
    
    def fileDecryptor(self):
        enkey = base64.encodestring(bytes(self.crukey, 'utf-8'))
        verific = hashlib.md5(enkey).hexdigest()
        filename = hashlib.md5(bytes(self.sirkey, 'utf-8')).hexdigest()
        if not os.path.exists('data/' + filename + '.databox'):
            result = None
        else :
            with open('data/' + filename + '.databox', 'r') as filed:
                lines = filed.readlines()
                if verific != lines[0][:-1] :
                    result = 'Wrong Password!'
                else :
                    result = list(map(lambda x : rc4(self.crukey, x).decrypt() , lines[1:]))
        return(result)

# RC4 Cryptographic Tool
class rc4(object):
    def __init__(self, Keys, text, choose = 512):
        self.crukey = bytes(Keys, 'utf-8')
        self.btext = text
        self.mode = choose if choose >= 32 else 32
    
    def __box_swaping(self, n, i, j, Box, Keys):
        cloBox = Box
        keyLen = len(Keys)
        b = (j + Box[i] + ord(Keys[i % keyLen])) % n
        cloBox[i],cloBox[b] = cloBox[b],cloBox[i]
        return(cloBox, b)
    
    def __chr_swaping(self, n, i, j, Box, chars):
        a = (i + 1) % n
        b = (j + Box[i]) % n
        cloBox = Box
        cloBox[a],cloBox[b] = cloBox[b],cloBox[a]
        k = chr(ord(chars) ^ cloBox[(cloBox[a] + cloBox[b]) % n])
        return(a, b, k, cloBox)
    
    def encrypt(self):
        key = hashlib.md5(self.crukey).hexdigest()
        n = self.mode
        box = list(range(n))
        j = 0
        for i in range(n):
            box, j = self.__box_swaping(n, i, j, box, key)
        result = ''
        i = 0
        j = 0
        for element in self.btext:
            i, j, k, box = self.__chr_swaping(n, i, j, box, element)
            result += k
        return(str(base64.b64encode(result.encode('utf-8')), encoding='utf-8'))
    
    def decrypt(self):
        text = base64.b64decode(self.btext).decode()
        key = hashlib.md5(self.crukey).hexdigest()
        n = self.mode
        box = list(range(n))
        j = 0
        for i in range(n):
            box, j = self.__box_swaping(n, i, j, box, key)
        result = ''
        i = 0
        j = 0
        for element in text:
            i, j, k, box = self.__chr_swaping(n, i, j, box, element)
            result += k
        return(result)

# Email Content Creator
class emailText(object):
    def __init__(self):
        self.massages = MIMEMultipart()
    
    def addTitle(self, ttext):
        self.massages["Subject"] = ttext

    def addSender(self, mailaddr, name):
        self.sender = "%s <%s>" % (name, mailaddr)
        self.massages["From"] = "%s <%s>" % (name, mailaddr)

    def addAttachment(self):
        pass

# Email App Creator
class emailApp(object):
    def __init__(self, addr, name, psw, serv):
        self.address = addr
        self.username = name
        self.password = psw
        self.link = serv.split(':')[0]
        self.host = int(serv.split(':')[1] if ':' in serv else '465')
    
    def logServer(self, mailtxt):
        try:
            insv = smtplib.SMTP_SSL(self.link, self.host)
            insv.login(self.address, self.password)
            insv.sendmail(mailtxt.sender, )
        except smtplib.SMTPException as e:
	        print(e)

# INITIALIZATION

colorama.init()

# FUNCTIONS

def getConfig():
    pass

# COMMANDTOOL

# MAINSPROGRAM

if __name__ == '__main__':
    pass