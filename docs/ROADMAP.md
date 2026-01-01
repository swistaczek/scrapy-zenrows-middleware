# ZenRows Scrapy Middleware - Feature Roadmap

## Version 1.1.0 (Current Release)

### New Features

#### 8 New API Parameters

| Parameter | Type | Description | Global Setting |
|-----------|------|-------------|----------------|
| `session_id` | int (1-99999) | Maintain same IP for up to 10 minutes | `ZENROWS_SESSION_ID` |
| `wait_for` | str (CSS selector) | Wait for element to appear in DOM | - |
| `original_status` | bool | Return target's original HTTP status | `USE_ZENROWS_ORIGINAL_STATUS` |
| `block_resources` | str | Block resources (image,media,font) | `ZENROWS_BLOCK_RESOURCES` |
| `response_type` | str | Convert to markdown/plaintext/pdf | - |
| `allowed_status_codes` | str | Get content from error pages | `ZENROWS_ALLOWED_STATUS_CODES` |
| `screenshot_selector` | str | Screenshot specific element | - |
| `proxy_city` | str | City-level geolocation | - |

#### Retry Middleware

New `ZenRowsRetryMiddleware` with exponential backoff:

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}

ZENROWS_RETRY_ENABLED = True
ZENROWS_MAX_RETRIES = 3
ZENROWS_RETRY_BACKOFF = 1.0
ZENROWS_RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
```

#### Parameter Validation

Automatic validation with warnings for:
- `session_id` range (1-99999)
- `screenshot_selector` + `screenshot_fullpage` mutual exclusion
- `proxy_city` requires `premium_proxy`
- `screenshot` requires `js_render`

---

## Migration from v1.0.0

### Breaking Changes

None. v1.1.0 is fully backward compatible.

### New Settings

Add these optional settings to enable new features:

```python
# settings.py

# Session persistence (maintains same IP)
ZENROWS_SESSION_ID = None  # int: 1-99999

# Get original HTTP status from target
USE_ZENROWS_ORIGINAL_STATUS = False

# Block resources globally (speeds up scraping)
ZENROWS_BLOCK_RESOURCES = None  # "image,media,font,stylesheet"

# Allow specific error status codes
ZENROWS_ALLOWED_STATUS_CODES = None  # "404,500,503"

# Retry middleware settings
ZENROWS_RETRY_ENABLED = True
ZENROWS_MAX_RETRIES = 3
ZENROWS_RETRY_BACKOFF = 1.0
ZENROWS_RETRY_STATUS_CODES = [429, 500, 502, 503, 504]
```

### New Middleware Registration

To enable retry with exponential backoff:

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsRetryMiddleware": 550,  # NEW
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}
```

---

## Complete Parameter Reference

### Page Loading

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `js_render` | bool | false | Enable JavaScript rendering |
| `wait` | int | 0 | Wait milliseconds after page load |
| `wait_for` | str | - | Wait for CSS selector in DOM |
| `block_resources` | str | - | Block resources (image,media,font,stylesheet,script) |
| `js_instructions` | str | - | JSON array of JS actions |

### Proxy Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `premium_proxy` | bool | false | Use residential IPs |
| `proxy_country` | str | - | Country code (us, de, jp) |
| `proxy_city` | str | - | City name (requires premium_proxy) |
| `session_id` | int | - | Maintain IP (1-99999, 10 min max) |

### Data Extraction

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `autoparse` | bool | false | Auto-extract structured data |
| `css_extractor` | str | - | CSS selectors in JSON format |
| `outputs` | str | - | Data types: tables,emails,hashtags |
| `response_type` | str | - | markdown, plaintext, pdf |
| `json_response` | bool | false | Capture XHR/Fetch as JSON |

### Screenshots

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `screenshot` | bool | false | Capture above-fold screenshot |
| `screenshot_fullpage` | bool | false | Capture full page |
| `screenshot_selector` | str | - | Screenshot specific element |
| `screenshot_format` | str | png | Image format: png, jpeg |
| `screenshot_quality` | int | - | JPEG quality: 1-100 |

### Response Handling

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `original_status` | bool | false | Return target's HTTP status |
| `allowed_status_codes` | str | - | Get content from error pages |
| `custom_headers` | bool | false | Enable custom headers |

---

## Example Configurations

### High-Performance Scraping

```python
# settings.py
ZENROWS_BLOCK_RESOURCES = "image,media,font,stylesheet"
USE_ZENROWS_PREMIUM_PROXY = True
ZENROWS_RETRY_ENABLED = True
ZENROWS_MAX_RETRIES = 5
```

### Session-Based Scraping

```python
# In spider
yield ZenRowsRequest(
    url="https://example.com/login",
    params={
        "session_id": 12345,
        "premium_proxy": "true",
        "js_render": "true",
    },
    callback=self.after_login,
)
```

### AI/LLM Pipeline

```python
# Get clean markdown for AI processing
yield ZenRowsRequest(
    url="https://blog.example.com/article",
    params={
        "response_type": "markdown",
        "block_resources": "image,media,font",
    },
    callback=self.process_for_llm,
)
```

### Debugging Failed Requests

```python
# Get content even from error pages
yield ZenRowsRequest(
    url="https://example.com/may-fail",
    params={
        "original_status": "true",
        "allowed_status_codes": "404,500,503",
    },
    callback=self.handle_response,
)
```

---

## Best Practices

### 1. Use Block Resources

Block unnecessary resources to speed up scraping and reduce costs:

```python
params = {
    "js_render": "true",
    "block_resources": "image,media,font",
    "wait_for": ".main-content",
}
```

### 2. Use wait_for Instead of wait

`wait_for` is more reliable than fixed `wait` for dynamic content:

```python
# Better - waits for specific element
params = {"wait_for": ".product-list"}

# Less reliable - fixed delay
params = {"wait": "5000"}
```

### 3. Enable Retry Middleware

Always enable retry for production spiders:

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_zenrows.ZenRowsRetryMiddleware": 550,
    "scrapy_zenrows.ZenRowsMiddleware": 543,
}
ZENROWS_MAX_RETRIES = 3
ZENROWS_RETRY_BACKOFF = 1.0
```

### 4. Use Sessions for Multi-Step Flows

Maintain IP consistency for login flows and multi-page processes:

```python
SESSION_ID = 12345  # Use same ID across requests

yield ZenRowsRequest(url="/login", params={"session_id": SESSION_ID})
yield ZenRowsRequest(url="/dashboard", params={"session_id": SESSION_ID})
yield ZenRowsRequest(url="/export", params={"session_id": SESSION_ID})
```

### 5. Validate Your Parameters

The middleware automatically validates parameters and logs warnings.
Check your logs for messages like:

- `session_id must be between 1 and 99999`
- `screenshot_selector and screenshot_fullpage are mutually exclusive`
- `proxy_city requires premium_proxy=true`
- `screenshot requires js_render=true`

---

## Changelog

### v1.1.0

- Added 8 new ZenRows API parameters
- Added `ZenRowsRetryMiddleware` with exponential backoff
- Added parameter validation with warning messages
- Added comprehensive docstrings
- Improved Scrapy 2.0+ compatibility
- Added new example spiders

### v1.0.0

- Initial release
- Basic ZenRows integration
- Support for core parameters
