"""Page Object representing the Momo E-Commerce Home Page."""

from typing import List, Optional
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from pages.search_results_page import SearchResultsPage
from config.config import BASE_URL, SHORT_TIMEOUT, DEFAULT_TIMEOUT


class HomePage(BasePage):
    """Encapsulates locators and user actions on Momo Shopping Homepage (Main.jsp)."""

    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def search_input(self) -> Locator:
        return self.page.locator(
            "header input[type='text'], input.search-input, input[placeholder]"
        ).first

    @property
    def search_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('搜尋'), input[type='submit'][value='搜尋'], .search-btn"
        ).first

    @property
    def hot_search_popup(self) -> Locator:
        return self.page.locator(
            "div[class*='pop'], div[class*='popup'], div[class*='recommend']"
        )

    @property
    def hot_keywords(self) -> Locator:
        return self.page.locator(
            "header a[href*='search'], header a[href*='keyword'], div[class*='keyword'] a"
        )

    def load(self) -> "HomePage":
        """Navigates to Momo main page and waits for DOM to be ready."""
        self.navigate_to(BASE_URL, wait_until="load")
        return self

    def get_search_placeholder(self) -> str:
        """Returns the search input placeholder text."""
        return self.search_input.get_attribute("placeholder") or ""

    def get_search_input_value(self) -> str:
        """Returns the current text in the search input field."""
        return self.search_input.input_value()

    def clear_search_input(self) -> None:
        """Clears the search input field."""
        self.search_input.click()
        self.search_input.clear()

    def enter_search_keyword(self, keyword: str) -> None:
        """Fills the search input with a keyword."""
        self.search_input.click()
        self.search_input.fill(keyword)

    def type_search_keyword_sequentially(self, keyword: str, delay: int = 50) -> None:
        """Types the keyword character by character to trigger auto-suggest."""
        self.search_input.click()
        self.search_input.press_sequentially(keyword, delay=delay)

    def click_search_button(self) -> SearchResultsPage:
        """Clicks the search button and returns the SearchResultsPage."""
        self.search_button.click()
        try:
            self.page.wait_for_url("**/search/**", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")
        return SearchResultsPage(self.page)

    def press_enter_to_search(self) -> SearchResultsPage:
        """Submits the search query by pressing the Enter key."""
        self.search_input.press("Enter")
        try:
            self.page.wait_for_url("**/search/**", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")
        return SearchResultsPage(self.page)

    def search_for(self, keyword: str, use_enter: bool = False) -> SearchResultsPage:
        """High-level utility to perform a search from the home page."""
        self.clear_search_input()
        self.enter_search_keyword(keyword)
        if use_enter:
            return self.press_enter_to_search()
        return self.click_search_button()

    def get_visible_hot_keywords(self) -> List[str]:
        """Returns visible hot keyword texts."""
        elements = self.hot_keywords.all()
        return [el.inner_text().strip() for el in elements if el.is_visible() and el.inner_text().strip()]
