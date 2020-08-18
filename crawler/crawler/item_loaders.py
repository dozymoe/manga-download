from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join

class ComicSerieLoader(ItemLoader):

    title_in = TakeFirst()
    title_out = TakeFirst()

    image_in = TakeFirst()
    image_out = TakeFirst()

    alternative_in = TakeFirst()
    alternative_out = TakeFirst()

    author_in = TakeFirst()
    author_out = TakeFirst()

    genres_in = Join(', ')
    genres_out = TakeFirst()

    description_in = Join('\n')
    description_out = TakeFirst()
