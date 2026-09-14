"""Page Object representing the Momo E-Commerce Search Results Page."""

import re
import urllib.parse
import math
from typing import List, Optional
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.config import SHORT_TIMEOUT, DEFAULT_TIMEOUT


class SearchResultsPage(BasePage):
    """Encapsulates locators and user actions on Momo Search Results Page."""

    # Momo renders a separate card structure for the mobile site.  Keep these
    # selectors together so every product helper interrogates the same cards.
    PRODUCT_ITEM_SELECTOR = (
        ".listAreaLi, [id^='search-goods-item-'], .productItem, .goods-item, "
        ".mobile .home article > ul > li"
    )
    PRODUCT_TITLE_SELECTORS = [
        ".content-info__goods-title-box h3",
        ".content-info__goods-title-box",
        ".product-title",
        ".goods-title",
        "[class*='title']",
        "img[alt]",
        ".product-name",
        ".goods-name",
    ]

    def __init__(self, page: Page):
        super().__init__(page)

    def _is_mobile_view(self) -> bool:
        """Detect if we're in a mobile view based on viewport or user agent."""
        try:
            # Check viewport size - mobile views typically have smaller width
            viewport_size = self.page.viewport_size
            if viewport_size:
                return viewport_size['width'] < 768  # Common mobile breakpoint

            # Fallback: check user agent for mobile indicators
            user_agent = self.page.evaluate("navigator.userAgent").lower()
            mobile_indicators = ['iphone', 'android', 'ipad', 'mobile']
            return any(indicator in user_agent for indicator in mobile_indicators)
        except Exception:
            return False

    def _wait_for_overlays_to_disappear(self, timeout: int = 1000) -> None:
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
                try:
                    overlay.wait_for(state="hidden", timeout=timeout)
                except Exception:
                    pass  # Continue if timeout occurs

    def _get_product_elements(self) -> Locator:
        """Get product item locator with flexible selectors."""
        return self.page.locator(self.PRODUCT_ITEM_SELECTOR)

    def _extract_product_title(self, item: Locator) -> str:
        """Extract meaningful title from a product item element."""
        # Try multiple selectors for product title
        for title_selector in self.PRODUCT_TITLE_SELECTORS:
            title_element = item.locator(title_selector).first
            if title_element.count() > 0:
                title_text = title_element.inner_text().strip()
                if title_text:
                    return title_text

        # Fallback: try to get title from img alt attribute
        img_element = item.locator("img").first
        if img_element.count() > 0:
            alt_text = img_element.get_attribute("alt")
            if alt_text and alt_text.strip():
                return alt_text.strip()

        # Final fallback: use item's text content and extract meaningful title
        item_text = item.inner_text().strip()
        if item_text:
            # Take first line or first meaningful chunk as title
            lines = [line.strip() for line in item_text.split('\n') if line.strip()]
            if lines:
                # Skip lines that look like prices, prices, or ads
                filtered_lines = [line for line in lines if not (
                    line.startswith('Ad') or
                    line.startswith('$') or
                    line.startswith('NT$') or
                    line.startswith('¥') or
                    (any(c.isdigit() for c in line[:10]) and ('$' in line or 'NT' in line or '¥' in line))
                )]
                if filtered_lines:
                    return filtered_lines[0][:100]  # Limit title length
                else:
                    return lines[0][:100]  # Limit title length

        return "Unknown Product"

    def _wait_for_products_to_stabilize(self, max_attempts: int = 5, delay: int = 1000) -> int:
        """Wait for product count to stabilize and return stable count."""
        stable_count = 0
        for attempt in range(max_attempts):
            # Wait for overlays to disappear before each count check
            self._wait_for_overlays_to_disappear()
            current_count = self._get_product_elements().count()

            if current_count == stable_count and current_count > 0:
                return current_count

            stable_count = current_count
            if attempt < max_attempts - 1:  # Don't wait after last attempt
                self.page.wait_for_timeout(delay)

        return stable_count

    @property
    def search_input(self) -> Locator:
        """Get search input locator with mobile/desktop adaptation."""
        if self._is_mobile_view():
            # In mobile view on search results page, look for visible search inputs
            # Exclude the ticker input
            mobile_search_inputs = self.page.locator(
                "input[type='text']:not([name='search-input-ticker']):visible"
            )
            if mobile_search_inputs.count() > 0:
                return mobile_search_inputs.first

        # Try multiple selectors for search input that work in both desktop and mobile
        selectors = [
            "input#header-search-input",
            "input.search-input",
            "input[placeholder*='搜尋' i]",
            "input[placeholder*='商品' i]",
            "input[placeholder*='關鍵字' i]",
            "input[placeholder*='Search' i]",
            "[data-testid*='search' i] input",
            "input[name*='search' i]",
            "input[id*='search' i]",
            "input[type='text']"  # fallback
        ]

        for selector in selectors:
            locator = self.page.locator(selector).first
            if locator.count() > 0:
                return locator

        # Final fallback to original selector
        return self.page.locator(
            "input#header-search-input, input.search-input, input[placeholder]"
        ).first

    @property
    def search_button(self) -> Locator:
        """Get search button locator with mobile/desktop adaptation."""
        if self._is_mobile_view():
            # In mobile view, look for visible search buttons
            mobile_search_buttons = self.page.locator(
                "button:visible, input[type='submit']:visible, [role='button']:visible"
            ).filter(
                has_text="搜尋"
            ).or_(
                self.page.locator(
                    "button:visible, input[type='submit']:visible, [role='button']:visible"
                ).filter(
                    has_text="Search"
                )
            ).or_(
                self.page.locator(
                    "[aria-label*='搜尋' i]:visible, [aria-label*='search' i]:visible"
                )
            )

            if mobile_search_buttons.count() > 0:
                return mobile_search_buttons.first

        # Try multiple selectors for search button
        selectors = [
            "button:has-text('搜尋')",
            "button:has-text('搜索')",
            "button:has-text('Search')",
            "input[type='submit'][value='搜尋']",
            "input[type='submit'][value='搜索']",
            "input[type='submit'][value='Search']",
            ".search-btn",
            ".btn-search",
            "[class*='search-btn']",
            "[class*='btn-search']",
            "button[type='submit']",
            "[role='button'][aria-label*='搜尋' i]",
            "[role='button'][title*='搜尋' i]"
        ]

        for selector in selectors:
            locator = self.page.locator(selector).first
            if locator.count() > 0:
                return locator

        # Final fallback to original selector
        return self.page.locator(
            "button:has-text('搜尋'), input[type='submit'][value='搜尋'], .search-btn"
        ).first

    @property
    def product_items(self) -> Locator:
        """Get product items locator."""
        return self._get_product_elements()

    @property
    def no_results_container(self) -> Locator:
        """Get no results container locator."""
        return self.page.locator(".noResultText > div:nth-child(1)").first

    @property
    def sort_relevance_btn(self) -> Locator:
        """Get sort by relevance button locator."""
        return self.page.locator(".menuSearchType li.accuracyPrd, #searchType li.accuracyPrd").first

    @property
    def sort_popularity_btn(self) -> Locator:
        """Get sort by popularity button locator."""
        return self.page.locator(".menuSearchType li.popularPrd, #searchType li.popularPrd").first

    @property
    def sort_newest_btn(self) -> Locator:
        """Get sort by newest button locator."""
        return self.page.locator(".menuSearchType li.newPrd, #searchType li.newPrd").first

    @property
    def sort_price_btn(self) -> Locator:
        """Get sort by price button locator."""
        return self.page.locator(".menuSearchType li.priceHeight, #searchType li.priceHeight").first

    @property
    def attr_list(self) -> Locator:
        """Get attribute list locator."""
        return self.page.locator("#attrList, .attrList")

    @property
    def pagination_area(self) -> Locator:
        """Get pagination area locator."""
        return self.page.locator(".pageArea:not(.topPage), .pageArea").last

    @property
    def next_page_button(self) -> Locator:
        """Get next page button locator."""
        return self.page.locator("div:has-text('下一頁'), a:has-text('＞')").last

    @property
    def previous_page_button(self) -> Locator:
        """Get previous page button locator."""
        return self.page.locator("div:has-text('上一頁'), a:has-text('＜')").last

    @property
    def filters_container(self) -> Locator:
        """Get the mobile or desktop filters container."""
        return self.page.locator(".filterMenu, .filterWindow, #attrList, .attrList").first

    def get_product_count(self) -> int:
        """Returns the number of product cards rendered on the page."""
        # Wait for overlays to disappear to avoid interaction interception
        self._wait_for_overlays_to_disappear()

        # Wait a bit for initial page settlement
        self.page.wait_for_timeout(2000)

        # Strategy 1: Wait for product items with increased timeout
        try:
            self.page.wait_for_selector(
                self.PRODUCT_ITEM_SELECTOR,
                timeout=10000  # Reasonable timeout for mobile
            )

            # Wait a bit more for potential lazy loading
            self.page.wait_for_timeout(2000)

            # Wait for overlays to disappear before counting
            self._wait_for_overlays_to_disappear()

            # Get stable count
            count = self._wait_for_products_to_stabilize()
            if count > 0:
                return count
        except Exception:
            pass

        # Strategy 2: Try to find products using JavaScript evaluation
        try:
            js_count = self.page.evaluate("""
                () => {
                    // Common product selectors for Momo mobile
                    const selectors = [
                        '.listAreaLi',
                        '[id^="search-goods-item-"]',
                        '.productItem',
                        '.goods-item',
                        '.mobile .home article > ul > li',
                        '.item',
                        '[class*="product"]',
                        '[class*="goods"]',
                        'div[pid]',
                        'li[data-item]'
                    ];

                    let maxCount = 0;
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > maxCount) {
                                maxCount = elements.length;
                            }
                        } catch (e) {
                            // Continue trying other selectors
                        }
                    }

                    // If still no products, look for elements with product-like characteristics
                    if (maxCount === 0) {
                        const allElements = document.querySelectorAll('div, li, article');
                        let productLikeCount = 0;

                        allElements.forEach(el => {
                            const rect = el.getBoundingClientRect();
                            // Reasonable size for product items
                            if (rect.width > 50 && rect.height > 50 &&
                                rect.width < 1200 && rect.height < 1200) {
                                const hasText = el.innerText.trim().length > 0;
                                const hasImg = el.querySelector('img') !== null;
                                const hasPrice = /[\\d,]+\\s*元/.test(el.innerText);

                                // Count as product-like if it has text or image (and not just a price wrapper)
                                if ((hasText || hasImg) && !hasPrice) {
                                    productLikeCount++;
                                }
                            }
                        });

                        return productLikeCount;
                    }

                    return maxCount;
                }
            """)

            if js_count > 0:
                return int(js_count)
        except Exception:
            pass

        # Strategy 3: Final fallback with original selectors and reasonable timeout
        try:
            self.page.wait_for_selector(
                self.PRODUCT_ITEM_SELECTOR,
                timeout=8000
            )
            # Wait for overlays to disappear before final count
            self._wait_for_overlays_to_disappear()
            return self._get_product_elements().count()
        except Exception:
            return 0

    def get_product_titles(self, limit: int = 30) -> List[str]:
        """Extracts text titles of displayed products."""
        # Wait for overlays to disappear to avoid interaction interception
        self._wait_for_overlays_to_disappear()

        # Wait a bit for initial page settlement
        self.page.wait_for_timeout(2000)

        # Strategy 1: Wait for product items with increased timeout
        try:
            self.page.wait_for_selector(
                self.PRODUCT_ITEM_SELECTOR,
                timeout=10000  # Increased timeout for mobile
            )

            # Wait a bit more for potential lazy loading
            self.page.wait_for_timeout(2000)

            # Wait for overlays to disappear before counting
            self._wait_for_overlays_to_disappear()

            count = self._get_product_elements().count()
            if count > 0:
                # Wait for stabilization
                stable_count = self._wait_for_products_to_stabilize()
                if stable_count > 0:
                    # Extract actual product titles
                    titles = []
                    for i in range(min(stable_count, limit)):
                        item = self._get_product_elements().nth(i)
                        # Wait a bit for content to load
                        self.page.wait_for_timeout(300)
                        # Wait for overlays to disappear before accessing item
                        self._wait_for_overlays_to_disappear()
                        title = self._extract_product_title(item)
                        titles.append(title)
                    return titles
        except Exception:
            pass

        # Strategy 2: Try to find products using JavaScript evaluation
        try:
            js_count = self.page.evaluate("""
                () => {
                    // Common product selectors for Momo mobile
                    const selectors = [
                        '.listAreaLi',
                        '[id^="search-goods-item-"]',
                        '.productItem',
                        '.goods-item',
                        '.mobile .home article > ul > li',
                        '.item',
                        '[class*="product"]',
                        '[class*="goods"]',
                        'div[pid]',
                        'li[data-item]'
                    ];

                    let maxCount = 0;
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > maxCount) {
                                maxCount = elements.length;
                            }
                        } catch (e) {
                            // Continue trying other selectors
                        }
                    }

                    // If still no products, look for elements with product-like characteristics
                    if (maxCount === 0) {
                        const allElements = document.querySelectorAll('div, li, article');
                        let productLikeCount = 0;

                        allElements.forEach(el => {
                            const rect = el.getBoundingClientRect();
                            // Reasonable size for product items
                            if (rect.width > 50 && rect.height > 50 &&
                                rect.width < 1200 && rect.height < 1200) {
                                const hasText = el.innerText.trim().length > 0;
                                const hasImg = el.querySelector('img') !== null;
                                const hasPrice = /[\\d,]+\\s*元/.test(el.innerText);

                                // Count as product-like if it has text or image (and not just a price wrapper)
                                if ((hasText || hasImg) && !hasPrice) {
                                    productLikeCount++;
                                }
                            }
                        });

                        return productLikeCount;
                    }

                    return maxCount;
                }
            """)

            if js_count > 0:
                count = min(int(js_count), limit)
                # Extract actual product titles using JavaScript
                titles = self.page.evaluate(f"""
                    () => {{
                        const selectors = [
                            '.listAreaLi',
                            '[id^="search-goods-item-"]',
                            '.productItem',
                            '.goods-item',
                            '.mobile .home article > ul > li'
                        ];
                        let items = [];
                        for (const selector of selectors) {{
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {{
                                items = elements;
                                break;
                            }}
                        }}
                        if (items.length === 0) {{
                            return [];
                        }}
                        const titles = [];
                        for (let i = 0; i < Math.min({count}, items.length); i++) {{
                            const item = items[i];
                            let title = '';
                            // Try multiple selectors for product title
                            const titleSelectors = [
                                '.content-info__goods-title-box h3',
                                '.content-info__goods-title-box',
                                '.product-title',
                                '.goods-title',
                                '[class*="title"]',
                                'img[alt]',
                                '.product-name',
                                '.goods-name'
                            ];
                            for (const selector of titleSelectors) {{
                                const element = item.querySelector(selector);
                                if (element) {{
                                    if (selector.includes('img[alt]')) {{
                                        title = element.alt?.trim() || '';
                                    }} else {{
                                        title = element.innerText?.trim() || '';
                                    }}
                                    if (title) {{
                                        break;
                                    }}
                                }}
                            }}
                            // Fallback: use item's text content and extract meaningful title
                            if (!title) {{
                                const itemText = item.innerText?.trim() || '';
                                if (itemText) {{
                                    // Take first line or first meaningful chunk as title
                                    const lines = itemText.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
                                    if (lines.length > 0) {{
                                        // Skip lines that look like prices, prices, or ads
                                        const filteredLines = lines.filter(line => !(
                                            line.startsWith('Ad') ||
                                            line.startsWith('$') ||
                                            line.startsWith('NT$') ||
                                            line.startsWith('¥') ||
                                            (/[\\d,]/.test(line.substring(0, 10)) && /[\\$NT¥]/.test(line))
                                        ));
                                        if (filteredLines.length > 0) {{
                                            title = filteredLines[0].substring(0, 100);
                                        }} else {{
                                            title = lines[0].substring(0, 100);
                                        }}
                            }}
                            }}
                            titles.push(title);
                        }}
                        return titles;
                    }}
                """)
                return titles
        except Exception:
            pass

        # Strategy 3: Final fallback with original selectors and longer timeout
        try:
            self.page.wait_for_selector(
                self.PRODUCT_ITEM_SELECTOR,
                timeout=8000
            )
            # Wait for overlays to disappear before counting
            self._wait_for_overlays_to_disappear()
            count = min(self._get_product_elements().count(), limit)

            # Extract actual product titles
            titles = []
            for i in range(count):
                item = self._get_product_elements().nth(i)
                # Wait a bit for content to load
                self.page.wait_for_timeout(300)
                # Wait for overlays to disappear before accessing item
                self._wait_for_overlays_to_disappear()
                title = self._extract_product_title(item)
                titles.append(title)
            return titles
        except Exception:
            # Never manufacture titles: a fake value can make a test report
            # look like a relevance failure when extraction was the real issue.
            return []

    def get_product_prices(self, limit: int = 30, exclude_ad: bool = False) -> List[int]:
        """Extracts and parses integer prices of displayed products."""
        # Wait for overlays to disappear
        self._wait_for_overlays_to_disappear()

        # Wait briefly for products to load
        self.page.wait_for_timeout(2000)

        # Extract prices using JavaScript evaluation
        try:
            js_prices = self.page.evaluate(f"""
                () => {{
                    const prices = [];
                    const items = document.querySelectorAll(".listAreaLi, [id^='search-goods-item-'], .productItem, .goods-item");
                    const limit = {limit};

                    for (let i = 0; i < Math.min(items.length, limit); i++) {{
                        const item = items[i];
                        let price = null;
                        const itemText = item.innerText || '';
                        if ({str(exclude_ad).lower()} && /^Ad\\s*$/m.test(itemText)) {{
                            continue;
                        }}

                        // Mobile titles contain model numbers and capacities.
                        // Read the currency-marked sale price before examining
                        // generic elements so those numbers are not misread.
                        const currencyMatch = itemText.match(/(?:NT\\$|\\$)\\s*([\\d,]+)/);
                        if (currencyMatch) {{
                            price = parseInt(currencyMatch[1].replace(/,/g, ''), 10);
                        }}

                        // Try common price selectors
                        const selectors = ['.price', '[class*="price"]', '.money', '[class*="money"]', 'span', 'b'];

                        for (const selector of selectors) {{
                            if (price !== null) break;
                            const elements = item.querySelectorAll(selector);
                            for (let j = 0; j < Math.min(elements.length, 2); j++) {{
                                const text = elements[j]?.innerText?.trim();
                                if (text && text.length > 0) {{
                                    // Extract digits and decimal points only
                                    const numMatch = text.match(/[\\d,]+\\.?\\d*/);
                                    if (numMatch) {{
                                        const numStr = numMatch[0].replace(/,/g, '');
                                        const priceFloat = parseFloat(numStr);
                                        const priceInt = Math.floor(priceFloat);
                                        if (!isNaN(priceInt) && priceInt > 0 && priceInt < 1000000) {{
                                            price = priceInt;
                                            break;
                                        }}
                                    }}
                                }}
                            }}
                            if (price !== null) break;
                        }}

                        // Fallback: extract from item text
                        if (price === null) {{
                            if (itemText) {{
                                // Look for sequences of digits that look like prices
                                const numMatches = itemText.match(/\\b\\d{{2,6}}\\b/g);
                                if (numMatches) {{
                                    for (const numStr of numMatches) {{
                                        const priceInt = parseInt(numStr, 10);
                                        // Filter for reasonable price range and exclude obvious non-prices
                                        if (!isNaN(priceInt) &&
                                            priceInt >= 50 &&      // Minimum reasonable price
                                            priceInt <= 500000 &&  // Maximum reasonable price
                                            priceInt !== 2024 &&   // Exclude years
                                            priceInt !== 2025 &&   // Exclude years
                                            priceInt !== 12 &&     // Exclude months
                                            priceInt !== 24 &&     // Exclude hours
                                            priceInt !== 60) {{
                                            price = priceInt;
                                            break;
                                        }}
                                    }}
                                }}
                            }}
                        }}

                        if (price !== null) {{
                            prices.push(price);
                        }}
                    }}
                    return prices;
                }}
            """)

            print(f"[DEBUG] JavaScript extracted prices: {js_prices}")
            if js_prices and len(js_prices) > 0:
                # Validate prices
                valid_prices = [p for p in js_prices if isinstance(p, (int, float)) and not (isinstance(p, float) and math.isnan(p)) and 0 < p < 1000000]
                # Convert to int if needed
                valid_prices = [int(p) for p in valid_prices]
                if valid_prices:
                    print(f"[DEBUG] Valid prices after validation: {valid_prices}")
                    return valid_prices[:limit]
        except Exception as e:
            print(f"[DEBUG] JavaScript price extraction failed: {e}")
            # If JavaScript fails, fall back to simple text extraction
            pass

        # Fallback: Simple text-based extraction
        prices: List[int] = []
        total_items = self._get_product_elements().count()
        print(f"[DEBUG] Fallback: total product items found: {total_items}")

        for i in range(total_items):
            if len(prices) >= limit:
                break

            item = self._get_product_elements().nth(i)
            try:
                item_text = item.inner_text()
                print(f"[DEBUG] Item {i} text: {item_text[:200]}")  # Limit to 200 chars
                if item_text:
                    if exclude_ad and item_text.lstrip().startswith("Ad"):
                        continue
                    import re
                    # Model numbers and capacities can be numeric. The first
                    # currency-marked amount is the displayed sale price.
                    price_matches = re.findall(r"(?:NT\$|\$)\s*([\d,]+)", item_text)
                    print(f"[DEBUG] Item {i} currency prices: {price_matches}")
                    for match in price_matches:
                        try:
                            price_int = int(match.replace(",", ""))
                            if 50 <= price_int <= 500000 and price_int not in [2024, 2025, 12, 24, 60]:
                                prices.append(price_int)
                                print(f"[DEBUG] Item {i} accepted price: {price_int}")
                                break  # Take first valid price per item
                            else:
                                print(f"[DEBUG] Item {i} rejected price {price_int} (out of range or excluded)")
                        except ValueError:
                            print(f"[DEBUG] Item {i} failed to convert {match} to int")
                            continue
            except Exception as e:
                print(f"[DEBUG] Item {i} caused exception: {e}")
                continue  # Skip problematic items

        print(f"[DEBUG] Final prices list: {prices}")
        return prices

    def is_no_results_found(self) -> bool:
        """Returns True if the no-results message is visible."""
        try:
            self.page.wait_for_timeout(300)
            if self.no_results_container.count() > 0 and self.no_results_container.is_visible():
                message = self.no_results_container.inner_text().strip()
                return "很抱歉，查無" in message and "相關商品" in message
        except Exception:
            pass

        body_text = self.page.locator("body").inner_text()
        return "很抱歉，查無" in body_text and "相關商品" in body_text

    def get_no_results_message(self) -> str:
        """Returns the text message displayed when no products match the query."""
        try:
            if self.no_results_container.count() > 0:
                return self.no_results_container.inner_text().strip()
        except Exception:
            pass

        body_text = self.page.locator("body").inner_text()
        for line in body_text.splitlines():
            if "很抱歉，查無" in line and "相關商品" in line:
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

    def click_next_page(self) -> None:
        """Clicks the next page button."""
        self.next_page_button.scroll_into_view_if_needed()
        self.next_page_button.click()
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    def click_previous_page(self) -> None:
        """Clicks the previous page button."""
        self.previous_page_button.scroll_into_view_if_needed()
        self.previous_page_button.click()
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    def get_filter_options_count(self) -> int:
        """Returns the number of available filter options."""
        return self.attr_list.locator("label").count()

    def apply_filter_by_index(self, index: int) -> None:
        """Applies a filter by its index in the filter list."""
        filter_labels = self.attr_list.locator("label")
        if filter_labels.count() > index:
            label_text = filter_labels.nth(index).inner_text().strip()
            self.apply_filter(label_text)

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
        # Wait for overlays to disappear
        self._wait_for_overlays_to_disappear()

        if self._is_mobile_view():
            # Mobile view: need to click search activator first if not already in search mode
            # Check if we already have a visible search input (not the ticker)
            visible_search_input = self.page.locator(
                "input[type='text']:not([name='search-input-ticker']):visible"
            ).first

            if visible_search_input.count() == 0:
                # Need to activate search first
                search_activator = self.page.locator("[aria-label*='搜尋' i]").first
                if search_activator.count() > 0:
                    search_activator.click()
                    # Wait for search interface to appear instead of fixed timeout
                    try:
                        self.page.wait_for_selector(
                            "input[type='text']:not([name='search-input-ticker']):visible",
                            timeout=5000
                        )
                    except Exception:
                        self.page.wait_for_timeout(1000)  # Fallback

                    # Now enter keyword in the activated search input
                    visible_search_input = self.page.locator(
                        "input[type='text']:not([name='search-input-ticker']):visible"
                    ).first
                    if visible_search_input.count() > 0:
                        visible_search_input.click()
                        visible_search_input.fill(keyword)
                    else:
                        # Fallback: try to find any visible input
                        inputs = self.page.locator("input:visible")
                        if inputs.count() > 0:
                            inputs.first.click()
                            inputs.first.fill(keyword)
                else:
                    # No activator found, try direct input
                    inputs = self.page.locator("input:visible")
                    if inputs.count() > 0:
                        inputs.first.click()
                        inputs.first.fill(keyword)

            # Now click the search button
            search_button = self.page.locator(
                "button:has-text('搜尋'), button:has-text('Search'), "
                "[aria-label*='搜尋' i]:not([aria-label='搜尋框']), "
                "[aria-label*='search' i]:not([aria-label='搜尋框']), "
                ".search-btn, .btn-search, input[type='submit']"
            ).first
            if search_button.count() > 0:
                search_button.click()
            else:
                # Fallback: press Enter in the search input
                visible_search_input = self.page.locator(
                    "input[type='text']:not([name='search-input-ticker']):visible"
                ).first
                if visible_search_input.count() > 0:
                    visible_search_input.press("Enter")
        else:
            # Desktop view or fallback
            self.search_input.click()
            self.search_input.fill(keyword)
            self.search_button.click()

        try:
            self.page.wait_for_url(f"**/search/*{keyword}*", timeout=60000)
        except Exception:
            # Fallback: wait for search results page search input to be visible
            try:
                self.search_input.wait_for(state="visible", timeout=10000)
            except Exception:
                self.page.wait_for_load_state("domcontentloaded")
