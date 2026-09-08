"""Test Suite: Basic Search Functionality on Momo E-Commerce Platform."""

import urllib.parse
import pytest
from playwright.sync_api import Page
from pages.home_page import HomePage
from data.search_test_data import VALID_SEARCH_KEYWORDS, SearchTestCase


@pytest.mark.smoke
@pytest.mark.regression
class TestSearchBasic:
    """Validates core search execution flows, input controls, and result rendering."""

    def test_homepage_search_ui_elements_present(self, home_page: HomePage):
        """Validates that search input field and search button are visible and operational."""
        assert home_page.is_element_visible(home_page.search_input), "Search input should be visible on homepage"
        assert home_page.is_element_visible(home_page.search_button), "Search button should be visible on homepage"
        
        # Verify placeholder exists
        placeholder = home_page.get_search_placeholder()
        assert isinstance(placeholder, str), "Placeholder should be a valid string"

    def test_search_by_button_click(self, home_page: HomePage):
        """Verifies searching by clicking the search button returns relevant products."""
        keyword = "iPhone"
        results_page = home_page.search_for(keyword, use_enter=False)
        
        # Verify navigation to search URL
        current_url = results_page.get_current_url()
        decoded_url = urllib.parse.unquote(current_url)
        assert "search" in decoded_url, f"Expected 'search' in URL, got {decoded_url}"
        assert keyword.lower() in decoded_url.lower(), f"Expected keyword '{keyword}' in URL: {decoded_url}"

        # Verify products rendered
        product_count = results_page.get_product_count()
        assert product_count > 0, f"Expected product count > 0 for keyword '{keyword}', got {product_count}"

        # Verify product titles contain relevant brand/product terms
        titles = results_page.get_product_titles(limit=5)
        assert len(titles) > 0, "Should retrieve product titles"
        assert any("iphone" in t.lower() or "apple" in t.lower() for t in titles), (
            f"Expected at least one product title to contain 'iPhone' or 'Apple'. Titles: {titles}"
        )

    def test_search_by_enter_key(self, home_page: HomePage):
        """Verifies submitting search via keyboard 'Enter' key performs accurate query execution."""
        keyword = "除濕機"
        results_page = home_page.search_for(keyword, use_enter=True)

        current_url = results_page.get_current_url()
        decoded_url = urllib.parse.unquote(current_url)
        assert "search" in decoded_url, f"Expected 'search' in URL: {decoded_url}"
        assert keyword in decoded_url, f"Expected '{keyword}' in URL: {decoded_url}"

        product_count = results_page.get_product_count()
        assert product_count > 0, f"Expected products for '{keyword}', got {product_count}"

        titles = results_page.get_product_titles(limit=5)
        assert any(keyword in t or "除濕" in t for t in titles), (
            f"Expected search keyword in product titles. Got: {titles}"
        )

    @pytest.mark.parametrize("test_case", VALID_SEARCH_KEYWORDS, ids=[tc.keyword for tc in VALID_SEARCH_KEYWORDS])
    def test_parameterized_category_searches(self, home_page: HomePage, test_case: SearchTestCase):
        """Validates search across diverse categories (English, Chinese, alphanumeric, models)."""
        results_page = home_page.search_for(test_case.keyword)
        
        # Verify URL reflects the searched keyword
        decoded_url = urllib.parse.unquote(results_page.get_current_url())
        assert test_case.keyword.lower() in decoded_url.lower() or "search" in decoded_url

        # Verify products are returned for valid inventory items
        product_count = results_page.get_product_count()
        assert product_count > 0, (
            f"Failed category search for '{test_case.keyword}' ({test_case.category}): 0 products found"
        )

        # Verify product price integrity
        prices = results_page.get_product_prices(limit=5)
        assert len(prices) > 0, f"Prices should be displayed for '{test_case.keyword}'"
        assert all(p > 0 for p in prices), f"All product prices must be positive integers: {prices}"

    def test_secondary_search_from_results_page(self, home_page: HomePage):
        """Verifies performing a consecutive search from the Search Results page."""
        first_query = "iPad"
        second_query = "MacBook"

        results_page = home_page.search_for(first_query)
        assert results_page.get_product_count() > 0

        # Perform secondary search from results page
        results_page.search_again(second_query)
        decoded_url = urllib.parse.unquote(results_page.get_current_url())
        assert second_query.lower() in decoded_url.lower(), f"Expected '{second_query}' in URL: {decoded_url}"
        assert results_page.get_product_count() > 0

        titles = results_page.get_product_titles(limit=5)
        assert any("mac" in t.lower() or "apple" in t.lower() for t in titles), (
            f"Expected secondary search results to match '{second_query}'. Got: {titles}"
        )
