import scrapy
from scrapy_selenium import SeleniumRequest
from ..items import ComicSerie


class MangabatSpider(scrapy.Spider):
    name = 'mangabat'
    allowed_domains = ['read.mangabat.com']
    start_urls = [
        'https://read.mangabat.com/read-tk25033', # Gantz
        #'https://read.mangabat.com/read-mt390512', # Gantz:e
        #'https://read.mangabat.com/read-ka14123', # Gantz:g
        #'https://read.mangabat.com/read-za31375', # Gantz Origins: Oku Hiroya And Sf Movie Stories
        #'https://read.mangabat.com/read-ui14779', # Berserk
        #'https://read.mangabat.com/read-wn15010', # Nana To Kaoru
        #'https://read.mangabat.com/read-cy380991', # Nana To Kaoru Arashi
        #'https://read.mangabat.com/read-iz387166', # Nana To Kaoru Kokosei No Sm Gokko
    ]

    def parse(self, response):
        item = ComicSerie()
        item['title'] = response.css('.story-info-right > h1::text')
        item['image'] = response.css('.story-info-left > .info-image > img::attr(src)')
        item['alternative'] = response.css('.story-info-right > .variations-tableinfo > tbody > tr[1] > td[2] > h2::text')
        item['author'] = response.css('.story-info-right > .variations-tableinfo > tbody > tr[2] > td[2] > a::text')
        item['genres'] = response.css('.story-info-right > .variations-tableinfo > tbody > tr[4] > td[2] > a::text')
        item['description'] = response.css('#panel-story-info-description::text')
        return item
