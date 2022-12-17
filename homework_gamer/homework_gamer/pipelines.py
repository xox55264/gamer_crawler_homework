# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from homework_gamer.utils import RedisHelper
import json

class HomeworkGamerPipeline(object):

    def open_spider(self, spider):
        self.redis_helper = RedisHelper()

    def process_item(self, item, spider):
        key = f'scrapy_{item["article_id"]}_article' if 'article_id' in item else f'scrapy_{item["comment_id"]}_comment'
        self.redis_helper.set_value(key, json.dumps(dict(item), ensure_ascii=False), expire=600)
        return item
