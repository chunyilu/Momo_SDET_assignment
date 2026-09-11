# Software Development Engineer in Test (SDET) - Test Plan

## Feature Under Test: Main Search Bar Component
* **Target Application:** Momoshop (富邦媒體科技)
* **URL:** [https://www.momoshop.com.tw/main/Main.jsp](https://www.momoshop.com.tw/main/Main.jsp)
* **Target Element Selector:** `body > header > div.mu-relative.mu-mx-auto.mu-w-full.mu-max-w-[1920px] > div.mu-mx-auto.mu-flex.mu-w-content.mu-flex-wrap > div.mu-ml-0.mu-mt-0.mu-box-border.mu-flex.mu-h-[120px].mu-w-[569px].mu-flex-col.mu-items-center.mu-justify-center.mu-pt-[25px] > div:nth-child(1) > div > div > div > div > input`

---

## 1. Test Suite Summary

| Category | Priority | Test Cases Count | Description |
| :--- | :--- | :--- | :--- |
| **Functional & Input Validation** | High / Critical | 10 | Core search logic, keyword matching, boundary testing, and string encoding |
| **UI / UX & Auto-Suggest** | Medium / High | 6 | Placeholder text, auto-complete dropdown, clear button, keyboard navigation |
| **Security & Injection** | Critical | 4 | Cross-Site Scripting (XSS), SQL Injection (SQLi), and script sanitization |
| **Cross-Browser & Responsive** | Medium | 3 | CSS selector stability across viewports, screen resolutions, and browsers |
| **Performance & API Integration** | High | 3 | Search debouncing, latency benchmarks, and network offline handling |

---

## 2. Detailed Test Cases

### 2.1 Functional & Input Validation

| TC ID | Test Scenario | Steps | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **TC-FUNC-01** | Valid Exact Keyword Search | 1. Navigate to Momoshop homepage.<br>2. Focus search `<input>` element.<br>3. Type `"iPhone 15"`.<br>4. Press `Enter` or click the search icon button. | Navigates to search result page (URL containing search query parameters) displaying relevant products. | **P0 (Critical)** |
| **TC-FUNC-02** | Partial & Fuzzy Keyword Match | 1. Enter `"iPhone"` or slight typo like `"iPhne"`.<br>2. Submit search. | Search page returns matching products and/or "Did you mean..." recommendation tags. | **P1 (High)** |
| **TC-FUNC-03** | Chinese & Multi-language Input | 1. Enter Traditional Chinese string `"衛生紙"` or multi-language string `"Dyson 吹風機"`.<br>2. Submit search. | Correctly encodes input parameters via UTF-8 and returns relevant product listings. | **P0 (Critical)** |
| **TC-FUNC-04** | Search with Leading/Trailing Spaces | 1. Type `"  衛生紙  "` with extra whitespace.<br>2. Submit search. | Whitespace is automatically trimmed before sending request; search results match `"衛生紙"`. | **P2 (Medium)** |
| **TC-FUNC-05** | Empty Search Submission | 1. Leave input field empty.<br>2. Click search button or press `Enter`. | Prevents unnecessary network request/page submission, or shows UI prompt ("Please enter search keyword"). | **P1 (High)** |
| **TC-FUNC-06** | Special Characters Input | 1. Enter `!@#$%^&*()_+-=[]{}|;:',.<>?/`.<br>2. Submit search. | Application sanitizes input without throwing HTTP 500 error or breaking URL query structure. | **P1 (High)** |
| **TC-FUNC-07** | Boundary Length Test | 1. Paste a string with 500+ characters into `<input>`.<br>2. Submit search. | Input element enforces `maxlength` attribute or gracefully truncates input without UI distortion. | **P2 (Medium)** |
| **TC-FUNC-08** | Numeric SKU / Product ID Search | 1. Enter exact product ID (e.g., `"12345678"`).<br>2. Submit search. | Navigates directly to specific product detail page or displays exact item match. | **P1 (High)** |
| **TC-FUNC-09** | Multi-keyword Logic (AND/OR) | 1. Enter multi-word query `"NIKE 慢跑鞋 黑"`.<br>2. Submit search. | Search results correctly filter items matching all key criteria. | **P1 (High)** |
| **TC-FUNC-10** | Copy-Paste via Clipboard | 1. Copy text to system clipboard.<br>2. Paste into search box via `Ctrl+V` or context menu. | Text pastes successfully and triggers input event listeners / auto-suggest dropdown. | **P2 (Medium)** |

---

### 2.2 UI / UX & Auto-Suggest

| TC ID | Test Scenario | Steps | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **TC-UI-01** | Placeholder Text Verification | 1. Observe input element on initial load. | Displays expected dynamic or static placeholder text (e.g., "請輸入商品名稱或關鍵字"). | **P2 (Medium)** |
| **TC-UI-02** | Focus & Blur Styling | 1. Focus input box.<br>2. Click outside input box. | Active state shows focus ring/border highlight; blur state resets styling smoothly. | **P3 (Low)** |
| **TC-UI-03** | Auto-Suggest Dropdown | 1. Type `"衛生"` into input box. | Dropdown opens listing matching trending keywords, categories, or recent search history. | **P1 (High)** |
| **TC-UI-04** | Auto-Suggest Keyboard Nav | 1. Type `"iPhone"`.<br>2. Press `Arrow Down` / `Arrow Up` key.<br>3. Press `Enter`. | Highlights dropdown list items sequentially and submits selected item on `Enter`. | **P2 (Medium)** |
| **TC-UI-05** | Clear Button Functionality | 1. Type any string.<br>2. Click "X" clear button inside/adjacent to input box. | Input field value is cleared, focus remains/resets, auto-suggest menu closes. | **P2 (Medium)** |
| **TC-UI-06** | Trending Keywords / History | 1. Click search input box without typing. | Displays recent search history tags or current popular search trends. | **P2 (Medium)** |

---

### 2.3 Security & Vulnerability Testing

| TC ID | Test Scenario | Steps | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SEC-01** | Reflected XSS Injection | 1. Enter `<script>alert('XSS')</script>` or `<img src=x onerror=alert(1)>`.<br>2. Submit search. | Input is properly sanitized/encoded; no JavaScript code executes in DOM or search result view. | **P0 (Critical)** |
| **TC-SEC-02** | SQL Injection Attempt | 1. Enter `' OR '1'='1` or `1'; DROP TABLE goods;--`.<br>2. Submit search. | Backend uses parameterized queries; handles input safely without revealing DB errors. | **P0 (Critical)** |
| **TC-SEC-03** | HTML Tag Injection | 1. Enter `<h1>Big Text</h1>` or `<b>Test</b>`.<br>2. Submit search. | HTML tags render as plain text strings rather than parsed visual HTML tags. | **P1 (High)** |
| **TC-SEC-04** | Query Parameter Tampering | 1. Manually edit URL search parameter (`?keyword=...`). | Server side validates query parameter safely and gracefully handles unexpected syntax. | **P1 (High)** |

---

### 2.4 Performance & Network Integration

| TC ID | Test Scenario | Steps | Expected Result | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **TC-PERF-01** | Input Debouncing | 1. Type characters rapidly (`"s-a-m-s-u-n-g"`). | Auto-suggest API debounces request (~200ms-300ms delay) to avoid server request spam. | **P1 (High)** |
| **TC-PERF-02** | API Response Latency | 1. Measure response time on search submit under normal network conditions. | Search API returns and page renders within target SLA (< 1.5 seconds). | **P2 (Medium)** |
| **TC-PERF-03** | Network Disconnection | 1. Disconnect network / set DevTools to Offline.<br>2. Attempt search. | Gracefully shows offline alert or fallback error message without throwing uncaught exceptions. | **P2 (Medium)** |

---

## 3. SDET Automation & Selector Optimization Strategy

### 3.1 Selector Fragility Analysis
The target CSS selector provided:
```css
body > header > div.mu-relative.mu-mx-auto.mu-w-full.mu-max-w-[1920px] > div.mu-mx-auto.mu-flex.mu-w-content.mu-flex-wrap > div.mu-ml-0.mu-mt-0.mu-box-border.mu-flex.mu-h-[120px].mu-w-[569px].mu-flex-col.mu-items-center.mu-justify-center.mu-pt-[25px] > div:nth-child(1) > div > div > div > div > input
```
**Issues identified:**
* Contains strict utility class names (e.g., Tailwind CSS / Micro-Frontend generated classes like `mu-w-[569px]`). Any CSS design tweak will break tests.
* Deeply nested DOM path (`div > div > div > div > input`) makes execution fragile and sensitive to minor layout updates.

### 3.2 Recommended Locator Strategy
Request the development team to add dedicated testing attributes:
```html
<input data-testid="main-search-input" id="keyword" name="keyword" ... />
```

### 3.3 Sample Playwright Test Script (TypeScript)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Momoshop Main Search Input Suite', () => {
  const BASE_URL = 'https://www.momoshop.com.tw/main/Main.jsp';

  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test('TC-FUNC-01: Valid keyword search should navigate to results page', async ({ page }) => {
    // Robust multi-fallback selector
    const searchInput = page.locator('input[placeholder*="搜尋"], input#keyword, [data-testid="main-search-input"]').first();
    
    await expect(searchInput).toBeVisible();
    await searchInput.fill('iPhone 15');
    await searchInput.press('Enter');

    // Verify navigation and query string
    await expect(page).toHaveURL(/.*keyword=iPhone%2015.*/);
  });

  test('TC-SEC-01: Sanitize XSS payload in search input', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="搜尋"], input#keyword').first();
    
    await searchInput.fill('<script>alert("XSS")</script>');
    await searchInput.press('Enter');

    // Ensure no unhandled browser dialog or executed script
    await expect(page.locator('body')).not.toContainText('XSS');
  });
});
```
