from elasticsearch import Elasticsearch
es = Elasticsearch()

r = es.search(index="cbn_week_index")

def searchData(data):
    counter = 0;
    search_body={
        "size":20,
        "query": {
            "match_phrase": {
                "article_date":data
            }
        }
    }
    res = es.search(index="cbn_week_index", filter_path=['hits'], body=search_body)
    for hit in res['hits']['hits']:
        counter+=1
        print("\n"+str(counter)+"#####"+str(hit["_source"]["magazine_date"]))
        print("%(user_status)s\n%(magazine_no)s\n%(article_page_url)s" % hit["_source"])
    print("搜索到 %d Hits:" % res['hits']['total'])

searchData("创客教育")