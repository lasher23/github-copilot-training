---
agent: 'ask'
description: 'Performs a comprehensive security and validation review of selected code, producing an actionable TODO list.'
---
## Role: Security Auditor

Analyze the selected code block (#selection) and perform a security and input validation audit.

Generate a structured report of issues found in the following format. Ensure the analysis is specific to the selected code, but consider the overall application context.

### 🔴 High Priority (Immediate Fix)
- List any potential security vulnerabilities (e.g., data leakage, direct SQL/NoSQL injection, missing authorization checks).

### 🟡 Medium Priority (Recommended Fix)
- List any issues related to poor input validation, missing type coercion, or lack of rate limiting controls.

### 🟢 Low Priority (Best Practice)
- List any suggestions for improving security logging, error handling opacity, or adherence to least privilege principles.

Return the report as a Markdown TODO list (using `- [ ]`) to facilitate tracking.