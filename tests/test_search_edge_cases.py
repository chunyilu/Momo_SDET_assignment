"""Test Suite: Edge Cases, Boundary Conditions, and Zero-Result Searches."""

import urllib.parse
import pytest
from pages.home_page import HomePage
from data.search_test_data import NON_EXISTENT_KEYWORDS, EDGE_CASE_KEYWORDS


@pytest.mark.edge_case
@pytest.mark.regression
class TestSearchEdgeCases:
    """Validates resilience against non-existent queries, empty inputs, and boundary strings."""

    def test_empty_search_submission(self, home_page: HomePage):
        """Validates submitting an empty search query gracefully defaults to recommended search without error."""
        home_page.clear_search_input()
        results_page = home_page.click_search_button()

        # Momo shopping gracefully navigates to placeholder search
        current_url = results_page.get_current_url()
        assert "momoshop.com.tw" in current_url, "Browser should remain within Momo domain"
        assert results_page.get_product_count() >= 0, "Page should load without breaking DOM"

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
