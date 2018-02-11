from elasticsearch import Elasticsearch

es = Elasticsearch()

def setCNBAnalyzer():
    the_mapping = {
        "properties": {
            "magazine_title": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "article_title": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "article_note": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "article_author": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "article_text": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "article_date": {
                "type": "date"
            },
            "magazine_date": {
                "type": "date"
            }
        }
    }
    es.index(index="article_cbnweekly_index", doc_type='cbnweekly',body={})
    es.indices.put_mapping(index="article_cbnweekly_index", doc_type='cbnweekly', body=the_mapping)
    print("Mapping cbnweekly done \n ik_smart...")


def setArticleAnalyzer():
    name=input("文章索引名称:\n")
    the_mapping = {
        "properties": {
            "website": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "title": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "summary": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "category": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "author": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "text": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "other": {
                "type": "text",
                "analyzer": "ik_smart",
                "search_analyzer": "ik_smart"
            },
            "date": {
                "type": "date"
            },
            "magazine_date": {
                "type": "date"
            },
            "crwaler_time":{
                "type": "date"
            }

        }
    }
    es.index(index='article_'+name+'_index', doc_type=name,body={})
    es.indices.put_mapping(index='article_'+name+'_index', doc_type=name, body=the_mapping)
    print("Mapping{name}done \n ik_smart...")
    
if __name__=="__main__":
    ins = input("选择mapping对象 1:cbnweek 2:Article\n")
    if ins=='1':
        print('即将mapping cbnweek')
        setCNBAnalyzer()
    if ins=='2':
        print('即将mapping Article')
        setArticleAnalyzer()
