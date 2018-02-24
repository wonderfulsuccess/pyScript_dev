from elasticsearch import Elasticsearch
es = Elasticsearch()

r = es.search(index="article_duozhiwang_index")

def searchData(data):
    counter = 0;
    search_body={
        "size":10,
        "query": {
            "match_phrase": {
                "text":data
            }
        }
    }
    res = es.search(index=['article_duozhiwang_index','article_jingmeiti_index'], body=search_body)
    print("搜索到 %d Hits:" % res['hits']['total'])

searchData("创客")