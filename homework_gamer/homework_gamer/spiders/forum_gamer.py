import scrapy
import json
import hashlib
import re
from datetime import datetime, timedelta
from homework_gamer.items import ForumCrawlerItem, ForumCommentCrawlerItem
from homework_gamer.utils import RedisHelper
from pydispatch import dispatcher


class ForumGamerSpider(scrapy.Spider):
    name = 'forum_gamer'
    allowed_domains = ['forum.gamer.com.tw']
    check_url = False
    proxy = False
    # config setting
    custom_settings = {'LOG_FILE': 'fg.log', 'FEED_URI': 'fg.jl'}
    # custom_settings = {'LOG_FILE': 'fg.log'}
    redis_helper = RedisHelper()
    page = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        dispatcher.connect(self.spider_opened, scrapy.signals.spider_opened)
        dispatcher.connect(self.spider_closed, scrapy.signals.spider_closed)

    def spider_opened(self):
        self.exist = self.redis_helper.check_spider_exist(f'{self.name}_{self.forum_id}')

    def spider_closed(self):
        if not self.exist:
            self.redis_helper.remove_spider_key(f'{self.name}_{self.forum_id}')

    def start_requests(self):
        yield scrapy.Request(url='https://forum.gamer.com.tw/B.php?bsn={}'.format(self.forum_id),
                             callback=self.forum_parse)

    def forum_parse(self, response):
        if self.exist:
            self.crawler.engine.close_spider(self, reason=f'spider {self.name}_{self.forum_id} exist')
            return
        # get all articles
        for article_info in response.xpath('//table[@class="b-list"]/tr[contains(@class,"b-list-item")]'):
            category = article_info.xpath('.//a[@data-subbsn]/text()').get()
            article_href = article_info.xpath('.//*[contains(@class,"b-list__main__title")]/@href').get()
            article_url = 'https://forum.gamer.com.tw/{}'.format(article_href)
            yield scrapy.Request(url=article_url,
                                 meta={'category': category},
                                 callback=self.article_parse)

        # go to next page
        next_page_href = response.xpath('//a[@class="next"]/@href').get()
        if next_page_href and self.page <= int(self.total_pages):
            forum_url = f'https://forum.gamer.com.tw/B.php{next_page_href}'
            self.page += 1
            yield scrapy.Request(url=forum_url,
                                 callback=self.forum_parse)

    def article_parse(self, response):
        forum_item = ForumCrawlerItem()
        article_id = 0
        first_published_date = response.xpath(
            '//section[contains(@id, "post")]//div[@class="c-post__header__info"]/a/@data-mtime').get()
        if not self.check_published_date(first_published_date):
            return
        # get article info
        for article in response.xpath('//section[contains(@id, "post")]'):
            part_url = article.xpath('.//div[@class="c-post__header__author"]/a[@class="floor"]/@href').get()
            forum_item['url'] = f'https://forum.gamer.com.tw/{part_url}' if part_url else response.url
            forum_item['title'] = article.xpath('.//h1/text()').get() or ''
            forum_item['reply_id'] = article_id
            content = []
            for each_content in article.xpath('.//div[@class="c-article__content"]//text()').getall():
                each_content_after_encoded = each_content
                if re.findall(r'《([a-zA-Z][a-zA-Z0-9]{3,11}) \(.{0,10}\)》', each_content):
                    for user_id in re.findall(r'《([a-zA-Z][a-zA-Z0-9]{3,11}) \(.{0,10}\)》', each_content):
                        encoded_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
                        each_content_after_encoded = each_content_after_encoded.replace(user_id, encoded_user_id)
                content.append(each_content_after_encoded)
            forum_item['content'] = content
            forum_item['author_id'] = hashlib.sha256(
                article.xpath('.//a[@class="userid"]/text()').get().encode('utf-8')).hexdigest() or ''
            forum_item['author_name'] = article.xpath('.//a[@class="username"]/text()').get() or ''
            forum_item['published_time'] = article.xpath(
                './/div[@class="c-post__header__info"]/a/@data-mtime').get() or ''
            forum_item['forum_title'] = self.forum_title
            forum_item['category'] = response.meta['category']
            article_id = article.xpath('./@id').get().split('_')[-1]
            forum_item['article_id'] = article_id

            if article.xpath('.//span[@class="postgp"]/span/text()').get() == '爆':
                like = 1001
            else:
                like = article.xpath('.//span[@class="postgp"]/span/text()').get()

            if article.xpath('.//span[@class="postbp"]/span/text()').get() == '-':
                dislike = 0
            elif article.xpath('.//span[@class="postbp"]/span/text()').get() == 'X':
                dislike = 51
            else:
                dislike = article.xpath('.//span[@class="postbp"]/span/text()').get()

            forum_item['reactions'] = {'like': int(like), 'dislike': int(dislike)}
            yield forum_item
            # call api to get all comment in current article
            comment_url = 'https://forum.gamer.com.tw/ajax/moreCommend.php?bsn={fid}&snB={aid}&returnHtml=0'.format(
                fid=self.forum_id,
                aid=article_id)
            yield scrapy.Request(url=comment_url, callback=self.comment_parse)
        # go to next page
        if response.xpath('//section[@class="c-section"]//a[@class="next"]/@href').get():
            next_page_url = 'https://forum.gamer.com.tw/C.php{}'.format(
                response.xpath('//section[@class="c-section"]//a[@class="next"]/@href').get())
            yield scrapy.Request(url=next_page_url,
                                 meta={'category': response.meta['category']},
                                 callback=self.article_parse)

    def comment_parse(self, response):
        forum_comment_item = ForumCommentCrawlerItem()
        comment_data = json.loads(response.body.decode('utf-8'))
        # get comment info
        for key in comment_data.keys():
            if key != 'next_snC':
                forum_comment_item['author_id'] = hashlib.sha256(
                    comment_data[key]['userid'].encode('utf-8')).hexdigest()
                forum_comment_item['author_name'] = comment_data[key]['nick']
                forum_comment_item['published_time'] = comment_data[key]['wtime']
                comment_after_encoded = comment_data[key]['comment']
                if re.findall(r'\[([a-zA-Z][a-zA-Z0-9]{3,11}):.{0,10}\]', comment_data[key]['comment']):
                    for user_id in re.findall(r'\[([a-zA-Z][a-zA-Z0-9]{3,11}):.{0,10}\]', comment_data[key]['comment']):
                        encoded_user_id = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
                        comment_after_encoded = comment_after_encoded.replace(user_id, encoded_user_id)
                    forum_comment_item['content'] = [comment_after_encoded]
                else:
                    forum_comment_item['content'] = [comment_data[key]['comment']]
                forum_comment_item['comment_id'] = comment_data[key]['sn']
                forum_comment_item['reply_id'] = comment_data[key]['snB']
                like = comment_data[key]['gp']
                dislike = comment_data[key]['bp']
                forum_comment_item['reactions'] = {'like': int(like), 'dislike': int(dislike)}
                yield forum_comment_item

    def check_published_date(self, date_string, range=7):
        published_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return published_time + timedelta(days=range) >= datetime.today()
