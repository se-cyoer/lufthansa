"""
@author: koala
"""
import scrapy
from scrapy.crawler import CrawlerProcess


class FirstSpider(scrapy.Spider):
    name = 'first'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        "TWISTED_REACTOR": 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        "DOWNLOADER_MIDDLEWARES": {
            'lufthansa.lufthansa.middlewares.LufthansaDownloaderMiddleware': 543,
        }
    }

    start_url = 'https://www.lufthansa.com/cn/en/homepage'

    def start_requests(self):
        for count in range(1):
            yield scrapy.Request(url=self.start_url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        self.logger.info(">>>>>>>>response headers<<<<<<<<<<<")
        self.logger.debug(response.status)
        self.logger.debug(response.url)


process = CrawlerProcess()
process.crawl(FirstSpider)
process.start()
