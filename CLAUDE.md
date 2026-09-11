# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔧 Common Development Commands

### Test Execution
```bash
# Run all tests (default)
./run_tests.sh all

# Run specific test suites
./run_tests.sh smoke        # High-priority core tests
./run_tests.sh regression   # Full regression suite
./run_tests.sh filter-sort  # Sorting & filtering tests
./run_tests.sh edge-case    # Edge cases & security tests
./run_tests.sh headed       # Run with visible browser UI

# Direct pytest invocations
pytest                      # All tests with HTML report
pytest -m smoke             # Only smoke tests
pytest tests/test_search_basic.py  # Specific test file
pytest -k "price"           # Tests matching keyword
pytest --headed --slowmo=200  # Headed mode with slow motion
```

### Environment Setup
```bash
# Initialize development environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Code Quality
```bash
# View latest test report
xdg-open reports/test_report.html  # Linux
open reports/test_report.html      # macOS

# Check for failing tests
pytest --tb=short -x  # Stop on first failure
```

## 🏗️ Code Architecture & Structure

### Project Layout
```
Momo_SDET_assignment/
├── tests/                 # Test suites organized by functionality
│   ├── test_search_basic.py          # Core search flows (submit, navigation)
│   ├── test_search_suggestions.py    # Input responsiveness & focus
│   ├── test_search_sorting_filtering.py # Sort options & filters
│   ├── test_search_pagination.py     # Multi-page navigation
│   ├── test_search_edge_cases.py     # Empty queries, special chars
│   └── test_search_security.py       # XSS & SQLi resilience
├── pages/                 # Page Object Models (POM)
│   ├── base_page.py           # Shared UI interactions & utilities
│   ├── home_page.py           # Homepage elements & actions
│   └── search_results_page.py # Results page elements & actions
├── config/                # Configuration & constants
│   └── config.py              # Environment, timeouts, viewpoints
├── data/                  # Test data & parameterization
│   └── search_test_data.py    # Keywords, edge cases, security payloads
├── reports/               # Test execution artifacts
│   ├── test_report.html       # Self-contained HTML report
│   └── screenshots/           # Failure screenshots
├── conftest.py            # Pytest fixtures (browser, context, page)
├── pytest.ini             # Test configuration & markers
├── run_tests.sh           # Test execution wrapper script
└── requirements.txt       # Dependencies (pytest, playwright, etc.)
```

### Key Design Patterns

1. **Page Object Model (POM)**
   - Each page (`HomePage`, `SearchResultsPage`) encapsulates locators and actions
   - Tests interact with page objects, not raw selectors
   - Located in `/pages/` directory

2. **Fixture-Based Test Isolation** (`conftest.py`)
   - Session-scoped browser for performance
   - Function-scoped context/page for test isolation
   - Automatic failure screenshot capture

3. **Data-Driven Testing**
   - Test data in `/data/search_test_data.py`
   - Parameterized tests using `@pytest.mark.parametrize`
   - Separates test logic from test data

4. **Resilient Locator Strategies**
   - Fallback selectors to withstand UI changes
   - Example: `input#header-search-input, input.search-input, input[placeholder]`
   - Explicit waits instead of fixed sleeps

5. **Ad/Sponsored Content Handling**
   - `get_product_prices(exclude_ad=True)` filters out sponsored items
   - Critical for validating organic search result integrity

### Test Markers (defined in pytest.ini)
- `smoke`: Critical path tests for quick validation
- `regression`: Complete test suite
- `filter_sort`: Sorting & filtering operations
- `pagination`: Multi-page navigation tests
- `edge_case`: Boundary conditions & special inputs
- `security`: XSS & SQLi protection tests

### Important Implementation Details

1. **Price Sorting Validation**
   - Sponsored ads (`Ad`) are pinned regardless of sort order
   - Use `exclude_ad=True` in `get_product_prices()` for accurate sorting validation
   - Refer to `test_search_sorting_filtering.py` for examples

2. **Test Reporting**
   - HTML report auto-generated at `reports/test_report.html`
   - Failure screenshots saved to `reports/screenshots/`
   - Self-contained report includes all assets

3. **Configuration**
   - Centralized in `config/config.py`
   - Environment variables, timeouts, viewports, headers
   - Easy to modify for different environments

### When Modifying This Codebase

- **Adding new tests**: Place in appropriate test file based on functionality
- **Adding new page elements**: Update relevant POM in `/pages/`
- **Adding test data**: Update `/data/search_test_data.py`
- **Changing test execution**: Modify `run_tests.sh` or `pytest.ini`
- **Updating locators**: Check all POM files for selector usage
- **Maintaining test isolation**: Use function-scoped fixtures, avoid shared state

This framework follows SDET best practices with emphasis on flakiness reduction, maintainable locators, and clear separation of concerns between test logic and implementation details.