from urllib.parse import urljoin

import scrapy
from scrapy import Request

from sainsburys.items import SainsburysItem


class BasicSpider(scrapy.Spider):
    name = 'basic'
    allowed_domains = ['www.sainsburys.co.uk']
    start_urls = ['https://www.sainsburys.co.uk/shop/gb/groceries/meat-fish']

    def parse(self, response):
        
        urls = response.css("ul.categories.departments li a::attr(href)").extract()

        for url in urls:
            
            yield response.follow(url, callback=self.parse_department)
            # yield Request(urljoin(response.url, url), callback=self.parse_department)

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

        print()
        print(response.url)
        print()

        product_name = response.css("h1.pd__header::attr(text)").extract()
        product_image = response.css("img.pd__image::attr(src)").extract()

        print()
        print(product_name, product_image)
        print()

        item = SainsburysItem()

        item["url"] = response.url
        item["name"] = product_name
        item["image"] = product_image

        yield item
