import scrapy
from scrapy.linkextractors import LinkExtractor
import joblib
from irwebcrawl.features.feature_extraction import Extractor


class DutchSpider(scrapy.Spider):
    name = 'dutchspider'

    start_urls = [
        'https://nos.nl/liveblog/2407093-reizigers-uit-zuid-afrika-vast-op-schiphol-nijmegen-verbiedt-demonstratie'
    ]

    def __init__(self, *a, **kw):
        super(DutchSpider, self).__init__(*a, **kw)
        self.url_classifier = joblib.load('../classifiers/decision_tree.joblib')
        self.extractor = Extractor()

    def parse(self, response, **kwargs):
        for link in LinkExtractor().extract_links(response):
            yield {
                'href': str(link.url),
                'dutch?': self.url_classifier.predict(self.extractor.extract_features(link.url))
            }

        yield from response.follow_all(LinkExtractor().extract_links(response))
