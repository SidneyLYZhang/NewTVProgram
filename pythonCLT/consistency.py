# AUTHOR    : Liangyi ZHang <ly.zhang.1985@gmail.com>
# LICENSE   : MIT License

# 一致性检验
# 1. Kappa 检验 (Cohen's Kappa)
# 2. Kendall’s W 检验

# REFERENCE:
#       1. https://scikit-learn.org/stable/modules/model_evaluation.html#cohen-kappa
#       2. http://www.real-statistics.com/reliability/kendalls-w/

# PACKAGES

import pandas as pd
import numpy as np
import click
from sklearn.metrics import cohen_kappa_score
from scipy.stats.distributions import chi2
from pampy import match, HEAD, TAIL

# COMMANDTOOL

@click.command()
@click.argument("filename", type = click.Path(exists = True))
@click.option('--idx/--no-idx', default = False, 
                help = 'Whether the CSV file contains a column header. The default is not included. CSV文件是否包含列标题，默认不包含。')
@click.option('--kendallsw', 'functype', flag_value = 'kendallsw', default = True,
                help = 'Consistency test using the Kendalls W method (default) . 使用Kendalls W方法进行一致性检验（默认选择）。')
@click.option('--kappa', 'functype', flag_value = 'kappa',
                help = 'Consistency test using the Kappa method. 使用Kappa方法进行一致性检验。')
def computingResult(filename, functype, idx):
    '''
        一致性检验工具，目前主要实现Cohen's Kappa检验与Kendall's W检验。\n
        由于Cohen's Kappa检验是双元检验，多于两个被检情况时会自动检验每两种情况的一致性。\n
        程序默认使用Kendall's W检验进行一致性分析。\n
        数据使用csv文件输入，每一列为一个被检情况。\n
        \t\n
        FILENAME  \t  Data file(in csv). 数据文件（csv格式）。
    '''
    mkdata = getDatas(okFP(filename), idx)
    res = match(
        functype,
        'kendallsw', kendallsW(mkdata) ,
        'kappa', kappa(mkdata)
    )
    format_echo(res)

# FUNCTIONS

def okFP(pfile):
    return(pfile.replace('\\', '/'))

def getDatas(dafile, idx):
    if idx :
        hns = 0
    else :
        hns = None
    return(pd.read_csv(dafile, header = hns, sep = ','))

def kendallsW(datas):
    dim = datas.shape
    S = np.var(list(datas.apply(sum, axis = 0))) * dim[1]
    d = (dim[0]**2)*(dim[1]**3 - dim[1])
    w = S / d
    xx = dim[1] * (dim[0] - 1) * w
    df = dim[0] - 1
    pv = chi2.sf(xx, df)
    return({'type' : 'Kendall\'s W Test',
            'value' :  w ,
            'p-value' : pv })

def namePair(lnames):
    return(
        match(
            lnames,
            [int, int], lambda a,b : [(a, b)] ,
            [str, str], lambda a,b : [(a, b)] ,
            [str, int], lambda a,b : [(a, b)] ,
            [int, str], lambda a,b : [(a, b)] ,
            [HEAD, TAIL], lambda a,t : list(map(lambda x : (a, x), t)) + namePair(t)
        )
    )

def amend(samp, floornum):
    if samp[1] < floornum :
        return((samp[0] , 1 + samp[1]))
    else :
        return(samp)

def kappa(datas):
    dns = list(map(lambda x : int(x), list(datas.columns.values)))
    if datas.shape[1] > 2 :
        pns = namePair(dns)
        res = dict(zip(
            list(map(lambda x : ' - '.join([str(y) for y in x]), pns)),
            list(map(lambda x : cohen_kappa_score(datas[x[0]],datas[x[1]]), pns))
        ))
    else :
        res = cohen_kappa_score(datas[dns[0]],datas[dns[1]])
    if isinstance(res, dict) :
        res = dict(list(
            map(lambda x : amend(x, 0) , zip(res.keys(),res.values()))
        ))
    else :
        if res < 0 :
            res = 1 + res
    return({'type' : 'Kappa Test',
            'value' :  res })

def format_echo(datas):
    print('\n' + '='*100 + '\n')
    print('使用 {} 方法对数据的一致性进行检验：'.format(datas['type']))
    print('\n')
    vdl = datas['value']
    if isinstance(vdl, dict):
        for c in vdl :
            print("被检情况{0:>10s}之间的一致性为:{1:1.5f}".format(c, vdl[c]))
    else :
        print("被检情况之间的一致性为:{0:1.5f}".format(vdl))
    if 'p-value' in datas.keys() :
        print("一致性的p值为:{0:2.5f}%".format(datas['p-value']*100))
    print('\n' + '='*100 + '\n')
    print(
    '''
        程度说明：
        0%  ~ 25%： 较底的一致性水平。
        25% ~ 75%： 一般程度的一致性。
        75% ~ 100%：极高一致性。
    ''')

# MAINSPROGRAM

if __name__ == "__main__":
    computingResult()