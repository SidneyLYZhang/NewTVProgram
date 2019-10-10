# getting Baidu Index or iQiyi Index

# PACKAGES

## pip packages
import json
import requests as rq
import time
import pandas as pd
import random
import datetime as dte
## own packages
from regionbaidu import baiducode
from regionbaidu import baiducode_selection as bcs
from iqiyicode import iqiyicode

# CLASS

class indexGainer(object):
    """
    抓取节目内容的基础数据，主要基于百度指数和爱奇艺指数。
    使用requests进行实际数据抓取，并使用json进行数据解读。
    方法：
    
    """
    __HEADER = {
        'baidu' :{
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,de;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5,fr;q=0.4',
            'Connection': 'keep-alive',
            'Host': 'index.baidu.com',
            'Referer': 'http://index.baidu.com/v2/main/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        },
        'iqiyi' :{
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'http://index.iqiyi.com',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
    }
    def __init__(self, content, header = None, cookies = None, stagetime = None, period = '30', engine = 'baidu'):
        if engine not in ['baidu', 'iqiyi']:
            print('\n'.join([
                "{0} is not a valid input.", 
                "Please select a variable in followed list as input...",
                "Engine : {1}"
            ]).format(engine, str(['baidu', 'iqiyi'])))
            raise Exception("Selected an Engine that is not supported...")
        else :
            self.__engine = engine
            if engine == 'iqiyi':
                try :
                    id = iqiyicode(content).select(by = 'aid')
                except :
                    id = ''
                self.__header = {
                    'Referer': ('http://index.iqiyi.com/q/?name={0}&aid={1}'.format(content,id)).encode('utf8')
                }
                if stagetime:
                    timegap = stagetime
                else:
                    timegap = [indexGainer.today(delta = int(period)), indexGainer.today()]
                if header :
                    self.__header = {**indexGainer.__HEADER[engine], **self.__header, **header}
                else:
                    self.__header = {**indexGainer.__HEADER[engine], **self.__header}
            else :
                id = ''
                self.__header = indexGainer.__HEADER[engine]
                timegap = stagetime
            self.__cookie = cookies
            self.__engine_url = {
                'baidu':{
                    'topicinfo':{
                        'host':'http://index.baidu.com/api/SugApi/sug',
                        'params':{
                            'inputword%5B%5D' : content
                        }
                    },
                    'interest':{
                        'host':'http://index.baidu.com/api/SocialApi/interest',
                        'params':{
                            'wordlist%5B%5D' : content,
                            'typeid' : '',
                            'callback' : '_jsonp' + self.random_chars()
                        }
                    },
                    'regions':{
                        'host':'http://index.baidu.com/api/SearchApi/region',
                        'params':{
                            'region' : '0',
                            'word' : content,
                            'startDate' : stagetime[0] if stagetime else '',
                            'endDate' : stagetime[1] if stagetime else '',
                            'days' : '' if stagetime else period
                        }
                    },
                    'baseinfo':{
                        'host':'http://index.baidu.com/api/SocialApi/baseAttributes',
                        'params':{
                            'wordlist%5B%5D' : content
                        }
                    }
                },
                'iqiyi':{
                    'emotion':{
                        'host' : 'http://pcw-api.iqiyi.com/indextrend/video/audiencepoint',
                        'params' : {
                            'qipuId' : id,
                            'startDate' : timegap[0],
                            'endDate' : timegap[1],
                            'requester' : 'qiyiindex',
                            'isBF' : 'true'
                        }
                    },
                    'trend':{
                        'host':'https://uaa.if.iqiyi.com/video_index/v2/get_index_trend',
                        'params':{
                            'album_id' : id,
                            'time_window' : period
                        }
                    },
                    'platform':{
                        'host':'https://uaa.if.iqiyi.com/video_index/v2/get_platform_distribution',
                        'params':{
                            'album_id' : id
                        }
                    },
                    'province':{
                        'host' : 'https://uaa.if.iqiyi.com/video_index/v2/get_province_distribution',
                        'params':{
                            'album_id' : id
                        }
                    },
                    'scence':{
                        'host' : 'http://pcw-api.iqiyi.com/indextrend/video/scene',
                        'params':{
                            'albumId' : id
                        }
                    },
                    'starsinfo':{
                        'host': 'https://uaa.if.iqiyi.com/video_index/v2/star_appearance',
                        'params':{
                            'album_id' : id
                        }
                    },
                    'baseinfo':{
                        'host':'https://uaa.if.iqiyi.com/video_index/v2/get_user_profile',
                        'params':{
                            'album_id' : id
                        }
                    }
                }
            }[engine]
            if engine == 'iqiyi' and id == '' :
                self.__data = None
            else:
                self.__data = self.__load(engine)
    
    def __len__(self):
        return len(self.__data)
    
    def __str__(self):
        if self.__data :
            res = ["Have been obtained this Index Data of {0} characteristics from {1}.".format(self.__len__(), self.__engine)]
            res.extend(["Characteristics of this Index Data are :\n    {}".format(list(self.__data.keys()))])
            res.extend(["All Index Data:"])
            for i in self.__data.keys():
                res.extend([i])
                res.extend([indexGainer.repr_dict(self.__data[i])])
        else :
            res = ['In {} , there are No index-data...'.format(self.__engine)]
        return '\n'.join(res)
    
    def __repr__(self):
        return (self.__str__())
    
    def __web_resolve(self, tkey, plus_param = None):
        if plus_param :
            para = {**self.__engine_url[tkey]['params'], **plus_param}
        else:
            para = self.__engine_url[tkey]['params']
        i = 0
        while i < 5 :
            try :
                res = rq.get(self.__engine_url[tkey]['host'], 
                    params = para, 
                    headers = self.__header, 
                    cookies = self.__cookie, timeout = (3, 25)).json()
                return res
            except rq.exceptions.RequestException:
                i += 1
    
    def __load(self, engine):
        getting = {
            'baidu' : self.__baidu_resolve,
            'iqiyi' : self.__iqiyi_resolve
        }[engine]
        res = {}
        for key in self.__engine_url.keys() :
            tmp = self.__web_resolve(key)
            print('getting {}\'s data...'.format(key))
            res[key] = getting(key, tmp)
            if key == 'interest' :
                tmp = res[key]
                for i in res[key]:
                    print('      getting {}\'s sub-data...'.format(key))
                    ntmp = self.__web_resolve(key, plus_param = {'typeid' : i['typeId']})
                    tmp.extend(getting(key, ntmp))
                res[key] = tmp
            print('have been gotten {}\'s data...'.format(key))
            time.sleep(5)
        return(res)
    
    @staticmethod
    def __iqiyi_resolve(key, data):
        tmp = {
             'emotion':lambda x : {'data':x['data'][0]['data']},
             'trend': lambda x : {'data':x['details'][0]['data'],'tags':x['playtime']},
             'platform': lambda x : {'data' : x['data'][0]},
             'province': lambda x : {'data' : x['data'][0]},
             'scence': lambda x : {'data' : x['data']['data'][0]},
             'starsinfo': lambda x : {'data' : x['data'][0]},
             'baseinfo': lambda x : {
                 'age':{'data':x['data']['details'][0][str(x['ids'][0])]['age'],'tags':x['data']['ageLabels']},
                 'constellation':{'data':x['data']['details'][0][str(x['ids'][0])]['constellation'],'tags':x['data']['constellationLabels']},
                 'education':{'data':x['data']['details'][0][str(x['ids'][0])]['education'],'tags':x['data']['educationLabels']},
                 'gender':{'data':x['data']['details'][0][str(x['ids'][0])]['gender'],'tags':x['data']['genderLabels']},
                 'interest':{'data':x['data']['details'][0][str(x['ids'][0])]['interest'],'tags':x['data']['interestLabels']}}
        }[key](data)
        return tmp
    
    @staticmethod
    def __baidu_resolve(key, data):
        tmp = {
            'topicinfo': lambda x : x['data']['wordlist'][0],
            'interest': lambda x : x['data']['result'][0]['interest'],
            'regions': lambda x : {
                'city':{'data':list(x['data']['region'][0]['city_real'].values()),'tags':bcs(list(x['data']['region'][0]['city_real'].keys()),'city')},
                'province':{'data':list(x['data']['region'][0]['prov_real'].values()),'tags':bcs(list(x['data']['region'][0]['prov_real'].keys()),'province')},
                'region':{'data':list(x['data']['region'][0]['prov_real'].values()),'tags':bcs(list(x['data']['region'][0]['prov_real'].keys()),'region')}},
            'baseinfo': lambda x : {
                'age':x['data']['result'][0]['age'],
                'gender':x['data']['result'][0]['gender']}
        }[key](data)
        return(tmp)
    
    @staticmethod
    def random_chars():
        base_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        tmp = int(str(random.random())[2:])
        res = []
        while tmp != 0:
            res.append(base_chars[tmp % 36])
            tmp = tmp // 36
        res.reverse()
        return ''.join(res)
    
    @staticmethod
    def repr_dict(data, n = 0):
        gap = '    '
        res = []
        try :
            length = len(data)
        except :
            length = 1
        if isinstance(data, dict) :
            tags = list(data.keys())
            if length > 6 :
                tags = tags[:3] + tags[-3:]
            for key, value in data.items():
                if key in tags:
                    res.extend([(gap * n + '{0}:\n' + gap * (n + 1) + '{1}').format(key, indexGainer.repr_dict(value,n = n+1))])
                else :
                    if res[-1] != '...':
                        res.extend([gap * (n + 1) + '...'])
        elif isinstance(data,list) :
            tmp = gap * n + '['
            ln = 0
            for item in data :
                if ln < 3 | ln > (length - 3):
                    if isinstance(item, dict) :
                        tmp += '\n'
                        tmp += indexGainer.repr_dict(item,n = n+1)
                        if ln < length :
                            tmp += ','
                        else :
                            tmp += '\n'
                    else:
                        tmp += str(item)
                        if ln < length :
                            tmp += ','
                else :
                    if '...' not in tmp :
                        tmp += '\n' + gap * (n + 1) + '...,\n'
            tmp += ']'
            res.extend([tmp])
        else :
            res.extend([str(data)])
        return '\n'.join(res)
    
    @staticmethod
    def today(delta = 0):
        res = (dte.datetime.now() - dte.timedelta(days = delta)).strftime("%Y-%m-%d")
        return res
    
    def extracting(self):
        return(self.__data)
    
    def databy(self, character):
        return(self.__data[character])
    
    def characteristics(self):
        return list(self.__engine_url.keys())

# TESTMAINPROGRAM

if __name__ == "__main__":
    test = indexGainer('复仇者联盟4：终局之战', engine = 'iqiyi')
    print(test)