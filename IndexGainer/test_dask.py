import dask.dataframe as dd
import numpy as np
import psutil
from functools import reduce
from itertools import zip_longest,product
import os
import re
from datetime import datetime as dt
import pandas as pd
import time
import requests as rq

cls = lambda : os.system('cls')
now = lambda : dt.now().strftime("%Y-%m-%d %H:%M:%S")

fdr = "E:/Chongqing_alwaysaction/alwaysaction.csv" #big: 1.44GB
okfile = "E:/Chongqing_alwaysaction/alwaysaction_ok.csv"
fpp = open(okfile, 'w+', encoding='utf8')
ffp = open("E:/Chongqing_alwaysaction/wrong.csv", 'w+', encoding='utf8')

cnames = ["user","progid","name","progtype","lang","times","lastdate"] # 广电号 - 节目集ID - 节目集名称 - 节目类型 - 总收视时长（分钟） - 总收视次数 - 最后收视时间

with open(fdr, "r", encoding = 'utf8') as f :
    fpp.write(';'.join(cnames)+'\n')
    for i in f:
        if "NULL\tNULL" not in i :
            tmp = i.split('\t')
            if len(tmp) == 7 :
                tmp[-1] = tmp[-1][:19]
                tmp = ';'.join(tmp) + '\n'
                fpp.write(tmp)
            else :
                ffp.write(i)
        else :
            ffp.write(i)

fpp.close()
ffp.close()

cfuns = {
    "name" : 'category',
    "progtype" : 'category'
}

y = dd.read_csv(okfile, sep = ';', dtype = cfuns, parse_dates = ['lastdate'])

y.head()

y.name.unique().compute()
y.user.unique().compute()

uni_len = dd.Aggregation(
    name = 'uni_len',
    chunk = lambda x : x.unique(),
    agg = lambda xa : len(xa)
)

a = y.groupby('name').agg({'lang':sum,'times':sum, 'user': uni_len}).compute()

y['hour'] = y.lastdate.dt.hour

y.hour = y['hour'].cat.as_known()
y.name = y['name'].cat.as_known()

a = y.pivot_table(index='name', columns='hour', values='lang', aggfunc='sum').compute()

a.sort_values(by=['0'])

a.to_excel("E:/pivot_hour.xlsx")

files = "C:/Users/1/Downloads/name_list.txt"

with open(files,'r',encoding = 'utf8') as ff :
    titleslist = ff.read().split('\n')

titleslist = titleslist[:-1]
ziel = 0
test = dict()

while ziel<3000 :
    print(ziel)
    print(titleslist[ziel])
    try :
        test[titleslist[ziel]] = indexGainer(titleslist[ziel], engine = 'iqiyi')
        print("\n\nwaitings...\n\n")
        time.sleep(1)
    except :
        print("warning...\n\n")
    ziel += 1

def getdatald (data) :
    ressdata = list()
    for i in data:
        ressdata.append(data[i]['data'])
    return pd.DataFrame(ressdata, columns=data[i]["tags"], index=list(data.keys()))

def getpedia(title):
    heads = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,de;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5,fr;q=0.4",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "shuyantech.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    mt = 'http://shuyantech.com/api/cndbpedia/ment2ent?q='
    vt = 'http://shuyantech.com/api/cndbpedia/value?q=[movie]&attr=类型'
    print('Getting datas of key words : ' + title + ' ...\n\n')
    td = rq.get( (mt + title) , headers = heads).json()['ret']
    if len(td) == 1 :
        vturl = vt.replace("[movie]",td[0])
    elif len(td) > 1 :
        keywords = ['主演','指导','动画','网剧','电视剧','电影']
        for i in td :
            for word in keywords :
                if word in i :
                    vturl = vt.replace("[movie]",i)
                    break
    else :
        vturl = ""
    time.sleep(5)
    if vturl :
        print('Data is ok...\nBegin to query the typedata of video ...\n')
        td = rq.get( vturl , headers = heads).json()['ret']
        print('...waiting...\n\n\n')
        time.sleep(5)
        return td
    else :
        print('Warning...\n')
        print('no data...\n\n')
        return ['']

res = dict()
for i in text :
    try :
        res[i] = getpedia(i)
    except:
        time.sleep(5)
        continue

def havespilt(x):
    tt = [' ，', ' / ' , ' \\ ' , ' ', '/', '\\', '，', ',', '、']
    res = [False, '']
    for i in tt :
        if i in x :
            res = [True, i]
            break
    return res

dtmp = []
for i in res.keys() :
    tmp = res[i]
    if tmp and "" not in tmp :
        for j in tmp :
            hs = havespilt(j)
            if hs[0] :
                for k in j.split(hs[1]) :
                    dtmp.append([i, k])
            else:
                dtmp.append([i, j])

a = pd.DataFrame(dtmp, columns = ["prog","type"])
aa = a.groupby('type').agg(len)

