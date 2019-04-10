'''
    =============================================================================================================
    YouTube频道用户偏好分析 —— 超简略版
    =============================================================================================================
    
    @SidneyZhang 2019.04.08

    这个程序主要期望用于解决YouTube上节目名称与用户喜好之间的偏好关系。

    并非基于模型的偏好求解，而是关注用户偏好的逻辑形态与可解释性逼近。为达到这一目的，近义词、词性、情感偏好
    都是需要考虑的。同时，为了减少代码量，主题模型使用现有技术模型，不另作重复。

    一般来说，用户偏好是由用户行为反映出来的统计特征；而YouTube很简洁的用点赞与点踩两个行为为用户偏好做了标
    记，同时这些标记必然来自于较为忠诚的用户，这个"忠诚"可以是对YouTube的，也可以是对这个频道的，因为不需要
    准确区分用户所忠诚的对象，只需要了解这个用户的行为反映了这个忠实用户的偏好就可以了。
    
    如何提取用户偏好呢？

    1. 文本的关键词：

    借助节目文本的总和，提取出关键词，利用关键词结合点赞/点踩频次生成词云，确定不同频道的核心偏好。主要借助 
    SnowNLP 的分词与关键词能力。

    2. 比较标题文本的近似程度：

    文本之间的相似性，利用Word2Vec比较不同节目标题文本之间的相似性，结合点赞/点踩的加权行为，可以生成不同来
    源频道的运营区隔程度，或者说是节目的内在共通程度。主要借助 Synonyms 进行向量化比较。

    3. 关键词的相似度：

    比较关键词之间的联系，进一步集中用户选择和核心趋向。主要借助 Synonyms 进行向量化的近义词比较。

    4. 节目标题的情绪与用户选择：

    节目标题的情绪与用户的选择，可以导出用户进行标记的情绪基点，从而明确已收视用户行为偏好。主要借助 SnowNLP 
    的情绪化分析完成相关内容。
    
    核心方法来自于已建立好的NLP模型，使用对自然语言的分析，完成上述关键的分析过程。

    仅这件事而言，应该加入视频中所有的对话、旁白等音频文本，但限于无法拿到对应视频进行文本识别，所以仅依赖外
    部已有的人工标题作为原始视频语义的近似。同时，由于没有时间进一步进行深层文本含义的对比，以及文本序列模式
    的分析，所以也导致用户行为所体现的意义可能存在偏移，用户的喜好也无法进一步分解。综上，这里所期望解决的，
    仅为初步的结论，甚至说只是粗糙的前置分析框架。

    --------------------------------------------------------------------------------------------------------------

    参考：

    1. [SnowNLP](https://github.com/isnowfy/snownlp)
    2. [Synonyms](https://github.com/huyingxi/Synonyms)
    3. [悟乙己 : 六款中文分词模块尝试](https://blog.csdn.net/sinat_26917383/article/details/77067515)

    授权信息：

    @online{Synonyms:hain2017,
        author = {Hai Liang Wang, Hu Ying Xi},
        title = {中文近义词工具包Synonyms},
        year = 2017,
        url = {https://github.com/huyingxi/Synonyms},
        urldate = {2017-09-27}
    }
'''

# AUTHOR  : Sidney Zhang <ly.zhang.1985@gmail.com> <twitter@sidneyzhang>
# LICENSE : MIT License

# MODELS

from snownlp import SnowNLP
import os
import pandas as pd
import math
import numpy as np
from pampy import match, TAIL, _

# INFORMATIOPNS

def info_here():
    i = os.system("cls")
    print(__doc__)

# TEXT FOR ANALYSIS

def getDatas(fnames): #getting datas from csv-files
    snames = list(map(lambda x : x + '.csv', fnames))
    res = list(map(lambda x : pd.read_csv(x, header = None, sep = ','), snames))
    return(dict(zip(fnames, res)))

def vecMag(vs): #computing magnitude of vector
    return(pow(sum(list(map(lambda x : x ** 2, vs))),1/2)/len(vs))

def getSimilar(senc1, senc2): #computing similarity for two strings-lists
    resu = list(map(lambda x : np.mean(SnowNLP(senc2).sim(x)), senc1))
    return(resu)

def namePair(lnames): #getting pairs of filenames for composing
    return(
        match(
            lnames,
            [str, str], lambda a,b : [(a, b)] ,
            [str, TAIL], lambda a,t : list(map(lambda x : (a, x), t)) + namePair(t)
        )
    )

def putStrlist(names, data): #getting the corresponding text
    return(
        dict(
            zip(names, list(map(lambda x : list(data[x][0]) , names)))
        )
    )

def zipStrdata(fnames, strdts, datas): #sorting text and weighted data
    return(
        dict(zip(
            fnames,
            list(map(lambda x : list(zip(strdts[x], list(datas[x][1]))) , fnames))
        ))
    )

def getKeywords(fnames, strdts, datas): #basic keywords processor
    orig = zipStrdata(fnames, strdts, datas)
    orikey = dict(zip(fnames, list(map(
        lambda x : list(map(lambda y : SnowNLP(y[0]).keywords(2) + [y[1]] , orig[x])),
        fnames
    ))))
    return(orikey)

def compressKeywords(orikey): #compressing keywords-lists
    labels = ['o','t','w']
    fname = list(orikey.keys())
    mittel = dict(zip(
        fname,
        list(map(lambda x : pd.DataFrame.from_records(orikey[x], columns=labels) , fname))
    ))
    uniall = dict(zip(
        fname,
        list(map(lambda x : list(pd.Series(list(mittel[x]['o'].unique()) + list(mittel[x]['t'].unique())).unique()), 
                fname))
    ))
    result = dict(zip(
        fname,
        list(map(
            lambda x : list(zip(
                uniall[x],
                list(np.sum([list(map(lambda y : mittel[x].loc[mittel[x]['o'] == y].w.sum() , uniall[x])),
                        list(map(lambda z : mittel[x].loc[mittel[x]['t'] == z].w.sum() , uniall[x]))],
                        axis = 0))
            )),
            fname
        ))
    ))
    return(result)

def sentiPreference(fnames, strdts, datas): #handling user sentiment trends
    orig = zipStrdata(fnames, strdts, datas)
    okposi = dict(zip(fnames, list(map(
        lambda x : list(map(lambda y : (SnowNLP(y[0]).sentiments * y[1] , y[1]) , orig[x])),
        fnames
    ))))
    return(okposi)

def sumTulist(orid): #computing sum of each element in tuple-list
    return((sum(list(map(lambda x : x[0] , orid))) , sum(list(map(lambda x : x[1] , orid)))))

# MAINSPROGRAM

if __name__ == "__main__":
    #before everything
    filesname = ['REBO', 'QINGGAN', 'SHAONV', 'TUHAO']
    dts = getDatas(filesname)
    strDic = putStrlist(filesname, dts)
    nameTwins = namePair(filesname)
    info_here()
    #startting to analysis
    #1
    first_result = dict(zip(
        list(map(lambda x : " - ".join(x) , nameTwins)), 
        list(map(lambda x : getSimilar(strDic[x[0]],strDic[x[1]]) , nameTwins))
    ))
    first_result = dict(zip(
        list(first_result.keys()),
        list(map(lambda x : vecMag(first_result[x]) , list(first_result.keys())))
    )) #a.t.p. getting similarity of each channel
    resultfile = pd.DataFrame.from_dict(first_result, orient='index')
    resultfile.to_csv('similar_channel.csv')
    #2
    second_result = sentiPreference(filesname,strDic,dts)
    second_result = dict(zip(
        filesname,
        list(map(lambda x : sumTulist(second_result[x]) , filesname))
    ))
    second_result = dict(zip(
        filesname,
        list(map(lambda x : second_result[x][0]/second_result[x][1] , filesname))
    )) #a.t.p. getting sensitivity of each channel
    resultfile = pd.DataFrame.from_dict(second_result, orient='index')
    resultfile.to_csv('senti_channel.csv')
    #3
    third_result = getKeywords(filesname,strDic,dts)
    third_result = compressKeywords(third_result)
    for i in filesname:
        resultfile = pd.DataFrame.from_records(third_result[i])
        resultfile.to_csv('keywors_'+ i +'.csv')
    