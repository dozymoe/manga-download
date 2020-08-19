import logging
import re
import scrapy
from scrapy_selenium import SeleniumRequest
from ..items import ComicSerie, ChapterUrl
from ..item_loaders import ComicSerieLoader

_logger = logging.getLogger(__name__)


class MangabatSpider(scrapy.Spider):
    name = 'mangabat'
    allowed_domains = [
        'm.mangabat.com',
        'read.mangabat.com',
    ]
    start_urls = [
        'https://read.mangabat.com/read-tk25033', # Gantz
        'https://m.mangabat.com/read-mt390512', # Gantz:e
        'https://read.mangabat.com/read-ka14123', # Gantz:g
        'https://read.mangabat.com/read-za31375', # Gantz Origins: Oku Hiroya And Sf Movie Stories
        'https://read.mangabat.com/read-ui14779', # Berserk
        #'https://read.mangabat.com/read-wn15010', # Nana To Kaoru
        'https://m.mangabat.com/read-cy380991', # Nana To Kaoru Arashi
        'https://m.mangabat.com/read-iz387166', # Nana To Kaoru Kokosei No Sm Gokko
        'https://read.mangabat.com/read-el14060', # Onepunch-Man
        'https://read.mangabat.com/read-np14412', # Overlord
        'https://m.mangabat.com/read-zx377716', # Goblin Slayer
        'https://read.mangabat.com/read-lo43185', # Goblin Slayer Gaiden 2: Tsubanari No Daikatana
        'https://read.mangabat.com/read-ip39886', # Goblin Slayer: Side Story Year One
        'https://m.mangabat.com/read-hm385405', # Goblin Slayer: Brand New Day
        'https://read.mangabat.com/read-yq13739', # Kingdom
    ]
    VOLUME_PATTERN = re.compile(r'(Vol.|Volume )(?P<num>\d+)')
    CHAPTER_PATTERN = re.compile(r'Chapter (?P<num>\d+)(\.(?P<extra>\d+))?')


    def parse(self, response):
        l = ComicSerieLoader(item=ComicSerie(), response=response)
        l.add_css('title', '.story-info-right > h1::text')
        l.add_css('image', '.story-info-left > .info-image > img::attr(src)')
        l.add_css('alternative', '.story-info-right > .variations-tableInfo > tbody > tr:nth-child(1) > td:nth-child(2) > h2::text')
        l.add_css('author', '.story-info-right > .variations-tableInfo > tbody > tr:nth-child(2) > td:nth-child(2) > a::text')
        l.add_css('genres', '.story-info-right > .variations-tableInfo > tbody > tr:nth-child(4) > td:nth-child(2) > a::text')
        l.add_css('description', '#panel-story-info-description::text')
        item = l.load_item()
        yield item
        for anchor in response.css('.panel-story-chapter-list .row-content-chapter a'):
            kwargs = {'serie': item['title']}
            title = anchor.xpath('.//text()').get()

            match = re.search(self.VOLUME_PATTERN, title)
            if match:
                kwargs['volume'] = match.group('num')
                title = title.replace(match.group(), '')

            match = re.search(self.CHAPTER_PATTERN, title)
            if match:
                kwargs['chapter'] = match.group('num')
                if match.group('extra'):
                    kwargs['chapter_extra'] = match.group('extra')
                title = title.replace(match.group(), '')

            title = title.strip().lstrip(':').strip()

            kwargs['title'] = title

            url = response.urljoin(anchor.attrib['href'])
            yield scrapy.Request(url=url, callback=self.parse_chapter,
                    cb_kwargs=kwargs)


    def parse_chapter(self, response, **kwargs):
        for img in response.css('.container-chapter-reader > img'):
            item = ChapterUrl()
            item['url'] = response.urljoin(img.attrib['src'])
            item['referer'] = response.url
            item['img_alt'] = img.attrib['alt']
            item['img_title'] = img.attrib['title']
            for key, value in kwargs.items():
                item[key] = value
            yield item
