# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BaotintucItem(scrapy.Item):
    # define the fields for your item here like:
    topic = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field()
    images = scrapy.Field()  # Danh sách ảnh đã tải
    article_file = scrapy.Field()  # Tên file HTML của bài viết 