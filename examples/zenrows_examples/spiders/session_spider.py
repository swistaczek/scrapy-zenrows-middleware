"""
Example: Session-based scraping with IP persistence.

This spider demonstrates using session_id to maintain the same IP
across multiple requests, essential for:
- Login flows
- Multi-step processes
- Shopping cart flows
- Any scenario requiring session state

The session_id maintains the same IP for up to 10 minutes.
"""

import scrapy

from scrapy_zenrows import ZenRowsRequest


class SessionSpider(scrapy.Spider):
    name = "session_spider"

    # Use the same session ID across all requests
    SESSION_ID = 12345  # Can be any integer 1-99999

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        },
    }

    def start_requests(self):
        # Step 1: Access login page
        yield ZenRowsRequest(
            url="https://httpbin.org/cookies/set/session_test/step1",
            params={
                "session_id": self.SESSION_ID,
                "premium_proxy": "true",
            },
            callback=self.after_login_page,
            meta={"step": 1},
        )

    def after_login_page(self, response):
        self.logger.info(f"Step 1 completed. Status: {response.status}")
        self.logger.info(f"Response: {response.text[:200]}")

        # Step 2: Submit login (same session ID = same IP)
        yield ZenRowsRequest(
            url="https://httpbin.org/cookies/set/session_test/step2",
            params={
                "session_id": self.SESSION_ID,
                "premium_proxy": "true",
            },
            callback=self.after_login,
            meta={"step": 2},
        )

    def after_login(self, response):
        self.logger.info(f"Step 2 completed. Status: {response.status}")
        self.logger.info(f"Response: {response.text[:200]}")

        # Step 3: Access protected content (still same IP)
        yield ZenRowsRequest(
            url="https://httpbin.org/cookies",
            params={
                "session_id": self.SESSION_ID,
                "premium_proxy": "true",
            },
            callback=self.parse_dashboard,
            meta={"step": 3},
        )

    def parse_dashboard(self, response):
        self.logger.info(f"Step 3 completed. Status: {response.status}")

        # All cookies set in previous steps should be visible
        # because we used the same IP (session_id)
        yield {
            "step": response.meta["step"],
            "url": response.url,
            "cookies_preserved": response.text,
        }
