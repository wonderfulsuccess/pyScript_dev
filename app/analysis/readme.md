#nlp.py使用步骤
nlp包含了两个重要功能
1. word3vec
2. lsi文档相似性计算机

对于第一个功能使用非常简单
def train_w2v_model(_index):训练一个index的词向量并且自动保存模型
def train_w2v_model_all():训练es数据库中的所有文档对应的词向量并且自动保存模型

对于第二个功能稍微复杂一些，正常使用步骤如下：
1. def get_docs(index):Get all of the article of a index
2. def create_text(docs,index):create texts list base on a docs and index, the main purpose of index is to give a name to the texts list pickle will be save
3. def create_corpus(texts_pickle):texts_pickle is the same meaning with index we use index as the name of all kinds of mode include:texts pickle/coupus/dictionary/tfidf/similarity
4. def create_topic_model(cor, topics=10): topics quantity do not have any relationship with create_similarity_model num quantity. this function is used to creat lsi topic model based on unsuperised ML fro topics analysis and similarity mode
5. def create_similarity_model(mod, num=10):create a similarity model for a lis model
6. def article_find_similarity(index, article):find the similarity articles form index for artice/sentience/question/bow...
7. class Simlarity():FOR app using