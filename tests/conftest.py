"""
Shared pytest fixtures for scrapy-zenrows tests.
"""

import os

import pytest
from scrapy.settings import Settings


@pytest.fixture
def api_key():
    """Get API key from environment or use test placeholder."""
    return os.getenv("ZENROWS_API_KEY", "test_api_key_placeholder")


@pytest.fixture
def mock_settings(api_key):
    """Create Scrapy Settings with ZenRows configuration."""
    return Settings(
        {
            "ZENROWS_API_KEY": api_key,
            "USE_ZENROWS_PREMIUM_PROXY": False,
            "USE_ZENROWS_JS_RENDER": False,
            "USE_ZENROWS_ORIGINAL_STATUS": False,
            "ZENROWS_SESSION_ID": None,
            "ZENROWS_BLOCK_RESOURCES": None,
            "ZENROWS_ALLOWED_STATUS_CODES": None,
        }
    )


@pytest.fixture
def mock_settings_with_defaults(api_key):
    """Create Scrapy Settings with ZenRows defaults enabled."""
    return Settings(
        {
            "ZENROWS_API_KEY": api_key,
            "USE_ZENROWS_PREMIUM_PROXY": True,
            "USE_ZENROWS_JS_RENDER": True,
            "USE_ZENROWS_ORIGINAL_STATUS": True,
            "ZENROWS_SESSION_ID": 12345,
            "ZENROWS_BLOCK_RESOURCES": "image,font",
            "ZENROWS_ALLOWED_STATUS_CODES": "404,500",
        }
    )


@pytest.fixture
def retry_settings():
    """Create Scrapy Settings for retry middleware."""
    return Settings(
        {
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_MAX_RETRIES": 3,
            "ZENROWS_RETRY_BACKOFF": 1.0,
            "ZENROWS_RETRY_STATUS_CODES": [429, 500, 502, 503, 504],
        }
    )


@pytest.fixture
def custom_retry_settings():
    """Create custom Scrapy Settings for retry middleware."""
    return Settings(
        {
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_MAX_RETRIES": 5,
            "ZENROWS_RETRY_BACKOFF": 2.0,
            "ZENROWS_RETRY_STATUS_CODES": [429, 500, 503],
        }
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (require real API key)")
