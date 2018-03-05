# encoding=utf-8
from __future__ import print_function, unicode_literals
import jieba
from collections import Counter
from bosonnlp import BosonNLP
from elasticsearch import Elasticsearch
import gensim
from gensim import corpora, models, similarities
import pickle
import re
from os import listdir
from os import system
from os.path import isfile, join
from math import ceil
import arrow
import gc

# logger
import coloredlogs,logging
lg = logging.getLogger(__name__)
coloredlogs.install(level='error')

# 调用玻森NLP接口
# bsnlp = BosonNLP('KIFQBZJd.21708.q68ctXtgAOQj')
# 卡其jieba并行分词 速度似乎没变化 :(
jieba.enable_parallel(4)
DICT_PATH = "/Users/claire/Elasticsearch/pyScript_dev/app/analysis/"
DICT = DICT_PATH+'mydict.txt'
# jieba.load_userdict('mydict.txt')

TRAINED_MODEL_FOLDER = './analysis/trained_model/'
STOP_WORDS_PATH = "./analysis/stopwords.txt"

jieba.load_userdict(DICT)
jieba.enable_parallel()

# 对doc进行分词之前 过滤出中文
p_zh = "[\u4e00-\u9fa5]"
pattern_zh = re.compile(p_zh)

def segment(text):
    '''
    对一段text进行分词
    input：
    text:待分词的原始文章

    return:
    seg:分词后的text list
    '''

    source_text = text
    source_text = ''.join(pattern_zh.findall(source_text))

    stop_words=[]
    # 得到分词原始list
    seg_list = list(jieba.cut((source_text), cut_all=False))

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
    '''
    词频统计
    seg:text分词后的list
    size:需要统计的出现频率最高的数量
    '''
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
    '''
    训练一个特定ES数据库中的index类型数据
    input:
    _index:ES index名称

    output:
    保存训练好的词向量模型
    '''
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

        source_text = i['_source'][article_text]
        source_text = ''.join(pattern_zh.findall(source_text))

        segs=jieba.cut(source_text, cut_all=False)
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
    '''
    将ES中所有文章训练为一个词向量模型
    Output:
    训练结果保存为一个模型
    '''
    # 寻找 './trained_model/'目录下的所有*texts.pickle文件 组合成为一整个texts
    texts=[]
    files_in_trained_model = [f for f in listdir(TRAINED_MODEL_FOLDER) if isfile(join(TRAINED_MODEL_FOLDER, f))]
    for file_name in files_in_trained_model:
        # 由于对每个单独的index文档都会有一个 texts pickle 去除那些带有all合并的数据
        if ('texts.pickle' in file_name) and (file_name.split('_')[0] in ['cbnweek','hurun','duozhiwang','jingmeiti','fudaoquan','souhujiaodian','guandian']):
            print(file_name)
            with open(TRAINED_MODEL_FOLDER+file_name, 'rb') as handle:
                texts += pickle.load(handle)

    # 去除texts中每个text的第一个元素：每篇文章的_id，防止相似词被干扰
    print('去除texts中每个text的第一个元素')
    none_id_texts=[]
    for text in texts:
        none_id_texts.append(text[1:])

    print('无_id texts加工完毕', len(none_id_texts))

    print("正在训练词向量 文章总数:", len(none_id_texts))
    w2v_model=gensim.models.Word2Vec(none_id_texts,size=100,window=5,min_count=1)
    # for i in range(0,len(dictionary)):
    #     print(dictionary[i])
    #     print(model[dictionary[i]])
    # 小测试
    print(w2v_model.similar_by_word('教育',topn=5))
    # 持久化模型
    w2v_model.save('./trained_model/all_w2v_model')


class W2VSimilarity():
    '''
    计算 相似词工具对象 
    '''
    def __init__(self):
        self.model = gensim.models.Word2Vec.load('./analysis/trained_model/all_w2v_model')

    def simi_words(self,word):
        # lg.info('计算相似词')
        return self.model.similar_by_word(str(word),topn=5)

    def test(self):
        print(self.model.similar_by_word('学习',topn=5))

def get_docs(index):
    '''
    根据index获取ES中的所有文档
    input:
    index:ES数据index

    output:
    docs该index的所有文档
    '''
    index = 'article_'+index+'_index'
    es = Elasticsearch(timeout=120)
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
    docs=[]
    # 如果文章总数大于50000则分批从es中提取文档 每批50000
    if total<=50000:
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
    
    else:
        this_total = 50000
        get_loop = ceil(total/50000)
        for i in range(get_loop):
            if i==get_loop-1:
                this_total=total-(50000*i)
            search_body={
                "size":this_total,
                "from":50000*i,
                "query": {
                "match_all": {}
                }
            }
            docs += es.search(index=index,body=search_body)['hits']['hits']

    print('-'*80)
    print(len(docs))
    return docs


def create_text(docs,index):
    '''
    根据一个index的文档，分词产生texts并保存
    input:
    docs:get_docs的返回值
    index:主要用于是定保存输出数据的文件(模型)名
    
    output:
    保存texts list pickle模型
    '''

    index = 'article_'+index+'_index'
    texts=[]

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
        
        source_text = i['_source'][article_text]
        source_text = ''.join(pattern_zh.findall(source_text))

        segs=jieba.cut(source_text,cut_all=False)
        
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

    pcikle_index_name = TRAINED_MODEL_FOLDER+index.split('_')[1]+'_texts_index'+'.pickle'
    # save texts_index[] 存储texts中每个list的第一个元素 也就是_id 这样能加快寻找相似文章的模块加载速度
    texts_index=[]
    for text in texts:
        texts_index.append(text[:1])

    with open(pcikle_index_name, 'wb') as handle:
        pickle.dump(texts_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # load pickle for a test
    # with open(pcikle_name, 'rb') as handle:
        # texts = pickle.load(handle)
        # print(len(texts))

def combine_text(text_list,text_name):
    '''
    事实证明分词是一个很耗时间的工作，因此决定保存每一个分词过的index
    遇到需要合并多个index text则直接从保存的text pickle中读取拼接再保存即可
    '''
    text_list_pickle=[]
    texts=[]
    for tl in text_list:
        text_list_pickle.append(tl+'_texts.pickle')

    for tlp in text_list_pickle:
        with open(TRAINED_MODEL_FOLDER+tlp, 'rb') as handle:
            texts += pickle.load(handle)
    print(str(text_list),'连接之后的texts长度为:' ,len(texts))
    lg.info('保存合并的texts中...')

    with open(TRAINED_MODEL_FOLDER+text_name+'_texts.pickle', 'wb') as handle:
        pickle.dump(texts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    pcikle_index_name = TRAINED_MODEL_FOLDER+text_name+'_texts_index'+'.pickle'
    # save texts_index[] 存储texts中每个list的第一个元素 也就是_id 这样能加快寻找相似文章的模块加载速度
    texts_index=[]
    for text in texts:
        texts_index.append(text[:1])

    with open(pcikle_index_name, 'wb') as handle:
        pickle.dump(texts_index, handle, protocol=pickle.HIGHEST_PROTOCOL)

    lg.info('保存合并的texts成功:'+text_name+'_texts.pickle')

def create_corpus(texts_pickle):
    texts=[]
    print('打开pickle',texts_pickle)    
    with open(TRAINED_MODEL_FOLDER+texts_pickle+'_texts'+'.pickle', 'rb') as handle:
        texts = pickle.load(handle)
        print(len(texts))
    
    model_name = TRAINED_MODEL_FOLDER+texts_pickle

    print('生成词典',model_name+'.dict')
    dictionary = corpora.Dictionary(texts)
    print('保存词典 ',model_name+'.dict')
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
    lg.info(article_seg)
    # 2.根据生成的词典转化为bow向量
    lg.info('词向量转化')
    article_corpus = dictionary.doc2bow(article_seg)
    # 3.计算article的词tfidf
    lg.info('计算tfidf')
    article_corpus_tfidf = tfidf_model[article_corpus]
    # 4.计算LSI主题模型
    lg.info('寻找相似文章')
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
        print('-'*20, str(arrow.now()),'-'*20)
        self.index = TRAINED_MODEL_FOLDER+index
        self.dictionary = corpora.Dictionary.load(self.index+'.dict')
        self.lsi_model = models.LsiModel.load(self.index+'_model.lsi')
        self.tfidf_model = models.TfidfModel.load(self.index+'.tfidf')
        self.similarity_lsi=similarities.Similarity.load(self.index+'_model_lsi.simi')

        self.texts_index = []
        # 该加载过程有些耗费时间 决定将其放在初始化构造函数之中
        lg.info('准备加载texts index pickle'+self.index)
        with open(self.index+'_texts_index'+'.pickle', 'rb') as handle:
            self.texts_index = pickle.load(handle)
        lg.info('加载texts index pickle 完成'+self.index)
    def article_find_similarity(self, article):
        # 1.分词
        article_seg = segment(article)
        # 2.根据生成的词典转化为bow向量
        lg.info('词向量转化')
        article_corpus = self.dictionary.doc2bow(article_seg)
        # 3.计算article的词tfidf
        lg.info('计算tfidf')
        article_corpus_tfidf = self.tfidf_model[article_corpus]
        # 4.计算LSI主题模型
        lg.info('寻找相似文章')
        article_corpus_lsi = self.lsi_model[article_corpus_tfidf]
        sims = self.similarity_lsi[article_corpus_lsi]
        sim_data=[]
        print(sim_data)
        for sim in sims:
            # print(sim[1])
            t=[]
            t.append(self.texts_index[sim[0]][0])
            t.append(sim[1])
            sim_data.append(t)
        return sim_data


def create_index_models(index,ts=10,ss=30):
    '''
    创建单个网站的主题模型和相似性模型
    '''
    docs_name = index+'_docs'
    docs_name = get_docs(index)
    create_text(docs=docs_name, index=index)
    del(docs_name)
    gc.collect()
    create_corpus(index)  
    create_topic_model(index,ts)
    create_similarity_model(index,ss)


def create_industry_models(industry,ts=10,ss=60):
    '''
    创建一个行业的所有主题模型和相似性模型
    '''
    combine_text(text_list=industry['index'],text_name=industry['name'])
    create_corpus(industry['name'])
    create_topic_model(industry['name'],10)
    create_similarity_model(industry['name'],30)

def update_all_models():
    # delete_sure = input('你确定要删除所有模型吗？')
    # if delete_sure != 'yes':
    #     return
    # lg.warning('删除所有训练模型...')
    # system('rm -f ./trained_model/*')
    # system('rm -f ../trained_model/*')
    # lg.warning('删除训练模型完成')
    
    # website=['cbnweek','hurun','duozhiwang','jingmeiti','fudaoquan','jiemodui','souhujiaodian','guandian']
    website=['duozhiwang','jingmeiti','fudaoquan','jiemodui']
    industry={
        'edu':{
            'name':'edu',
            'index':['duozhiwang','jingmeiti','fudaoquan','jiemodui']
        },
        'realestate':{
            'name':'realestate',
            'index':['souhujiaodian','guandian']
        }
    }
    # 单个网站模型
    for index in website:
        create_index_models(index)
    # create_index_models
    # 行业模型
    create_industry_models(industry['edu'])
    # create_industry_models(industry['realestate'])

    # 训练所有预料的词向量 之所以放在alledu之前是为了避免排除其对应的texts pickle
    train_w2v_model_all()

    lg.info("copy similarity model to app/trained_model/")
    system('cp ./trained_model/*-LSI-index.* ../trained_model/')

def create_text_index(texts_pickle):
    '''
    此前有一些texts pickle文档没有生成 texts index pickle 通过该函数生成并保存
    此函数的功能已经在生成texts时已经添加 顾以后该函数基本上用不到
    '''
    texts=[]
    lg.info('打开pickle'+texts_pickle)
    with open(TRAINED_MODEL_FOLDER+texts_pickle+'_texts'+'.pickle', 'rb') as handle:
        texts = pickle.load(handle)
        print(len(texts))

    lg.info('打开pickle完成'+texts_pickle)
    pcikle_index_name = TRAINED_MODEL_FOLDER+texts_pickle+'_texts_index'+'.pickle'

    lg.info('生成 texts index'+texts_pickle)
    texts_index=[]
    for text in texts:
        texts_index.append(text[:1])
    lg.info(len(texts_index))
    with open(pcikle_index_name, 'wb') as handle:
        pickle.dump(texts_index, handle, protocol=pickle.HIGHEST_PROTOCOL)
    lg.info('保存 texts index'+texts_pickle)

if __name__=="__main__":
    TRAINED_MODEL_FOLDER = './trained_model/'
    STOP_WORDS_PATH = "./stopwords.txt"

    update_all_models()
