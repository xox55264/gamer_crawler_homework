# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HomeworkGamerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ForumCrawlerItem(scrapy.Item):
    '''
    spider_name        -> crawled by which spider(type:str)
    author_id          -> author id with sha256 encode(type:str)
    author_name        -> author's nick_name(optional)(default: '')(type:str)
    url                -> url of this article(type:str)
    created_time       -> time when data been created(type:str)
    published_time     -> time when article been published(type:str)
    forum_title        -> the forum title that article belong(type:str)
    category           -> the category that article belong(type:str)
    title              -> the title of article(optional)(default: '')(type:str)
    content            -> the content of article(type:list<str>)
    article_id         -> the id of article been given by website(type:str)
    reactions          -> the reactions of article(type:dict<int>)(key:reaction)(value:counts)
    reply_id           -> which article id he reply(optional)(default: '')(type:str)
    reply_info         -> the info about the article he reply(optional)(default: [])(type:list<str>)
    views              -> this topic been watched(optional)(default: -1)(type:int)
    keywords           -> the keyword about this article or topic(optional)(default: [])(type:list<str>)
    item_id            -> {spider_name}_{reply_id} with sha1 encode(type:str)
    kafka_topics       -> kafka topic(type:list<str>)
    item_type          -> type of item(type:str)(value:forum)
    '''

    author_id = scrapy.Field()
    author_name = scrapy.Field()
    url = scrapy.Field()
    published_time = scrapy.Field()
    forum_title = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    article_id = scrapy.Field()
    reactions = scrapy.Field()
    reply_id = scrapy.Field()
    reply_info = scrapy.Field()
    views = scrapy.Field()
    keywords = scrapy.Field()
    item_id = scrapy.Field()
    kafka_topics = scrapy.Field()
    item_type = scrapy.Field()

    pass


class ForumCommentCrawlerItem(scrapy.Item):
    '''
    spider_name        -> crawled by which spider(type:str)
    author_id          -> author id with sha256 encode(type:str)
    author_name        -> author's nick_name(optional)(default: '')(type:str)
    created_time       -> time when data been created(type:str)
    published_time     -> time when article been published(type:str)
    content            -> the content of article(type:list<str>)
    comment_id         -> the id of comment been given by website or create under the rule {reply_id}_{auto increase number} (type:str)
    reactions          -> the reactions of article(type:dict<int>)(key:reaction)(value:counts)
    reply_id           -> which article id he reply(optional)(default: '')(type:str)
    kafka_topics       -> kafka topic(type:list<str>)
    item_type          -> type of item(type:str)(value:forum_comment)
    item_id            -> {spider_name}_{reply_id}_{comment_id} with sha1 encode(type:str)
    '''

    author_id = scrapy.Field()
    author_name = scrapy.Field()
    published_time = scrapy.Field()
    content = scrapy.Field()
    comment_id = scrapy.Field()
    reactions = scrapy.Field()
    reply_id = scrapy.Field()

    pass
