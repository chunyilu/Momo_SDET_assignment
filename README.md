# Momo Shopping Search Test Automation Framework (SDET)

An enterprise-grade, end-to-end test automation framework built with **Python**, **pytest**, and **Playwright** designed to rigorously validate the search ecosystem on [momo購物網 (momoshop.com.tw)](https://www.momoshop.com.tw/main/Main.jsp).

---

## 1. Executive Summary & Design Philosophy

The search functionality on an e-commerce platform is the primary driver of product discovery, conversion rate, and revenue generation. Defects in query resolution, result relevancy, filtering, or sorting directly harm user experience and business outcomes.

To maximize test utility and return on investment (ROI), this framework focuses on:
- **Flakiness Reduction**: Dynamic locator evaluation and explicit state transition synchronization instead of fragile fixed sleeps.
- **Organic vs. Sponsored Integrity**: Explicit handling for pinned advertisement products (`Ad`) to ensure algorithmic sorting assertions remain strictly valid.
- **Fast Feedback Loop**: Session-scoped browser sharing with isolated per-test contexts for optimal test execution speed and zero test leakage.
- **Maintainability**: Strict adherence to the Page Object Model (POM) separating DOM locators and page actions from test assertions.

---

## 2. Framework Architecture

```
Momo_SDET_assignment/
├── config/
│   ├── __init__.py
│   └── config.py               # Environment variables, timeouts, viewports, headers
├── data/
│   ├── __init__.py
│   └── search_test_data.py     # Parameterized test datasets, edge cases, security payloads
├── pages/
│   ├── __init__.py
│   ├── base_page.py            # Reusable UI interactions, screenshot captures, navigation
│   ├── home_page.py            # Momo HomePage POM (search bar, hot keywords, triggers)
│   └── search_results_page.py  # SearchResultsPage POM (cards, prices, sort, filter, pagination)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures (browser, context, page, failure screenshots)
│   ├── test_search_basic.py    # Core query execution (click, enter, parameterized categories)
│   ├── test_search_suggestions.py # Keystroke responsiveness, input clearing, focus
│   ├── test_search_sorting_filtering.py # Popularity, newest, price toggle, spec filtering
│   ├── test_search_pagination.py # Multi-page navigation, page index integrity
│   ├── test_search_edge_cases.py # Zero-results, blank queries, boundary strings
│   └── test_search_security.py   # XSS payload sanitization and SQL injection resilience
├── reports/
│   ├── test_report.html        # Self-contained HTML test report
│   └── screenshots/            # Automated failure capture artifacts
├── conftest.py                 # Root pytest configuration & screenshot hook
├── pytest.ini                  # Markers, test discovery paths, reporting flags
├── requirements.txt            # Dependency manifest
└── run_tests.sh                # Executable test runner script
```

---

## 3. Test Coverage Matrix

| Test Suite | Test Cases Covered | Key Verifications |
| :--- | :--- | :--- |
| **`test_search_basic.py`** | 6 test scenarios | • Homepage search input & button visibility<br>• Query submission via Search Button click<br>• Query submission via keyboard `Enter`<br>• Parameterized multi-category searches (English, Chinese, alphanumeric)<br>• Product title relevancy matching<br>• Secondary query from Search Results page |
| **`test_search_suggestions.py`** | 3 test scenarios | • Input field value persistence & clear mechanism<br>• Search bar focus states<br>• Sequential keystroke typing (`press_sequentially`) |
| **`test_search_sorting_filtering.py`** | 4 test scenarios | • Monthly sales popularity sort (`searchType=6`)<br>• Newest product release sort (`searchType=5`)<br>• Price sort toggle (Low-to-High `searchType=3` / High-to-Low `searchType=2`)<br>• Dynamic attribute filter application (`attr=...`) |
| **`test_search_pagination.py`** | 2 test scenarios | • Navigation from Page 1 to Page 2<br>• Verification that Page 2 product offset differs from Page 1<br>• Active pagination indicator status verification |
| **`test_search_edge_cases.py`** | 10 test scenarios | • Blank/empty query submission handling<br>• Non-existent inventory queries display friendly "很抱歉，查無相關商品"<br>• Symbols (`+`, `/`, `&`, `""`), Unicode emojis (`✨📱`), boundary strings (>100 chars) |
| **`test_search_security.py`** | 4 test scenarios | • Cross-Site Scripting (XSS) payload sanitization (no unauthorized popups)<br>• SQL Injection syntax safety (no backend error leakages or 500 status) |

---

## 4. Engineering & SDET Highlights

### A. Resilient Locator Strategies
Momo Shopping's frontend combines modern Tailwind utility classes with dynamic IDs. The framework uses structural fallback selectors (e.g. `input#header-search-input, input.search-input, input[placeholder]`) to withstand UI layout changes across different viewport dimensions and AB experiments.

### B. Organic vs. Sponsored Ad Separation
In e-commerce search results, sponsored/advertising products (`Ad`) are pinned to the top of the list regardless of user-selected sort order. The `get_product_prices` helper contains intelligent filtering (`exclude_ad=True`) to validate algorithmic sorting accuracy without false positives triggered by sponsored placement.

### C. Automated Failure Artifacts
The `pytest_runtest_makereport` hook automatically takes full-resolution screenshots at the exact moment of failure and saves them to `reports/screenshots/FAIL_<test_name>.png`, drastically lowering triage time.

---

## 5. Prerequisites & Quick Start

### Prerequisites
- Python 3.10+
- Linux / macOS / Windows WSL2

### Installation

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browser binaries
playwright install chromium
```

---

## 6. Running the Tests

### Using the Test Runner Script
```bash
# Run all 32 tests
./run_tests.sh all

# Run high-priority Smoke tests
./run_tests.sh smoke

# Run Full Regression suite
./run_tests.sh regression

# Run Sorting & Filtering tests
./run_tests.sh filter-sort

# Run Edge Case & Security tests
./run_tests.sh edge-case

# Run in Headed mode (with browser UI visible)
./run_tests.sh headed
```

### Direct Pytest Invocations
```bash
# Run all tests with HTML report
pytest

# Run only smoke tests
pytest -m smoke

# Run a specific test module
pytest tests/test_search_basic.py

# Run in headed mode with custom slow-motion
pytest --headed --slowmo=200
```

---

## 7. Test Reporting

Upon completion, pytest generates a self-contained HTML report at:
`reports/test_report.html`

Open the report in any browser:
```bash
# Linux
xdg-open reports/test_report.html

# macOS
open reports/test_report.html
```

---

## 8. Continuous Integration (CI/CD)

The suite is designed for frictionless integration with GitHub Actions or GitLab CI.

### GitHub Actions Workflow Example (`.github/workflows/e2e-tests.yml`):
```yaml
name: Momo E2E Search Tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  schedule:
    - cron: '0 2 * * *' # Nightly regression run

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: 'pip'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium
      - name: Execute Pytest Suite
        run: pytest
      - name: Upload Test Report & Screenshots
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-artifacts
          path: |
            reports/test_report.html
            reports/screenshots/
```
