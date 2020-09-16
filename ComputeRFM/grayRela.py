'''
  ____                    ____                    _       _   _
 / ___|_ __ __ _ _   _   / ___|___  _ __ _ __ ___| | __ _| |_(_) ___  _ __
| |  _| '__/ _` | | | | | |   / _ \| '__| '__/ _ \ |/ _` | __| |/ _ \| '_ \
| |_| | | | (_| | |_| | | |__| (_) | |  | | |  __/ | (_| | |_| | (_) | | | |
 \____|_|  \__,_|\__, |  \____\___/|_|  |_|  \___|_|\__,_|\__|_|\___/|_| |_|
                 |___/

Update : 2020-09-15
Author : Liangyi Zhang

=======================================================================================

计算基本的灰度相关性。

参考： 
1. https://www.dmu.ac.uk/documents/technology-documents/research-faculties/cci/lu-grey-system-2015.pdf
2. https://www.jeffjournal.org/papers/Volume7/7.2.11H.Hasani.pdf
'''

from functools import reduce
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class grayrelative(object):
    __slots__ = ['__data','__GRCoefficien','__columns','__gray', '__weight']
    def __init__(self, data, selection = None, weight = None):
        self.__data = data
        self.__GRCoefficien = None
        if weight is None :
            self.__weight = None
        else :
            if sum(weight) != 1 :
                raise ValueError("the sum of weight must be equal to 1 !\n")
            elif len(weight) != len(data) :
                raise ValueError("the weight is too large!\n")
            else :
                self.__weight = weight
        if selection is None:
            self.__columns = data.columns.tolist()
        elif isinstance(selection,list) :
            tmp = pd.Series(selection)
            self.__columns = tmp[tmp.isin(data.columns)].tolist()                
        else :
            raise TypeError("错误数据 selection !\n")
        self.__gray = pd.DataFrame(index=data.index)
        for i,pis in data[self.__columns].iteritems():
            MAX = pis.max()
            MIN = pis.min()
            MEAN = pis.mean()
            self.__gray[i] = (pis-MEAN)/(MAX-MIN)
    def __call__(self, output = False):
        if self.__GRCoefficien is None :
            res = pd.DataFrame()
            for i in self.__columns :
                res[i] = self.__gra(i)
            self.__GRCoefficien = res
        if output :
            return(self.__GRCoefficien)
    def __gra(self, m):
        tmpc = self.__columns.copy() # 记录列信息
        stt = self.__gray[m] #标准要素
        tmpc.remove(m)
        ce = self.__gray[tmpc] #比较要素
        cn, cm = ce.shape # 记录行列范围
        delta = 1/cm
        note = np.zeros([cm, cn]) #基准比较差异
        for i in range(cm):
            for j in range(cn):
                note[i, j] = abs(ce.iloc[j, i] - stt.iloc[j])
        note = pd.DataFrame(note)
        note_min, note_max = note.T.min(), note.T.max()
        mit = np.zeros([cm, cn]) #差异的中间数据
        for i in range(cm):
            for j in range(cn):
                mit[i, j] = (note_min[i] + delta * note_max[i]) / (note.iloc[i, j] + delta * note_max[i])
        if self.__weight is None :
            result = [pd.Series(mit[i, :]).mean() for i in range(cm)]
        else :
            result = [sum(np.multiply(mit[i,:],self.__weight)) for i in range(cm)]
        result.insert(self.__columns.index(m), 1)
        return(pd.Series(result, index = self.__columns))
    def getGRGrade(self):
        '''
        直接返回灰度相关系数
        '''
        if self.__GRCoefficien is None :
            self()
        return(self.__GRCoefficien)
    def test(self):
        '''
        主要用于测试
        '''
        return(self.__gray)
    def plot(self, save = None, title = None, only_core = True, size = (16,10), dpi = 600, annot = False):
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        f, ax = plt.subplots(figsize=size)
        if (title is None) or (title is False):
            ax.set_title('GRA HeatMap')
        else :
            ax.set_title(title)
        if only_core :
            mask = np.zeros_like(self.__GRCoefficien)
            mask[np.triu_indices_from(mask)] = True
        else :
            mask = np.zeros_like(self.__GRCoefficien)
        with sns.axes_style("white"):
            sns.heatmap(self.__GRCoefficien,
                        cmap="YlGnBu",
                        annot=annot,
                        fmt = '.2f',
                        mask=mask)
        if save is None:
            plt.show()
        else:
            plt.savefig(save, bbox_inches='tight', transparent=True, dpi=dpi)

if __name__ == "__main__" :
    data = pd.DataFrame(np.random.random([9,4]), columns = ['a','b','c','d'])
    model = grayrelative(data)
    model(output = True)
    '''# example:
                  a         b         c         d
        a  1.000000  0.697232  0.605001  0.605297
        b  0.706260  1.000000  0.664751  0.567917
        c  0.665841  0.716484  1.000000  0.624213
        d  0.636339  0.585494  0.596689  1.000000
    '''
    model.plot()