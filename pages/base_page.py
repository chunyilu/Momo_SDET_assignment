"""Base Page class for Momo E-Commerce UI Automation Framework."""

import os
from typing import Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from config.config import DEFAULT_TIMEOUT, SHORT_TIMEOUT


class BasePage:
    """Provides common browser interactions, robust wait strategies, and utility methods."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to(self, url: str, wait_until: str = "load") -> None:
        """Navigates to a specific URL with error handling and default timeout."""
        self.page.goto(url, wait_until=wait_until, timeout=DEFAULT_TIMEOUT)

    def get_title(self) -> str:
        """Returns the current page title."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Returns the current page URL."""
        return self.page.url

    def wait_for_url_contains(self, fragment: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Waits until URL contains the given substring."""
        try:
            self.page.wait_for_url(f"**/*{fragment}*", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_load_state(self, state: str = "domcontentloaded") -> None:
        """Waits for page load state (domcontentloaded, load, networkidle)."""
        self.page.wait_for_load_state(state, timeout=DEFAULT_TIMEOUT)

    def is_element_visible(self, locator: Locator, timeout: int = SHORT_TIMEOUT) -> bool:
        """Checks if a locator element is visible within timeout."""
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except (PlaywrightTimeoutError, Exception):
            return False

    def take_screenshot(self, file_name: str, directory: str = "reports/screenshots") -> str:
        """Takes a full page screenshot for reporting and debugging."""
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{file_name}.png")
        self.page.screenshot(path=file_path, full_page=False)
        return file_path
