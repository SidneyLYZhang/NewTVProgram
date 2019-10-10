# Bayes Classification Verification
# 贝叶斯分类验证
# 
# Copyright (C) 2019  Liangyi Zhang
# AUTHOR ： Liangyi Zhang <zly@lyzhang.me>
# 
# 基于贝叶斯定理的分类先验计算模式。主要用于未知用户属性时，根据用户基本行为，根据已可验证的用户行为作为先验，
# 计算这个用户的未知属性情况。
#
# 基本计算模式：
# 有行为的用户在某属性上的贝叶斯概率（即分类验证概率，某用户u在其行为集S_u的条件下有属性A的概率）：
#                P(A|S_u) = \frac{P(S_u|A) \dot P(A)}{P(S_u)} 
#                                  = \frac{\sum^j (P(S_u|j) \dot P(j|A)) \dot P(A)}{\sum_i^N (P(S|i) \dot P(i|u))}
# 其中：
#      1. P（A）某属性的独立概率；
#      2. P（j|A）某属性A条件下有行为j的概率；
#      3. P（S_u|j）有行为j时，用户u会形成当前行为序列S_u的概率；
#      4. P（S|i）某行为i在行为全集S的中的发生概率；
#      5. P（i|u）对某个用户而言，有行为i的概率。
# 所以代入已知条件：
#       已知的行为序列S及对应某属性A的可验证概率为：{ P_j(A) | j \in S } ；
#       已知用户的行为的分布为：{ P_j(U) | j \in S }，
#       已知行为S总数为N，以及各用户对应的行为数为N_u
#       已知属性A_o的互斥属性组内属性数量为M_o （\Unition M_o = A）
# 则可计算得到：
#                P(A|S_u) = \frac{\sum_j (\frac{P_j(u)}{N_u} \dot P_j(A))}{(\sum_j (P_j(s_u) \dot P_j(u))) * M_o}
# 
# 由上述计算模式，即可计算对应条件下的属性概率。于是，对于一组有效的互斥属性，需要分别计算每一个属性的条件概率，
# 例如一个互斥属性组{A_1,A_2,A_3,...,A_n}，某用户u在其上可计算得到各属性的概率{p_1,p_2,...,p_n}，则：
# 概率大于1/n的属性，就是可认定的有效属性，如果：
#       1. 有效属性只有1个，毋庸置疑，用户在这个属性上是显著的；
#       2. 有效属性有多个，则说明用户是非单一组成的，存在多个协同者共同组成这个用户单位的行为，但存在主导型用户，
#          当然也存在一种可能性，这个用户是一个行为离群的用户，有一定行为独特性；
#       3. 有效属性为空，说明用户必然是非单一组成，用户的行为模式较为离散，以最高概率属性认定用户的属性。
# 
# 由此可设计模型输出结果形式： ( {P} , Status ) ， {N:P} 为选择出的属性N列表及对应概率P，Status 为是否为有效
# 属性（True为有效，False为无效）。
# 

# PACKAGES

## pip packages
import requests as rq
import json
import pandas as pd
import time
import random
## own packages
from indexGainer import indexGainer as indG

# CLASS

class bayesclassVerification(object):
    '''
    计算某用户在某互斥属性组下有效属性及对应概率。
    '''
    def __init__(self, user_actions, probabilities, action_list = None):
        pass
    
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    def translate(self):
        pass
    
    def extracting(self):
        pass
    
    def squeeze(self):
        pass
    
    def toDataFrame(self, big = False):
        pass

class effectBayeslabels(object):
    '''
    计算在全属性下的有效标签列表与对应概率。
    '''
    def __init__(self):
        pass
    
    def __load(self):
        pass
    
    def __effectiveness(self):
        pass
    
    def get_labels(self):
        pass

class effectiveLabels(object):
    '''
    生成用户属性标签。
    '''
    def __init__(self):
        pass

    def __load(self):
        pass

    def to_sql(self):
        pass

    def to_file(self):
        pass