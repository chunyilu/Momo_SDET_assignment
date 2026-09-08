"""Test Suite: Search Input Auto-complete & Suggestions on Momo Platform."""

import pytest
from pages.home_page import HomePage


@pytest.mark.regression
class TestSearchSuggestions:
    """Validates search input interaction, typing events, suggestions and clearing behavior."""

    def test_search_input_type_and_clear(self, home_page: HomePage):
        """Validates typing into the search bar, checking input value, and clearing."""
        keyword = "PlayStation 5"
        home_page.enter_search_keyword(keyword)
        assert home_page.get_search_input_value() == keyword, "Search input should reflect typed value"

        home_page.clear_search_input()
        assert home_page.get_search_input_value() == "", "Search input should be empty after clear"

    def test_search_input_focus_interaction(self, home_page: HomePage):
        """Validates focusing on search bar and verifying interactive status."""
        home_page.search_input.click()
        home_page.page.wait_for_timeout(500)
        
        # Verify search input is enabled and editable
        assert home_page.search_input.is_editable(), "Search input should be editable on focus"

    def test_sequential_typing_responsiveness(self, home_page: HomePage):
        """Validates sequential keystroke typing simulating realistic human input."""
        keyword = "Dyson"
        home_page.type_search_keyword_sequentially(keyword, delay=40)
        assert home_page.get_search_input_value() == keyword, "Search input should match sequential typed text"

        # Execute search and verify success
        results = home_page.click_search_button()
        assert results.get_product_count() > 0, "Products should load after sequential typing search"
