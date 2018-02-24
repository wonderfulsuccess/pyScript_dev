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

# file_handler = logging.FileHandler("page_json.log")
# lg.addHandler(file_handler)

class GuandianSpider(scrapy.Spider):
    name = 'guandian'
    data_destination = 'ES'
    counter=0
    
    def start_requests(self):
        # 指定url
        for page in range(0,page_deepth):
            yield scrapy.Request(url='http://www.guandian.cn/api.php?op=getindex2016_content&modelid=1&type=query-scroll&a='+str(page), callback=self.parse)

    def parse(self, response):
        # 获取一个page的所有文章链接

        data = response.body_as_unicode()
        # 去除首尾的()
        Data = data[1:-1]
        lg.critical(Data)

        if 'html><head>' in Data:
            return
        try:
            Data = json.loads(Data)
        except Exception as e:
            lg.critical(str(data))
            pass
        
        article_urls = []
        summarys = []
        date = []
        title = []
        for i in Data:
            article_urls.append('http://www.guandian.cn'+i['mainURL'])
            summarys.append(i['abstract'])
            date.append(i['timer'])
            title.append(i['titleText'])
        print(self.counter,'-'*40,len(article_urls))
        for u in article_urls:
            self.counter += 1
            # lg.critical(str(self.counter)+'----'+u)
            meta_data = {
                'summary':summarys[article_urls.index(u)],
                'date':date[article_urls.index(u)],
                'title':title[article_urls.index(u)],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)

    def parse_article(self, response):
        if 'html><head>' in response.body_as_unicode():
            return

        item = ArticleItem()

        # item["the_id"] it is a counter will be asigned in pipelines
        item["website"]      = '观点房产'
        item["title"]        = remove_csv_noise(response.meta['title'])
        item["link"]         = response.url
        item["summary"]      = remove_csv_noise(response.meta['summary'])
        item["date"]         = remove_csv_noise(response.meta['date'])
        item["category"]     = '资讯'
        item["author"]       = remove_csv_noise(response.xpath('//div[@class="con_l_info_l"]/a/text()').extract()[-1])
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = remove_csv_noise(html2text.html2text(response.xpath('//div[@class="con_l_inner"]').extract()[0]))
        # item["crwaler_time"] = 
        item["other"]        = '观点房产 资讯'

        yield item