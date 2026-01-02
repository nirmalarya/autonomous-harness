---
name: code-quality
description: Production-quality code standards for autonomous coding sessions. Use when implementing features to ensure security, reliability, and maintainability. Covers error handling, input validation, type safety, and clean code practices.
---

# Code Quality Standards

Write production-ready code during autonomous sessions.

## When to Use

- Implementing any feature (frontend, backend, infrastructure)
- Writing code that will be committed to production
- Before marking features as passing

## Core Principles

**1. Security First**
- Validate all external input (user input, API responses, file contents)
- Never trust data from outside your control
- Prevent OWASP Top 10 vulnerabilities

**2. Fail Gracefully**
- Handle errors explicitly, don't let them crash
- Provide meaningful error messages
- Log errors for debugging

**3. Type Safety**
- Use TypeScript for JavaScript projects
- Use type hints for Python projects
- Define interfaces/types for data structures

**4. Clean Code**
- Functions do one thing well
- Clear variable and function names
- No premature optimization

## Security Checklist

**Input Validation:**
```typescript
// ✅ Good - Validate before use
function processEmail(email: string) {
  if (!email || !email.includes('@')) {
    throw new Error('Invalid email address');
  }
  // Process validated email
}

// ❌ Bad - No validation
function processEmail(email: string) {
  sendEmail(email); // What if email is malicious?
}
```

**SQL Injection Prevention:**
```typescript
// ✅ Good - Use parameterized queries
const user = await db.query('SELECT * FROM users WHERE email = ?', [email]);

// ❌ Bad - String concatenation
const user = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

**XSS Prevention:**
```typescript
// ✅ Good - Escape output
<div>{escapeHtml(userInput)}</div>

// ❌ Bad - Raw HTML
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

**Authentication:**
```typescript
// ✅ Good - Check auth on protected routes
if (!req.session.user) {
  return res.status(401).json({error: 'Unauthorized'});
}

// ❌ Bad - No auth check
const data = await getUserData(req.params.userId);
```

## Error Handling

**API Routes:**
```typescript
// ✅ Good - Try/catch with proper errors
app.post('/api/create', async (req, res) => {
  try {
    const result = await createResource(req.body);
    res.json(result);
  } catch (error) {
    console.error('Create failed:', error);
    res.status(500).json({error: 'Failed to create resource'});
  }
});

// ❌ Bad - No error handling
app.post('/api/create', async (req, res) => {
  const result = await createResource(req.body); // Crashes on error
  res.json(result);
});
```

**Frontend:**
```typescript
// ✅ Good - Handle fetch errors
try {
  const response = await fetch('/api/data');
  if (!response.ok) throw new Error('Failed to fetch');
  const data = await response.json();
  setData(data);
} catch (error) {
  setError('Unable to load data. Please try again.');
}

// ❌ Bad - No error handling
const response = await fetch('/api/data');
const data = await response.json();
setData(data);
```

## Type Safety

**TypeScript Interfaces:**
```typescript
// ✅ Good - Define types
interface User {
  id: number;
  email: string;
  name: string;
}

function getUser(id: number): Promise<User> {
  return db.query<User>('SELECT * FROM users WHERE id = ?', [id]);
}

// ❌ Bad - Any types
function getUser(id: any): Promise<any> {
  return db.query('SELECT * FROM users WHERE id = ?', [id]);
}
```

**Python Type Hints:**
```python
# ✅ Good - Type hints
def get_user(user_id: int) -> dict[str, Any]:
    return db.query("SELECT * FROM users WHERE id = ?", [user_id])

# ❌ Bad - No types
def get_user(user_id):
    return db.query("SELECT * FROM users WHERE id = ?", [user_id])
```

## Clean Code Patterns

**Single Responsibility:**
```typescript
// ✅ Good - One function, one job
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function sendWelcomeEmail(email: string) {
  if (!validateEmail(email)) throw new Error('Invalid email');
  emailService.send(email, 'Welcome!');
}

// ❌ Bad - Function does too much
function processUser(email: string) {
  // Validates, sends email, logs, updates DB...
}
```

**Clear Naming:**
```typescript
// ✅ Good - Clear intent
const isAuthenticated = checkUserSession(req);
const activeUsers = users.filter(u => u.status === 'active');

// ❌ Bad - Unclear
const x = check(req);
const arr = users.filter(u => u.s === 'a');
```

**Avoid Magic Numbers:**
```typescript
// ✅ Good - Named constants
const MAX_RETRY_ATTEMPTS = 3;
const CACHE_TTL_SECONDS = 3600;

for (let i = 0; i < MAX_RETRY_ATTEMPTS; i++) {
  // Retry logic
}

// ❌ Bad - Magic numbers
for (let i = 0; i < 3; i++) {
  // What is 3?
}
```

## Pre-Commit Checklist

Before marking a feature as passing:

- [ ] Input validation on all external data
- [ ] Error handling with try/catch
- [ ] Type safety (TypeScript/Python types)
- [ ] No console.log in production code (use proper logging)
- [ ] No hardcoded secrets or API keys
- [ ] Functions are focused (single responsibility)
- [ ] Variable names are clear and descriptive
- [ ] E2E test passes (for UI features)

## Common Mistakes to Avoid

**1. Trusting External Input**
```typescript
// ❌ Never assume input is valid
const userId = req.params.id; // Could be "../../../etc/passwd"
const file = await readFile(`/uploads/${userId}`); // Path traversal!
```

**2. Swallowing Errors**
```typescript
// ❌ Silent failures hide bugs
try {
  await criticalOperation();
} catch (e) {
  // Ignored - now you don't know it failed!
}
```

**3. Using `any` Type**
```typescript
// ❌ Defeats TypeScript's purpose
function process(data: any): any {
  return data.something; // No type checking
}
```

**4. Missing Null Checks**
```typescript
// ❌ Will crash if user is null
const email = user.email; // TypeError: Cannot read property 'email' of null

// ✅ Check first
const email = user?.email ?? 'default@example.com';
```

## Framework-Specific Notes

**Next.js:**
- Use Server Actions for mutations (not API routes)
- Validate input with Zod schemas
- Handle loading/error states in UI

**FastAPI:**
- Use Pydantic models for validation
- Return proper HTTP status codes
- Handle exceptions with exception handlers

**Express:**
- Use middleware for auth/validation
- Always include error handling middleware
- Use async/await with try/catch

These standards ensure code is secure, reliable, and maintainable in production.
