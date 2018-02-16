import os
from elasticsearch import Elasticsearch
from settings import WEB_LIST
from analysis.nlp import Simlarity
import arrow

es = Elasticsearch()
sort_map={
        'score':'_score',
        'date':'date',
        }
cbnweek_sort_map={
        'score':'_score',
        'date':'article_date',
        }
# 主题相似性有多个文档集合匹配模型 需要一一定义
sim={
    'cbnweek':Simlarity('cbnweek'),
    'duozhiwang':Simlarity('duozhiwang'),
    'jingmeiti':Simlarity('jingmeiti'),
    'hurun':Simlarity('hurun'),
    'all':Simlarity('alledu'),
}

def searchCbnWeekData(data, match_model,sort):

    search_body={
        "size":100,
        "query": {
             "bool": {
                "should": [
                    { match_model: { "magazine_url": data}},
                    { match_model: { "article_text": data}},]
                }
        },
        "sort": [
        {
            cbnweek_sort_map[sort]: {
            "order": "desc"
            }
        }],
        # "sort":{"article_date":{"order","desc"}},
        "highlight" : {
            "pre_tags" : ['<strong class="w3-text-green">'],
            "post_tags" : ["</strong>"],
            "fields" : {
                "article_text":{}
            }
        },
    }
    res = es.search(index="article_cbnweek_index", body=search_body)
    res["search_data"]=data
    return res

def searchArticleData(data, index, data_type, match_model, sort):
    search_body={
        "size":100,
        "query": {
            match_model: {
                "text":data,
            }
        },
        "sort": [
        {
            sort_map[sort]: {
            "order": "desc"
            }
        }],
        # "sort":{"date":{"order","desc"}},
        "highlight" : {
            "pre_tags" : ['<strong class="w3-text-green">'],
            "post_tags" : ["</strong>"],
            "fields" : {
                "text":{}
            }
        }
    }

    res = es.search(index=index, doc_type=data_type, body=search_body)
    res["search_data"]=data
    return res

def searchAllData(data, match_model, sort):
    search_body={
        "size":100,
        "query": {
            match_model: {
                "text":data,
            }
        },
        "sort": [
        {
            sort_map[sort]: {
            "order": "desc"
            }
        }],
        # "sort":{"date":{"order","desc"}},
        "highlight" : {
            "pre_tags" : ['<strong class="w3-text-green">'],
            "post_tags" : ["</strong>"],
            "fields" : {
                "text":{}
            }
        }
    }
    res = es.search(body=search_body)
    res["search_data"]=data
    return res

def getcbnweekData():
    search_body={
        "size":1,
        "query": {
            "match_all": {}
        }
    }
    res = es.search(body=search_body, index='article_cbnweek_index', doc_type='cbnweekly')

    total = res['hits']['total']
    search_body={
        "size":total,
        "query": {
            "match_all": {}
        },
        "sort":[
        {
            "article_date": {
            "order": "desc"
            }
        }]
    }
    res = es.search(body=search_body, index='article_cbnweek_index', doc_type='cbnweekly')
    data = res['hits']['hits']
    magazines=[]
    magazines_shadow=[]
    for i in data:
        if i['_source']['magazine_no'] not in magazines_shadow:
            magazine={}
            magazine['magazine_title']=i['_source']['magazine_title']
            magazine['magazine_page_url']=i['_source']['magazine_page_url']
            magazine['magazine_no']=i['_source']['magazine_no']
            magazine['magazine_date']=str(arrow.get(i['_source']['magazine_date']).format('YYYY/MM/DD'))
            magazine['magazine_url']=i['_source']['magazine_url']
            magazines.append(magazine)
            magazines_shadow.append(i['_source']['magazine_no'])
    return(magazines)

def getArticle(_index, _type, _id):
    search_body={
        "query": {
            "match_phrase": {
                "_id":_id
            }
        }
    }
    res = es.search(body=search_body, index=_index, doc_type=_type)
    return res

def searchIDList(id):
    # should_body = []
    # for id in id_list:
    #     sb={"match_phrase":{"_id":id[0]}}
    #     should_body.append(sb)
    # should_body=str(should_body).replace("'",'"')
    search_body={
        "query":{
            "match_phrase":{
                "_id":id
            }
        }
    }
    res = es.search(body=search_body)
    return res['hits']['hits'][0]


def gensimSearch(data, index, sim_type='lsi', sort='score'):
    raw_data=sim[index].article_find_similarity(article=data)
    res={}
    search_data=data
    # 防止搜索字符安太长撑爆页眉
    if len(search_data) >= 20:
        search_data=data[:20]+'...'
    res["search_data"]=search_data
    res['hits']={}
    res['hits']['total']=len(raw_data)
    res['hits']['hits']=[]
    for i in raw_data:
        append_data = searchIDList(i[0])
        append_data['_score'] = i[1]
        res['hits']['hits'].append(append_data)
    # res_datatype={
    #     'search_data':'***********',
    #     'hits':{
    #         'total':789,
    #         'hits':[
    #             {
    #                 '_index':'***',
    #                 '_source':{
    #                      XXXXX
    #                  }
    #             }
    #         ]
    #     }
    # }
    return res
    

def notCode(html):
    data = html.replace('<code>','<div>').replace('</code>','</div>')
    data = data.replace('<pre>','').replace('</pre>','')
    return data