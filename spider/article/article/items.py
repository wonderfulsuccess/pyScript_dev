# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    the_id      = scrapy.Field() # str 编号
    website     = scrapy.Field() # str 网站名称
    title       = scrapy.Field() # str 文章标题
    link        = scrapy.Field() # str 文章url
    summary     = scrapy.Field() # str 原文摘要
    category    = scrapy.Field() # list 文章内别
    date        = scrapy.Field() # str 发布时间
    author      = scrapy.Field() # str 作者
    text        = scrapy.Field() # list 正文段落
    crwaler_time= scrapy.Field() # str 抓取时间
    other       = scrapy.Field() # list 其他信息

