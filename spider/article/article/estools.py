from elasticsearch import Elasticsearch
import arrow

es = Elasticsearch()

def indexArticleDoc(index, item):
    try:
        date = str(arrow.get(item['date'],'YYYY-M-D h:m:s')) #多知网时间转化
    except Exception as e:
        # date = str(arrow.get(item['date'],'YYYY-M-D')) #鲸媒体时间转化
        t = str(item['date'])
        if t=='' :
            return
        if '：' in t:
            t=t.split('：')    
            date = str(arrow.get(t[-1],'YYYY-M-D')) #胡润百富
        else:
            if '-' in t:
                date = str(arrow.get(t,'YYYY-M-D')) #鲸媒体时间转化
            else:
                date = str(arrow.get(item['crwaler_time']))
    doc = {
        'csv_name':'es_pipeline',
        'the_id':str(item['the_id']),
        'website':str(item['website']),
        'title':str(item['title']),
        'link':str(item['link']),
        'summary':str(item['summary']),
        'category':str(item['category']),
        'date':date,
        'author':str(item['author']),
        'text':str(item['text']),
        'crwaler_time':str(arrow.get(item['crwaler_time'])),
        'other':str(item['other']),
        'timestamp': str(arrow.now()),
    }
    res = es.index(index='article_'+index+'_index', doc_type=index, id=item['link'], body=doc)