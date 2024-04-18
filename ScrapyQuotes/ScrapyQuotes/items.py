# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyQuotesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()  # 标题
    star = scrapy.Field()  # 星
    Comment = scrapy.Field()  # 评论数
    asin = scrapy.Field()   # 产品编号

