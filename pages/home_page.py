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

    def _wait_for_overlays_to_hidden(self, timeout: int = 20000) -> None:
        """Wait for common overlays to disappear to avoid interaction interception."""
        overlay_selectors = [
            "[data-testid='ad-overlay']",
            "[data-testid='app-redirect-overlay']",
            '[class*="mu-bg-black/40"]',
            '[class*="mu-bg-black/60"]'
        ]
        for overlay_selector in overlay_selectors:
            overlay = self.page.locator(overlay_selector)
            if overlay.count() > 0:
                print(f"[DEBUG] Waiting for overlay to be gone: {overlay_selector}")
                # Try multiple strategies to wait for overlay to be gone
                try:
                    # First, wait for it to be detached from DOM
                    overlay.wait_for(state="detached", timeout=timeout//2)
                    print(f"[DEBUG] Overlay detached: {overlay_selector}")
                except Exception:
                    try:
                        # If still attached, wait for it to be hidden
                        overlay.wait_for(state="hidden", timeout=timeout//3)
                        print(f"[DEBUG] Overlay hidden: {overlay_selector}")
                    except Exception:
                        try:
                            # If still not hidden, wait for it to not be visible
                            overlay.wait_for(state="hidden", timeout=timeout//6)
                            print(f"[DEBUG] Overlay not visible: {overlay_selector}")
                        except Exception:
                            # Final fallback: wait a bit and hope it's gone
                            print(f"[DEBUG] Timeout waiting for overlay, waiting 2s and continuing: {overlay_selector}")
                            self.page.wait_for_timeout(2000)
            else:
                print(f"[DEBUG] No overlay found for selector: {overlay_selector}")

    def _is_mobile_view(self) -> bool:
        """Detect if we're in a mobile view based on viewport or user agent."""
        try:
            # Check viewport size - mobile views typically have smaller width
            viewport_size = self.page.viewport_size
            if viewport_size:
                return viewport_size['width'] < 768  # Common mobile breakpoint

            # Fallback: check user agent for mobile indicators
            user_agent = self.page.evaluate("navigator.userAgent")
            mobile_indicators = ['iPhone', 'Android', 'iPad', 'Mobile']
            return any(indicator in user_agent for indicator in mobile_indicators)
        except Exception:
            return False

    @property
    def search_input(self) -> Locator:
        # If we're in mobile view, we need to handle the mobile search flow differently
        if self._is_mobile_view():
            # In mobile view, first try to find the search activation element
            # This is the element with aria-label containing "搜尋" that opens the search
            mobile_search_activator = self.page.locator("[aria-label*='搜尋' i]").first
            if mobile_search_activator.count() > 0:
                # Return the activator - the search flow will handle clicking it first
                return mobile_search_activator

        # Desktop view or fallback to original logic
        # Strategy 0: Find by data-testid (not empty) and interactable (not readonly, not aria-hidden)
        try:
            inputs = self.page.locator("input[data-testid]:not([data-testid=''])")
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                if (not inp.get_attribute("readonly") and
                    not inp.get_attribute("aria-hidden") and
                    inp.get_attribute("name") != "search-input-ticker"):
                    return inp
        except Exception:
            pass

        # Strategy 1: Find by placeholder text (most reliable for search input)
        # Look for inputs with search-related placeholders that are interactable
        search_placeholders = [
            "placeholder*='搜尋'",
            "placeholder*='商品'",
            "placeholder*='關鍵字'",
            "placeholder*='Search'",
            "placeholder*='search'"
        ]

        for placeholder in search_placeholders:
            # Find inputs with this placeholder that are not readonly and not aria-hidden
            inputs = self.page.locator(
                f"input[{placeholder}]:not([readonly]):not([aria-hidden])"
            )
            if inputs.count() > 0:
                # Additional filtering to exclude known ticker characteristics
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    # Double-check it's not the ticker by checking specific attributes
                    if (not inp.get_attribute("readonly") and
                        not inp.get_attribute("aria-hidden") and
                        inp.get_attribute("name") != "search-input-ticker"):
                        return inp
                # If all inputs with this placeholder failed the check, return first anyway
                return inputs.first

        # Strategy 2: Find by common search input patterns (more flexible)
        search_patterns = [
            "input#header-search-input",
            "input.search-input",
            "input[placeholder*='搜尋' i]",  # case-insensitive
            "input[placeholder*='商品' i]",
            "input[placeholder*='關鍵字' i]",
            "input[placeholder*='Search' i]",
            "[data-testid*='search' i] input",
            "input[name*='search' i]",
            "input[id*='search' i]"
        ]

        for pattern in search_patterns:
            try:
                inputs = self.page.locator(pattern)
                for i in range(inputs.count()):
                    inp = inputs.nth(i)
                    if (not inp.get_attribute("readonly") and
                        not inp.get_attribute("aria-hidden") and
                        inp.get_attribute("name") != "search-input-ticker"):
                        return inp
            except Exception:
                continue

        # Strategy 3: Find all text inputs and filter to get interactable ones
        # Expanded search scope beyond just header
        all_text_inputs = self.page.locator(
            "input[type='text'], input.search-input, input[placeholder]"
        )

        # Manually filter since filter() with lambda seems problematic
        interactable_inputs = []
        for i in range(all_text_inputs.count()):
            inp = all_text_inputs.nth(i)
            if (not inp.get_attribute("readonly") and
                not inp.get_attribute("aria-hidden") and
                inp.get_attribute("name") != "search-input-ticker"):
                interactable_inputs.append(inp)

        if interactable_inputs:
            # Among interactable inputs, prefer those with search-related placeholders
            for inp in interactable_inputs:
                placeholder = inp.get_attribute("placeholder") or ""
                if any(search_term in placeholder.lower() for search_term in ['搜尋', '商品', '關鍵字', 'search']):
                    return inp
            # If none have search placeholders, return the first interactable input
            return interactable_inputs[0]

        # Strategy 4: Fallback to original approach
        inputs = self.page.locator(
            "header input[type='text'], input.search-input, input[placeholder]"
        )

        # Filter out known ticker characteristics using has_not (try to make this work)
        try:
            filtered_inputs = inputs.filter(has_not=self.page.locator("[readonly]"))
            filtered_inputs = filtered_inputs.filter(has_not=self.page.locator("[aria-hidden='true']"))
            filtered_inputs = filtered_inputs.filter(has_not=self.page.locator("[name='search-input-ticker']"))
            ticker_class_locator = self.page.locator(".mu-absolute.mu-inset-0.mu-h-full.mu-w-full.mu-cursor-pointer.mu-opacity-0")
            if ticker_class_locator.count() > 0:
                filtered_inputs = filtered_inputs.filter(has_not=ticker_class_locator)

            if filtered_inputs.count() > 0:
                return filtered_inputs.first
        except Exception:
            pass  # If filtering fails, continue to fallback

        # Final fallback
        return self.page.locator(
            "header input[type='text'], input.search-input, input[placeholder]"
        ).first

    @property
    def search_button(self) -> Locator:
        # If we're in mobile view and the search input is an activator, we need to handle this specially
        if self._is_mobile_view():
            # Check if our search_input is actually the mobile search activator
            search_locator = self.page.locator("[aria-label*='搜尋' i]").first
            if search_locator.count() > 0:
                # In mobile view after clicking the activator, look for the actual search button
                # Common mobile search button patterns that appear after activator is clicked
                mobile_button_patterns = [
                    "button:has-text('搜尋')",
                    "button:has-text('Search')",
                    "[aria-label*='搜尋' i]:not([aria-label='搜尋框'])",  # Not the activator itself
                    "[aria-label*='search' i]:not([aria-label='搜尋框'])",
                    ".search-btn",
                    ".btn-search",
                    "[class*='search-btn']",
                    "[class*='btn-search']",
                    "input[type='submit']",
                    "button[type='submit']"
                ]

                for pattern in mobile_button_patterns:
                    btn = self.page.locator(pattern).first
                    if btn.count() > 0:
                        return btn

        # Desktop view or fallback to original logic
        # Try to find by common button patterns for search
        button_patterns = [
            # Text-based patterns
            "button:has-text('搜尋')",
            "button:has-text('搜索')",  # Simplified Chinese
            "button:has-text('Search')",  # English
            "input[type='submit'][value='搜尋']",
            "input[type='submit'][value='搜索']",
            "input[type='submit'][value='Search']",
            # Class-based patterns
            ".search-btn",
            ".btn-search",
            "[class*='search-btn']",
            "[class*='btn-search']",
            # ARIA and title attributes
            "button[aria-label*='搜尋' i]",  # Case-insensitive aria-label
            "button[title*='搜尋' i]",
            "[role='button'][aria-label*='搜尋' i]",
            # Type-based patterns (most reliable)
            "input[type='submit']",
            "button[type='submit']",
            # Form-based patterns
            "form button[type='submit']",
            "form input[type='submit']",
            # Generic button/role patterns (last resort)
            "button",
            "[role='button']"
        ]

        for pattern in button_patterns:
            locator = self.page.locator(pattern)
            if locator.count() > 0:
                return locator.first

        # Fallback to original locator
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
        # Handle mobile view where search_input might be the activator
        if self._is_mobile_view():
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                # Activators don't have meaningful placeholders, return empty or default
                return ""

        return self.search_input.get_attribute("placeholder") or ""

    def get_search_input_value(self) -> str:
        """Returns the current text in the search input field."""
        # Handle mobile view where we need to check if search is activated
        if self._is_mobile_view():
            # Check if we're in activated state by looking for actual search inputs
            actual_search_inputs = self.page.locator(
                "input[type='text']:not([name='search-input-ticker']):visible"
            )
            if actual_search_inputs.count() > 0:
                # Return the value of the first actual search input (not the ticker)
                return actual_search_inputs.first.input_value() or ""

        return self.search_input.input_value()

    def clear_search_input(self) -> None:
        """Clears the search input field."""
        self._wait_for_overlays_to_hidden()

        if self._is_mobile_view():
            # Mobile search flow: click activator, then clear the revealed input
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                # Wait for overlays to be hidden before clicking activator
                self._wait_for_overlays_to_hidden()
                activator.click(force=True)
                # Wait for search interface to appear
                self.page.wait_for_timeout(1000)

                # Now clear the actual search input (not the ticker)
                actual_search_input = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                ).first
                if actual_search_input.count() > 0:
                    # Wait for overlays to be hidden before clicking actual search input
                    self._wait_for_overlays_to_hidden()
                    actual_search_input.click(force=True)
                    actual_search_input.clear()
                return

        # Desktop view or fallback
        # Wait for overlays to be hidden before clicking search input
        self._wait_for_overlays_to_hidden()
        self.search_input.click(force=True)
        self.search_input.clear()

    def enter_search_keyword(self, keyword: str) -> None:
        """Fills the search input with a keyword."""
        self._wait_for_overlays_to_hidden()

        if self._is_mobile_view():
            # Mobile search flow: click activator, then enter keyword in revealed input
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                # Wait for overlays to be hidden before clicking activator
                self._wait_for_overlays_to_hidden()
                activator.click(force=True)
                # Wait for search interface to appear
                self.page.wait_for_timeout(1000)

                # Now enter keyword in the actual search input (not the ticker)
                actual_search_input = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                ).first
                if actual_search_input.count() > 0:
                    # Wait for overlays to be hidden before clicking actual search input
                    self._wait_for_overlays_to_hidden()
                    actual_search_input.click(force=True)
                    actual_search_input.fill(keyword)
                return

        # Desktop view or fallback
        # Wait for overlays to be hidden before filling search input
        self._wait_for_overlays_to_hidden()
        # Debug: print information about candidate inputs
        try:
            inputs = self.page.locator("input[data-testid]:not([data-testid=''])")
            print(f"[DEBUG] Found {inputs.count()} inputs with non-empty data-testid")
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                placeholder = inp.get_attribute("placeholder") or ""
                readonly = inp.get_attribute("readonly")
                aria_hidden = inp.get_attribute("aria-hidden")
                name = inp.get_attribute("name")
                print(f"[DEBUG] Input {i}: placeholder='{placeholder}', readonly={readonly}, aria-hidden={aria_hidden}, name='{name}'")
        except Exception as e:
            print(f"[DEBUG] Error checking data-testid inputs: {e}")
        print(f"[DEBUG] Entering keyword: {keyword}")
        print(f"[DEBUG] Search input placeholder: {self.search_input.get_attribute('placeholder')}")
        print(f"[DEBUG] Search input data-testid: {self.search_input.get_attribute('data-testid')}")
        print(f"[DEBUG] Search input readonly: {self.search_input.get_attribute('readonly')}")
        print(f"[DEBUG] Search input aria-hidden: {self.search_input.get_attribute('aria-hidden')}")
        print(f"[DEBUG] Search input name: {self.search_input.get_attribute('name')}")
        self.search_input.fill(keyword)

    def type_search_keyword_sequentially(self, keyword: str, delay: int = 50) -> None:
        """Types the keyword character by character to trigger auto-suggest."""
        self._wait_for_overlays_to_hidden()

        if self._is_mobile_view():
            # Mobile search flow: click activator, then type in revealed input
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                activator.click()
                # Wait for search interface to appear
                self.page.wait_for_timeout(1000)

                # Now type in the actual search input (not the ticker)
                actual_search_input = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                ).first
                if actual_search_input.count() > 0:
                    actual_search_input.click()
                    actual_search_input.press_sequentially(keyword, delay=delay)
                return

        # Desktop view or fallback
        self.search_input.press_sequentially(keyword, delay=delay)

    def click_search_button(self) -> SearchResultsPage:
        """Clicks the search button and returns the SearchResultsPage."""
        # Handle potential overlays that might block the search button
        self._wait_for_overlays_to_hidden()

        if self._is_mobile_view():
            # Mobile search flow: might need to click activator first if not already active
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                # Check if search is already activated by looking for visible search inputs
                visible_search_inputs = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                )
                if visible_search_inputs.count() == 0:
                    # Search not activated yet, click activator
                    # Wait for overlays to be hidden before clicking activator
                    self._wait_for_overlays_to_hidden()
                    activator.click(force=True)
                    # Wait for search interface to appear
                    self.page.wait_for_timeout(1000)

            # Now click the search button
            search_button = self.page.locator(
                "button:has-text('搜尋'), button:has-text('Search'), "
                "[aria-label*='搜尋' i]:not([aria-label='搜尋框']), "
                "[aria-label*='search' i]:not([aria-label='搜尋框']), "
                ".search-btn, .btn-search, input[type='submit']"
            ).first

            if search_button.count() > 0:
                print(f"[DEBUG] Mobile search button locator: {search_button}")
                print(f"[DEBUG] Mobile search button count: {search_button.count()}")
                if search_button.count() > 0:
                    print(f"[DEBUG] Mobile search button inner text: {search_button.first.inner_text()}")
                    print(f"[DEBUG] Mobile search button tag name: {search_button.first.evaluate('el => el.tagName')}")
                try:
                    # Try to click the search button
                    print("[DEBUG] Attempting regular click on mobile search button")
                    search_button.click()
                    print("[DEBUG] Regular click succeeded")
                except Exception as e:
                    print(f"[DEBUG] Regular click failed: {e}")
                    # If regular click fails due to overlays, try force click
                    try:
                        print("[DEBUG] Attempting force click on mobile search button")
                        search_button.click(force=True)
                        print("[DEBUG] Force click succeeded")
                    except Exception as e2:
                        print(f"[DEBUG] Force click failed: {e2}")
                        # If force click also fails, try the original approach
                        print("[DEBUG] Attempting original click again")
                        search_button.click()
                        print("[DEBUG] Original click succeeded")

                try:
                    print("[DEBUG] Waiting for URL to change to **/search/**")
                    self.page.wait_for_url("**/search/**", timeout=120000)
                    print("[DEBUG] URL changed to search")

                    # Wait for search results to load after URL change
                    print("[DEBUG] Waiting for search results to load...")
                    results_page = SearchResultsPage(self.page)
                    # Wait for either products to appear or a clear indication that search completed
                    try:
                        # Wait for network to be idle (indicates resources have loaded)
                        results_page.page.wait_for_load_state("networkidle", timeout=10000)
                        print("[DEBUG] Network idle reached")

                        # Additional wait for dynamic content to settle
                        results_page.page.wait_for_timeout(2000)
                        print("[DEBUG] Additional settle time completed")

                    except Exception as e:
                        print(f"[DEBUG] Timeout waiting for network idle: {e}")
                        # Fallback: wait for product items with longer timeout
                        try:
                            results_page.page.wait_for_selector(
                                ".listAreaLi, [id^='search-goods-item-'], .productItem, .goods-item",
                                timeout=DEFAULT_TIMEOUT
                            )
                            print("[DEBUG] Search results loaded successfully (via product selectors)")
                        except Exception as e2:
                            print(f"[DEBUG] Timeout waiting for product selectors: {e2}")
                            # Last resort: wait for page to have substantial content
                            try:
                                results_page.page.wait_for_function(
                                    "() => document.body.innerText.length > 1000",
                                    timeout=10000
                                )
                                print("[DEBUG] Page has substantial content")
                            except Exception as e3:
                                print(f"[DEBUG] Timeout waiting for substantial content: {e3}")
                                # Continue anyway - we'll let get_product_count handle timeouts

                except Exception as e:
                    print(f"[DEBUG] Waiting for URL timed out: {e}")
                    # Fallback: wait for search results page search input to be visible
                    try:
                        print("[DEBUG] Falling back to waiting for search results page search input")
                        results_page = SearchResultsPage(self.page)
                        results_page.search_input.wait_for(state="visible", timeout=10000)
                        print("[DEBUG] Search results page search input visible")
                    except Exception as e2:
                        print(f"[DEBUG] Fallback also timed out: {e2}")
                        self.page.wait_for_load_state("domcontentloaded")
                        print("[DEBUG] Waited for domcontentloaded")
                return SearchResultsPage(self.page)

        # Desktop view or fallback to original logic
        print(f"[DEBUG] Search button locator: {self.search_button}")
        print(f"[DEBUG] Search button count: {self.search_button.count()}")
        if self.search_button.count() > 0:
            print(f"[DEBUG] Search button inner text: {self.search_button.first.inner_text()}")
            print(f"[DEBUG] Search button tag name: {self.search_button.first.evaluate('el => el.tagName')}")
        try:
            # Try to click the search button
            print("[DEBUG] Attempting regular click on search button")
            self.search_button.click()
            print("[DEBUG] Regular click succeeded")
        except Exception as e:
            print(f"[DEBUG] Regular click failed: {e}")
            # If regular click fails due to overlays, try force click
            try:
                print("[DEBUG] Attempting force click on search button")
                self.search_button.click(force=True)
                print("[DEBUG] Force click succeeded")
            except Exception as e2:
                print(f"[DEBUG] Force click failed: {e2}")
                # If force click also fails, try the original approach
                print("[DEBUG] Attempting original click again")
                self.search_button.click()
                print("[DEBUG] Original click succeeded")

        try:
            print("[DEBUG] Waiting for URL to change to **/search/**")
            self.page.wait_for_url("**/search/**", timeout=120000)
            print("[DEBUG] URL changed to search")

            # Wait for search results to load after URL change
            print("[DEBUG] Waiting for search results to load...")
            results_page = SearchResultsPage(self.page)
            # Wait for either products to appear or a clear indication that search completed
            try:
                # Wait for network to be idle (indicates resources have loaded)
                results_page.page.wait_for_load_state("networkidle", timeout=10000)
                print("[DEBUG] Network idle reached")

                # Additional wait for dynamic content to settle
                results_page.page.wait_for_timeout(2000)
                print("[DEBUG] Additional settle time completed")

            except Exception as e:
                print(f"[DEBUG] Timeout waiting for network idle: {e}")
                # Fallback: wait for product items with longer timeout
                try:
                    results_page.page.wait_for_selector(
                        ".listAreaLi, [id^='search-goods-item-'], .productItem, .goods-item",
                        timeout=DEFAULT_TIMEOUT
                    )
                    print("[DEBUG] Search results loaded successfully (via product selectors)")
                except Exception as e2:
                    print(f"[DEBUG] Timeout waiting for product selectors: {e2}")
                    # Last resort: wait for page to have substantial content
                    try:
                        results_page.page.wait_for_function(
                            "() => document.body.innerText.length > 1000",
                            timeout=10000
                        )
                        print("[DEBUG] Page has substantial content")
                    except Exception as e3:
                        print(f"[DEBUG] Timeout waiting for substantial content: {e3}")
                        # Continue anyway - we'll let get_product_count handle timeouts

        except Exception as e:
            print(f"[DEBUG] Waiting for URL timed out: {e}")
            # Fallback: wait for search results page search input to be visible
            try:
                print("[DEBUG] Falling back to waiting for search results page search input")
                results_page = SearchResultsPage(self.page)
                results_page.search_input.wait_for(state="visible", timeout=10000)
                print("[DEBUG] Search results page search input visible")
            except Exception as e2:
                print(f"[DEBUG] Fallback also timed out: {e2}")
                self.page.wait_for_load_state("domcontentloaded")
                print("[DEBUG] Waited for domcontentloaded")
        return SearchResultsPage(self.page)

    def press_enter_to_search(self) -> SearchResultsPage:
        """Submits the search query by pressing the Enter key."""
        if self._is_mobile_view():
            # Mobile search flow: ensure search is activated, then press enter in search input
            activator = self.page.locator("[aria-label*='搜尋' i]").first
            if activator.count() > 0:
                # Check if search is already activated by looking for visible search inputs
                visible_search_inputs = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                )
                if visible_search_inputs.count() == 0:
                    # Search not activated yet, click activator
                    activator.click()
                    # Wait for search interface to appear
                    self.page.wait_for_timeout(1000)

            # Now press Enter in the actual search input (not the ticker)
            actual_search_input = self.page.locator(
                "input[type='text']:not([name='search-input-ticker']):visible"
            ).first
            if actual_search_input.count() > 0:
                actual_search_input.click()
                actual_search_input.press("Enter")
            else:
                # Fallback: press enter on the activator itself
                activator.press("Enter")
        else:
            # Desktop view or fallback
            self.search_input.press("Enter")

        try:
            self.page.wait_for_url("**/search/**", timeout=120000)
        except Exception:
            # Fallback: wait for search results page search input to be visible
            try:
                results_page = SearchResultsPage(self.page)
                results_page.search_input.wait_for(state="visible", timeout=10000)
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