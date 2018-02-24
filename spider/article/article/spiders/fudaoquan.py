# -*- coding: utf-8 -*-

import re
import scrapy
from article.items import ArticleItem
import html2text
from article.tools import remove_csv_noise
from article.settings import UPDATE_DEEPTH as page_deepth

class DuozhiwangSpider(scrapy.Spider):
    name = 'fudaoquan'
    # 直接存入ES
    data_destination = 'ES'
    def start_requests(self):
        # 指定url
        # page_deepth = input(self.name+'输入更新页码深度...\n')
        # page_deepth = 10
        for page in range(1,int(page_deepth)+1):
            yield scrapy.Request(url='https://fudaoquan.com/page/'+str(page), callback=self.parse)

    
    def parse(self, response):
        # 获取一个page的所有文章链接
        article_urls = response.xpath('//article/a/@href').extract()
        summarys = response.xpath('//article/p[@class="note"]/text()').extract()
        title = response.xpath('//article/header/h2/a/text()').extract()
        date = response.xpath('//article/p[@class="meta"]/time/text()').extract()
        author = response.xpath('//article/p[@class="meta"]/span/text()').extract()
        for u in article_urls:
            meta_data = {
                'summary':summarys[article_urls.index(u)],
                'title':title[article_urls.index(u)],
                'date':date[article_urls.index(u)],
                'author':author[article_urls.index(u)],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)

    
    def parse_article(self, response):

        item = ArticleItem()

        # item["the_id"]       =
        item["website"]      = "辅导圈"
        item["title"]        = remove_csv_noise(response.meta['title'])
        item["link"]         = response.url
        item["summary"]      = remove_csv_noise(response.meta['summary'])
        item["date"]         = remove_csv_noise(response.meta['date'])
        item["category"]     = remove_csv_noise(response.xpath('//div[@class="article-meta"]/span/a/text()').extract())
        item["author"]       = remove_csv_noise(response.meta['author'])
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = remove_csv_noise(html2text.html2text(response.xpath('//article[@class="article-content"]').extract()[0]))
        # item["crwaler_time"] = 
        item["other"]        = '教育'

        yield item