"""
Example: High-performance scraping with block_resources.

This spider demonstrates using block_resources to:
- Speed up page loading
- Reduce bandwidth usage
- Lower API costs
- Focus on content, not assets

Resources that can be blocked:
- image: Images (jpg, png, gif, webp, svg)
- media: Video and audio files
- font: Web fonts
- stylesheet: CSS files
- script: JavaScript files (use carefully)
"""

import scrapy

from scrapy_zenrows import ZenRowsRequest


class OptimizedSpider(scrapy.Spider):
    name = "optimized_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        },
        # Global resource blocking
        "ZENROWS_BLOCK_RESOURCES": "image,media,font",
    }

    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/",
            "https://books.toscrape.com/",
        ]

        for url in urls:
            # Minimal blocking - just images and media
            yield ZenRowsRequest(
                url=url,
                params={
                    "js_render": "true",
                    "block_resources": "image,media",
                },
                callback=self.parse,
                meta={"blocking": "minimal"},
            )

            # Aggressive blocking - everything except HTML/JS
            yield ZenRowsRequest(
                url=url,
                params={
                    "js_render": "true",
                    "block_resources": "image,media,font,stylesheet",
                },
                callback=self.parse,
                meta={"blocking": "aggressive"},
            )

    def parse(self, response):
        blocking_level = response.meta["blocking"]

        # Measure response size (indicator of resources blocked)
        response_size = len(response.body)

        self.logger.info(f"URL: {response.url}, Blocking: {blocking_level}, Response size: {response_size} bytes")

        yield {
            "url": response.url,
            "blocking_level": blocking_level,
            "response_size_bytes": response_size,
            "title": response.css("title::text").get(),
            "status": response.status,
        }
