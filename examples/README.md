# ZenRows Scrapy Examples

Example spiders demonstrating various scrapy-zenrows features.

## Setup

1. Install dependencies:
   ```bash
   pip install scrapy-zenrows
   ```

2. Set your API key:
   ```bash
   export ZENROWS_API_KEY="your_api_key_here"
   ```

## Running Examples

From the `examples` directory:

```bash
# Run a specific spider
scrapy crawl session_spider

# Run with output to JSON
scrapy crawl ai_pipeline_spider -o output.json
```

## Available Spiders

| Spider | Description | Key Features |
|--------|-------------|--------------|
| `session_spider` | Multi-step session flow | `session_id`, IP persistence |
| `dynamic_content_spider` | JavaScript-rendered pages | `js_render`, `wait_for` |
| `optimized_spider` | Fast scraping | `block_resources` |
| `ai_pipeline_spider` | LLM/NLP content extraction | `response_type` (markdown/plaintext) |
| `antibot_bypass_spider` | Protected site scraping | `premium_proxy`, `js_render` |
| `screenshot_spider` | Page screenshots | `screenshot`, `screenshot_fullpage` |
| `pagination_spider` | Multi-page scraping | Pagination handling |
| `concurrent_ecommerce_spider` | E-commerce scraping | Concurrent requests |
| `custom_headers_spider` | Custom HTTP headers | `custom_headers` |
| `table_parsing_spider` | HTML table extraction | CSS selectors |

## Spider Details

### Session Spider (`session_spider`)
Demonstrates maintaining the same IP across multiple requests for login flows:
```python
yield ZenRowsRequest(
    url="https://example.com/login",
    params={"session_id": 12345, "premium_proxy": "true"},
)
```

### Dynamic Content Spider (`dynamic_content_spider`)
Scrapes JavaScript-rendered content with wait conditions:
```python
yield ZenRowsRequest(
    url="https://example.com/spa",
    params={"js_render": "true", "wait_for": ".content-loaded"},
)
```

### Optimized Spider (`optimized_spider`)
Fast scraping by blocking unnecessary resources:
```python
yield ZenRowsRequest(
    url="https://example.com",
    params={"block_resources": "image,font,media,stylesheet"},
)
```

### AI Pipeline Spider (`ai_pipeline_spider`)
Get clean content for LLM processing:
```python
yield ZenRowsRequest(
    url="https://example.com/article",
    params={"response_type": "markdown"},
)
```

## Configuration

Override default settings per spider using `custom_settings`:

```python
class MySpider(scrapy.Spider):
    custom_settings = {
        "ZENROWS_API_KEY": "...",
        "USE_ZENROWS_PREMIUM_PROXY": True,
        "ZENROWS_MAX_RETRIES": 5,
    }
```

Or per request using the `params` dict:

```python
yield ZenRowsRequest(
    url="...",
    params={"premium_proxy": "true", "js_render": "true"},
)
```
