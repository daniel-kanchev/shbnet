import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from shbnet.items import Article


class shbnetSpider(scrapy.Spider):
    name = 'shbnet'
    start_urls = ['https://www.shbnet.com/News_Listing']

    def parse(self, response):
        links = response.xpath('//a[@rel="tag"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="pagetitle"]/h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="col-md-8"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
