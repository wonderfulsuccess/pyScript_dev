# encoding=utf-8
from __future__ import print_function, unicode_literals
import jieba
from collections import Counter
from bosonnlp import BosonNLP
from elasticsearch import Elasticsearch
import gensim
from gensim import corpora

# 调用玻森NLP接口
bsnlp = BosonNLP('KIFQBZJd.21708.q68ctXtgAOQj')

def segment(text):
    stop_words=[]
    # 得到分词原始list
    seg_list = list(jieba.cut(text))

    # 加载停用词，转化为一个list一个词为一个项目
    with open('./analysis/stopwords.txt') as f:
        read = f.read()
        stop_words = read.splitlines()

    # 将单个文档分词成为一个list，文档集合和文档list的集合
    seg=[]
    for i in seg_list:
        if i not in stop_words:
            seg.append(i)

    return seg

def words_count(seg, size=10):
    #词频统计
    wf = Counter()  
    for i in seg:
        if i in ['\r', '\n', '\r\n']:
            continue
        wf[i] += 1

    return dict(wf.most_common(size))

# print('常用词频度统计结果')  
# for (k,v) in wf.most_common(10):  
#     print(k,v)  

def train_w2v_model(_index):
    index="article_"+str(_index)+"_index"
    texts=[]
    stop_words=[]

    es = Elasticsearch()
    search_body={
        "size":1,
        "from":0,
        "query": {
            "match_all": {}
        }
    }

    # 第一查询获取文档总数
    res = es.search(index=index, body=search_body)
    total = int(res['hits']['total'])
    print(total)
    search_body={
        "size":total,
        "from":0,
        "query": {
            "match_all": {}
        }
    }
    # 需要先修改ES setting max_result_window 参数 其默认为10000
    res = es.search(index=index, body=search_body)
    docs = res['hits']['hits']
    print(len(docs))

    # 加载停用词，转化为一个list一个词为一个项目
    with open('stopwords.txt') as f:
        read = f.read()
        stop_words = read.splitlines()
    print("正在分词 文章总数:", len(docs))

    article_text = "text"
    if _index=="cbnweekly":
        article_text = "article_text"

    cou=0
    for i in docs:
        doc_seg=[]
        if i['_source']=={}:
            continue
        segs=jieba.cut(i['_source'][article_text])
        for seg in segs:
            if seg not in stop_words:
                doc_seg.append(seg)
        texts.append(doc_seg)
        cou+=1
        print(cou)

    # 生成词典
    # dictionary = corpora.Dictionary(texts)
    # 生成词向量
    print("正在训练词向量 文章总数:", len(docs))
    w2v_model=gensim.models.Word2Vec(texts,size=100,window=5,min_count=1)
    # for i in range(0,len(dictionary)):
    #     print(dictionary[i])
    #     print(model[dictionary[i]])
    # 小测试
    print(w2v_model.similar_by_word('高管',topn=5))
    # 持久化模型
    w2v_model.save('./trained_model/'+str(_index)+'_w2v_model')

    # new_model = gensim.models.Word2Vec.load('./trained_model/cbnweekly_w2v_model')
    # print(new_model.similar_by_word('高管',topn=5))

# train_w2v_model('cbnweekly')

def train_w2v_model_all():
    es = Elasticsearch()
    texts=[]
    stop_words=[]
    search_body={
        "query": {
            "match_all": {}
        }
    }

    # 第一查询获取文档总数
    res = es.search(body=search_body)
    total = int(res['hits']['total'])
    print(total)

    search_body={
        "size":total,
        "from":0,
        "query": {
            "match_all": {}
        }
    }
    # 需要先修改ES setting max_result_window 参数 其默认为10000
    res = es.search(body=search_body)
    docs = res['hits']['hits']
    print(len(docs))

    # 加载停用词，转化为一个list一个词为一个项目
    with open('stopwords.txt') as f:
        read = f.read()
        stop_words = read.splitlines()
    print("正在分词 文章总数:", len(docs))

    cou=0
    for i in docs:
        doc_seg=[]
        if i['_source']=={}:
            continue
        
        article_text = "text"
        if i['_type']=="cbnweekly":
            article_text = "article_text"
        
        segs=jieba.cut(i['_source'][article_text])
        
        for seg in segs:
            if seg not in stop_words:
                doc_seg.append(seg)
        texts.append(doc_seg)
        cou+=1
        print(cou, i['_id'])

    # 生成词典
    # dictionary = corpora.Dictionary(texts)
    # 生成词向量
    print("正在训练词向量 文章总数:", len(docs))
    w2v_model=gensim.models.Word2Vec(texts,size=100,window=5,min_count=1)
    # for i in range(0,len(dictionary)):
    #     print(dictionary[i])
    #     print(model[dictionary[i]])
    # 小测试
    print(w2v_model.similar_by_word('教育',topn=5))
    # 持久化模型
    w2v_model.save('./trained_model/all_w2v_model')



class W2VSimilarity():
    def __init__(self):
        self.model = gensim.models.Word2Vec.load('./analysis/trained_model/all_w2v_model')

    def simi_words(self,word):
        return self.model.similar_by_word(str(word),topn=5)

    def test(self):
        print(self.model.similar_by_word('学习',topn=5))


















        