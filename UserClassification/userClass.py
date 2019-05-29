'''
    ================================================================================================================
    用户分类的机器学习方法
    ================================================================================================================

    @SidneyZhang 2019.04.11

    分类，是机器学习（Machine learning）中较为常见的方法，基本上可以分为有监督方法（Supervised learning）与无监
    督方法（Unsupervised learning）两个类别。有监督方法里面的神经网络(Neural Network)、支持向量机（Support-Vector 
    Machine）、朴素贝叶斯（Naive Bayes classifier）等等方法都是比较常见且使用广泛的方法；无监督发方法里面的高斯混
    合模型（Gaussian Mixture Model）、K均值方法（k-means Clustering）等，也在不同领域有很多的应用。
    
    但是，对于用户分类来说，除了是否需要通过“监督”来进行分类外，还需要考虑原始数据的复杂程度。一般情况，对用户进行分
    类需要基于用户的行为、描述属性与用户反馈。这些数据一般情况下很难形成紧密数据矩阵（即包含很少的空值和0值），所以为
    了应付用户行为稀疏的问题，分类算法又被划分了两个分类角度，可以较高效率处理稀疏数据的方法，以及只在稠密数据状态下
    拥有较好性能的方法。

    所以为确定用户的分类，可以有以下两种计算思路：

    1. 数据降维后进行用户分类
    2. 对所有数据使用可在稀疏数据条件下性能优异的方法

    那么，就可以依照不同计算思路，详细整理出不同的用户分类实现方式。

    （一）基于数据降维的思路

    压缩数据维度的方法也有很多。

    （二）适用稀疏数据的思路

    

    ----------------------------------------------------------------------------------------------------------------

    参考文献：
    1. https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_california_housing.html#sklearn.datasets.fetch_california_housing
    2. https://archive.ics.uci.edu/ml/datasets/Wine

    ----------------------------------------------------------------------------------------------------------------

    Copyright 2019 Liangyi Zhang(SidneyZhang)

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

# AUTHOR:       Sidney Zhang <ly.zhang.1985@gmail.com> <twitter@sidneyzhang>
# POSTSCRIPT :  Ich bin faul, also ist der Code zusammen. I'm lazy, so all the code is here.

# PACKAGES

import os
import subprocess
import platform
import time
import re
import pandas as pd

# INFORMATION

def info_here():
    if platform.system() == "Windows" :
        i = subprocess.call("cls", shell = True)
    else :
        i = subprocess.call("clear")
    print(__doc__)
    plat_info = {
        "Current Operating System" : platform.platform() ,
        "CPU Information" : platform.processor() ,
        "Current Python Information" : " ".join(platform.python_build()) ,
        "Start Operation Time" : time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    }
    print("\n"*2 + "-"*112 + "\n")
    if not i :
        print("# YOUR SYSTEM INFORMATIONS :\n")
        for c in plat_info :
            print("{0:<27s}:{1:s}".format(c,plat_info[c]))
    else :
        print("Start Operation Time" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    print("\n" + "-"*112 + "\n")

# FUNCTIONS

def hasDir(pladir): #use to determine if there is a existing path
    if '/' in pladir :
        lastSlash = [i.start() for i in re.finditer('/', pladir)][-1]
        return(os.path.isdir(pladir[0:lastSlash]))
    else :
        return(False)

def getCSVData(fileloc): #getting datas from csv-file
    if hasDir(fileloc):
        print()
    else : #loading uci wine dataset
        pass

# MAINPROGRAM