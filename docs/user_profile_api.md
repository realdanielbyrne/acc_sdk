# User Profile API

The `AccUserProfileApi` class provides methods to retrieve information about the authenticated user in Autodesk Construction Cloud (ACC).
This API requires a 3-legged token with the `user-profile:read` scope.

## Get User Information

Retrieve basic information about the authenticated user.

```python
user_info = acc.user_profile.get_user_info()
print(user_info)
```

The response includes details such as:

- User ID
- Email address
- Name
- Preferred language
- Picture URL
- Other OpenID Connect standard claims
