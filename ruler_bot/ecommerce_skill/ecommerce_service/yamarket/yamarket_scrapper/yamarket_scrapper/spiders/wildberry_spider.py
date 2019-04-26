
import scrapy


class WildberrySpider(scrapy.Spider):
    name = "products"

    def start_requests(self):
        # base_url = "https://market.yandex.ru/search?&text=хороший телефон"
        base_url = "https://www.wildberries.ru/catalog/0/search.aspx?search=тапки"
        urls = [
            base_url,

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = 'products-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        import ipdb; ipdb.set_trace()

        for each_thing in response.xpath('//span[@itemtype="http://schema.org/Thing"]'):
            # first_image_selector = each_thing.xpath(".//a[@class='ref_goods_n_p']")[0]
            product_url = each_thing.xpath(".//a[@class='ref_goods_n_p']/@href")[0].get()
            image_url = each_thing.xpath(".//img[@class='thumbnail']/@src")[0].get()
            # '//img2.wbstatic.net/c246x328/new/4960000/4968752-1.jpg'


            product_name = each_thing.css('span.goods-name::text').get()
            product_brand = each_thing.css('strong.brand-name::text').get()
            product_price = each_thing.css('ins.lower-price::text').get()

            outdict = {
                "product_url": product_url,
                "product_image_url": image_url,
                "product_name": product_name,
                "product_brand": product_brand,
                "product_price": product_price,
            }
            yield outdict

    def get_data(self, response):
        response.css('span.goods-name').getall()
        # name
        response.css('div.dtlist-inner-brand-name span.goods-name::text').getall()
        # brand name
        response.css('div.dtlist-inner-brand-name strong.brand-name::text').getall()

        # price
        response.css('ins.lower-price::text').getall()
        # print(response.css('ins.lower-price::text').getall()[0])

        #img
        response.css('img.thumbnail').getall()

        for each_thing in response.xpath('//span[@itemtype="http://schema.org/Thing"]'):
            # first_image_selector = each_thing.xpath(".//a[@class='ref_goods_n_p']")[0]
            product_url = each_thing.xpath(".//a[@class='ref_goods_n_p']/@href")[0].get()
            image_url = each_thing.xpath(".//img[@class='thumbnail']/@src")[0].get()
            # '//img2.wbstatic.net/c246x328/new/4960000/4968752-1.jpg'


            product_name = each_thing.css('span.goods-name::text').get()
            product_brand = each_thing.css('strong.brand-name::text').get()
            product_price = each_thing.css('ins.lower-price::text').get()

            outdict = {
                "product_url": product_url,
                "product_image_url": image_url,
                "product_name": product_name,
                "product_brand": product_brand,
                "product_price": product_price,
            }
            yield outdict
