import os
from elasticsearch import Elasticsearch
from settings import WEB_LIST
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

def searchCbnWeekData(data, match_model,sort):

    search_body={
        "size":100,
        "query": {
             "bool": {
                "should": [
                    { match_model: { "magazine_url": data}},
                    { match_model: { "article_text": data}}]
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

def notCode(html):
    data = html.replace('<code>','<div>').replace('</code>','</div>')
    data = data.replace('<pre>','').replace('</pre>','')
    return data