from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, Markup
from settings import WEB_LIST
from analysis.nlp import segment
from analysis.nlp import words_count
from analysis.nlp import W2VSimilarity
from model import searchCbnWeekData
from model import searchArticleData
from model import searchAllData
from model import getArticle
from model import notCode
from model import getcbnweekData
import markdown2

app = Flask(__name__)
w2v = W2VSimilarity()

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # 获取表单数据
        try:
            search_data = request.form['keywords']
            website = request.form['website']
            match_model = request.form['match_model']
            sort = request.form['sort_model']
        except Exception as e:
            # 搜索数据
            search_data = "教育"
            # 数据文档名称
            website='cbnweek'
            # 匹配模式
            match_model = 'match'
        if(website == 'all'):
            data = searchAllData(search_data,match_model,sort)
            return render_template('list_article.html', res=data)
        if(website == "cbnweek"):
            data = searchCbnWeekData(search_data, match_model,sort)
            return render_template('list_cbnweek.html', res=data)
        if(website in ["duozhiwang","jingmeiti","hurun"]):
            article_index = "article_"+str(website)+"_index"
            data = searchArticleData(data=search_data, index=article_index , data_type=str(website), match_model=match_model,sort=sort)
            return render_template('list_article.html', res=data)
    else:
        return render_template('index.html', data=WEB_LIST)
    

@app.route('/list')
def get_list():
    return render_template('list.html')


@app.route('/article')
def get_article():
    _id = request.args.get('id')
    _index = request.args.get('index')
    _type = request.args.get('type')
    article = getArticle(_index=_index, _type=_type, _id=_id)
    article=article['hits']['hits'][0]['_source']
    simi_words={}

    if _type in ["duozhiwang","jingmeiti","hurun"]:
        article['article_title']=article['title']
        article['article_note']=article['summary']
        article['article_text']=article['text']
        article['article_url']=article['link']
        article['article_date']=article['date']

    # 分词
    seg=segment(article['article_text'])
    # 将markdown转化为html markdown2可能会将连续的四个空格翻译为code 去掉
    article['article_text']=markdown2.markdown(article['article_text'].replace('    ',''))
    # 为方便图片查看直接为其添加一个class属性 当然 正确做法是使用js
    article['article_text']=article['article_text'].replace('<img', '<img class="w3-image w3-round"')

    data=words_count(seg,30)
    # entity=bsnlp.ner(article['article_text'])
    # print(entity)
    for k,v in data.items():
        # 也许词典中没有统计出来的词
        try:
            simi_words[k] = list(w2v.simi_words(k))
        except Exception as e:
            simi_words[k] = list(range(len(data.items())))
        
    return render_template('article.html', article=article, data=data, simi_words=simi_words)


@app.route('/cbnweek', methods=['GET', 'POST'])
def show_cbnweek():
    if request.method == 'GET':
        cbnweek=getcbnweekData()
        return render_template('cbnweek.html', data=cbnweek)

@app.route('/cbnweek_magazine_articles')
def show_magazine_articles():
    magazine_url = request.args.get('url')
    data = searchCbnWeekData(magazine_url, 'match_phrase','date')
    return render_template('list_cbnweek.html', res=data)

