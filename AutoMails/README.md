# EMAILAPP脚本说明

## 缘由

对现在的工作来说，每周都要发送大量邮件，而且这些邮件都是定期通报类型的内容，基本不会有大幅度的改变，所以各位领导关注的点就到了邮件标题、抄送人员全不全等这类问题上了。尤其是在有一次把标题写错了之后，更是深深觉得人力难免有穷时，还是写成程序来的简单自如，自动化办公无外乎如是。

而且作为一个数据科学从业者，这也算是个无奈的动作。所以就有了这个Python脚本。虽然我这就是一个重复造轮子的事情，但是，市面上的email python脚本都不太令人满意。最大的不满意就是很多都只为了学习smtplib，而不是真的要弄得好用。虽然我重复造的这个轮子也就那么回事，但自己用的爽快异常啊~~

## 脚本主要内容介绍

脚本主要基于TOML语言定制配置，同时也基于TOML构建EMAIL内容。当然，所有脚本内容都是Python写的。依赖如下库（/模块）：

- os
- re
- sys
- toml
- click
- base64
- smtplib
- hashlib
- pyfiglet
- colorama
- termcolor
- PyInquirer

对各个库文件的需求我就不一一说明了，想详细搞清楚的可以直接看脚本就好了，我也有详细注释。这里主要说明脚本参数、邮件格式与附件添加模式等

### 脚本参数说明

为了增加脚本的自由度，或者说，让这个脚本更接近邮件发送软件的状态，必然需要使用一些参数增加自由度。主要参数有：

- email 参数
- passkey 参数
- config 参数
- tail/no-tail 参数

#### 参数 email 与 passkey

email，这个参数主要用来把邮件地址传入到脚本中。用于直接指定使用什么邮箱进行邮件发送。

相对的，passkey就稍微复杂一些。当你曾经保存过登陆信息的时候，passkey就作为检验登录信息的关键密钥，否则，就作为指定的邮箱登录密码。

#### 参数 config

这个参数，必须为toml文件，包含两个主要部分：user，email。

user部分，需要写明邮箱信息，以便后续邮件发送。email部分，则为所要发送的邮件内容。

#### 参数 tail/no-tail

默认的是no-tail，就不添加签名，如果你需要为邮件添加签名，那么，需要在启动时，使用tail参数指示EmailApp CLI启用签名邮件的模式。
同样，签名内容会同登录信息一起保存到数据文件中，以方便下次使用。每次增加新的签名都需要为不同签名设置不同名称，以备下次使用时选择。

### 配置文件说明

现在就来详细说明配置文件。主要配置的就是Email SMTP服务器的情况，同时，默认使用SSL连接，对于TLS模式以后有时间我再写吧……

另外就是，不支持gmail……谁让gmail需要使用google api呢……所以，等我哪天更闲一些的时候再考虑更新好了……暂时还是别想了啊……捂脸……

配置文件格式：

```toml
# Email 配置文件
# 用户信息
# password指用户邮箱的登录密码，有的邮箱需要使用专用密码，请按照邮箱提供网站的使用指引填写密码。
# 如果你之前登陆过，可以仅使用email与passkeys两个属性自动加载已保存信息。
[information]
    name = "名字"
    email = "user@user.com"
    password = '1234567890'
    passkeys = '000000'
    # EmailSMTP信息
    host = "smtp.company.com"
    port = 465
    # 是否保存登录信息
    log = 'False'
# 邮件内容
[email]
    # 收件人
    To = ['topeason@xxx.com', '...@xxx.com']
    To_name = ['peason', '...']
    # 抄送
    Cc = ['cc@cc.com', 'c...@cc.com']
    Cc_name = ['Cc', 'c...'']
    # 密件抄送
    Bcc = ['bcc@bcc.com', 'bcc2@bcc2.com']
    Bcc_name = ['Bcc','Bcc2']
    # 标题
    Subject = 'Emails Title'
    # 邮件正文
    context = '''
    user, hi!
    hello world! From python！
    '''
    # 正文类型，仅支持plain与html两种
    type = 'plain'
    # 附件
    attachment = ['~\file.txt', '~\file2.xxx']
    # 如须在邮件正文中显示图片，需要使用image添加图片附件，并在需要展示图片位置使用‘<img src="cid:image*">’标出。
    # 其中，‘*’表示添加的图片顺序。如没有在正文中添加标识，自动把图片变为普通附件发送。
    image = ['~\xxx.png','~\xxx.jpg']
# 邮件的签名部分
[tail]
    # 签名标识
    name = 'Names'
    # 签名内容
    context = '''
    <div>
        <div><br><br><br>------------------</div>
        <div style="font-size:14px;"><div>名字 &nbsp; &nbsp; <font size="2">Ming Zi</font></div>
        <div><b>公司 &nbsp;&nbsp; 部门</b></div>
        <div>电话：18622430733</div>
        <div>电子邮件：<a href="mailto:user@user.net" target="_blank">user@user.net</a></div>
        <div><img src="cid:image1"></div>
    </div>
    '''
    # 是否要保存这个签名档，True为要保存，False为不要保存。不使用save关键词的时候，默认为不保存。
    save = 'True'
```

配置文件的使用，就按照这个示例写就可以了。当然，如果你以前使用这个CLI登陆过Email并成功发过邮件，那么在 `[information]` 部分就不需要写很多信息了，只需要写email和passkeys就可以。比较重要的一点是，type支持两种模式，一个是plain一个是html，这个模式用于邮件正文的构建模式。

所以，配置文件的最小保留关键词是：email、passkeys、To、Subject、context、type。

### 签名的使用说明

一般情况下，这个email cli是默认不添加签名的。签名的录入模式，是html的，所以，如果使用签名，邮件主体内容格式将自动转换为html。

对于html格式，请自主阅读html相关教程。这里给出一个模板：

```html
<div>
        <div><br><br><br>------------------</div>
        <div style="font-size:14px;"><div>名字 &nbsp; &nbsp; <font size="2">Ming Zi</font></div>
        <div><b>公司 &nbsp;&nbsp; 部门</b></div>
        <div>电话：18622430733</div>
        <div>电子邮件：<a href="mailto:user@user.net" target="_blank">user@user.net</a></div>
        <div><img src="cid:image1"></div>
</div>
```

## 初始化这个脚本

首先，前提是你有安装Python，这个是最低的要求。安装Python，可以遵循[python官方](https://devguide.python.org/setup/)的指引。

如果是Windows10，可以在 Microsoft Store 中搜索Python下载3.7版本的。

当你已经安装好Python，就可以在你的命令行工具中，输入以下命令，完成这个脚本的初始化：

```Bash
> python init.py
```

这个python脚本会把所需要的Package安装好，然后就可以正常使用Email-App CLI了。

## 其他说明

当前脚本版本为： 1.3.0

## 版权声明

此python CLI工具，主要实现email发送功能。遵循GUN GPL3开源协议。

如需直接使用这个一工具中的代码，需标注代码来源。

Copyright (C) 2019  Liangyi Zhang <zly@lyzhang.me>
