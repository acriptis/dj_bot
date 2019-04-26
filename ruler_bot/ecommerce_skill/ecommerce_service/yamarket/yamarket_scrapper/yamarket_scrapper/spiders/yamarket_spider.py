import scrapy


class YaMarketSpider(scrapy.Spider):
    name = "products"

    def start_requests(self):
        base_url = "https://market.yandex.ru/search?&text=хороший телефон"
        base_url = "https://www.wildberries.ru/catalog/0/search.aspx?search=тапки"
        urls = [
            base_url,

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'products-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)