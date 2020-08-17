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
