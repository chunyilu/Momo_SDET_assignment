"""Test data sets for Momo SDET Search Test Suite."""

from dataclasses import dataclass
from typing import List


@dataclass
class SearchTestCase:
    keyword: str
    expected_matches: bool
    category: str
    description: str


# Standard Search Keywords (Positive Test Cases)
VALID_SEARCH_KEYWORDS = [
    SearchTestCase(
        keyword="iPhone",
        expected_matches=True,
        category="Consumer Electronics",
        description="Global tech brand keyword in English"
    ),
    SearchTestCase(
        keyword="除濕機",
        expected_matches=True,
        category="Home Appliances",
        description="High volume seasonal home appliance in Traditional Chinese"
    ),
    SearchTestCase(
        keyword="Nintendo Switch",
        expected_matches=True,
        category="Gaming",
        description="Multi-word gaming console keyword"
    ),
    SearchTestCase(
        keyword="衛生紙",
        expected_matches=True,
        category="Daily Commodities",
        description="FMCG daily consumer staple keyword"
    ),
    SearchTestCase(
        keyword="SONY WH-1000XM5",
        expected_matches=True,
        category="Audio",
        description="Specific model number with hyphen and letters"
    ),
]

# Non-existent & Zero-Result Test Cases
NON_EXISTENT_KEYWORDS = [
    "xyzqwertyuiop9876543210zzz",
    "___nonexistent_product_momo_test___",
    "qwerty12345xyz99999",
]

# Edge Cases & Special Characters
EDGE_CASE_KEYWORDS = [
    "   ",                         # Pure whitespace
    "✨📱",                         # Unicode Emojis
    "iPhone / iPad + Mac",        # Special symbols (+, /, spaces)
    "\"Apple\"",                  # Enclosed double quotes
    "C&A",                        # Ampersand symbol
    "A" * 120,                    # Extremely long keyword string
]

# Security & Injection Sanitization Test Cases
SECURITY_PAYLOADS = [
    "<script>alert('xss')</script>",
    "'; DROP TABLE products; --",
    "' OR '1'='1",
    "<img src=x onerror=alert(1)>",
]
