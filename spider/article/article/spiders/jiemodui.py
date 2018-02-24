# -*- coding: utf-8 -*-

import re
import scrapy
from article.items import ArticleItem
import html2text
from article.tools import remove_csv_noise
import json

from article.settings import UPDATE_DEEPTH as page_deepth
import coloredlogs,logging,sys
lg = logging.getLogger(__name__)
coloredlogs.install(level='critical')

class JiemoduiSpider(scrapy.Spider):
    name = 'jiemodui'
    # 直接存入ES
    data_destination = 'ES'
    def start_requests(self):
        # 指定url
        # page_deepth = input(self.name+'输入更新页码深度...\n')
        # page_deepth = 10
        for page in range(1,int(page_deepth)+1):
            yield scrapy.Request(url='https://www.jiemodui.com/Api/Index/news?p='+str(page), callback=self.parse)

    
    def parse(self, response):
        # 获取一个page的所有文章链接
        data = response.body_as_unicode()
        data = json.loads(data)
        data = data['list']
        # lg.critical(data)
        article_urls = []
        summarys = []
        date = []
        title = []
        author=[]
        category=[]
        for i in data:
            article_urls.append('https://www.jiemodui.com/N/'+str(i['id'])+'.html')
            summarys.append(i['brief'])
            date.append(i['utime'])
            title.append(i['name'])
            author.append(i['writer'])
            category.append(i['topic'])

        for u in article_urls:
            meta_data = {
                'summary':summarys[article_urls.index(u)],
                'date':date[article_urls.index(u)],
                'title':title[article_urls.index(u)],
                'author':author[article_urls.index(u)],
                'category':category[article_urls.index(u)],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)


    def parse_article(self, response):

        item = ArticleItem()

        # item["the_id"]       =
        item["website"]      = "芥末堆"
        item["title"]        = remove_csv_noise(response.meta['title'])
        item["link"]         = response.url
        item["summary"]      = remove_csv_noise(response.meta['summary'])
        item["date"]         = remove_csv_noise(response.meta['date'])
        item["category"]     = remove_csv_noise(response.meta['category'])
        item["author"]       = remove_csv_noise(response.meta['author'])
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = remove_csv_noise(html2text.html2text(response.xpath('//article[@class="content"]').extract()[0]))
        # item["crwaler_time"] = 
        item["other"]        = '教育'

        yield item