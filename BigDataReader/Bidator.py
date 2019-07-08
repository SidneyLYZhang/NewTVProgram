# PACKAGES

import os
import re
import math
import time
import numpy as np
from scipy import stats

# CLASSES

class Bidator(object):
    '''
        针对CSV的数据读取，
        可用于超大数据集的读取，并可进行基本的数据计算。
        提供 for 循环处理每行数据，
        以及列数据的快捷提取。
    '''
    LARGEST_NORMAL = 200 # 标记最大直读数据的长度
    def __init__(self, filepath, sep = ',', header = False):
        self.__sep = sep
        self.__fpath = filepath.replace('\\','/')
        if not os.path.isfile(self.__fpath) :
            with open(self.__fpath, mode = 'w+', encoding = 'utf-8') as df :
                df.write('')
        self.__data = self.__load()
        self.__header = header
        if header :
            self.__colnames = (next(self.__data)).split(sep)
            self.ncol = len((next(self.__data)).split(sep))
        else :
            if os.path.getsize(self.__fpath) :
                self.ncol = len((next(self.__data)).split(sep))
                self.__colnames = list(range(self.ncol))
            else :
                self.ncol = 0
                self.__colnames = []
        self.__data = self.__load()
    
    def __iter__(self):
        self.__data = self.__load()
        return(self.__data)
    
    def __next__(self):
        try:
            res = next(self.__data).split(self.__sep)
        except StopIteration :
            self.__data = self.__load()
        return(res)
    
    def __getitem__(self, key):
        if key not in self.__colnames :
            raise KeyError
        else :
            locs = self.__colnames.index(key)
            res = list(map(lambda x : x.split(self.__sep)[locs] , self.__data))
            if 'NULL' in res or 'NULL\n' in res :
                strLen = list(map(len , [i for i in res if not i.startswith('NULL')]))
            else :
                strLen = list(map(len , res))
            thisstrs = True if self.__is_chinese(res) else False
            thistime = True if len(set(strLen)) == 1 and strLen[0] in [8,10,14,16,17,19] else False
            res = list(map(lambda x : self.__transtype(x, in_typed = (thisstrs , thistime)) , res))
            self.__data = self.__load()
            return(res)
    
    def __str__(self):
        length = self.__len__()
        res = ['file : ' + self.__fpath]
        res.append('matrix data of size : ' + str(self.ncol) + '*' + str(length) + "\n")
        if length > Bidator.LARGEST_NORMAL :
            res.append('first 5 rows of data : ')
            mind_data = self.head()
            format_this = list(map(lambda x : '{' + str(x) + '}' , range(5)))
            format_this = '\n'.join(format_this)
        else :
            res.append('data : ')
            mind_data = self.totaldata()['data']
            format_this = list(map(lambda x : '{' + str(x) + '}' , range(length)))
            format_this = '\n'.join(format_this)
        res.append(format_this.format(*mind_data))
        return("{0}\n{1}\n{2}\n{3}".format(*res))
    
    def __repr__(self):
        return(self.__str__())
    
    def __len__(self):
        nl = sum(1 for _ in self.__data)
        self.__data = self.__load()
        return(nl)

    def __del__(self):
        path = self.__fpath
        os.remove(path)
        print('Del is done!')
    
    def __load(self):
        df = open(self.__fpath, mode = 'r', newline = '', encoding = 'utf-8')
        if self.__header :
            head = True
        else :
            head = False
        for i in df:
            if not head :
                yield i
            else :
                head = False
    
    def __transtype(self, xstr, in_typed = (False, False)):
        x = xstr.replace('\n','')
        if x.startswith('0') and ('.' not in x) or in_typed[0] :
            if x == '0' :
                return(0)
            else :
                return(x)
        elif x.startswith(tuple(['NULL','null','NA','na'])):
            return(None)
        elif x.startswith(tuple(['Inf','INF','inf'])) :
            return(math.inf)
        else :
            if in_typed[1] :
                try :
                    if ' ' in x :
                        lastp = ' %H:%M:%S'
                    else :
                        lastp = ''
                    res = ("/" in x and "%Y/%m/%d") \
                        or ("-" in x and "%Y-%m-%d") \
                        or ("." in x and "%Y.%m.%d") \
                        or ("~" in x and "%Y~%m~%d") \
                        or ("\\" in x and "%Y\\%m\\%d") \
                        or ("%Y%m%d")
                    return(time.strptime(x, (res + lastp)))
                except :
                    return(float(x))
            else :
                try :
                    return(float(x))
                except :
                    return(x)
    
    def __is_chinese(self , check_str) :
        if isinstance(check_str,list) :
            chs = ''.join(check_str)
        else :
            chs = check_str
        for i in chs :
            if u'\u4e00' <= i <= u'\u9fff' :
                return(True)
        return(False)
    
    def setColnames(self, names):
        if isinstance(names, list) :
            if len(names) == self.ncols() :
                self.__colnames = names
                return(True)
            else :
                print('Input List is wrong!')
                raise IndexError
        else :
            print('Need to use List as this input.')
            raise IOError

    def ncols(self):
        self.ncol = len((next(self.__data)).split(self.__sep))
        self.__data = self.__load()
        return(self.ncol)
    
    def getColnames(self):
        return(self.__colnames)
    
    def statistics(self):
        '''
        逐列统计，计算数据基本统计指标。
        每行数据为：计算的列名称，最小值、25%分位数、中位数、平均值、75%分位数、95%分位数、最大值、
                   众数、极差、样本量、方差、标准差、协方差、标准误差、偏度、峰度。
        '''
        opnow = os.path.split(self.__fpath)
        if not os.path.exists(opnow[0] + '/stats_data') :
            os.mkdir(opnow[0] + '/stats_data')
        res = Bidator(opnow[0] + '/stats_data/statsData_' + opnow[1] , sep = self.__sep)
        is_cols = ['dataname','min','percentile25%','percentile50%','mean',
            'percentile75%','percentile95%','max','mode','range','samples',
            'var','std','coefficient','standard_error','Skewness','Kurtosis']
        res.append(is_cols)
        res.__header = True
        for col in self.__colnames:
            lineData = [col]
            coldata = self.__getitem__(col)
            if None in coldata:
                coldata = [i for i in coldata if i != None]
            if not isinstance(coldata[0], str) :
                if isinstance(coldata[0], time.struct_time) :
                    lineData = lineData + [time.strftime('%Y-%m-%d %H:%M:%S', min(coldata))]
                    lineData = lineData + [None, None, None, None, None]
                    lineData = lineData + [time.strftime('%Y-%m-%d %H:%M:%S', max(coldata))]
                    lineData = lineData + [None, None]
                    lineData.extend([len(coldata)])
                    lineData = lineData + [None, None, None, None, None, None]
                else :
                    lineData.extend(list(np.percentile(coldata, [0, 25, 50, 75, 95, 100])))
                    lineData.insert(4, np.mean(coldata))
                    lineData.extend([stats.mode(coldata)[0][0]])
                    lineData.extend([np.ptp(coldata)])
                    lineData.extend([len(coldata)])
                    lineData.extend([np.var(coldata,ddof=1)])
                    lineData.extend([np.std(coldata,ddof=1)])
                    lineData.extend([np.mean(coldata)/np.std(coldata)])
                    lineData.extend([np.std(coldata)/(len(coldata)**0.5)])
                    lineData.extend([stats.skew(coldata)])
                    lineData.extend([stats.kurtosis(coldata)])
            else :
                lineData = lineData + [None, None, None, None, None, None, None, None, None]                                                    
                lineData.extend([len(coldata)])
                lineData = lineData + [None, None, None, None, None, None]
            res.append(lineData)
        res.setColnames(is_cols)
        return(res)
    
    def clear(self):
        self.__colnames = []
        self.ncol = 0
        self.__header = False
        os.remove(self.__fpath)
        with open(self.__fpath, mode = 'w+', encoding = 'utf-8') as df :
            df.write('')
    
    def head(self, n = 5):
        ni = 0
        res = []
        for i in self.__data :
            ni += 1
            if ni > n :
                break
            res.append(list(map(self.__transtype , i.split(self.__sep))))
        self.__data = self.__load()
        return(res)
    
    def tail(self, n = 5):
        ni = self.__len__()
        res = []
        for i in self.__data :
            ni -= 1
            if ni < n :
                res.append(list(map(self.__transtype , i.split(self.__sep))))
        self.__data = self.__load()
        return(res)
    
    def totaldata(self):
        '''
        根据类变量LARGEST_NORMAL，来判断一次性提取全部数据。
        '''
        length = self.__len__()
        if length > Bidator.LARGEST_NORMAL :
            print("This Data is too LARGE, it can NOT be read DIRECTLY!")
            print("Please try <next> or <class.__getitem__> methods. ")
            raise MemoryError
        else :
            mind_data = np.array(list(map(self.__getitem__ , self.__colnames)))
            res = dict()
            res['data'] = list(map(lambda x : list(mind_data[:, x]) , range(length)))
            res['colnames'] = self.__colnames
            self.__data = self.__load()
            return(res)
    
    def append(self, dataList):
        '''
        增加一行数据。
        '''
        data_file = open(self.__fpath, mode = 'a', encoding = 'utf-8')
        data_file.write(self.__sep.join(list(map(str , dataList))) + '\n')
        data_file.close()
        self.__data = self.__load()
    
    @staticmethod
    def zero(ncol = 4, nrow = 4, sep = ',', colnames = [1,2,3,4]):
        newData = Bidator('new_data.csv', sep = sep)
        for i in range(nrow + 1) :
            if i == 0 :
                newData.append(colnames)
                newData.__header = True
            newData.append([0] * ncol)
        newData.setColnames(colnames)
        return(newData)

# AUTHOR    : Liangyi ZHang <zly@lyzhang.me>
# LICENSE   :
#    Class Bidaor for python on using to reading big data
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



