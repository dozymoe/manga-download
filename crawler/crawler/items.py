# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ComicSerie(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    alternative = scrapy.Field()
    author = scrapy.Field()
    genres = scrapy.Field()
    description = scrapy.Field()


class ChapterUrl(scrapy.Item):
    url = scrapy.Field()
    referer = scrapy.Field()
    serie = scrapy.Field()
    volume = scrapy.Field()
    chapter = scrapy.Field()
    chapter_extra = scrapy.Field()
    title = scrapy.Field()
    img_alt = scrapy.Field()
    img_title = scrapy.Field()
