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

    因为我确实比较懒，所以没有对这个小玩意做任何拆分，把一切都写在了一起。所以， 
    除非你很闲，不用看具体代码完全可以。看一下使用说明就好。
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

# REFERENCES
#    1. https://github.com/CITGuru/PyInquirer
#    2. 

# INSTRUCTION MANUAL
#    1. Explanation for Configuration of Email 配置文件说明(README.md)
#    2. Getting Help 获取帮助(python emailapp.py --help)

# PACKAGES

import os
import re
import six
import sys
import toml
import time
import click
import base64
import smtplib
import hashlib
import colorama
import datetime as dte

# REQUESTS

from termcolor import colored
from email.header import Header
from pyfiglet import figlet_format
from examples import custom_style_2
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from PyInquirer import style_from_dict, Token, prompt
from __future__ import print_function, unicode_literals

# CLASSES

# File Cryptor
class fileCryptor(object):
    def __init__(self, address, Keys):
        self.crukey = Keys
        self.sirkey = address
        self.datas = {
            'password' : '0',
            'host' : '0.0.0.0:0',
            'name' : 'Name Name',
            'tail' : {'default' : '<div>' + str(dte.date.today()) + '</div>'}
        }
    
    def __data_translate(self, oriData = None):
        if not oriData:
            tip = list(self.datas.values())[:-1]
            tip = tip + list(map(lambda x : x + '/<-GAP->/' + self.datas['tail'][x] , self.datas['tail'].keys()))
        else :
            tip = ['password', 'host', 'name']
            tip = dict(zip(tip, oriData[0:3]))
            tip['tail'] = dict(list(map(lambda x : x.split('/<-GAP->/') , oriData[3:])))
            tip['tail']['default'] = '<div>' + str(dte.date.today()) + '</div>'
            self.upgrade(tip)
        return(tip)
    
    def fileEncryptor(self):
        enkey = base64.encodestring(bytes(self.crukey, 'utf-8'))
        encryText = [hashlib.md5(enkey).hexdigest()]
        filename = hashlib.md5(bytes(self.sirkey, 'utf-8')).hexdigest()
        strText = self.__data_translate()
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
                    result = self.__data_translate(result)
        return(result)
    
    def upgrade(self, keydata):
        tk_keys = ['password','host','name']
        tk_data = dict([(k,keydata.get(k,None)) for k in tk_keys])
        self.datas.update(tk_data)
        self.datas['tail'].update(keydata['tail'])

    @classmethod
    def fileValid(addr, keys = '000000'):
        enkey = base64.encodestring(bytes(keys, 'utf-8'))
        verific = hashlib.md5(enkey).hexdigest()
        filename = hashlib.md5(bytes(addr, 'utf-8')).hexdigest()
        if not os.path.exists('data/' + filename + '.databox'):
            ref = False
            rek = False
        else :
            ref = True
            with open('data/' + filename + '.databox', 'r') as filed:
                lines = filed.readlines()
                if verific != lines[0][:-1] :
                    rek = False
                else :
                    rek = True
        if keys == '000000':
            return(ref)
        else :
            return(ref, rek)

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
    
    def addRecipient(self, mailaddr, name):
        pass

    def addCc(self, mailaddr, name):
        pass
    
    def addBcc(self, mailaddr, name):
        pass
    
    def addContent(self, mailaddr, name):
        pass
    
    def addAttachment(self, mode, fileplace):
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
            insv.sendmail(mailtxt.sender)
        except smtplib.SMTPException as e:
	        print(e)

# INITIALIZATION

colorama.init()

# FUNCTIONS

def print__(text, color = 'yellow', font = 'slant', figlet = False):
    '''
    格式化输出函数
    '''
    if figlet :
        six.print_(colored(figlet_format(text, font=font), color))
    else:
        six.print_(colored(text, color))


def getConfig(cfpath):
    '''
    加载Toml配置文件函数
    '''
    with open(cfpath, 'rb') as f:
        content = f.read()
    dic = toml.loads(content.decode('utf8'))
    user_infor = dic['information']
    in_email = dic['email']
    tail_infor = dic['tail']
    return(user_infor, in_email, tail_infor)

def is_valid(rcT,addr):
    '''
    输入检验函数，基于正则化表示的检验
    '''
    ok_re = re.compile(rcT)
    res = True if ok_re.match(addr) else False
    return(res)

def mailQuest():
    mailre = r'^[a-zA-Z0-9\.\_]{1,25}@[a-zA-Z0-9]{2,20}\.[a-zA-Z\.]{2,7}$'
    questions = [
        {
            'type' : 'input',
            'name' : 'mailaddr',
            'message' : '你准备使用哪一个邮箱发送邮件？\n==>>> ',
            'validate' : lambda x : is_valid(mailre, x) or '这不是一个有效的邮箱地址，请检查后重新录入。'
        }
    ]
    answers = prompt(questions, style=custom_style_2)
    file_ok = fileCryptor.fileValid(answers['mailaddr'])
    if not file_ok :
        answers.update(askPassword())
    else :
        questions = [
            {
                'type' : 'confirm',
                'message' : '曾保存 ‘' + answers['mailaddr'] + '’这个邮箱的信息，是否使用之前保存的信息？\n==>>> ',
                'name' : 'useSaved',
                'default' : True
            }
        ]
        tip = prompt(questions, style=custom_style_2)
        if tip['useSaved'] :
            answers.update(askpasskey(answers['mailaddr']))
        else :
            answers.update(askPassword())
    return(answers)

def askPassword():
    questions = [
        {
            'type' : 'password',
            'name' : 'passwords',
            'message' : '请输入邮箱登陆密码(如果邮箱已经开启)。\n==>>> '
        }
    ]
    answers = prompt(questions, style=custom_style_2)
    return(answers)

def askpasskey(mailname):
    questions = [
        {
            'type' : 'password',
            'name' : 'passkeys',
            'message' : '请输入' + mailname + '报讯信息的密码。\n==>>> '
        }
    ]
    answers = prompt(questions, style=custom_style_2)
    return(answers)

def configmailQuest():
    urlre = r'^([a-zA-Z]{1,4}\.[a-zA-Z0-9\_\-]{1,25}\.[a-zA-Z0-9\.]{2,7}|(?:[0-9]{1,3}\.){3}[0-9]{1,3}):[0-9]{2,4}$'
    questions = [
        {
            'type' : 'input',
            'name' : 'smtpurl',
            'message' : '请提供你所使用邮箱的SMTP服务器，一般可在你的邮箱设置中找到。\n==>>> ',
            'default' : 'smtp.web.com:234',
            'validate' : lambda x : is_valid(urlre, x) or '服务器地址无效，请按照“网址:端口”的格式录入。'
        },
        {
            'type' : 'password',
            'name' : 'passwords',
            'message' : '请输入邮箱登陆密码：\n==>>> '
        }
    ]
    answers = prompt(questions, style=custom_style_2)
    answers['smtpurl'] = answers['smtpurl'].split(':')
    answers['smtpurl'][1] = int(answers['smtpurl'][1])
    return(answers)

# COMMANDTOOL

@click.command()
@click.option('--email', default = '',
                help = '直接使用你的邮箱地址。')
@click.option('--passkey', default = '000000',
                help = '如果你曾经使用这个脚本登陆过你的邮箱，可使用当时设置的加密密码直接完成邮箱登录。')
@click.option('--config', default = '.', type = click.Path(exists = True), 
                help = '邮箱的配置文件，默认不选择。')
def do_commend(email, passkey, config):
    '''
        Email Sender CLI in python...\n
        v2.0.1\n
        遵循GUN GPL3开源协议。\n
        \n
        Copyright (C) 2019  Liangyi Zhang <zly@lyzhang.me>
    '''
    print__('Email Sender CLI', figlet = True)
    print__('                by Sidney Zhang <zly@lyzhang.me>', color = 'white')
    print__('                version 2.0.1', color = 'white')
    pass

# MAINSPROGRAM

if __name__ == '__main__':
    do_commend()