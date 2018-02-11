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

class DuozhiwangSpider(scrapy.Spider):
    name = 'duozhiwang'
    
    def start_requests(self):
        # 指定url
        page_deepth = input('输入更新页码深度...\n')
        for page in range(1,int(page_deepth)+1):
            yield scrapy.Request(url='http://www.duozhi.com/?page='+str(page), callback=self.parse)

    
    def parse(self, response):
        # 获取一个page的所有文章链接
        article_urls = response.xpath('//div[@class="post"]/h3/a/@href').extract()
        summarys = response.xpath('//div[@class="post-content"]/div[@class="desc"]/p/text()').extract()
        for u in article_urls:
            meta_data = {
                'summary':summarys[article_urls.index(u)],
            }
            yield scrapy.Request(url=u, meta=meta_data, callback=self.parse_article)

    
    def parse_article(self, response):

        item = ArticleItem()

        # item["the_id"]       =
        item["website"]      = "多知网"
        item["title"]        = response.xpath('//head/title/text()').extract()[0].replace(',','，').replace('\n','').replace('\r','')
        item["link"]         = response.url
        item["summary"]      = response.meta['summary'].replace(',','，').replace('\n','').replace('\r','')
        item["category"]     = str(response.xpath('//ul[@class="nav-menu"]/li[@class="item current"]/a/text()').extract()).replace(',','，').replace('\n','').replace('\r','')
        item["date"]         = response.xpath('//span[@class="meta-date"]/text()').extract()[0].replace(',','，').replace('\n','').replace('\r','')
        item["author"]       = str(response.xpath('//div[@class="subject"]/div[@class="meta"]/text()').extract()[1]).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # 根据xpath语法选取正文部分的HTML传递给html2text
        item["text"]         = html2text.html2text(response.xpath('//div[@class="subject-content"]').extract()[0]).replace(',','，').replace('\n','').replace('\r','')
        # item["crwaler_time"] = 
        item["other"]        = ''

        yield item