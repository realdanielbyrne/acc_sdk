# Project Users API

The `AccProjectUsersApi` provides extensive methods to manage users within your Autodesk Construction Cloud (ACC) projects, including retrieving user details, adding new users individually or in bulk, updating permissions, and removing users.

## Get Users from a Project

Retrieve all or a filtered subset of users from a specific project.

```python
project_id = "your_project_uuid"
users = acc.project_users.get_users(project_id)
print(users)
```

To paginate through results or apply filters:

```python
filtered_users = acc.project_users.get_users(project_id, query_params={"limit": 50}, follow_pagination=True)
```

## Get Detailed User Information

Fetch detailed information for a specific user in a project.

```python
user_info = acc.project_users.get_user(project_id="your_project_uuid", user_id="user_uuid")
print(user_info)
```

## Add a Single User to a Project

Add a new user by specifying their email and product access.

```python
new_user = {
    "email": "user@example.com",
    "products": AccProjectUsersApi.productmember
}
created_user = acc.project_users.add_user(project_id="your_project_uuid", user=new_user)
print(created_user)
```

## Import Users to a Project (Bulk)

Efficiently add multiple users at once. Provide a list of users with their email and desired products.

```python
bulk_users = [
    {"email": "user1@example.com", "products": AccProjectUsersApi.productmember},
    {"email": "user2@example.com", "products": AccProjectUsersApi.productadmin}
]

acc.project_users.import_users(project_id="your_project_uuid", users=bulk_users)
```

## Update User Permissions

Update permissions or product access for a specific user.

```python
update_data = {"products": AccProjectUsersApi.productadmin}
updated_user = acc.project_users.patch(project_id="your_project_uuid", target_user_id="user_uuid", data=update_data)
print(updated_user)
```

## Batch Update Users Across Multiple Projects

Apply product or permission updates to multiple users across several projects.

```python
projects = acc.projects.get_all_active_projects()
users = [
    {"email": "user@example.com", "products": AccProjectUsersApi.productadmin},
    {"email": "anotheruser@example.com", "products": AccProjectUsersApi.productmember}
]

acc.project_users.patch_project_users(projects=projects, users=users)
```

## Delete a User from a Project

Remove an individual user from a specific project.

```python
acc.project_users.delete(project_id="your_project_uuid", target_user_id="user_uuid")
```

## Bulk Delete Users from a Project

Remove multiple users by specifying their email addresses.

```python
users_to_remove = [
    {"email": "user1@example.com"},
    {"email": "user2@example.com"}
]

acc.project_users.delete_users(project_id="your_project_uuid", users=users_to_remove)
```
