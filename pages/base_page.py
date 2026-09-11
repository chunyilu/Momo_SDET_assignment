"""Base Page Object with common functionality."""

from playwright.sync_api import Page


class BasePage:
    """Base page object with common functionality."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str, wait_until: str = "load") -> "BasePage":
        """Navigates to a URL."""
        self.page.goto(url, wait_until=wait_until)
        return self

    def is_element_visible(self, locator) -> bool:
        """Checks if an element is visible."""
        try:
            return locator.count() > 0 and locator.first.is_visible()
        except Exception:
            return False

    def get_current_url(self) -> str:
        """Returns the current URL of the page."""
        return self.page.url

    def _wait_for_overlays_to_hidden(self, timeout: int = 10000) -> None:
        """Wait for blocking overlays to disappear to avoid interaction interception.

        This method distinguishes between:
        1. Blocking overlays (ads, app-redirect overlays) that block interactions
        2. Useful overlays (like mobile search overlay) that contain interactive elements
        """
        # Only wait for truly blocking overlays to disappear
        blocking_overlay_selectors = [
            "[data-testid='ad-overlay']",
            "[data-testid='app-redirect-overlay']",
            # Note: We do NOT wait for mobile-search-overlay to disappear because
            # it contains the actual search input we need to interact with in mobile view
        ]

        for overlay_selector in blocking_overlay_selectors:
            overlay = self.page.locator(overlay_selector)
            if overlay.count() > 0:
                try:
                    overlay.wait_for(state="hidden", timeout=timeout)
                except Exception:
                    # If timeout, continue anyway - the overlay might not block in all cases
                    pass