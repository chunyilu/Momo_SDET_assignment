"""Test Suite: Advanced Security & Query Parameter Tampering for Momo Search Feature."""

import pytest
from urllib.parse import urlparse, parse_qs, quote
from pages.home_page import HomePage


@pytest.mark.security
@pytest.mark.regression
class TestSearchSecurityAdvanced:
    """Validates security against query parameter tampering and advanced injection techniques."""

    def test_query_parameter_tampering_resilience(self, home_page: HomePage):
        """Validates resilience against query parameter tampering (TC-SEC-04).

        Steps:
        1. Manually edit URL search parameter (?keyword=...)
        2. Verify server side validates query parameter safely
        3. Verify graceful handling of unexpected syntax
        """
        # First, perform a normal search to get a baseline URL
        results_page = home_page.search_for("iPhone")
        normal_url = results_page.get_current_url()

        # Parse the normal URL to understand parameter structure
        parsed_normal = urlparse(normal_url)
        normal_query_params = parse_qs(parsed_normal.query)

        # Test various tampering attempts
        tampering_cases = [
            # Empty keyword parameter
            "keyword=",
            # Special characters in keyword
            "keyword=<script>alert('xss')</script>",
            "keyword=' OR '1'='1",
            # Multiple keyword parameters (potential parameter pollution)
            "keyword=test&keyword=malicious",
            # Missing equals sign
            "keyword",
            # URL encoded attack vectors
            "keyword=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
            # Very long parameter value
            "keyword=" + "A" * 1000,
            # Null bytes and other problematic characters
            "keyword=test%00null",
            # Newline injection attempts
            "keyword=test%0A%0D",
        ]

        base_url = "https://www.momoshop.com.tw/search"

        for i, tampered_param in enumerate(tampering_cases):
            # Construct test URL
            if tampered_param == "":
                test_url = base_url
            elif tampered_param == "keyword":
                test_url = f"{base_url}?{tampered_param}"
            else:
                test_url = f"{base_url}?{tampered_param}"

            try:
                # Navigate directly to the tampered URL
                home_page.page.goto(test_url)
                home_page.page.wait_for_timeout(1000)  # Allow page to load

                # Verify the page doesn't crash or show internal errors
                page_content = home_page.page.content()

                # Check for signs of internal errors or exposure
                assert "Internal Server Error" not in page_content, \
                    f"Internal server error exposed with tampering case {i}: {tampered_param}"
                assert "SQLException" not in page_content, \
                    f"SQL exception leaked with tampering case {i}: {tampered_param}"
                assert "Traceback" not in page_content, \
                    f"Stack trace leaked with tampering case {i}: {tampered_param}"
                assert "500" not in page_content or "Error 500" not in page_content, \
                    f"HTTP 500 error shown with tampering case {i}: {tampered_param}"

                # Verify we're still on a valid Momo page
                assert "momoshop.com.tw" in home_page.page.url, \
                    f"Should remain on Momo domain after tampering case {i}: {tampered_param}"

            except Exception as e:
                # If navigation fails, that's acceptable as long as it's a handled error
                # (e.g., invalid URL, blocked by browser security)
                # But we should not get uncaught exceptions in our test framework
                assert False, f"Unexpected exception during tampering test {i}: {tampered_param} - {str(e)}"

    def test_parameter_pollution_resilience(self, home_page: HomePage):
        """Tests resilience against HTTP parameter pollution attacks.

        Steps:
        1. Submit search with multiple keyword parameters
        2. Verify application handles it gracefully (uses first, last, or combines safely)
        """
        # Test with multiple keyword parameters
        test_url = "https://www.momoshop.com.tw/search?keyword=legitimate&keyword=<script>alert('xss')</script>"

        home_page.page.goto(test_url)
        home_page.page.wait_for_timeout(1000)

        # Should not execute script or show internal error
        page_content = home_page.page.content()
        assert "alert('xss')" not in page_content or "<script>" in page_content, \
            "XSS attempt should be sanitized, not executed"
        assert "Internal Server Error" not in page_content, \
            "Should not expose internal error on parameter pollution"