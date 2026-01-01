"""
Example: Scraping content for AI/LLM pipelines.

This spider demonstrates using response_type to:
- Get clean markdown for LLM processing
- Extract plaintext for NLP pipelines
- Generate PDFs for document processing

response_type options:
- markdown: Clean markdown format
- plaintext: Plain text without formatting
- pdf: PDF document (base64 encoded)
"""

import json

import scrapy

from scrapy_zenrows import ZenRowsRequest


class AIPipelineSpider(scrapy.Spider):
    name = "ai_pipeline_spider"

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
            "scrapy_zenrows.ZenRowsMiddleware": 543,
        },
    }

    def start_requests(self):
        # Article URL for processing
        url = "https://quotes.toscrape.com/"

        # Get markdown for LLM processing
        yield ZenRowsRequest(
            url=url,
            params={
                "response_type": "markdown",
                "block_resources": "image,media,font",  # Speed up
            },
            callback=self.parse_markdown,
            meta={"format": "markdown"},
        )

        # Get plaintext for NLP
        yield ZenRowsRequest(
            url=url,
            params={
                "response_type": "plaintext",
            },
            callback=self.parse_plaintext,
            meta={"format": "plaintext"},
        )

        # Get HTML with autoparse for structured extraction
        yield ZenRowsRequest(
            url=url,
            params={
                "autoparse": "true",
            },
            callback=self.parse_structured,
            meta={"format": "autoparse"},
        )

    def parse_markdown(self, response):
        """Process markdown response for LLM."""
        markdown_content = response.text

        self.logger.info(f"Markdown content length: {len(markdown_content)}")
        self.logger.info(f"First 500 chars:\n{markdown_content[:500]}")

        yield {
            "format": "markdown",
            "url": response.url,
            "content_length": len(markdown_content),
            "content": markdown_content,
            # Ready for LLM processing
            "llm_prompt": f"Summarize this content:\n\n{markdown_content[:2000]}",
        }

    def parse_plaintext(self, response):
        """Process plaintext response for NLP."""
        text_content = response.text

        self.logger.info(f"Plaintext content length: {len(text_content)}")

        # Simple word count for NLP preprocessing
        words = text_content.split()

        yield {
            "format": "plaintext",
            "url": response.url,
            "content_length": len(text_content),
            "word_count": len(words),
            "content": text_content,
        }

    def parse_structured(self, response):
        """Process autoparse structured response."""
        try:
            # Autoparse returns JSON
            structured_data = response.json()
            self.logger.info(f"Structured data keys: {structured_data.keys()}")
        except json.JSONDecodeError:
            # Fallback if not JSON
            structured_data = {"raw": response.text}

        yield {
            "format": "autoparse",
            "url": response.url,
            "structured_data": structured_data,
        }
