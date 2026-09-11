# Bug / Issue Report Template (SDET Standard)

## 1. Issue Summary
* **Title:** `[Component / Module] Concise summary of the defect`  
  *(Example: `[Checkout - API] 500 Internal Server Error when applying a valid 100% discount promo code`)*
* **Environment:** `[Staging / QA / Dev / Prod-like]`
* **Platform / OS:** `[e.g., iOS 17.4, Android 14, Web - Chrome v122, Ubuntu 22.04]`
* **App / Build Version:** `[e.g., v2.14.0-rc3 or Commit Hash #a1b2c3d]`
* **Severity:** `[Blocker / Critical / Major / Minor / Trivial]`
* **Priority:** `[P0 - Immediate / P1 - High / P2 - Medium / P3 - Low]`
* **Automation Candidate:** `[Yes / No / Pending Fix]`

---

## 2. Defect Description
A clear, concise explanation of what went wrong, including context or preconditions (e.g., specific feature toggles, user roles, or dataset requirements).

### Preconditions
1. User is logged in as `Standard User`.
2. Cart contains at least 1 item valued over $10.
3. Feature flag `ENABLE_NEW_CHECKOUT_FLOW` is set to `true`.

---

## 3. Steps to Reproduce
1. Navigate to `...`
2. Click on `...`
3. Enter payload/data: `...`
4. Execute action: `...`

---

## 4. Expected vs. Actual Result
* **Expected Result:** The order total updates to `$0.00`, and the checkout proceeds to the confirmation page.
* **Actual Result:** The API returns `500 Internal Server Error`, displaying generic error toast `An unexpected error occurred` on the UI.

---

## 5. SDET Diagnostics & Technical Details

### API Request / Response
* **Endpoint:** `POST /api/v1/checkout/apply-promo`
* **Request Payload:**
```json
{
  "cart_id": "cart_883219",
  "promo_code": "FREE100"
}
```
* **Response Body:**
```json
{
  "status": 500,
  "error_code": "ERR_DIVISION_BY_ZERO",
  "message": "Calculated total results in invalid payment threshold."
}
```

### Automation Context
* **Failed Automated Test Case:** `tests/checkout/test_promo_codes.py::test_full_discount_promo`
* **Test Framework:** `Pytest / Playwright / Appium`
* **Stack Trace / Error Log:**
```text
AssertionError: Expected status code 200, but got 500.
Response time: 240ms
Traceback:
  File "tests/checkout/test_promo_codes.py", line 42, in test_full_discount_promo
    assert response.status_code == 200
```

---

## 6. Attachments & Evidence
* **Logs:** Attached `app_server.log`
* **Screenshots / Video:** Attached `checkout_error_500.png`
* **Network Trace:** Attached `checkout_flow.har`
