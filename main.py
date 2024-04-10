import json

import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess

class DataPipline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'fullname' in adapter.keys():
            if not dict(adapter) in self.authors:
               self.authors.append(dict(adapter))
        if 'quote' in adapter.keys():
            self.quotes.append(dict(adapter))

    def close_spider(self, spider):
        with open('quotes.json', 'w', encoding='utf-8') as fd:
            json.dump(self.quotes, fd, ensure_ascii=False, indent=2)
        with open('authors.json', 'w', encoding='utf-8') as fd:
            json.dump(self.authors, fd, ensure_ascii=False, indent=2)

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]
    custom_settings = {"ITEM_PIPELINES": {DataPipline: 300}}

    def parse(self, response, **kwargs):
        for q in response.xpath("/html//div[@class='quote']"):
            yield {
                "quote": q.xpath("span[@class='text']/text()").get().strip(),
                "author": q.xpath("span/small[@class='author']/text()").get().strip(),
                "tags": q.xpath("div[@class='tags']/a/text()").extract()
            }
            #yield QuoteItem(quote=quote, author=author, tags=tags)
            yield response.follow(url=self.start_urls[0] + q.xpath("span/a/@href").get(), callback=self.parse_author)

        next_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)


    def parse_author(self, response, **kwargs):
        content = response.xpath("/html//div[@class='author-details']")
        yield {
            "fullname": content.xpath("h3[@class='author-title']/text()").get().strip(),
            "born_date": content.xpath("p/span[@class='author-born-date']/text()").get().strip(),
            "born_location": content.xpath("p/span[@class='author-born-location']/text()").get().strip(),
            "description": content.xpath("div[@class='author-description']/text()").get().strip()
        }

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()