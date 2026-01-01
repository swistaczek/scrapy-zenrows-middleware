"""
Example: Scraping dynamic content with wait_for.

This spider demonstrates using wait_for to handle:
- Single Page Applications (SPAs)
- AJAX-loaded content
- Lazy-loaded elements
- Any content that loads after initial page render

wait_for is more reliable than fixed wait times because it
waits for a specific CSS selector to appear in the DOM.
"""

import scrapy

from scrapy_zenrows import ZenRowsRequest


class DynamicContentSpider(scrapy.Spider):
    name = "dynamic_content_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        },
    }

    def start_requests(self):
        # Example 1: Wait for specific element to load
        yield ZenRowsRequest(
            url="https://quotes.toscrape.com/js/",
            params={
                "js_render": "true",
                "wait_for": ".quote",  # Wait for quotes to load
            },
            callback=self.parse_quotes,
            meta={"example": "wait_for_element"},
        )

        # Example 2: Combine wait_for with block_resources for speed
        yield ZenRowsRequest(
            url="https://quotes.toscrape.com/js/",
            params={
                "js_render": "true",
                "wait_for": ".quote",
                "block_resources": "image,font,stylesheet",  # Faster loading
            },
            callback=self.parse_quotes,
            meta={"example": "optimized_wait"},
        )

        # Example 3: Wait for table data
        yield ZenRowsRequest(
            url="https://quotes.toscrape.com/js/",
            params={
                "js_render": "true",
                "wait_for": ".quote .text",  # More specific selector
                "premium_proxy": "true",
            },
            callback=self.parse_quotes,
            meta={"example": "specific_selector"},
        )

    def parse_quotes(self, response):
        example_type = response.meta["example"]
        self.logger.info(f"Parsing with strategy: {example_type}")

        quotes = response.css(".quote")
        self.logger.info(f"Found {len(quotes)} quotes")

        for quote in quotes:
            yield {
                "example": example_type,
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tag::text").getall(),
            }
