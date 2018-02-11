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


class cbnweekItem(scrapy.Item):
    magazine_title = scrapy.Field()     #杂志名称
    magazine_url = scrapy.Field()       #杂志链接
    magazine_page_url = scrapy.Field()  #杂志封面图片链接
    magazine_no = scrapy.Field()        #杂志编号
    magazine_date = scrapy.Field()      #杂志出版时间
    article_title = scrapy.Field()      #文章标题
    article_page_url = scrapy.Field()   #文章主题图链接
    article_url = scrapy.Field()        #文章链接
    article_note = scrapy.Field()       #文章大意
    article_author = scrapy.Field()     #文章作者
    article_date = scrapy.Field()       #文章时间
    article_text = scrapy.Field()       #文章文本
    user_status = scrapy.Field()        #用户登录状态

