# Authentication API

The `Authentication` class provides comprehensive methods to manage authentication with the Autodesk Construction Cloud (ACC) API. It supports both 2-legged and 3-legged OAuth flows, token management, and various authentication-related operations.

## Initialize Authentication

Create a new instance of the Authentication client with your credentials.

```python
auth_client = Authentication(
    client_id="your_client_id",
    client_secret="your_client_secret",
    admin_email="admin@example.com",  # Optional, for 2-legged user impersonation
    session={},  # Flask session or dictionary to store tokens
    callback_url="http://your-app/callback",  # Required for 3-legged flow
    logout_url="http://your-app/logout"  # Optional, for logout redirect
)
```

## 2-Legged Authentication

Obtain a client credentials token for server-to-server operations.

```python
scopes = [
    "data:read",
    "data:write",
    "account:read",
    "account:write"
]
token = auth_client.request_2legged_token(scopes=scopes)
```

## 3-Legged Authentication

The 3-legged authentication process involves multiple steps:

1. First, generate the authorization URL that the user will visit:

```python
# Define the scopes needed for your application
scopes = [
    "user-profile:read",
    "data:read",
    "data:write",
    "account:read",
    "account:write"
]

# Get the authorization URL
auth_url = auth_client.get_authorization_url(scopes=scopes)
```

2. The user visits the authorization URL and authenticates with Autodesk. Upon successful authentication, Autodesk redirects the user to your callback URL with an authorization code.

3. In your callback handler, exchange the authorization code for access and refresh tokens:

```python
# Exchange the authorization code for tokens
token_data = auth_client.request_authcode_access_token(
    code=request.args.get("code"),  # The code from the callback
    scopes=scopes
)
```

4. When the access token expires, use the refresh token to obtain a new access token:

```python
# Refresh the token with optional subset of scopes
new_token = auth_client.request_private_refresh_token(
    scopes=["data:read", "data:write"]  # Optional subset of original scopes
)
```

For a complete example of implementing 3-legged authentication in a web application, see the Flask example in the main README.

## Token Management

Manage and validate your authentication tokens.

```python
# Check if a token is valid
is_valid = auth_client.is_authorized("accapi_3legged")

# Get remaining time until token expiration
expires_in = auth_client.expires_in("accapi_3legged")

# Revoke a token
auth_client.revoke_private_token("accapi_3legged")

# Clear all tokens from session
auth_client.clear_all_tokens()
```

## User Profile Information

Retrieve information about the authenticated user.

```python
# Get user profile information
user_info = auth_client.get_user_info()
print(user_info)
```

## Token Types and Scopes

The Authentication class supports various token types and scopes:

- **2-Legged Tokens**: For server-to-server operations
- **3-Legged Tokens**: For user-specific operations
- **Public Tokens**: Without client secret (PKCE flow)
- **Private Tokens**: With client secret

Common scopes include:

- `user-profile:read`: Access user profile information
- `data:read` and `data:write`: Access project data
- `account:read` and `account:write`: Manage account settings
- `viewables:read`: Access viewable files
