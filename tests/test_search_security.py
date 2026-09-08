"""Test Suite: Search Input Security & Injection Sanitization."""

import pytest
from pages.home_page import HomePage
from data.search_test_data import SECURITY_PAYLOADS


@pytest.mark.security
@pytest.mark.regression
class TestSearchSecurity:
    """Validates security defenses against Cross-Site Scripting (XSS) and SQL injection payloads."""

    @pytest.mark.parametrize("payload", SECURITY_PAYLOADS)
    def test_search_injection_resilience(self, home_page: HomePage, payload: str):
        """Validates that search input safely sanitizes injection payloads without executing unauthorized scripts."""
        unhandled_dialogs = []

        # Listen for any alert/confirm/prompt dialogs triggered by XSS execution
        home_page.page.on("dialog", lambda dialog: (unhandled_dialogs.append(dialog.message), dialog.dismiss()))

        results_page = home_page.search_for(payload)

        # Assert no malicious script triggered a popup dialog
        assert len(unhandled_dialogs) == 0, f"XSS vulnerability detected! Dialog popped up with message: {unhandled_dialogs}"

        # Assert no internal server error or stack trace leakage is exposed
        body_html = results_page.page.content()
        assert "SQLException" not in body_html, "SQL exception leakage detected in response"
        assert "Internal Server Error" not in body_html, "Internal 500 error triggered by payload"
        assert "Traceback (most recent call last)" not in body_html, "Stack trace leakage detected"
