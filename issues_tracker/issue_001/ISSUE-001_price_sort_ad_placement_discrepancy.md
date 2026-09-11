# Bug / Issue Report: Sponsored Ad Products Pinned Above Organic Results in Price Sort

## 1. Issue Summary
* **Title:** `[Search - Sorting & Filtering] Sponsored Ad Products Pinned Above Organic Results Violating Strict Price Sorting Order`
* **Environment:** `Production-like / Web Live`
* **Platform / OS:** `Web - Desktop Chrome v122 / Ubuntu 22.04 LTS`
* **App / Build Version:** `Momo E-Commerce Web Release (momoshop.com.tw)`
* **Severity:** `Major`
* **Priority:** `P1 - High`
* **Automation Candidate:** `Yes`

---

## 2. Defect Description
When users sort search results by Price (either Low-to-High `searchType=3` or High-to-Low `searchType=2`), sponsored/advertisement items (`.listAreaLi` containing `Ad` tag) remain pinned at top positions in the result grid regardless of their actual price. For example, when sorting by Price Low-to-High for `"iPad"`, a sponsored iPad device priced at `NT$32,900` appears at index 0 before organic accessory items priced at `NT$290`, violating mathematical monotonicity and degrading user trust in sorting accuracy.

### Preconditions
1. Client browser is navigated to `https://www.momoshop.com.tw/main/Main.jsp`.
2. Target search keyword returns both organic and sponsored advertising products (e.g., `"iPad"`, `"iPhone"`).
3. Search results page is fully rendered with default relevance sort.

---

## 3. Steps to Reproduce
1. Navigate to `https://www.momoshop.com.tw/main/Main.jsp`.
2. Enter `"iPad"` in the main search input.
3. Click the search button or press `Enter` to navigate to Search Results page.
4. Click on the Price Sort button (`li.priceHeight`) to toggle to **Price: Low to High** (`searchType=3`).
5. Observe the price sequence of the first 5 product cards displayed in the grid.

---

## 4. Expected vs. Actual Result
* **Expected Result:** Products are strictly ordered by ascending price (e.g., `NT$290 -> NT$350 -> NT$590 -> ...`), or sponsored ad placements are visually and structurally segregated into a designated "Sponsored / Ad" carousel/container outside the sorted organic grid.
* **Actual Result:** Sponsored products are interleaved at the top of the grid with high prices (e.g., `NT$32,900`), breaking the expected monotonic price ordering for end users and automated validation assertions.

---

## 5. SDET Diagnostics & Technical Details

### API Request / Response
* **Endpoint:** `GET /search/searchShop.jsp`
* **Query Parameters:**
```json
{
  "keyword": "iPad",
  "searchType": "3",
  "curPage": "1",
  "showType": "chessboardType"
}
```
* **Response Body (DOM Extract):**
```html
<li class="listAreaLi" id="search-goods-item-0">
  <div class="adTag">Ad</div>
  <h3 class="prdName">Apple iPad Pro 11吋 M4 (256GB)</h3>
  <span class="price"><b>32,900</b>元</span>
</li>
<li class="listAreaLi" id="search-goods-item-1">
  <h3 class="prdName">iPad 防摔透明保護套</h3>
  <span class="price"><b>290</b>元</span>
</li>
```

### Automation Context
* **Failed Automated Test Case:** `tests/test_search_sorting_filtering.py::TestSearchSortingFiltering::test_sort_by_price_toggle`
* **Test Framework:** `pytest (9.1.1) / Playwright (0.9.0)`
* **Stack Trace / Error Log:**
```text
AssertionError: Expected product prices to be monotonically non-decreasing when sorted Low-to-High.
Price Sequence extracted: [32900, 290, 350, 590, 890]
Traceback:
  File "tests/test_search_sorting_filtering.py", line 51, in test_sort_by_price_toggle
    assert prices == sorted(prices), f"Prices not sorted: {prices}"
```

---

## 6. Attachments & Evidence
* **Logs:** `../../reports/test_report.html`
* **Screenshots / Video:** Attached `FAIL_test_sort_by_price_toggle.png`
* **Network Trace:** `search_price_sort_3.har`
