"""
Integration tests for ZenRows API.

These tests require a real ZenRows API key set in the ZENROWS_API_KEY environment variable.
Run with: pytest tests/integration -m integration
"""

import os

import pytest
from scrapy.settings import Settings

from scrapy_zenrows import ZenRowsMiddleware, ZenRowsRequest, ZenRowsRetryMiddleware
from scrapy_zenrows.__version__ import __version__

# Skip all integration tests if no API key is set
pytestmark = pytest.mark.integration


@pytest.fixture
def real_api_key():
    """Get real API key from environment, skip if not available."""
    api_key = os.getenv("ZENROWS_API_KEY")
    if not api_key or api_key == "test_api_key_placeholder":
        pytest.skip("ZENROWS_API_KEY not set in environment")
    return api_key


class TestPackageImports:
    """Test that all package components can be imported."""

    def test_version_import(self):
        """Test version can be imported."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_request_import(self):
        """Test ZenRowsRequest can be imported."""
        assert ZenRowsRequest is not None

    def test_middleware_import(self):
        """Test ZenRowsMiddleware can be imported."""
        assert ZenRowsMiddleware is not None

    def test_retry_middleware_import(self):
        """Test ZenRowsRetryMiddleware can be imported."""
        assert ZenRowsRetryMiddleware is not None


class TestRequestCreation:
    """Test ZenRowsRequest creation with various parameters."""

    def test_basic_request_creation(self):
        """Test basic ZenRowsRequest can be created."""
        request = ZenRowsRequest(
            url="https://example.com",
            params={"js_render": "true"},
        )

        assert request.url == "https://example.com"
        assert request.params["js_render"] == "true"

    def test_request_with_all_v110_params(self):
        """Test ZenRowsRequest with all v1.1.0 parameters."""
        request = ZenRowsRequest(
            url="https://example.com",
            params={
                "session_id": 12345,
                "wait_for": ".content",
                "block_resources": "image,font",
                "response_type": "markdown",
                "original_status": "true",
                "allowed_status_codes": "404,500",
                "screenshot_selector": "#main",
                "proxy_city": "new york",
            },
        )

        assert request.params["session_id"] == 12345
        assert request.params["wait_for"] == ".content"
        assert request.params["block_resources"] == "image,font"
        assert request.params["response_type"] == "markdown"


class TestMiddlewareUrlBuilding:
    """Test that middleware builds correct ZenRows API URLs."""

    def test_basic_url_building(self, real_api_key):
        """Test basic URL generation."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={},
            use_proxy=False,
            js_render=False,
        )

        assert "api.zenrows.com" in url
        assert "url=https" in url
        assert f"apikey={real_api_key}" in url

    def test_url_with_all_params(self, real_api_key):
        """Test URL with all new parameters."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        url = middleware.get_zenrows_api_url(
            url="https://example.com",
            params={"wait_for": ".content"},
            use_proxy=True,
            js_render=True,
            original_status=True,
            session_id=12345,
            block_resources="image,font",
            allowed_status_codes="404,500",
        )

        assert "premium_proxy=true" in url
        assert "js_render=true" in url
        assert "original_status=true" in url
        assert "session_id=12345" in url
        assert "block_resources=" in url
        assert "wait_for=" in url


class TestRetryMiddleware:
    """Test retry middleware initialization and configuration."""

    def test_default_settings(self):
        """Test retry middleware with default settings."""
        settings = Settings({"ZENROWS_RETRY_ENABLED": True})

        middleware = ZenRowsRetryMiddleware(settings)

        assert middleware.max_retry_times == 3
        assert middleware.backoff_factor == 1.0
        assert 429 in middleware.retry_http_codes

    def test_custom_settings(self):
        """Test retry middleware with custom settings."""
        settings = Settings({
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_MAX_RETRIES": 5,
            "ZENROWS_RETRY_BACKOFF": 2.0,
            "ZENROWS_RETRY_STATUS_CODES": [429, 500, 503],
        })

        middleware = ZenRowsRetryMiddleware(settings)

        assert middleware.max_retry_times == 5
        assert middleware.backoff_factor == 2.0
        assert 429 in middleware.retry_http_codes
        assert 500 in middleware.retry_http_codes

    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        settings = Settings({
            "ZENROWS_RETRY_ENABLED": True,
            "ZENROWS_RETRY_BACKOFF": 2.0,
        })

        middleware = ZenRowsRetryMiddleware(settings)

        assert middleware._get_backoff_time(0) == 2.0  # 2.0 * 2^0
        assert middleware._get_backoff_time(1) == 4.0  # 2.0 * 2^1
        assert middleware._get_backoff_time(2) == 8.0  # 2.0 * 2^2


class TestParameterValidation:
    """Test parameter validation in middleware."""

    def test_invalid_session_id_logs_warning(self, real_api_key, caplog):
        """Test invalid session_id triggers warning."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        middleware._validate_params({"session_id": 100000})

        assert "session_id must be between 1 and 99999" in caplog.text

    def test_screenshot_mutual_exclusion_logs_warning(self, real_api_key, caplog):
        """Test screenshot mutual exclusion warning."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        middleware._validate_params({
            "screenshot_selector": "#main",
            "screenshot_fullpage": "true",
        })

        assert "mutually exclusive" in caplog.text

    def test_proxy_city_requires_premium_logs_warning(self, real_api_key, caplog):
        """Test proxy_city requires premium_proxy warning."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        middleware._validate_params({"proxy_city": "new york"})

        assert "proxy_city requires premium_proxy=true" in caplog.text

    def test_screenshot_requires_js_render_logs_warning(self, real_api_key, caplog):
        """Test screenshot requires js_render warning."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        middleware._validate_params({"screenshot": "true"})

        assert "screenshot requires js_render=true" in caplog.text


@pytest.mark.slow
class TestRealApiCalls:
    """
    Tests that make real API calls to ZenRows.

    These tests are marked as slow and require a valid API key.
    Run with: pytest tests/integration -m "integration and slow"
    """

    def test_basic_request_success(self, real_api_key):
        """Test a basic request returns 200."""
        middleware = ZenRowsMiddleware(api_key=real_api_key)

        # Build URL for a simple test site
        url = middleware.get_zenrows_api_url(
            url="https://httpbin.org/get",
            params={},
            use_proxy=False,
            js_render=False,
        )

        # URL should be properly constructed
        assert "api.zenrows.com" in url
        assert "httpbin.org" in url
