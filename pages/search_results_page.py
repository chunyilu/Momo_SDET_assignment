"""Page Object representing the Momo E-Commerce Search Results Page."""

import re
import urllib.parse
from typing import List, Optional
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.config import SHORT_TIMEOUT, DEFAULT_TIMEOUT


class SearchResultsPage(BasePage):
    """Encapsulates locators and user actions on Momo Search Results Page."""

    def __init__(self, page: Page):
        super().__init__(page)

    @property
    def search_input(self) -> Locator:
        return self.page.locator(
            "input#header-search-input, input.search-input, input[placeholder]"
        ).first

    @property
    def search_button(self) -> Locator:
        return self.page.locator(
            "button:has-text('搜尋'), input[type='submit'][value='搜尋'], .search-btn"
        ).first

    @property
    def product_items(self) -> Locator:
        return self.page.locator(".listAreaLi, [id^='search-goods-item-']")

    @property
    def no_results_container(self) -> Locator:
        return self.page.locator(
            "div:has-text('很抱歉，查無'), div:has-text('您可以調整關鍵字試試看'), .noResultArea, .emptyPrdArea"
        )

    @property
    def sort_relevance_btn(self) -> Locator:
        return self.page.locator(".menuSearchType li.accuracyPrd, #searchType li.accuracyPrd").first

    @property
    def sort_popularity_btn(self) -> Locator:
        return self.page.locator(".menuSearchType li.popularPrd, #searchType li.popularPrd").first

    @property
    def sort_newest_btn(self) -> Locator:
        return self.page.locator(".menuSearchType li.newPrd, #searchType li.newPrd").first

    @property
    def sort_price_btn(self) -> Locator:
        return self.page.locator(".menuSearchType li.priceHeight, #searchType li.priceHeight").first

    @property
    def attr_list(self) -> Locator:
        return self.page.locator("#attrList, .attrList")

    @property
    def pagination_area(self) -> Locator:
        return self.page.locator(".pageArea:not(.topPage), .pageArea").last

    @property
    def next_page_btn(self) -> Locator:
        return self.page.locator("div:has-text('下一頁'), a:has-text('＞')").last

    def get_product_count(self) -> int:
        """Returns the number of product cards rendered on the page."""
        try:
            self.page.wait_for_selector(".listAreaLi, [id^='search-goods-item-']", timeout=SHORT_TIMEOUT)
            return self.product_items.count()
        except Exception:
            return 0

    def get_product_titles(self, limit: int = 30) -> List[str]:
        """Extracts text titles of displayed products."""
        titles: List[str] = []
        count = min(self.product_items.count(), limit)
        for i in range(count):
            item = self.product_items.nth(i)
            # Find title via heading or image alt attribute
            title_loc = item.locator("h3, h4, h2, .prdName, a[title]").first
            title = ""
            if title_loc.count() > 0:
                title = title_loc.inner_text().strip()
            if not title:
                img_loc = item.locator("img[alt]").first
                if img_loc.count() > 0:
                    title = img_loc.get_attribute("alt") or ""
            if title:
                titles.append(title)
        return titles

    def get_product_prices(self, limit: int = 30, exclude_ad: bool = False) -> List[int]:
        """Extracts and parses integer prices of displayed products."""
        prices: List[int] = []
        total_items = self.product_items.count()
        for i in range(total_items):
            if len(prices) >= limit:
                break
            item = self.product_items.nth(i)
            item_text = item.inner_text().strip()
            
            # Skip sponsored ad banners when strictly validating organic prices
            if exclude_ad and (item_text.startswith("Ad\n") or item_text.startswith("Ad ")):
                continue

            spans = item.locator("span, b, p").all()
            for s in spans:
                text = s.inner_text().strip().replace(",", "")
                match = re.search(r"^\d{2,7}$", text)
                if match:
                    val = int(match.group(0))
                    if val > 0:
                        prices.append(val)
                        break
        return prices

    def is_no_results_found(self) -> bool:
        """Returns True if the 'no results found' message is visible or 0 products loaded."""
        try:
            self.page.wait_for_timeout(300)
        except Exception:
            pass
        body_text = self.page.locator("body").inner_text()
        return "很抱歉，查無" in body_text or "您可以調整關鍵字試試看" in body_text or self.get_product_count() == 0

    def get_no_results_message(self) -> str:
        """Returns the text message displayed when no products match the query."""
        if self.is_no_results_found():
            body_text = self.page.locator("body").inner_text()
            for line in body_text.splitlines():
                if "很抱歉，查無" in line or "相關商品" in line:
                    return line.strip()
        return ""

    def sort_by_relevance(self) -> None:
        """Sorts products by relevance (綜合推薦)."""
        self.sort_relevance_btn.scroll_into_view_if_needed()
        self.sort_relevance_btn.click()
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    def sort_by_popularity(self) -> None:
        """Sorts products by monthly sales popularity (月銷量, searchType=6)."""
        self.sort_popularity_btn.scroll_into_view_if_needed()
        self.sort_popularity_btn.click()
        try:
            self.page.wait_for_url("**searchType=6**", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")

    def sort_by_newest(self) -> None:
        """Sorts products by newest releases (新上市, searchType=5)."""
        self.sort_newest_btn.scroll_into_view_if_needed()
        self.sort_newest_btn.click()
        try:
            self.page.wait_for_url("**searchType=5**", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")

    def sort_by_price_low_to_high(self) -> None:
        """Sorts products by price ascending (Low -> High, searchType=3)."""
        current_url = self.page.url
        if "searchType=3" not in current_url:
            self.sort_price_btn.scroll_into_view_if_needed()
            self.sort_price_btn.click()
            try:
                self.page.wait_for_url("**searchType=3**", timeout=DEFAULT_TIMEOUT)
            except Exception:
                if "searchType=3" not in self.page.url:
                    self.sort_price_btn.click()
                    self.page.wait_for_load_state("domcontentloaded")

    def sort_by_price_high_to_low(self) -> None:
        """Sorts products by price descending (High -> Low, searchType=2)."""
        current_url = self.page.url
        if "searchType=2" not in current_url:
            self.sort_price_btn.scroll_into_view_if_needed()
            self.sort_price_btn.click()
            try:
                self.page.wait_for_url("**searchType=2**", timeout=DEFAULT_TIMEOUT)
            except Exception:
                if "searchType=2" not in self.page.url:
                    self.sort_price_btn.click()
                    self.page.wait_for_load_state("domcontentloaded")

    def apply_filter(self, filter_label: str) -> None:
        """Applies an attribute/category filter by clicking its label."""
        label_locator = self.page.locator(
            f"#attrList label[title*='{filter_label}'], #attrList label:has-text('{filter_label}'), label[title*='{filter_label}']"
        ).first
        label_locator.scroll_into_view_if_needed()
        label_locator.click()
        try:
            self.page.wait_for_url("**attr=**", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")

    def go_to_page(self, page_number: int) -> None:
        """Navigates to a specific pagination page."""
        page_btn = self.page.locator(
            f".pageArea:not(.topPage) .pagination-link:text-is('{page_number}'), "
            f".pageArea .pagination-item a:text-is('{page_number}')"
        ).last
        page_btn.scroll_into_view_if_needed()
        page_btn.click()
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    def get_active_page_number(self) -> int:
        """Returns the currently active page number."""
        selected_elem = self.page.locator(".pagination-link.selected").last
        if selected_elem.count() > 0:
            text = selected_elem.inner_text().strip()
            if text.isdigit():
                return int(text)
        return 1

    def search_again(self, keyword: str) -> None:
        """Performs a new search directly from the Search Results page."""
        self.search_input.click()
        self.search_input.fill(keyword)
        self.search_button.click()
        try:
            self.page.wait_for_url(f"**/search/*{keyword}*", timeout=DEFAULT_TIMEOUT)
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")
