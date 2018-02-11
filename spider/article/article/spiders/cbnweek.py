# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from faker import Factory
from article.items import cbnweekItem
from article.settings import UAPOOL
import html2text

f = Factory.create()
from lxml import etree


class CBNWeekSpider(scrapy.Spider):

    name = 'cbnweek'
    # CURRENT_MAGAZINE_NO=input("请输入杂志url编号...\n")
    # 如果要下载指定编号的杂志 只需要 修改数字或者 取消以上注释 在命令行中输入编号
    # 这种方式比较适合一本一本更新的情况 批量下载则需要 使用另外的脚本调用 爬虫并且传入杂志编号
    CURRENT_MAGAZINE_NO = '1'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Host':'www.cbnweek.com',
        'User-Agent': f.user_agent(),
        # 'User-Agent': UAPOOL[1],
    }

    def start_requests(self):
        return [Request('https://www.cbnweek.com/account/login',meta={'cookiejar' : "kjhs*&^78%$hjJJ8HkjKHnnndf*&^54sdnniiKhbnA"}, callback=self.parse)]

    def parse(self, response):
        print("准备登陆...可能需要补充完整的用户名和密码")
        login_data = {
            "username":"wonderful****",
            "password":"wzs1***",
        } 
        return [FormRequest.from_response(response,
            meta = {'cookiejar' : response.meta['cookiejar']},
            headers = self.headers,
            formdata = login_data,
            callback = self.afterlogin,
            dont_filter = True,
            )]

    def afterlogin(self, response):
        print("登录成功")
        print(response.xpath("/html/body/div[3]/div/div/nav/ul/li[5]/div/span/text()").extract())
        return [Request("https://www.cbnweek.com/magazines/"+str(self.CURRENT_MAGAZINE_NO),meta={'cookiejar': response.meta['cookiejar']}, callback=self.getMagazine)]
        # for i in range(400,481):
            # yield Request("https://www.cbnweek.com/magazines/"+str(i), meta={'cookiejar':response.meta['cookiejar']}, callback=self.getMagazine)

    def getMagazine(self, response):
        # title = response.xpath("/html/body/div[3]/div/div[2]/aside/div/div[1]/div[3]/div[1]/text()").extract()
        articles = response.xpath('//article[@class="article-item clearfix"]')
        
        magazine = response.xpath('//div[@class="aside-item aside-entry top-line"]')
        magazine_info = magazine[0].extract()
        magazine_info = etree.HTML(magazine_info)
        
        magazine_title = magazine_info.xpath('//div[@class="aside-title-magazine"]/text()')[0].replace(',','，').replace('\n','')
        magazine_url = response.url
        magazine_page_url = magazine_info.xpath('//img/@src')[0].replace(',','，').replace('\n','')
        magazine_no = magazine_info.xpath('//div[@class="text-muted"]/text()')[0].replace(',','，').replace('\n','')
        magazine_date = magazine_info.xpath('//div[@class="text-muted"]/text()')[1].replace(',','，').replace('\n','')
        
        for i in range(len(articles)):
            articles_info = articles[i].extract()
            articles_info = etree.HTML(articles_info)

            meta_data = {
                'cookiejar':response.meta['cookiejar'],
                'magazine_title' : magazine_title,
                'magazine_url' : magazine_url,
                'magazine_page_url' : magazine_page_url,
                'magazine_no' : magazine_no,
                'magazine_date' : magazine_date,
                'article_title' : articles_info.xpath('//div[@class="article-item-title"]/text()')[0].replace(',','，').replace('\n',''),
                'article_url' : "https://www.cbnweek.com"+articles_info.xpath('//a[@class="float-right article-item-image img-wrap"]/@href')[0].replace(',','，').replace('\n',''),
                'article_note' : articles_info.xpath('//p[@class="article-summary text-muted"]/text()')[0].replace(',','，').replace('\n',''),
                'article_author' : articles_info.xpath('//span[@class="author"]/text()')[0].replace(',','，').replace('\n',''),
                'article_date' : articles_info.xpath('//span[@class="article-time"]/text()')[0].replace(',','，').replace('\n',''),
            }

            yield Request(meta_data['article_url'], meta=meta_data, callback=self.download_article)

    def download_article(self, response):
        # data = response.xpath('//div[@class="article-content"]/p/text()').extract()
        text = str(html2text.html2text(response.xpath('////div[@class="article-content"]').extract()[0])).replace(',','，').replace('\n','').replace('\t','').replace('\r','')
        # if data[0]:
        #     data = data[0].extract()
        # else:
        #     data = data.extract()
        # text = etree.HTML(data)
        # text = ''.join(text.xpath('//p/text()'))
        # text = ''.join(data)
        # text = text.replace(',','，').replace('\n','')
        # print(text)
        item = cbnweekItem()
        item['magazine_title'] = response.meta['magazine_title']
        item['magazine_url'] = response.meta['magazine_url']
        item['magazine_page_url'] = response.meta['magazine_page_url']
        item['magazine_no'] = response.meta['magazine_no']
        item['magazine_date'] = response.meta['magazine_date']
        item['article_title'] = response.meta['article_title']
        item['article_page_url'] = response.xpath('//img/@src')[5].extract()
        item['article_url'] = response.meta['article_url']
        item['article_note'] = response.meta['article_note']
        item['article_author'] = response.meta['article_author']
        item['article_date'] = response.meta['article_date']
        item['article_text'] = text;
        item['user_status'] = ''.join(response.xpath('/html/body/div[2]/div/div/nav/ul/li[5]/div/span/text()').extract())
        yield item