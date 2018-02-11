# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import arrow
from article.settings import DATA_DESTION_PATH


# 所有在settings中制定的 pipeline都会被每一个item 撸一遍
# 根据爬虫的名字选择性跳过即可

class ArticlePipeline(object):

    def __init__(self):
        pass

    def open_spider(self,spider):
        # 如果是cnbweek spider直接返回
        if spider.name == 'cbnweek':
            return
        the_time = arrow.now()
        the_date = str(the_time.format('YYYYMMDD'))
        csv_name = spider.name+'_data_article'+the_date+'.csv'
        self.file = codecs.open(DATA_DESTION_PATH+csv_name,'w',encoding='utf-8')
        # 统计总数
        self.counter = 0
        self.file.seek(0)
        data_line = "the_id,website,title,link,summary,category,date,author,text,crwaler_time,other,for_pd\n"
        self.file.writelines(data_line)

    def process_item(self, item, spider):
        if spider.name == 'cbnweek':
            return item
        # 写入csv文件 self.file
        self.counter += 1
        item["the_id"] = self.counter
        item["crwaler_time"] = str(arrow.now())
        data_line = str(item["the_id"])+','+str(item["website"])+','+str(item["title"])+','+str(item["link"])+','+str(item["summary"])+','+str(item["category"])+','+str(item["date"])+','+str(item["author"])+','+str(item["text"])+','+str(item["crwaler_time"])+','+str(item["other"])+','+'\n'
        self.file.writelines(data_line)
        return item

    def close_spider(self, spider):
        if spider.name == 'cbnweek':
            return
        # 结束保存csv文件
        self.file.close()


class savecbnweekData(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        if spider.name != 'cbnweek':
            return

        CURRENT_MAGAZINE_NO = spider.CURRENT_MAGAZINE_NO
        self.counter = 0
        self.file = codecs.open(DATA_DESTION_PATH+'000cbnweek_data_maga'+str(CURRENT_MAGAZINE_NO)+'.csv', 'w', encoding='utf-8')
        self.file.seek(0)
        self.file.write("user_status,magazine_title,magazine_url,magazine_page_url,magazine_no,magazine_date,article_title,article_page_url,article_url,article_note,article_author,article_date,article_text\n")

    def process_item(self, item, spider):
        if spider.name != 'cbnweek':
            return item
        line = item['user_status']+','+item['magazine_title']+','+item['magazine_url']+','+item['magazine_page_url']+','+item['magazine_no']+','+item['magazine_date']+','+item['article_title']+','+item['article_page_url']+','+item['article_url']+','+item['article_note']+','+item['article_author']+','+item['article_date']+','+item['article_text']+','+'\n'
        self.file.write(line)
        self.counter += 1
        print(item['article_date'],"########################################", self.counter)
        return item

    def close_spider(self, spider):
        if spider.name != 'cbnweek':
            return

        self.file.close()
        