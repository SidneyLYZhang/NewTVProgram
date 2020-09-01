'''
  ____      _   _   _               ____  _____ __  __
 / ___| ___| |_| |_(_)_ __   __ _  |  _ \|  ___|  \/  |
| |  _ / _ \ __| __| | '_ \ / _` | | |_) | |_  | |\/| |
| |_| |  __/ |_| |_| | | | | (_| | |  _ <|  _| | |  | |
 \____|\___|\__|\__|_|_| |_|\__, | |_| \_\_|   |_|  |_|
                            |___/

Update: 2020-08-19
Author: Sidney Zhang
'''

################################################
#                   PACKAGE                    #
################################################

from functools import reduce
import pandas  as pd
import numpy as np

################################################
#                    CLASS                     #
################################################

class getRFM(object):
    '''
    默认分值区间划分：
        0：[min, mean, max]
        1：[min, median, max]
        2：[min, 25%, 75%, max]
        2.5：[min, 35%, 65%, max]
        3：[min, 25%, mean, 75%, max]
        3.5：[min, 25%, median, 75%, max]
        4：[min, 25%, median, mean, 75%, max]
        5：[min, 10%, 30%, 50%, 70%, 90%, max]
        其他: 自定义
    up-down代码：
        1：up
        0：down
    用户价值分表：
        1. 高价值用户       (1,1,1)
        2. 重要换回用户     (0,1,1)
        3. 重要深耕用户     (1,0,1)
        4. 重要挽留用户     (0,0,1)
        5. 潜力用户         (1,1,0)
        6. 新付费用户       (0,1,0)
        7. 一般用户         (1,0,0)
        8. 流失用户         (0,0,0)
    '''
    __slots__ = ['__data', '__theRFM', '__coreColu', '__bins', '__compare', '__noCalc']
    def __init__(self, data, r = "Recency", f = "Frequency", m = "Monetary", byScore = False, *argv, **kwargs):
        self.__data = data.copy()
        self.__theRFM = pd.Series([r,f,m], index=['r','f','m'])
        self.__coreColu = pd.Series(list(map(lambda x:x+'.score', self.__theRFM.tolist())) if byScore else self.__theRFM.tolist(), 
                                    index=['r','f','m'])
        self.__bins = {}
        dcfromkeys = lambda x,y,z: dict(map(lambda a,b: (a,x.get(a,b)),y,z))
        self.__compare = {'func': argv if argv else np.mean}
        pargs = dcfromkeys(kwargs,["dr", "df", "dm", "ascending"],[3,3,3,True])
        cargs = dcfromkeys(kwargs,['direction'],['large'])
        self.__compare.update({'pargs':pargs})
        self.__compare.update({'cargs':cargs})
        self.__noCalc = True
    def __call__(self, trans = False):
        if self.__noCalc :
            self.compute()
        keyname = list(map(lambda x : x + '.RFMcode' , self.__theRFM.tolist()))
        res = self.__data[keyname].copy()
        # calculate rfm-type
        def tranlate(x):
            code = [(1,1,1),(0,1,1),(1,0,1),(0,0,1),(1,1,0),(0,1,0),(1,0,0),(0,0,0)]
            title = ['高价值用户','重要换回用户','重要深耕用户','重要挽留用户',
                        '潜力用户','新付费用户','一般用户','流失用户']
            index = code.index(x)
            return(title[index] if trans else (index+1))
        res['RFM.Type'] = res.apply(lambda x : tranlate(tuple(x)), axis = 1)
        # calculate rfm-up/down
        for i in keyname:
            res[i] = res[i].astype(int)
            res.loc[res[i]==1,i] = 'up'
            res.loc[res[i]==0,i] = 'down'
        res.columns = list(map(lambda x : x + '.Result' , self.__theRFM.tolist()))+['RFM.Type']
        return(res)
    def __str__(self):
        if self.__noCalc :
            self.compute()
        res = "完整数据：\n\t"
        # 原始数据（有score数据时包含score数据）
        if (sl := list(filter(lambda x : '.score' in x, self.__coreColu.tolist()))) :
            d = self.__data[self.__theRFM.tolist()+self.__coreColu.tolist()]
        else:
            d = self.__data[self.__coreColu.tolist()]
        # 右衔接最终分类数据
        d = pd.concat([d, self()], axis=1)
        res += str(d).replace('\n','\n\t')
        # 当有score数据时，列出score划分区间
        if sl :
            res += '\n\n说明：\n\t'
            for i in range(len(sl)):
                x = ['r','f','m'][i]
                res += '{0}. {1}的分段区间为：{2}\n\t'.format(i, self.__theRFM[x], self.__bins[x])
        return(res)
    def __repr__(self):
        return(self.__str__())
    def __doPartition(self, dr = 3, df = 3, dm = 3, ascending = True):
        d = {'r': dr,'f': df,'m': dm}
        keydata = self.__data[self.__theRFM.tolist()]
        bins = {
                0:  ['min', 'mean', 'max'],
                1:  ['min', 'median', 'max'],
                2:  ['min', '25%', '75%', 'max'],
                2.5:['min', '35%', '65%', 'max'],
                3:  ['min', '25%', 'mean', '75%', 'max'],
                3.5:['min', '25%', 'median', '75%', 'max'],
                4:  ['min', '25%', 'median', 'mean', '75%', 'max'],
                5:  ['min', '10%', '30%', 'median', '70%', '90%', 'max']
        }
        if isinstance(ascending, list) :
            sl = dict(zip(['r','f','m'],ascending))
        else:
            sl = dict(zip(['r','f','m'],[ascending]*3))
        for i in d.keys() :
            if d[i] in [0,1,2,2.5,3,3.5,4,5]:
                tmp = keydata.quantile([0.1,0.3,0.35,0.65,0.7,0.9])
                tmp.index = ['10%','30%','35%','65%','70%','90%']
                tmp = keydata.describe().append(tmp).loc[bins[d[i]]]
                tmp = tmp[self.__theRFM[i]].tolist().sort()
            else :
                tmp = list(set(d[i] + [0,1]))
                tmp.sort()
                tmp = keydata.quantile(tmp)[self.__theRFM[i]].tolist().sort()
            self.__bins[i] = tmp if sl[i] else tmp[::-1]
        self.__calcScore()
    def __doCompares(self, funs, direction = "large"):
        '''
        direction : 仅接受"large"与"less"2种表值。
        funs : 需要针对分值或原始数值计算一个单一数据以用于比较。
        上述输入参数，可使用统一数值计算，
        '''
        tag = ['r','f','m']
        if isinstance(funs, list) :
            fs = dict(zip(['r','f','m'],funs))
        else :
            fs = dict(zip(['r','f','m'],[funs]*3))
        if isinstance(direction, list) :
            sl = dict(zip(['r','f','m'],direction))
        else :
            sl = dict(zip(['r','f','m'],[direction]*3))
        # byScore = True if list(filter(lambda x : '.score' in x, self.__coreColu)) else False
        def docomp(x):
            d = self.__data[self.__coreColu[x]]
            cbin = [-0.01, fs[x](d), max(d)]
            label = [0,1] if sl[x] == 'large' else [1,0]
            return(x, pd.cut(d, bins=cbin, labels = label))
        for key,value in map(docomp, tag):
            self.__data[self.__theRFM[key]+'.RFMcode'] = value
    def __calcScore(self):
        for i in ['r','f','m']:
            self.__data[self.__coreColu[i]] = pd.cut(self.__data[self.__theRFM[i]], 
                                                        bins=self.__bins[i], labels = range(1,len(self.__bins[i])))
    def setPartition(self, dr = 3, df = 3, dm = 3, ascending = True):
        self.__compare['pargs'].update({
            'dr':dr, 'df':df, 'dm':dm,
            'ascending':ascending
        })
        self.__noCalc = True
    def setCompares(self, direction = "large", *argv):
        self.__compare.update({'func': argv if argv else np.mean})
        self.__compare['cargs'].update({'direction':direction})
        self.__noCalc = True
    def compute(self):
        if list(filter(lambda x : '.score' in x, self.__coreColu.tolist())) :
            self.__doPartition(**self.__compare['pargs'])
            self.__calcScore()
        self.__doCompares(self.__compare['func'], **self.__compare['cargs'])
        self.__noCalc = False
    def describe(self):
        # 全统计数据
        # 分类人数
        # 可指定某个分类的统计情况
        pass
    def getInfo(self, output = False):
        # 展示关键中间结果：byScore为True时，展示Score值，否则展示rfm原始数据。
        return self.__data[self.__coreColu.tolist()]
    def test(self):
        return(self.__data)


################################################
#                 MAINPROGRAM                  #
################################################

if __name__ == "__main__" :
    pass