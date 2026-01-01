# Scrapy settings for ZenRows examples
#
# For simplicity, this file contains commonly used settings.
# See: https://docs.scrapy.org/en/latest/topics/settings.html

import os

BOT_NAME = "zenrows_examples"

SPIDER_MODULES = ["zenrows_examples.spiders"]
NEWSPIDER_MODULE = "zenrows_examples.spiders"

# Disable robots.txt for scraping examples
ROBOTSTXT_OBEY = False

# Enable ZenRows middleware
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}

# ZenRows API Key - set via environment variable
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY", "<YOUR_ZENROWS_API_KEY>")

# ZenRows default settings (can be overridden per-request)
USE_ZENROWS_PREMIUM_PROXY = False
USE_ZENROWS_JS_RENDER = False

# Retry settings
ZENROWS_RETRY_ENABLED = True
ZENROWS_MAX_RETRIES = 3
ZENROWS_RETRY_BACKOFF = 1.0

# Scrapy 2.7+ settings
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Logging
LOG_LEVEL = "INFO"
