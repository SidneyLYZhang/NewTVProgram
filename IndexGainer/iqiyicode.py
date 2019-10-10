# search iqiyi movie codes
import requests as rq
import json
import pandas as pd
import time

class iqiyicode(object):
    __HOST = 'https://uaa.if.iqiyi.com/video_index/v2/filtered_suggest_album'
    __HEADER = {
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'http://index.iqiyi.com',
        'Referer': 'http://index.iqiyi.com/',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    def __init__(self, content, connum = 10, header = None, pause = 3, match_ok = True):
        self.__params = {
            'key' : content,
            'platform' : 11,
            'rltnum' : connum
        }
        self.__match_ok = match_ok
        self.__header = {**header , **iqiyicode.__HEADER} if header else iqiyicode.__HEADER
        self.data = self.__load(pause)
    
    def __str__(self):
        return(str(pd.DataFrame(self.data)))
    
    def __repr__(self):
        return(self.__str__())
    
    def __load(self, n):
        datasets = rq.get(
            iqiyicode.__HOST,
            params = self.__params,
            headers = self.__header
        )
        time.sleep(n)
        datasets = json.loads(datasets.content)['data']
        res = list(map(
            lambda x : {
                'name' : x['name'],
                'tname' : x['cname'],
                'aid' : x['aid']
            },
            datasets
        ))
        return(res)
    
    def retrieve(self):
        return(self.data[0] if self.__match_ok else self.data)
    
    def select(self, by = None, all = False):
        if by :
            res = pd.DataFrame(self.data)[by].tolist()
            return(res if all else res[0])
        else :
            print('You can select a character from the following list : \n{} - {} - {}'.format(*list(self.data[0].keys())))
            return(None)

class getiqiyiaid(object):
    def __init__(self, namelist):
        names = namelist if isinstance(namelist,list) else [namelist]
        self.data = list(map(
            lambda x : iqiyicode(x).select(by = 'aid'),
            names
        ))