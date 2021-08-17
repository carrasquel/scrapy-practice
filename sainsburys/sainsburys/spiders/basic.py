import scrapy
from scrapy import Request


class BasicSpider(scrapy.Spider):
    name = 'basic'
    allowed_domains = ['https://www.sainsburys.co.uk/shop/gb/groceries/meath-fish/']
    start_urls = ['https://www.sainsburys.co.uk/shop/gb/groceries/meath-fish//']

    def parse(self, response):
        
        
        urls = response.css("ul.categories.departments li a::attr(href)").extract()

        for url in urls:

            yield response.follow(url, callback=self.parse_department)

    def parse_department(self, response):

        products = response.css("ul.productLister.gridView").extract()

        if products:
            for product in self.handle_product_listing(response):
                yield product
        
        pages = response.css("ul.categories.shelf li a::attr(href)").extract()

        if not pages:
            pages = response.css("ul.categories.aisles li a::attr(href)").extract()

        if not pages:
            return

        for url in pages:
            yield response.follow(url, callback=self.parse_department)

    def handle_product_listing(self, response):

        urls = response.css("ul.productLister.gridView li.gridItem h3 a::attr(href)").extract()

        for url in urls:
            yield response.follow(url, callback=self.parse_product)

        next_page = response.css("#productLister > div.pagination.paginationBottom > ul > li.next > a::attr(href)").extract()

        if next_page:
            yield response.follow(next_page, callback=self.handle_product_listing)

    def parse_product(self, response):

        pass
