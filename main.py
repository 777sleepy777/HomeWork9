import json

import scrapy
from itemadapter import ItemAdapter
from scrapy.crawler import CrawlerProcess
from models import Author, Quotes
import connect

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

            yield response.follow(url=self.start_urls[0] + q.xpath("span/a/@href").get(), callback=self.parse_author)

        next_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link[1:])


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

    with open("authors.json", encoding='utf-8') as file:
        data = json.load(file)
        for el in data:
            author = Author(fullname=el.get("fullname"), born_date=el.get("born_date"),
                           born_location=el.get("born_location"), description=el.get("description")) #.replace("[", "").replace("]", ""))
            print(author.fullname)
            author.save()

    with (open("quotes.json", encoding='utf-8') as file):
        data = json.load(file)
        for el in data:
            print(el.get('author'))
            author, *_ = Author.objects(fullname=el.get('author'))
            quote = Quotes(quote=el.get("quote"), author=author, tags=el.get('tags'))
            quote.save()