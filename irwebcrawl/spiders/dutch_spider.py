import scrapy
from scrapy.linkextractors import LinkExtractor
import joblib
from irwebcrawl.features.feature_extraction import Extractor
import os
import numpy as np
import warnings


class DutchSpider(scrapy.Spider):
    name = 'dutchspider'
    custom_settings = {'CLOSESPIDER_PAGECOUNT': 1000,
                       'DEPTH_PRIORITY': 1,
                       'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
                       'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
                       'DEPTH_LIMIT': 2
                       }

    custom_settings = {'CLOSESPIDER_PAGECOUNT': 1000,
                       'DEPTH_LIMIT': 2
                       }

    start_urls = [
        'https://nl.wikipedia.org/wiki/Huis_Oranje-Nassau',
        'https://nos.nl/liveblog/2407093-reizigers-uit-zuid-afrika-vast-op-schiphol-nijmegen-verbiedt-demonstratie',
        'https://www.brussel.be/toerisme',
        'https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/algemene-coronaregels/kort-overzicht-coronamaatregelen',
        'https://hetutrechtsarchief.nl/'
    ]

    # start_urls = ['https://hetutrechtsarchief.nl/']

    def __init__(self, *a, **kw):
        super(DutchSpider, self).__init__(*a, **kw)
        root_dir = os.path.abspath(os.path.dirname(__file__))
        classifier_path = os.path.join(root_dir, '../classifiers/decision_tree.joblib')
        self.url_classifier = joblib.load(classifier_path)
        self.extractor = Extractor()

    def parse(self, response, **kwargs):
        warnings.simplefilter("ignore")
        follow = []
        for link in LinkExtractor().extract_links(response):
            dutch = self.url_classifier.predict(
                np.array(self.extractor.extract_features(link.url)).reshape(1, -1))[0] == 1
            if dutch:
                follow.append(link)
            yield {
                'href': str(link.url),
                'dutch?': str(dutch)
            }

        yield from response.follow_all(follow)
