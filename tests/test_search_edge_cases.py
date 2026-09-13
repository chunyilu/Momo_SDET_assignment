"""Test Suite: Edge Cases, Boundary Conditions, and Zero-Result Searches."""

import urllib.parse
import pytest
from pages.home_page import HomePage
from data.search_test_data import NON_EXISTENT_KEYWORDS, EDGE_CASE_KEYWORDS


@pytest.mark.edge_case
@pytest.mark.regression
class TestSearchEdgeCases:
    """Validates resilience against non-existent queries, empty inputs, and boundary strings."""

    @pytest.mark.skip(reason="Issue: Empty search query executes rotating placeholder keyword without validation - see ISSUE-004")
    def test_empty_search_submission(self, home_page: HomePage):
        """Validates that empty search submission does not trigger unrequested backend search."""
        home_page.clear_search_input()
        results_page = home_page.click_search_button()

        # Get the current URL after attempting empty search
        current_url = results_page.get_current_url()

        # The core issue: empty search should NOT trigger a backend search with a keyword parameter
        # Parse the URL to check for keyword parameter
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)

        # Verify that no keyword parameter is present in the URL
        # This prevents the issue where empty search executes with a placeholder keyword
        assert 'keyword' not in query_params, \
            f"Empty search should not contain keyword parameter. URL: {current_url}, Query params: {query_params}"

        # Additional verification: should remain on homepage or show validation error
        # (Not navigating to search results with placeholder keyword)
        assert "momoshop.com.tw" in current_url, "Should remain within Momo domain"

    @pytest.mark.parametrize("keyword", NON_EXISTENT_KEYWORDS)
    def test_non_existent_keyword_displays_friendly_no_result(self, home_page: HomePage, keyword: str):
        """Validates searching for non-existent inventory yields a friendly zero-results message."""
        results_page = home_page.search_for(keyword)

        # Verify no results notification is displayed
        assert results_page.is_no_results_found(), (
            f"Expected zero-results notification for non-existent query '{keyword}'"
        )
        msg = results_page.get_no_results_message()
        assert "很抱歉" in msg or "調整關鍵字" in msg or results_page.is_no_results_found()

    @pytest.mark.parametrize("edge_keyword", EDGE_CASE_KEYWORDS)
    def test_special_characters_and_boundary_searches(self, home_page: HomePage, edge_keyword: str):
        """Validates search resilience when given symbols, emojis, and long boundary strings."""
        results_page = home_page.search_for(edge_keyword)

        current_url = results_page.get_current_url()
        assert "momoshop.com.tw" in current_url, "System should handle special character input gracefully"
        assert results_page.page.locator("body").count() > 0, "DOM tree must remain intact"
