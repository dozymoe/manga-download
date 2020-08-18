# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging
import json
import os
import re
from shutil import which
import subprocess
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import ComicSerie, ChapterUrl

_logger = logging.getLogger(__name__)


class ComicSeriePipeline:
    def process_item(self, item, spider):
        if isinstance(item, ComicSerie):
            basedir = os.path.join(os.environ['MANGA_BASEDIR'], item['title'])
            os.makedirs(basedir, exist_ok=True)
            filename = os.path.join(basedir, '%s.json' % item['title'])
            with open(filename, 'w') as f:
                json.dump(dict(item), f)
        return item


class ComicChapterPipeline:

    PAGE_URL_PATTERN = re.compile(r'/(?P<num>\d+)\.(?P<ext>png|jpg|jpeg)$')

    def process_item(self, item, spider):
        if isinstance(item, ChapterUrl):
            ## directory
            dirname = 'Volume_%s_Chapter_%s_%s_%s' % (item.get('volume', ''),
                    item.get('chapter', ''), item.get('chapter_extra', ''),
                    item.get('title', ''))
            basedir = os.path.join(os.environ['MANGA_BASEDIR'], item['serie'],
                    dirname)
            os.makedirs(basedir, exist_ok=True)

            ## filename
            match = re.search(self.PAGE_URL_PATTERN, item['url'])
            if match:
                filename = '%s.%s' % (match.group('num'), match.group('ext'))
            else:
                _logger.info(dict(item))
                raise Exception("Cannot guess image filename.")

            subprocess.check_call([
                    self.bin,
                    '--quiet',
                    '--category-index=0',
                    '--folder=%s' % basedir,
                    '--filename=%s' % filename,
                    '--http-referer=%s' % item['referer'],
                    '--http-user-agent=%s' % self.user_agent,
                    item['url']])
        return item


    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.bin = which('uget-gtk')


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
                user_agent=crawler.settings.get('USER_AGENT'))
