import scrapy


class DutchSpider(scrapy.Spider):
    name = 'quotes'
    """
    start_urls = [
        'https://nl.wikipedia.org/wiki/Huis_Oranje-Nassau',
        'https://nos.nl/liveblog/2407093-reizigers-uit-zuid-afrika-vast-op-schiphol-nijmegen-verbiedt-demonstratie'
    ]
    """
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]

    def parse(self, response, **kwargs):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }

        yield from response.follow_all(css='ul.pager a', callback=self.parse)
