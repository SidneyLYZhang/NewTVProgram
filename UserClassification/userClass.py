'''
    ===================================================================================================
    用户分类的机器学习方法
    ===================================================================================================

    @SidneyZhang 2019.04.11

    分类，是机器学习中较为常见的方法，基本上可以分为有监督方法与无监督方法两个类别。

    ----------------------------------------------------------------------------------------------------

    参考文献：

    ----------------------------------------------------------------------------------------------------

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

# AUTHOR:   Sidney Zhang <ly.zhang.1985@gmail.com> <twitter@sidneyzhang>

# PACKAGES

import subprocess
import platform

# INFORMATION

def info_here():
    if platform.system() == "Windows" :
        i = subprocess.call("cls", shell = True)
    else :
        i = subprocess.call("clear")
    print(__doc__)
    if not i :
        print()
    else :
        print("\n"*50)

# FUNCTIONS

# MAINPROGRAM