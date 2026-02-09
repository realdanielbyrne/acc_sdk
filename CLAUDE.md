# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**acc_sdk** is an unofficial Python SDK for the Autodesk Construction Cloud (ACC) API. It wraps multiple ACC REST APIs (projects, users, forms, sheets, data management, etc.) into a unified Python package. Requires Python >= 3.12.

## Common Commands

```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest tests/

# Run a single test file
poetry run pytest tests/test_forms.py

# Run a specific test
poetry run pytest tests/test_forms.py::TestForms::test_get_form_templates

# Format code
poetry run black acc_sdk tests

# Lint code
poetry run ruff check acc_sdk tests
```

## Architecture

### Entry Points
- `Acc` (in `acc.py`) is the main aggregator class users instantiate. It creates an `AccBase` instance and passes it to each API class.
- `Authentication` (in `authentication.py`) manages OAuth 2.0 tokens (2-legged and 3-legged flows). Users create this first, then pass it to `Acc`.
- Both are exported from `__init__.py`.

### Base Class Pattern
`AccBase` (in `base.py`) is a **shared state container** (not a parent class for inheritance). It holds: `auth_client`, `account_id`, `hub_id`, `company_id`, `user_info`, `admin_email`. Every API class receives an `AccBase` instance via its constructor and accesses tokens/IDs through it.

Key token method: `get_private_token()` returns whichever token is available, preferring 2-legged over 3-legged.

### API Class Pattern
Each API module (`projects.py`, `forms.py`, `sheets.py`, etc.) defines a class named `Acc[Module]Api` that follows this structure:
- Constructor takes `AccBase`, sets `self.base` and `self.base_url`
- `_get_headers(include_content_type=False)` — builds auth headers with Bearer token, optional Content-Type and User-Id
- `_handle_pagination(url, headers, params)` — follows `pagination.nextUrl` or `links.next.href` across pages
- `_handle_error_response(response)` — calls `raise_for_status()` with error detail printing
- Public methods named `get_*`, `create_*`, `update_*`, `delete_*` wrapping specific API endpoints
- Pagination is opt-in: many methods accept `follow_pagination=False` parameter

### Aggregator Service Attributes
The `Acc` class exposes API services as attributes:
- `acc.projects`, `acc.project_users`, `acc.account_users`
- `acc.sheets`, `acc.forms`, `acc.data_management`, `acc.data_connector`
- `acc.companies`, `acc.business_units`, `acc.user_profiles`

### Token Types and Scopes
- **2-legged** (client credentials): server-to-server, stored as `accapi_2legged` in session. Used for account admin operations (account_users, business_units, companies).
- **3-legged** (authorization code): user-delegated, stored as `accapi_3legged` in session. Used for user-context operations (sheets, forms, photos, data_connector).
- Some modules (projects, project_users, data_management) support both token types.

### Aggregator Convenience Methods
`Acc` class provides higher-level methods like `get_forms()`, `get_forms_for_past30()`, `get_forms_all_active_projects()` that combine calls from multiple API services (e.g., enriching forms data with user names from project_users).

## Testing Conventions

Tests use `unittest.TestCase` with `unittest.mock`. Each test file:
1. Creates a `MagicMock(spec=AccBase)` in `setUp`
2. Instantiates the API class with the mock base
3. Uses `@patch` to mock HTTP calls — newer tests use module-scoped paths like `@patch("acc_sdk.forms.requests.get")`, some older tests use `@patch("requests.get")`
4. Asserts on return values and that requests were called with correct URLs/headers/params
5. Tests pagination by using `side_effect` with multiple mock responses

## Code Style

- Google-style docstrings with Args, Returns, Example sections
- Methods prefixed with `_` are private/internal
- Modules use `requests` library directly (no httpx or aiohttp)
- `hub_id` is always `"b." + account_id`
