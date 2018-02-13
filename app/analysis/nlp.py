# encoding=utf-8
from __future__ import print_function, unicode_literals
import jieba
from collections import Counter
from bosonnlp import BosonNLP
from elasticsearch import Elasticsearch
import gensim
from gensim import corpora, models, similarities
import pickle

# 调用玻森NLP接口
bsnlp = BosonNLP('KIFQBZJd.21708.q68ctXtgAOQj')
# 卡其jieba并行分词 速度似乎没变化 :(
jieba.enable_parallel(4)
DICT_PATH = "/Users/claire/Elasticsearch/pyScript_dev/app/analysis/"
DICT = DICT_PATH+'mydict.txt'
# jieba.load_userdict('mydict.txt')

TRAINED_MODEL_FOLDER = './analysis/trained_model/'
STOP_WORDS_PATH = "./analysis/stopwords.txt"

jieba.load_userdict(DICT)

def segment(text):
    stop_words=[]
    # 得到分词原始list
    seg_list = list(jieba.cut((text), cut_all=True))

    # 加载停用词，转化为一个list一个词为一个项目
    with open(STOP_WORDS_PATH) as f:
        read = f.read()
        stop_words = read.splitlines()

    # 将单个文档分词成为一个list，文档集合和文档list的集合
    seg=[]
    for i in seg_list:
        if i=='':
                continue
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
        segs=jieba.cut(i['_source'][article_text], cut_all=True)
        for seg in segs:
            if seg=='':
                continue
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
    w2v_model.save(TRAINED_MODEL_FOLDER+str(_index)+'_w2v_model')

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
        
        segs=jieba.cut(i['_source'][article_text],cut_all=True)
        
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

def get_docs(index):
    index = 'article_'+index+'_index'
    es = Elasticsearch()
    texts=[]
    stop_words=[]
    search_body={
        "query": {
            "match_all": {}
        }
    }

    # 第一查询获取文档总数
    res = es.search(index=index,body=search_body)
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
    res = es.search(index=index,body=search_body)
    docs = res['hits']['hits']
    return docs


def create_text(docs,index):
    index = 'article_'+index+'_index'
    # es = Elasticsearch()
    texts=[]
    # stop_words=[]
    # search_body={
    #     "query": {
    #         "match_all": {}
    #     }
    # }

    # # 第一查询获取文档总数
    # res = es.search(index=index,body=search_body)
    # total = int(res['hits']['total'])
    # print(total)

    # search_body={
    #     "size":total,
    #     "from":0,
    #     "query": {
    #         "match_all": {}
    #     }
    # }
    # # 需要先修改ES setting max_result_window 参数 其默认为10000
    # res = es.search(index=index,body=search_body)
    # docs = res['hits']['hits']
    # print(len(docs))

    # 加载停用词，转化为一个list一个词为一个项目
    with open('stopwords.txt') as f:
        read = f.read()
        stop_words = read.splitlines()
    print("正在分词 文章总数:", len(docs))

    cou=0
    for i in docs:
        # 分词list头部添加_id方便查找原始文章
        doc_seg=[i['_id']]
        if i['_source']=={}:
            continue
        
        article_text = "text"
        if i['_type']=="cbnweekly":
            article_text = "article_text"
        
        segs=jieba.cut(i['_source'][article_text],cut_all=True)
        
        for seg in segs:
            if seg=='':
                continue
            if seg not in stop_words:
                doc_seg.append(seg)
        texts.append(doc_seg)
        cou+=1
        print(cou, i['_id'])

    pcikle_name = TRAINED_MODEL_FOLDER+index.split('_')[1]+'_texts'+'.pickle'
    # save texts[]
    with open(pcikle_name, 'wb') as handle:
        pickle.dump(texts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # load pickle
    with open(pcikle_name, 'rb') as handle:
        texts = pickle.load(handle)
        print(len(texts))


def create_corpus(texts_pickle):
    texts=[]
    with open(TRAINED_MODEL_FOLDER+texts_pickle+'_texts'+'.pickle', 'rb') as handle:
        texts = pickle.load(handle)
        print(len(texts))
    
    model_name = TRAINED_MODEL_FOLDER+texts_pickle

    print('生成词典',model_name+'.dict')
    dictionary = corpora.Dictionary(texts)
    print('保存词典',model_name+'.dict')
    dictionary.save(model_name+'.dict')
    print("词典总词数为:", len(dictionary))
    
    print('生成文档 corpus',model_name+'.mm')
    corpus = [dictionary.doc2bow(text) for text in texts]
    print('保存 corpus',model_name+'.mm')
    corpora.MmCorpus.serialize(model_name+'.mm', corpus)
    

def create_topic_model(cor, topics=10):
    model_name = TRAINED_MODEL_FOLDER+cor
    corpus = corpora.MmCorpus(model_name+'.mm')
    dictionary = corpora.Dictionary.load(model_name+'.dict')
    print('生成tfidf模型')
    tfidf_model = models.TfidfModel(corpus)
    tfidf_model.save(model_name+'.tfidf')

    print('生成corpus_tfidf')
    corpus_tfidf = tfidf_model[corpus]

    ## LSI模型 **************************************************
    print('生成转化为lsi模型', topics)
    lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=topics)
    print('Save lsi_model...')
    lsi_model.save(model_name+'_model.lsi') # same for tfidf, lda, ...
    corpus_lsi = lsi_model[corpus_tfidf]
    # lsi_model = models.LsiModel.load('lsi_model.lsi')

    ## LDA模型 **************************************************
    # print('生成转化为lda模型', topics)
    # lda_model = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=topics)
    # lda_model.save(model_name+'_model.lda')
    # lda_model.show_topics(topics)


def use_model():
    lda_model = models.LdaModel.load('./trained_model/duozhiwang_model.lda')
    for t in lda_model.show_topics(20):
        print(t)


def create_similarity_model(mod, num=10):
    mod = TRAINED_MODEL_FOLDER+mod
    # load corpus model
    corpus = corpora.MmCorpus(mod+'.mm')
    # load lsi topic model
    lsi_model = models.LsiModel.load(mod+'_model.lsi')
    # load tfidf model
    tfidf_model = models.TfidfModel.load(mod+'.tfidf')   

    # 计算corpus
    corpus_tfidf = tfidf_model[corpus]
    corpus_lsi = lsi_model[corpus_tfidf]
    print('生成similarity模型...')
    similarity_lsi=similarities.Similarity(mod+'_Similarity-LSI-index', corpus_lsi, num_features=400,num_best=num)
    # save similarity model
    similarity_lsi.save(mod+'_model_lsi.simi')

def article_find_similarity(index, article):
    # 相似性计算方法有多重 比如基于 Similarity-tfidf-index和Similarity-LSI-index
    # 加载模型
    index = TRAINED_MODEL_FOLDER+index
    print(index)
    dictionary = corpora.Dictionary.load(index+'.dict')
    lsi_model = models.LsiModel.load(index+'_model.lsi')
    tfidf_model = models.TfidfModel.load(index+'.tfidf')
    similarity_lsi=similarities.Similarity.load(index+'_model_lsi.simi')
    texts = []
    with open(index+'_texts'+'.pickle', 'rb') as handle:
        texts = pickle.load(handle)
    # 1.分词
    article_seg = segment(article)
    print(article_seg)
    # 2.根据生成的词典转化为bow向量
    print('词向量转化')
    article_corpus = dictionary.doc2bow(article_seg)
    # 3.计算article的词tfidf
    print('计算tfidf')
    article_corpus_tfidf = tfidf_model[article_corpus]
    # 4.计算LSI主题模型
    print('寻找相似文章')
    article_corpus_lsi = lsi_model[article_corpus_tfidf]

    # print("-"*40)
    sims = similarity_lsi[article_corpus_lsi]
    sim_data=[]
    for sim in sims:
        # print(sim[1])
        t=[]
        t.append(texts[sim[0]][0])
        t.append(sim[1])
        sim_data.append(t)
    # print(sim_data)
    return sim_data


class Simlarity():
    """docstring for Simlarity"""
    def __init__(self, index):
        self.index = TRAINED_MODEL_FOLDER+index
        self.dictionary = corpora.Dictionary.load(self.index+'.dict')
        self.lsi_model = models.LsiModel.load(self.index+'_model.lsi')
        self.tfidf_model = models.TfidfModel.load(self.index+'.tfidf')
        self.similarity_lsi=similarities.Similarity.load(self.index+'_model_lsi.simi')

    def article_find_similarity(self, article):
        texts = []
        with open(self.index+'_texts'+'.pickle', 'rb') as handle:
            texts = pickle.load(handle)
        # 1.分词
        article_seg = segment(article)
        print(article_seg)
        # 2.根据生成的词典转化为bow向量
        print('词向量转化')
        article_corpus = self.dictionary.doc2bow(article_seg)
        # 3.计算article的词tfidf
        print('计算tfidf')
        article_corpus_tfidf = self.tfidf_model[article_corpus]
        # 4.计算LSI主题模型
        print('寻找相似文章')
        article_corpus_lsi = self.lsi_model[article_corpus_tfidf]

        print("-"*40)
        sims = self.similarity_lsi[article_corpus_lsi]
        sim_data=[]
        print(sim_data)
        for sim in sims:
            # print(sim[1])
            t=[]
            t.append(texts[sim[0]][0])
            t.append(sim[1])
            sim_data.append(t)
        return sim_data


if __name__=="__main__":
    TRAINED_MODEL_FOLDER = './trained_model/'
    STOP_WORDS_PATH = "./stopwords.txt"
    # print('开始训练词向量模型 已有的模型即将被覆盖...')
    # train_w2v_model_all()

    # duozhiwang_docs = get_docs('duozhiwang')
    # jingmeiti_docs = get_docs('jingmeiti')
    # all_docs = duozhiwang_docs+jingmeiti_docs
    # print(len(duozhiwang_docs), len(jingmeiti_docs), len(all_docs))
    # create_text(docs=all_docs, index='all')
    create_corpus('all')
    create_topic_model('all',50)
    # use_model()
    create_similarity_model('all',30)
    print(article_find_similarity('all',"创客教育的未来在哪儿？"))
    '''
    '''




        