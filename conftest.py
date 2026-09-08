"""Pytest configuration and shared fixtures for Momo SDET Test Automation."""

import os
import pytest
from typing import Generator
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
from config.config import BASE_URL, DEFAULT_TIMEOUT, HEADLESS, SLOW_MO, USER_AGENT, VIEWPORT
from pages.home_page import HomePage


def pytest_addoption(parser):
    """Adds CLI options for custom test execution control."""
    try:
        parser.addoption(
            "--custom-slowmo",
            action="store",
            default=str(SLOW_MO),
            help="Custom slowdown for Playwright operations in milliseconds",
        )
    except Exception:
        pass


@pytest.fixture(scope="session")
def browser_instance(playwright: Playwright, request) -> Generator[Browser, None, None]:
    """Session-scoped browser instance for resource optimization."""
    slowmo_val = SLOW_MO
    try:
        slowmo_val = int(request.config.getoption("--custom-slowmo"))
    except Exception:
        pass

    browser = playwright.chromium.launch(
        headless=HEADLESS,
        slow_mo=slowmo_val,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser_instance: Browser) -> Generator[BrowserContext, None, None]:
    """Function-scoped context ensuring complete test isolation."""
    context = browser_instance.new_context(
        viewport=VIEWPORT,
        user_agent=USER_AGENT,
        locale="zh-TW",
        timezone_id="Asia/Taipei",
        accept_downloads=True,
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Function-scoped page fixture with default timeout."""
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    yield page
    page.close()


@pytest.fixture(scope="function")
def home_page(page: Page) -> HomePage:
    """Provides a pre-loaded instance of the Momo HomePage."""
    home = HomePage(page)
    home.load()
    return home


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Automatically captures screenshots upon test failure for root-cause analysis."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page_fixture = item.funcargs.get("page", None)
        if page_fixture:
            screenshot_dir = os.path.join(os.getcwd(), "reports", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            sanitized_name = item.name.replace("/", "_").replace("::", "_").replace("[", "_").replace("]", "_")
            screenshot_path = os.path.join(screenshot_dir, f"FAIL_{sanitized_name}.png")
            try:
                page_fixture.screenshot(path=screenshot_path, full_page=False)
                print(f"\n[Artifact] Failure screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"\n[Warning] Could not capture screenshot: {e}")
