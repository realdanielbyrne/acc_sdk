# Account Users API

The `AccAccountUsersApi` provides comprehensive methods to manage users within your Autodesk Construction Cloud (ACC) account, including fetching user details, searching users, creating new users, bulk importing users, and updating user status or associations.

## Get All Account Users

Retrieve a complete list of users associated with the account.

```python
users = acc.account_users.get_users()
print(users)
```

## Get User by Email

Fetch details of a specific user using their email address.

```python
user_email = "user@example.com"
user = acc.account_users.get_user_by_email(user_email)
print(user)
```

## Search Users by Name

Search for users within the account by their name.

```python
users_named_daniel = acc.account_users.get_users_search(name="Daniel")
print(users_named_daniel)
```

## Create a Single User

Add a new user to the account by providing at least an email and a company ID.

```python
new_user = {
    "email": "newuser@example.com",
    "company_id": "company123"
}
created_user = acc.account_users.post_user(new_user)
print(created_user)
```

## Bulk Import Users

Import multiple users at once by providing a list of user details.

```python
users_to_import = [
    {"email": "user1@example.com", "company_id": "company123"},
    {"email": "user2@example.com", "company_id": "company123"},
]
import_result = acc.account_users.post_users(users_to_import)
print(import_result)
```

## Update User Status or Company Association

Modify an existing user's status or assign them to a different company.

```python
updated_user = acc.account_users.patch_user(
    user_email="existinguser@example.com",
    status="active",
    company_id="newcompany123"
)
print(updated_user)
```
