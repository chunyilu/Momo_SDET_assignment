"""Test Suite: Search Results Pagination on Momo Platform."""

import pytest
from pages.home_page import HomePage


@pytest.mark.pagination
@pytest.mark.regression
class TestSearchPagination:
    """Validates multi-page navigation, page indicator accuracy, and item offset consistency."""

    def test_pagination_navigation_to_page_2(self, home_page: HomePage):
        """Validates navigating from page 1 to page 2 updates results and active page indicator."""
        results_page = home_page.search_for("iPhone")
        assert results_page.get_product_count() > 0

        # Capture page 1 first product title
        page_1_titles = results_page.get_product_titles(limit=3)
        assert len(page_1_titles) > 0, "Page 1 must render product titles"

        # Navigate to Page 2
        results_page.go_to_page(2)

        # Verify active page indicator
        assert results_page.get_active_page_number() == 2, "Active page indicator should be 2"

        # Capture page 2 first product title and verify pagination offset
        page_2_titles = results_page.get_product_titles(limit=3)
        assert len(page_2_titles) > 0, "Page 2 must render product titles"
        assert page_1_titles[0] != page_2_titles[0] or page_1_titles != page_2_titles, (
            f"Page 2 products should differ from Page 1 products. P1: {page_1_titles}, P2: {page_2_titles}"
        )

    def test_pagination_controls_displayed(self, home_page: HomePage):
        """Validates that pagination controls are rendered when results exceed single page."""
        results_page = home_page.search_for("Samsung")
        assert results_page.is_element_visible(results_page.pagination_area), (
            "Pagination area should be visible for multi-page search results"
        )
