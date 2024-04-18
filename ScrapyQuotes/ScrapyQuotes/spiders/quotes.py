import scrapy
from ..items import ScrapyQuotesItem
import re


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = [""]
    start_urls = [""]
    next_url_head = ''
    page = 0
    page_num = 1

    def parse(self, response, **kwargs):
        self.page += 1
        quotes = response.css("div.a-section.a-spacing-small.puis-padding-left-small.puis-padding-right-small")
        for quote in quotes:
            item = ScrapyQuotesItem()
            item["title"] = quote.css(
                "div.a-section.a-spacing-none.a-spacing-top-small.s-title-instructions-style "
                "span.a-size-base-plus.a-color-base.a-text-normal::text").extract_first(
                "")
            item["star"] = quote.css("span.a-icon-alt::text").extract_first("")
            item["Comment"] = quote.css("span.a-size-base.s-underline-text::text").extract_first()
            url_text = quote.css(
                "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal::attr(href)").extract_first()
            match = re.search(r'/dp/(.*?)/ref=', url_text)
            if match:
                item["asin"] = match.group(1)
            yield item

        href = response.css('a.s-pagination-item.s-pagination-next::attr(href)').extract_first()
        if self.page < self.page_num and href:
            next_url = self.next_url_head + href
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            print("到达页数限制或未找到下一页按钮")


