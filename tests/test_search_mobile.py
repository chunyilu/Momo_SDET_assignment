"""Test Suite: Mobile Search Functionality on Momo E-Commerce Platform."""
import urllib.parse
import pytest
from playwright.sync_api import Playwright, Page
from pages.home_page import HomePage
from data.search_test_data import VALID_SEARCH_KEYWORDS, SearchTestCase


@pytest.fixture(scope="function")
def mobile_page(playwright: Playwright) -> Page:
    """Create a mobile browser context using iPhone 14 device emulation."""
    mobile_device = playwright.devices['iPhone 14']
    browser = playwright.chromium.launch(
        headless=True,  # Can be overridden by environment variable
        slow_mo=0,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    context = browser.new_context(**mobile_device)
    page = context.new_page()
    yield page
    context.close()
    browser.close()


@pytest.fixture(scope="function")
def mobile_home_page(mobile_page: Page) -> HomePage:
    """Provides a pre-loaded instance of the Momo HomePage for mobile."""
    home = HomePage(mobile_page)
    home.load()
    return home


@pytest.mark.mobile
@pytest.mark.smoke
class TestSearchMobileBasic:
    """Validates core search execution flows on mobile devices."""

    def test_mobile_search_ui_elements_present(self, mobile_home_page: HomePage):
        """Validates that search input and button are visible on mobile homepage."""
        assert mobile_home_page.is_element_visible(mobile_home_page.search_input), \
            "Search input should be visible on mobile homepage"
        assert mobile_home_page.is_element_visible(mobile_home_page.search_button), \
            "Search button should be visible on mobile homepage"

    @pytest.mark.parametrize("test_case", VALID_SEARCH_KEYWORDS[:3], ids=[tc.keyword for tc in VALID_SEARCH_KEYWORDS[:3]])
    def test_mobile_search_by_button_click(self, mobile_home_page: HomePage, test_case: SearchTestCase):
        """Verifies searching by clicking the search button returns relevant products on mobile."""
        keyword = test_case.keyword
        results_page = mobile_home_page.search_for(keyword, use_enter=False)

        # Verify navigation to search URL
        current_url = results_page.get_current_url()
        decoded_url = urllib.parse.unquote(current_url)
        assert "search" in decoded_url, f"Expected 'search' in URL, got {decoded_url}"
        assert keyword.lower() in decoded_url.lower(), \
            f"Expected keyword '{keyword}' in URL: {decoded_url}"

        # Verify products rendered
        product_count = results_page.get_product_count()
        assert product_count > 0, f"Expected product count > 0 for keyword '{keyword}', got {product_count}"

        # Verify product titles contain relevant terms
        titles = results_page.get_product_titles(limit=3)
        assert len(titles) > 0, "Should retrieve product titles"
        # Check for at least one relevant term in titles
        relevant_terms = [keyword.lower(), test_case.category.lower()] if test_case.category else [keyword.lower()]
        assert any(any(term in t.lower() for term in relevant_terms) for t in titles), \
            f"Expected at least one product title to contain relevant terms {relevant_terms}. Titles: {titles}"

    def test_mobile_search_by_enter_key(self, mobile_home_page: HomePage):
        """Verifies submitting search via keyboard 'Enter' key performs accurate query execution on mobile."""
        keyword = "iPhone"
        results_page = mobile_home_page.search_for(keyword, use_enter=True)

        current_url = results_page.get_current_url()
        decoded_url = urllib.parse.unquote(current_url)
        assert "search" in decoded_url, f"Expected 'search' in URL: {decoded_url}"
        assert keyword.lower() in decoded_url.lower(), f"Expected '{keyword}' in URL: {decoded_url}"

        product_count = results_page.get_product_count()
        assert product_count > 0, f"Expected products for '{keyword}', got {product_count}"

        titles = results_page.get_product_titles(limit=3)
        assert any("iphone" in t.lower() or "apple" in t.lower() for t in titles), (
            f"Expected at least one product title to contain 'iPhone' or 'Apple'. Got: {titles}"
        )


@pytest.mark.mobile
class TestSearchMobileSortingFiltering:
    """Validates sorting and filtering functionality on mobile."""

    def test_mobile_sort_by_price_toggle(self, mobile_home_page: HomePage):
        """Verifies price sorting toggle works correctly on mobile (low to high / high to low)."""
        keyword = "手機"
        results_page = mobile_home_page.search_for(keyword)

        # Get initial prices (default sort: relevance)
        initial_prices = results_page.get_product_prices(exclude_ad=True, limit=10)
        assert len(initial_prices) > 0, "Should have products to sort"

        # Apply price low-to-high sort
        results_page.sort_by_price_low_to_high()
        low_to_high_prices = results_page.get_product_prices(exclude_ad=True, limit=10)
        assert len(low_to_high_prices) > 0, "Should have products after sorting"

        # Verify prices are sorted in ascending order
        assert low_to_high_prices == sorted(low_to_high_prices), \
            f"Prices should be sorted low to high. Got: {low_to_high_prices}"

        # Apply price high-to-low sort
        results_page.sort_by_price_high_to_low()
        high_to_low_prices = results_page.get_product_prices(exclude_ad=True, limit=10)
        assert len(high_to_low_prices) > 0, "Should have products after sorting"

        # Verify prices are sorted in descending order
        assert high_to_low_prices == sorted(high_to_low_prices, reverse=True), \
            f"Prices should be sorted high to low. Got: {high_to_low_prices}"

    def test_mobile_filter_by_category(self, mobile_home_page: HomePage):
        """Verifies category filtering works on mobile."""
        keyword = "筆電"
        results_page = mobile_home_page.search_for(keyword)

        # Apply a category filter (e.g., notebooks)
        # Note: This assumes there's a filter for "筆記型電腦" category
        # We'll use a generic approach: try to apply the first available filter
        # For simplicity, we'll test that filter UI is present and applicable
        # In a real scenario, we'd know specific filter values from the UI
        assert results_page.is_element_visible(results_page.filters_container), \
            "Filters container should be visible on search results page"

        # Try to apply a filter if available
        if results_page.get_filter_options_count() > 0:
            # Select the first filter option
            results_page.apply_filter_by_index(0)
            # Verify that the filter was applied (URL should contain filter parameter)
            current_url = results_page.get_current_url()
            # We just verify that something changed - in a real test we'd check for specific parameter
            assert "filter" in current_url or "cat" in current_url, \
                f"Expected filter parameters in URL after applying filter. URL: {current_url}"
        else:
            pytest.skip("No filter options available for this keyword")


@pytest.mark.mobile
class TestSearchMobilePagination:
    """Validates multi-page navigation on mobile."""

    def test_mobile_pagination_next_previous(self, mobile_home_page: HomePage):
        """Verifies next and previous page navigation works on mobile."""
        keyword = "電視"
        results_page = mobile_home_page.search_for(keyword)

        # Ensure we have multiple pages of results
        assert results_page.is_element_visible(results_page.next_page_button), \
            "Next page button should be visible for pagination test"

        # Go to next page
        results_page.click_next_page()
        assert results_page.is_element_visible(results_page.previous_page_button), \
            "Previous page button should be visible after navigating to next page"

        # Verify page number increased
        current_page = results_page.get_current_page_number()
        assert current_page == 2, f"Expected page 2 after clicking next, got page {current_page}"

        # Go back to previous page
        results_page.click_previous_page()
        assert results_page.get_current_page_number() == 1, \
            "Expected page 1 after clicking previous from page 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])