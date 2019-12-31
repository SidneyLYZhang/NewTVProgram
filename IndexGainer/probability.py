# Packages

import pandas as pd
import numpy as np
import psutil
from functools import reduce
from itertools import zip_longest,product
import os
import re
from datetime import datetime as dt
import matplotlib.pyplot as plt
import time
import seaborn as sbn

import userTypePosterior

# Status Informations

cls = lambda : os.system('cls')
now = lambda : dt.now().strftime("%Y-%m-%d %H:%M:%S")

sbn.set_style('whitegrid',{'font.sans-serif':['simhei','Arial']})

cnames = {
    "_A.csv" : ["ID","dis","city","activetime","isActive",
                    "lastactive","watchtimes","watchlang","watchdays","viewtimes","viewlang",
                    "reseetimes","reseelang","livetimes","livelang","gaptime","lastgaptime"],
    "_B.csv" : ["ID","progtype","times","lang","setnum"],
    "_C.csv" : ["ID","progid","progname","lasttime","lang"]
}

conFunc = {
    "_A.csv": {
        'cut' : ["dis","city"],
        "activetime" : lambda x : pd.to_datetime(x, format = "%Y%m%d"),
        "lastactive" : lambda x : pd.to_datetime(x, format = "%Y%m%d"),
        "isActive" : lambda x : pd.to_numeric(x, downcast = 'unsigned'),
        'transcon' : {
            'tip' : ["watchtimes","watchlang","watchdays","viewtimes","viewlang",
                    "reseetimes","reseelang","livetimes","livelang","gaptime","lastgaptime"],
            'func' : lambda x : pd.to_numeric(x, downcast = 'float')
        }
    },
    "_B.csv": {
        "progtype" : lambda x : x.astype('category'),
        "times" : lambda x : pd.to_numeric(x, downcast = 'unsigned'),
        "setnum" : lambda x : pd.to_numeric(x, downcast = 'unsigned')

    },
    "_C.csv": {
        'cut' : ["progid"],
        "progname" : lambda x : x.astype('category'),
        "lasttime" : lambda x : pd.to_datetime(x),
        "lang" : lambda x : pd.to_numeric(x, downcast = 'float')
    }
}

# Functions

def read_datas(fs, names, conver = None, sep = '\t', header = None):
    data = pd.read_csv(fs, header = header, sep = sep, names = names)
    if conver :
        for nai in conver.keys():
            if nai == 'cut' :
                tmp = names.copy()
                for i in conver[nai]:
                    tmp.remove(i)
                data = data[tmp]
            elif nai == 'transcon' :
                for xd in conver[nai]['tip']:
                    data[xd] = conver[nai]['func'](data[xd])
            else:
                data[nai] = conver[nai](data[nai])
    print("data : " + fs)
    data.info(memory_usage = 'deep')
    return(data)

def flash_isok():
    mp = psutil.virtual_memory().percent
    smp = "Memory Usage : {a:4.2f}%".format(a = mp)
    return(smp, mp)

# Main Part

if __name__ == "__main" :
    ff = "F:/data_Action/chongqing/active_1_C.csv" # "C:/Users/alfch/Downloads/每日文件中转站/活跃用户留存沉默分析/活跃用户明细1月第三部分.csv"
    a = read_datas(ff, cnames['_C.csv'], conver = conFunc['_C.csv'])
    idn = a.ID.unique()
    pnn = a.progname.unique()
    a["hour"] = a.lasttime.dt.hour
    ptx = a.pivot_table(index = "progname", columns = "hour", values = "lang", aggfunc = np.sum)
    sbn.heatmap(ptx)
    plt.show()
    kde = KernelDensity(kernel='gaussian', bandwidth = np.std(np.std(ptx).tolist())).fit(ptx)
    sort_a_data = a.groupby("progname").agg(len)
    
    result = {}
    for idx in idn :
        dcx = a[(a.ID == idx)].progname
        result[idx] = beyasprob(dcx)