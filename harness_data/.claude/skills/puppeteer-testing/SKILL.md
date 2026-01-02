---
name: puppeteer-testing
description: E2E testing for autonomous coding with Puppeteer MCP. Use when implementing user-facing features that require browser testing. Covers navigation, screenshots, interaction patterns, and browser cleanup.
---

# Puppeteer E2E Testing

Test user-facing features during autonomous coding sessions using Puppeteer MCP.

## When to Use

- Implementing UI features (forms, dashboards, auth flows)
- Verifying user interactions work end-to-end
- Validating features before marking as passing

## Basic Workflow

**1. Navigate**
```
[Tool: mcp__puppeteer__puppeteer_navigate]
Input: {'url': 'http://localhost:3000/page'}
```
Wait 2-3 seconds after navigation.

**2. Screenshot (Initial State)**
```
[Tool: mcp__puppeteer__puppeteer_screenshot]
Input: {'name': 'feature_42_step1_login_page'}
```
Naming: `feature_{ID}_step{N}_{description}`

**3. Interact with Page**
```
[Tool: mcp__puppeteer__puppeteer_evaluate]
Input: {
  'expression': '''
    const email = document.querySelector('input[name="email"]');
    const password = document.querySelector('input[name="password"]');
    const submit = document.querySelector('button[type="submit"]');

    if (email) email.value = "test@example.com";
    if (password) password.value = "SecurePass123!";
    if (submit) submit.click();

    return {success: true};
  '''
}
```
Use `evaluate` (not fill/click) for reliability.

**4. Wait for Response**
```bash
sleep 3  # Adjust: forms 2-3s, API calls 3-5s
```

**5. Screenshot (Final State)**
```
[Tool: mcp__puppeteer__puppeteer_screenshot]
Input: {'name': 'feature_42_step3_logged_in'}
```

**6. Document Results**

Create `test_results.json` in project root:
```json
{
  "feature_id": 42,
  "test_status": "passed",
  "test_steps": [
    {"step": 1, "action": "Navigate to login", "screenshot": "feature_42_step1_login_page.png", "status": "passed"},
    {"step": 2, "action": "Submit credentials", "status": "passed"},
    {"step": 3, "action": "Verify logged in", "screenshot": "feature_42_step3_logged_in.png", "status": "passed"}
  ]
}
```

## Browser Cleanup

**Automatic** in claude-harness v3.1.1+. PostToolUse hook closes browsers after screenshots when 5+ Chrome processes detected.

No manual cleanup needed.

## Common Patterns

**Authentication Flow:**
```javascript
localStorage.setItem('authToken', 'test-token');
localStorage.setItem('user', JSON.stringify({id: 1, email: "test@example.com"}));
window.location.reload();
return {authenticated: true};
```

**Form Validation:**
```javascript
document.querySelector('input[name="email"]').value = "invalid";
document.querySelector('form').submit();
await new Promise(resolve => setTimeout(resolve, 2000));
const error = document.querySelector('.error-message');
return {hasError: error !== null, errorText: error?.textContent};
```

**API Response Verification:**
```javascript
await new Promise(resolve => setTimeout(resolve, 3000));
const data = document.querySelector('.data-container')?.textContent;
return {dataLoaded: data !== null, content: data};
```

## Best Practices

- **Wait after navigation** - Always sleep 2-3 seconds
- **Check elements exist** - Use `if (element)` before interacting
- **3-5 screenshots per feature** - Initial, interaction, final states
- **Descriptive names** - `feature_42_step1_login_page`
- **Document results** - Create `test_results.json`

## Troubleshooting

**Element not found:** Increase wait time, verify selector, check screenshot
**Connection refused:** Verify server running, check port, wait longer
**Screenshots blank:** Wait longer, check console errors, verify CSS loaded
