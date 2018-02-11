# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import arrow
from article.settings import DATA_DESTION_PATH


class ArticlePipeline(object):

    def __init__(self):
        pass

    def open_spider(self,spider):
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
        # 写入csv文件 self.file
        self.counter += 1
        item["the_id"] = self.counter
        item["crwaler_time"] = str(arrow.now())
        data_line = str(item["the_id"])+','+str(item["website"])+','+str(item["title"])+','+str(item["link"])+','+str(item["summary"])+','+str(item["category"])+','+str(item["date"])+','+str(item["author"])+','+str(item["text"])+','+str(item["crwaler_time"])+','+str(item["other"])+','+'\n'
        self.file.writelines(data_line)
        return item

    def close_spider(self, spider):
        # 结束保存csv文件
        self.file.close()
        