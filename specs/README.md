# Example Specifications

This directory contains example app specifications for use with claude-harness.

## Available Examples

### 1. Claude.ai Clone (Comprehensive)
**File**: `claude_ai_clone_example.txt`

A complete, production-ready specification for building a full-featured chat application similar to claude.ai. This is the **canonical example** from Anthropic's official quickstarts.

**Features**:
- Complete fullstack app (React + Express + SQLite)
- 200+ comprehensive features
- Detailed UI/UX specifications with design system
- Conversation management and artifacts rendering
- Model selection and advanced settings
- Project organization and sharing
- Comprehensive API endpoint definitions

**Use this for**: Learning how to write comprehensive specs, understanding fullstack app requirements, testing the harness with a complex real-world application.

**Estimated completion**: 150-200 sessions (~2-3 weeks continuous running)

---

### 2. Simple Todo App (Minimal)
**File**: `simple_todo_spec.txt`

A minimal specification for testing or quick demonstrations.

**Use this for**: Quick tests, learning the basics, validating harness functionality, rapid prototyping.

**Estimated completion**: 10-20 sessions (~1-2 hours)

---

## Using These Specs

### Option 1: Use as Default Template
```bash
# Copy to your project directory
cp specs/claude_ai_clone_example.txt /path/to/your/project/app_spec.txt

# Run harness
claude-harness --project-dir /path/to/your/project --spec /path/to/your/project/app_spec.txt
```

### Option 2: Reference Directly
```bash
# Use spec directly from harness
claude-harness --project-dir /tmp/test-project --spec ./specs/claude_ai_clone_example.txt
```

### Option 3: Modify for Your Needs
```bash
# Copy and customize
cp specs/claude_ai_clone_example.txt my_custom_spec.txt
# Edit my_custom_spec.txt with your specific requirements
claude-harness --project-dir /tmp/my-project --spec my_custom_spec.txt
```

---

## Writing Your Own Specifications

Based on the Anthropic example (`claude_ai_clone_example.txt`), a good specification should include:

### Required Sections
1. **Project Overview** - What you're building
2. **Technology Stack** - Specific technologies with versions
   - **Frontend**: Framework, styling, state management, port
   - **Backend**: Server, database, APIs
   - **Communication**: REST, WebSockets, SSE, etc.

3. **Core Features** - Detailed feature descriptions
   - Group related features into sections
   - Be specific about UI elements (buttons, forms, pages)
   - Include interactions and workflows

4. **Database Schema** - Table definitions with key fields

5. **API Endpoints** - RESTful routes organized by resource

6. **UI Layout** - Visual structure description
   - Main layout (sidebar, main area, panels)
   - Responsive behavior
   - Component hierarchy

7. **Design System** - Visual design specifications
   - Color palette with hex codes
   - Typography (fonts, sizes, weights)
   - Component styles
   - Animations and transitions

8. **Implementation Steps** - Logical build order

9. **Success Criteria** - Definition of done

### Best Practices

✅ **DO**:
- Be explicit about frontend technologies (React, Next.js, Vue)
- Include UI layout and design system sections
- Describe user interactions and workflows
- Provide specific component examples
- Use concrete measurements (colors, spacing, timing)
- Mention responsive design requirements

❌ **DON'T**:
- Use ambiguous terms ("interface" could mean API or UI)
- Skip the design system section
- Forget to specify ports and configurations
- Leave technology choices undefined
- Write only backend/API requirements for fullstack apps

### Example: Good vs Bad Feature Descriptions

**Bad** (Ambiguous):
```
- User authentication
- Product management
- File upload interface
```

**Good** (Explicit):
```
- User login form with email/password fields, "Remember me" checkbox,
  and "Forgot password?" link. Form displays validation errors inline.
  Successful login redirects to dashboard.

- Product detail page showing product image, name, price, description,
  and "Add to Cart" button. Includes breadcrumb navigation and related
  products carousel at bottom.

- Drag-and-drop file upload component with preview thumbnails, progress
  bars, and file type validation (CSV, Excel, PDF only). Shows upload
  status and error messages.
```

---

## Troubleshooting

**Issue**: "Harness builds APIs but no UI"
- **Solution**: Check if spec mentions frontend technologies explicitly
- Add UI Layout and Design System sections
- Use feature descriptions that mention UI elements (forms, buttons, pages)
- See [CHANGELOG.md v3.6.0](../CHANGELOG.md#360---2026-01-14) for details

**Issue**: "Not enough features generated"
- **Solution**: Anthropic's example generates 200+ features from comprehensive spec
- Break features into granular, testable units
- Include both functional and UI/style features

**Issue**: "Agent doesn't use browser automation"
- **Solution**: Upgrade to v3.6.0+
- Ensure spec mentions frontend technology (React, Next.js, etc.)
- Feature descriptions should mention UI interactions

---

## Additional Resources

- [Anthropic's Autonomous Coding Quickstart](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- [Claude Code SDK Documentation](https://github.com/anthropics/claude-code-sdk)
- [Harness User Guide](../docs/USER_GUIDE.md)
- [Contributing Guide](../CONTRIBUTING.md)

---

## Credits

The `claude_ai_clone_example.txt` specification is from Anthropic's official [claude-quickstarts repository](https://github.com/anthropics/claude-quickstarts/blob/main/autonomous-coding/prompts/app_spec.txt) and serves as the gold standard for autonomous coding specifications.
