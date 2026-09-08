"""Configuration settings for Momo SDET Search Test Automation Suite."""

import os

BASE_URL = os.getenv("BASE_URL", "https://www.momoshop.com.tw/main/Main.jsp")
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))  # ms
SHORT_TIMEOUT = int(os.getenv("SHORT_TIMEOUT", "5000"))  # ms
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # ms

# Viewport & User Agent Configuration
VIEWPORT = {"width": 1920, "height": 1080}
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
