# -*- coding: utf-8 -*-
import re
import scrapy
from article.items import ArticleItem
import html2text
from article.tools import remove_csv_noise

from article.settings import UPDATE_DEEPTH as page_deepth

class SouhujiaodianSpider(scrapy.Spider):
    name = 'souhujiaodian'
    data_destination = 'ES'
    spider_mode = 'U'
    # list[1]为该城市在搜狐咨询的咨询文章页码数
    cities = {
        'hz':['杭州',1551],
        'nb':['宁波',129],
        'sh':['上海',3995],
        'bj':['北京',7561],
        'xm':['厦门',1030],
        'nj':['南京',1899],
        'cq':['重庆',2048],
        'wh':['武汉',1671],
    }
    
    def start_requests(self):
        # 指定url
        for city in self.cities:
            if self.spider_mode == 'U':
                self.cities[city][1]=int(page_deepth)
            for page in range(1,self.cities[city][1]+1):
                meta_data = {
                    'city':self.cities[city][0],
                }
                yield scrapy.Request(url='https://'+str(city)+'.focus.cn/zixun/'+str(page), meta=meta_data, callback=self.parse)

    
    def parse(self, response):
        # 获取一个page的所有文章链接
        article_urls = response.xpath('//div[@class="module-news-list"]/ul/li/a/@href').extract()
        summarys = response.xpath('//div[@class="module-news-list"]/ul/li/div/p[@class="news-list-detail-con"]/text()').extract()
        for u in article_urls:
            meta_data = {
                'summary':summarys[article_urls.index(u)],
                'city':response.meta['city'],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)

    
    def parse_article(self, response):

        city = response.meta['city']
        item = ArticleItem()

        # item["the_id"] it is a counter will be asigned in pipelines
        item["website"]      = '搜狐焦点 资讯 '+city
        item["title"]        = remove_csv_noise(response.xpath('//div[@class="main-content"]/h1/text()').extract())
        item["link"]         = response.url
        item["summary"]      = remove_csv_noise(response.meta['summary'])
        item["category"]     = remove_csv_noise(response.xpath('//div[@class="bread-crumbs-area global-clearfix"]/span/a/text()').extract())
        item["date"]         = remove_csv_noise(response.xpath('//div[@class="info-source"]/span/text()').extract()[0])
        item["author"]       = remove_csv_noise(response.xpath('//div[@class="info-source"]/span/a/text()').extract()[0])
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = remove_csv_noise(html2text.html2text(response.xpath('//div[@class="info-content"]').extract()[0]))
        # item["crwaler_time"] = 
        item["other"]        = '搜狐焦点 资讯 '+city

        yield item