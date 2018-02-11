# TODO list
# 1.文章时间转化有点蛋疼 需要修改
# 2.使用csv作为中间数据 csv对数据格式要求太严格 不过这个问题可以扔个爬虫部分解决
from elasticsearch import Elasticsearch
import pandas as pd
from os import listdir
from os.path import isfile, join
import arrow


es = Elasticsearch()

def indexData(mode='i'):
    "索引data目录下的所有csv文档到ES i:insert new data u:update exist data"
    dir_name='./data/'
    # list data 目录下所有的csv文档
    csv_files = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]
    for csv_file in csv_files:
        name=csv_file.split('_')[0]
        search_body={
            "size":1,
            "query": {
                "match_phrase": {
                    "csv_name":csv_file
                }
            }
        }
        res = es.search(body=search_body)
        # 为pandas增加表头 for_pd
        f = open(dir_name+csv_file,'r')
        f.seek(0)
        header = f.readline()
        body = f.read()
        f.close()
        # 如果csv文档已经被撸过 那么就跳过吧
        if 'for_pd' not in header:
            header = header.replace('\n','')
            header = header+',for_pd\n'
            f = open(dir_name+csv_file,'w')
            f.seek(0)
            f.write(header+body)
            f.close()
        # 如果数据库中找不到这份csv文件 意味着 csv文档是爬虫刚刚拿下来的 应该index
        if res['hits']['total']==0:
            if name=='cbnweekly':
                inserCBNWeeklyData(dir_name+csv_file,name)
            else:
                insertArticleData(dir_name+csv_file,name)
        else:
            if mode=='i':
                print(csv_file,'\t','文档已经存在....')
            elif mode=='u':
                if name=='cbnweek':
                    inserCBNWeeklyData(dir_name+csv_file,name)
                else:
                    insertArticleData(dir_name+csv_file,name)
            else:
                print('未知命令...')            



def inserCBNWeeklyData(csv_file,name):
    df = pd.read_csv(csv_file)
    data_length = len(df.index)
    print('正在index:',csv_file)
    for data in range(0,data_length):

        try:
            article_date=str(arrow.get(df.loc[data,'article_date'],'YYYY年M月D日'))
        except Exception as e:
            article_date=arrow.get(df.loc[data,'article_date'],'M月D日')
            article_date=article_date.replace(year=arrow.now().year)
            article_date=str(article_date)

        print(csv_file,data)
        doc = {
            'csv_name':csv_file,
            'user_status':str(df.loc[data,'user_status']),
            'magazine_title':str(df.loc[data,'magazine_title']),
            'magazine_url':str(df.loc[data,'magazine_url']),
            'magazine_page_url':str(df.loc[data,'magazine_page_url']),
            'magazine_no':str(df.loc[data,'magazine_no']),
            'magazine_date':str(arrow.get(df.loc[data,'magazine_date'],'YYYY.M.D')),
            'article_title':str(df.loc[data,'article_title']),
            'article_page_url':str(df.loc[data,'article_page_url']),
            'article_url':str(df.loc[data,'article_url']),
            'article_note':str(df.loc[data,'article_note']),
            'article_author':str(df.loc[data,'article_author']),
            'article_date':article_date,
            'article_text':str(df.loc[data,'article_text']),
            'timestamp': str(arrow.now()),
        }
        res = es.index(index='article_'+name+'_index', doc_type='cbnweekly', id=df.loc[data,'article_url'], body=doc)

def insertArticleData(csv_file, name):
    df = pd.read_csv(csv_file)
    data_length = len(df.index)
    print('正在index:',csv_file)
    for data in range(0,data_length):
        try:
            date = str(arrow.get(df.loc[data,'date'],'YYYY-M-D h:m:s')) #多知网时间转化
        except Exception as e:
            # date = str(arrow.get(df.loc[data,'date'],'YYYY-M-D')) #鲸媒体时间转化
            t = str(df.loc[data,'date'])
            if(t==''):
                continue
            if '：' in t:
                t=t.split('：')    
                date = str(arrow.get(t[-1],'YYYY-M-D')) #胡润百富
            else:
                if '-' in t:
                    date = str(arrow.get(t,'YYYY-M-D')) #鲸媒体时间转化
                else:
                    date = str(arrow.get(df.loc[data,'crwaler_time']))
        print(csv_file,data) 
        doc = {
            'csv_name':csv_file,
            'the_id':str(df.loc[data,'the_id']),
            'website':str(df.loc[data,'website']),
            'title':str(df.loc[data,'title']),
            'link':str(df.loc[data,'link']),
            'summary':str(df.loc[data,'summary']),
            'category':str(df.loc[data,'category']),
            'date':date,
            'author':str(df.loc[data,'author']),
            'text':str(df.loc[data,'text']),
            'crwaler_time':str(arrow.get(df.loc[data,'crwaler_time'])),
            'other':str(df.loc[data,'other']),
            'timestamp': str(arrow.now()),
        }
        res = es.index(index='article_'+name+'_index', doc_type=name, id=df.loc[data,'link'], body=doc)



def searchData(data):
    counter = 0;
    search_body={
        "size":20,
        "query": {
            "match_phrase": {
                "article_text":data
            }
        }
    }
    res = es.search(index="article_cbnweek_index", filter_path=['hits'], body=search_body)
    for hit in res['hits']['hits']:
        counter+=1
        # print("\n"+str(counter)+"#####"+str(hit["_source"]["magazine_date"]))
        # print("%(article_title)s\n%(magazine_no)s\n%(article_page_url)s" % hit["_source"])
        print("%(article_title)s" % hit["_source"])
    print("搜索到 %d Hits:" % res['hits']['total'])

if __name__=="__main__":
    indexData(input('输入命令...\n'))

















