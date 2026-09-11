"""Test Suite: Search Results Sorting & Filtering on Momo Platform."""

import urllib.parse
import pytest
from pages.home_page import HomePage


@pytest.mark.filter_sort
@pytest.mark.regression
class TestSearchSortingFiltering:
    """Validates sorting controls (relevance, sales popularity, newest, price) and attribute filters."""

    def test_sort_by_popularity(self, home_page: HomePage):
        """Validates sorting search results by monthly sales popularity (月銷量)."""
        results_page = home_page.search_for("iPhone")
        assert results_page.get_product_count() > 0

        # Sort by popularity
        results_page.sort_by_popularity()
        assert results_page.get_product_count() > 0, "Products should be displayed when sorted by popularity"
        
        # Verify URL reflects popularity searchType (searchType=6)
        current_url = results_page.get_current_url()
        assert "searchType=6" in current_url or "popular" in current_url.lower(), (
            f"Expected searchType=6 in URL for popularity sort. Got: {current_url}"
        )

    def test_sort_by_newest(self, home_page: HomePage):
        """Validates sorting search results by newest releases (新上市)."""
        results_page = home_page.search_for("iPad")
        assert results_page.get_product_count() > 0

        results_page.sort_by_newest()
        assert results_page.get_product_count() > 0, "Products should be displayed when sorted by newest"
        
        # Verify URL reflects newest searchType (searchType=5)
        current_url = results_page.get_current_url()
        assert "searchType=5" in current_url or "searchType=4" in current_url or "new" in current_url.lower(), (
            f"Expected searchType=5 in URL for newest sort. Got: {current_url}"
        )

    def test_sort_by_price_toggle(self, home_page: HomePage):
        """Validates price sort toggle (High to Low and Low to High) with price ordering verification."""
        results_page = home_page.search_for("iPad")
        assert results_page.get_product_count() > 0

        # 1. Sort Price Low to High
        results_page.sort_by_price_low_to_high()
        assert "searchType=3" in results_page.get_current_url(), (
            f"Expected searchType=3 for Low-to-High sort: {results_page.get_current_url()}"
        )
        assert results_page.get_product_count() > 0

        # Verify prices are sorted correctly (low to high)
        prices_with_ads = results_page.get_product_prices(limit=10, exclude_ad=False)
        prices_without_ads = results_page.get_product_prices(limit=10, exclude_ad=True)

        # Check that organic prices (without ads) are sorted correctly
        if len(prices_without_ads) >= 2:
            assert all(prices_without_ads[i] <= prices_without_ads[i+1]
                      for i in range(len(prices_without_ads)-1)), \
                f"Organic prices not sorted Low-to-High: {prices_without_ads}"

        # 2. Sort Price High to Low
        results_page.sort_by_price_high_to_low()
        assert "searchType=2" in results_page.get_current_url(), (
            f"Expected searchType=2 for High-to-Low sort: {results_page.get_current_url()}"
        )
        assert results_page.get_product_count() > 0

        # Verify prices are sorted correctly (high to low)
        prices_with_ads = results_page.get_product_prices(limit=10, exclude_ad=False)
        prices_without_ads = results_page.get_product_prices(limit=10, exclude_ad=True)

        # Check that organic prices (without ads) are sorted correctly
        if len(prices_without_ads) >= 2:
            assert all(prices_without_ads[i] >= prices_without_ads[i+1]
                      for i in range(len(prices_without_ads)-1)), \
                f"Organic prices not sorted High-to-Low: {prices_without_ads}"

    def test_attribute_filter_application(self, home_page: HomePage):
        """Validates applying an attribute filter (e.g. spec or brand) refines the search result set."""
        results_page = home_page.search_for("iPad")
        initial_count = results_page.get_product_count()
        assert initial_count > 0

        # Apply a visible attribute filter
        filter_label = "無線"
        results_page.apply_filter(filter_label)

        # Verify URL reflects filter parameters
        current_url = results_page.get_current_url()
        decoded_url = urllib.parse.unquote(current_url)
        assert "attr=" in current_url or "attrNo=" in current_url or filter_label in decoded_url, (
            f"Expected filter query in URL, got {decoded_url}"
        )

        # Verify filtered products exist
        filtered_count = results_page.get_product_count()
        assert filtered_count > 0, "Filtered result set should contain products"
