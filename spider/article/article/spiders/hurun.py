# -*- coding: utf-8 -*-

import re
import scrapy
from article.items import ArticleItem
import html2text

# item["he_id"]
# item["ebsite"]
# item["itle"]
# item["ink"]
# item["ummary"]
# item["ategory"]
# item["ate"]
# item["uthor"]
# item["ext"]
# item["rwaler_time"]
# item["ther"]

# 获取 右下角页码标签 r.xpath('//ul[@class="pagination"]/li/a/text()').extract()--['2', '3', '4', '5', '…', '下一页', '末页']


class HrunSpider(scrapy.Spider):
    name = 'hurun'
    url_pages_dic={}

    the_domin = 'http://www.hurun.net'
    
    def cs(data):
        return str(data).replace(',','，').replace('\n','').replace('\t','').replace('\r','')

    def start_requests(self):
        yield scrapy.Request(url='http://www.hurun.net/CN/Article?column=1&page=1', callback=self.parse_cat)

    
    def parse_cat(self, response):
        self.cat = response.xpath('//li[@class="col-xs-2"]/a/div/text()').extract()
        self.cat_urls = response.xpath('//li[@class="col-xs-2"]/a/@href').extract()
        for url in self.cat_urls:
            yield scrapy.Request(url=self.the_domin+url, callback=self.parse_page)

    def parse_page(self,response):
        page_list = response.xpath('//ul[@class="pagination"]/li/a/text()').extract()
        if("末页" in page_list):
            pages = int(response.xpath('//ul[@class="pagination"]/li/a/@href').extract()[-1].split('=')[-1])
        elif("下一页" in page_list):
            pages = len(response.xpath('//ul[@class="pagination"]/li/a/@href').extract())
        else:
            pages = 1
        self.url_pages_dic[response.url]=pages

        if(len(self.url_pages_dic)==12):
            for url in self.url_pages_dic.keys():
                for page in range(1, self.url_pages_dic[url]+1):
                    yield scrapy.Request(url=url+'&page='+str(page), callback=self.parse_article_list)

    def parse_article_list(self, response):
        article_url=response.xpath('//li[@class="col-xs-12 col-md-6 pr"]/a/@href').extract()
        article_url+=response.xpath('//li[@class="col-xs-12 col-md-6 pl"]/a/@href').extract()
        for url in article_url:
            yield scrapy.Request(url=self.the_domin+url, callback=self.parse_article)

    def parse_article(self, response):
        item = ArticleItem()
        # item["the_id"]       =
        item["website"]      = "胡润百富"
        item["title"]        = str(response.xpath('//div[@class="title"]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["link"]         = response.url
        item["summary"]      = str(response.xpath('//section[@class][@style]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["category"]     = str(response.xpath('//ol/li/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["date"]         = str(response.xpath('//div[@class="col-sm-6 navsource-l"]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["author"]       = str(response.xpath('//div[@class="col-xs-12 text-right"]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = str(html2text.html2text(response.xpath('//section[@style="font-size:16px;line-height:24px;"]').extract()[0])).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # item["crwaler_time"] = 
        item["other"]        = ''

        yield item

