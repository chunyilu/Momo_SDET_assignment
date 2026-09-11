# Bug / Issue Report: Empty Search Query Executes Rotating Placeholder Keyword Without Validation

## 1. Issue Summary
* **Title:** `[Search - Input Validation] Submitting Empty Search Query Triggers Unchecked Request with Dynamic Placeholder Value`
* **Environment:** `Production-like / Web Live`
* **Platform / OS:** `Web - Desktop Chrome v122 / Ubuntu 22.04 LTS`
* **App / Build Version:** `Momo E-Commerce Web Release (momoshop.com.tw)`
* **Severity:** `Minor`
* **Priority:** `P3 - Low`
* **Automation Candidate:** `Yes`

---

## 2. Defect Description
When a user submits the search form without entering any characters into the search bar, the web client fails to perform client-side input validation or display a user prompt ("請輸入關鍵字"). Instead, it silently substitutes whatever promotional or rotating placeholder keyword happens to be active in the placeholder attribute at that instant and initiates a full page navigation and database query. This causes unintended server load and surprising search results for users who accidentally clicked the search button.

### Preconditions
1. User is on the Momo homepage.
2. Search input field contains an empty string (`""`).

---

## 3. Steps to Reproduce
1. Navigate to `https://www.momoshop.com.tw/main/Main.jsp`.
2. Ensure search input is cleared.
3. Click the search magnifying glass icon or press `Enter`.
4. Observe network requests and destination URL.

---

## 4. Expected vs. Actual Result
* **Expected Result:** Frontend prevents empty submission and focuses the input field with a brief inline hint/tooltip prompting the user to type a keyword.
* **Actual Result:** Browser navigates to `/search/searchShop.jsp?keyword=<placeholder_item>`, executing an unrequested backend search.

---

## 5. SDET Diagnostics & Technical Details

### API Request / Response
* **Endpoint:** `GET /search/searchShop.jsp`
* **Generated Request URL:** `https://www.momoshop.com.tw/search/searchShop.jsp?keyword=%E6%BD%AE%E7%89%8C%E7%94%B7%E8%A3%9D&searchType=1`
* **Response Status:** `200 OK`

### Automation Context
* **Failed Automated Test Case:** `tests/test_search_edge_cases.py::TestSearchEdgeCases::test_empty_search_submission`
* **Test Framework:** `pytest (9.1.1) / Playwright (0.9.0)`
* **Observation / Log:**
```text
Warning: Empty search query submission navigated to implicit placeholder search '潮牌男裝'.
Expected: Client-side validation prevents redundant navigation.
```

---

## 6. Attachments & Evidence
* **Logs:** `../../reports/test_report.html`
* **Screenshots / Video:** Attached `reports/screenshots/EMPTY_SEARCH_TRIGGER.png`
* **Error Page:** Attached `EC404_error_page.html`
* **Network Trace:** `search_empty_submission.har`
