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

class JingmeitiSpider(scrapy.Spider):
    name = 'jingmeiti'
    
    def cs(data):
        return str(data).replace(',','，').replace('\n','').replace('\t','').replace('\r','')

    def start_requests(self):
        # 指定url
        page_deepth = input('输入更新页码深度...\n')
        for page in range(1,int(page_deepth)+1):
            yield scrapy.Request(url='http://www.jingmeiti.com/page/'+str(page), callback=self.parse)

    
    def parse(self, response):
        # 获取一个page的所有文章链接
        article_urls = response.xpath('//div[@class="ajax-load-con content posts-default wow fadeInUp"]/div/div/a/@href').extract()
        summarys = response.xpath('//div[@class="ajax-load-con content posts-default wow fadeInUp"]/div/div[@class="posts-default-box"]/div[@class="posts-default-content"]/div/text()').extract()

        for u in article_urls:
            meta_data = {
                'summary':summarys[article_urls.index(u)*3],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)

    def parse_article(self, response):

        item = ArticleItem()

        # item["the_id"]       =
        item["website"]      = "鲸媒体"
        item["title"]        = str(response.xpath('//h1[@class="title"]/text()').extract()[0]).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["link"]         = response.url
        item["summary"]      = str(response.meta['summary']).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["category"]     = str(response.xpath('//span[@itemprop="name"]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["date"]         = str(response.xpath('//span[@class="postclock"]/text()').extract()[0]).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        item["author"]       = str(response.xpath('//span[@class="postoriginal"]/text()').extract()).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = str(html2text.html2text(response.xpath('//div[@class="post-content"]').extract()[0])).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # item["crwaler_time"] = 
        item["other"]        = ''

        yield item