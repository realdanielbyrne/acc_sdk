# accapi/project_users.py
import requests
from .base import AccBase
import time


class AccProjectUsersApi:
    """
    This class provides methods to interact with the project users endpoint of the Autodesk Construction Cloud API.
    The class provides methods to get, post, patch, and delete users in a project as well as bulk implementations of these methods.

    Token must be Bearer <token>, where <token> is obtained via either two-legged or three-legged oauth flow.
    The GET methods require account:read and the POST, PATCH, and DELETE methods require account:write scopes.
    The POST, PATCH, and DELETE methods require the User-Id header to be set to the user's ID when two-legged authentication
    is used.

    Example:
        ```python
        from accapi import Acc
        acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)

        # Get users from a project
        users = acc.project_users.get_users(project_id="your_project_uuid")

        # Add a user to a project
        new_user = {
            "email": "user@example.com",
            "products": AccProjectUsersApi.productmember
        }
        created_user = acc.project_users.post_user(project_id="your_project_uuid", user=new_user)
        ```
    """

    productadmin = [
        {"key": "projectAdministration", "access": "administrator"},
        {"key": "designCollaboration", "access": "administrator"},
        {"key": "build", "access": "administrator"},
        {"key": "cost", "access": "administrator"},
        {"key": "modelCoordination", "access": "administrator"},
        {"key": "docs", "access": "administrator"},
        {"key": "insight", "access": "administrator"},
        {"key": "takeoff", "access": "administrator"},
    ]

    productmember = [
        {"key": "projectAdministration", "access": "none"},
        {"key": "designCollaboration", "access": "member"},
        {"key": "build", "access": "member"},
        {"key": "cost", "access": "member"},
        {"key": "modelCoordination", "access": "member"},
        {"key": "docs", "access": "member"},
        {"key": "insight", "access": "member"},
        {"key": "takeoff", "access": "member"},
    ]

    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/construction/admin"
        self.base = base
        self.user_id = self.base.user_info.get("uid")

    def _get_headers(self, include_content_type=False):
        """
        Constructs the headers required for API requests.

        Args:
            include_content_type (bool, optional): Whether to include Content-Type header. Defaults to False.

        Returns:
            dict: A dictionary containing the headers.
        """
        token = f"Bearer {self.base.get_private_token()}"
        headers = {"Authorization": token}

        if self.user_id:
            headers["User-Id"] = self.user_id

        if include_content_type:
            headers["Content-Type"] = "application/json"

        return headers

    def _handle_pagination(self, url, headers, params=None, follow_pagination=False):
        """
        Handles pagination for API requests.

        Args:
            url (str): The initial URL for the API request.
            headers (dict): The headers for the API request.
            params (dict, optional): Query parameters for the API request.
            follow_pagination (bool, optional): Whether to follow pagination links.

        Returns:
            list: A list of results from all pages.
        """
        all_results = []
        next_url = url

        while next_url:
            response = requests.get(next_url, headers=headers, params=params)
            self._handle_error_response(response)

            data = response.json()
            all_results.extend(data.get("results", []))

            # Get the next URL for pagination
            next_url = (
                data.get("pagination", {}).get("nextUrl") if follow_pagination else None
            )

            # Clear params for subsequent requests using the pagination URL
            params = None

        # Add uid field for each user
        for user in all_results:
            user["sub"] = user["uid"] = user["autodeskId"]

        return all_results

    def _handle_error_response(self, response):
        """
        Handles error responses from API calls.

        Args:
            response (requests.Response): The response object from the API call.

        Raises:
            Exception: If the response contains an error.
        """
        if response.status_code >= 400:
            try:
                error_json = response.json()
                errors = error_json.get("errors") or error_json.get("detail")
                if errors:
                    if isinstance(errors, list):
                        for error in errors:
                            print(f"API Error: {error}")
                    else:
                        print(f"API Error: {errors}")
            except:
                pass
            response.raise_for_status()

    def get_users(self, project_id: str, query_params=None, follow_pagination=False):
        """
        Retrieves information about a filtered subset of users in the specified project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projectsprojectId-users-GET/

        Args:
            project_id (str): Project UUID
            query_params (dict, optional): Query parameters for filtering and sorting results. Available parameters:
                - filter[products] (array): List of products users must have access to (e.g., "build", "cost", "docs")
                - filter[name] (string): User name pattern (max 255 chars)
                - filter[email] (string): Email pattern (max 255 chars)
                - filter[accessLevels] (array): User access levels ("accountAdmin", "projectAdmin", "executive")
                - filter[companyId] (string): Company ID filter
                - filter[companyName] (string): Company name pattern
                - filter[autodeskId] (array): List of Autodesk IDs
                - filter[id] (array): List of ACC IDs
                - filter[roleId] (string): Single role ID
                - filter[roleIds] (array): List of role IDs
                - filter[status] (array): User statuses ("active", "pending", "deleted")
                - sort (array): Fields to sort by with optional "asc"/"desc" direction
                - fields (array): Fields to include in response
                - orFilters (array): Fields to combine with OR operator
                - filterTextMatch (string): Text matching method ("contains", "startsWith", "endsWith", "equals")
                - limit (int): Max records per request (1-200, default 20)
                - offset (int): Starting record number for pagination
            follow_pagination (bool, optional): Returns all results if True. If False returns up to 200 results.

        Returns:
            list[dict]: user information, filtered by query_params

        Example:
            ```python
            # Get all users from a project
            users = acc.project_users.get_users(project_id="your_project_uuid")

            # Get users with pagination
            users = acc.project_users.get_users(
                project_id="your_project_uuid",
                query_params={"limit": 50},
                follow_pagination=True
            )

            # Get users with specific filters
            filtered_users = acc.project_users.get_users(
                project_id="your_project_uuid",
                query_params={"filter[email]": "user@example.com"}
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users"
        headers = self._get_headers()

        if query_params is None:
            query_params = {}

        # add limit, offset to query_params if they dont exist
        if query_params.get("limit") is None:
            query_params["limit"] = 200
        if query_params.get("offset") is None:
            query_params["offset"] = 0

        return self._handle_pagination(
            url, headers, params=query_params, follow_pagination=follow_pagination
        )

    def get_user(self, project_id: str, user_id: str, fields: list[str] = []) -> dict:
        """
        Retrieves detailed information about the specified user in a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projectsprojectId-users-userId-GET/

        Args:
            project_id (str): The project UUID
            user_id (str): The ID of the user. You can use either the ACC ID (id) or the Autodesk ID (autodeskId).
            fields (list[str], optional): List of user fields to return.

        Returns:
            dict: Detailed project user dictionary.

        Example:
            ```python
            # Get all user fields
            user = acc.project_users.get_user(
                project_id="your_project_uuid",
                user_id="user_uuid"
            )

            # Get specific user fields
            user = acc.project_users.get_user(
                project_id="your_project_uuid",
                user_id="user_uuid",
                fields=["email", "products"]
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users/{user_id}"
        headers = self._get_headers()
        query_params = {"fields": fields}

        response = requests.get(url, headers=headers, params=query_params)
        self._handle_error_response(response)

        user = response.json()
        user["sub"] = user["uid"] = user["autodeskId"]
        return user

    def get_user_by_email(self, project_id: str, email: str) -> dict:
        """
        Retrieves a user from a project by their email address.

        Args:
            project_id (str): The project UUID
            email (str): The email address of the user to find

        Returns:
            dict: User information if found, None if no user is found with the given email

        Example:
            ```python
            # Get user by email
            user = acc.project_users.get_user_by_email(
                project_id="your_project_uuid",
                email="user@example.com"
            )
            ```
        """
        users = self.get_users(
            project_id=project_id, query_params={"filter[email]": email}
        )
        return users[0] if users else None

    def post_user(self, project_id: str, user: dict) -> dict:
        """
        Adds a user to a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-POST/

        Args:
            project_id (str): The UUID of the project.
            user (dict): A user dictionary including a minimum of email and products keys.

        Returns:
            dict: user dictionary

        Example:
            ```python
            # Add a user with member access
            new_user = {
                "email": "user@example.com",
                "products": AccProjectUsersApi.productmember
            }
            created_user = acc.project_users.post_user(
                project_id="your_project_uuid",
                user=new_user
            )

            # Add a user with admin access
            admin_user = {
                "email": "admin@example.com",
                "products": AccProjectUsersApi.productadmin
            }
            created_admin = acc.project_users.post_user(
                project_id="your_project_uuid",
                user=admin_user
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users"
        headers = self._get_headers(include_content_type=True)

        if user.get("email") is None:
            raise ValueError("Email is required")
        if user.get("products") is None:
            raise ValueError("Products is required")

        modified_user = {"email": user.get("email"), "products": user.get("products")}
        if user.get("roleIds"):
            modified_user["roleIds"] = user.get("roleIds")

        response = requests.post(url, headers=headers, json=modified_user, timeout=100)
        self._handle_error_response(response)

        return response.json()

    def post_import_users(self, project_id: str, users: list[dict]) -> bool:
        """
        Imports a list of users into a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-v2-projects-project-Id-users-import-POST/

        Args:
            project_id (str): A project UUID
            users (list[dict]): A list of user dictionaries, each containing email and products keys.

        Returns:
            bool: True if the import was successful

        Example:
            ```python
            # Import multiple users
            users_to_import = [
                {
                    "email": "user1@example.com",
                    "products": AccProjectUsersApi.productmember
                },
                {
                    "email": "user2@example.com",
                    "products": AccProjectUsersApi.productadmin
                }
            ]
            acc.project_users.post_import_users(
                project_id="your_project_uuid",
                users=users_to_import
            )
            ```
        """
        url = f"{self.base_url}/v2/projects/{project_id}/users:import"
        headers = self._get_headers(include_content_type=True)

        if len(users) == 0:
            print("No users to import")
            return True

        # Modify users list to retain only specified fields and add roleIds
        modified_users = []
        for user in users:
            modified_user = {
                "email": user.get("email"),
                "products": user.get("products"),
                #'roleIds': [user.get('default_role_id')]
            }
            modified_users.append(modified_user)

        # Split the users list into chunks of 200
        for i in range(0, len(modified_users), 200):
            chunk = modified_users[i : i + 200]
            data = {"users": chunk}

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 202:
                print(f"Chunk {i//200 + 1} imported successfully")
            else:
                self._handle_error_response(response)

        return True

    def patch_user(self, project_id: str, target_user_id: str, data: dict):
        """
        Updates a user's information in a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-PATCH/


        Args:
            project_id (str): The project UUID
            target_user_id (str): The ID of the user to update
            data (dict): The data to update

        Returns:
            dict: Updated user information

        Example:
            ```python
            # Update user's product access
            update_data = {
                "products": AccProjectUsersApi.productadmin
            }
            updated_user = acc.project_users.patch_user(
                project_id="your_project_uuid",
                target_user_id="user_uuid",
                data=update_data
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users/{target_user_id}"
        headers = self._get_headers(include_content_type=True)

        response = requests.patch(url, headers=headers, json=data)
        self._handle_error_response(response)

        return response.json()

    def patch_project_users(
        self, projects: list[dict], users: list[dict], products: list[dict] = None
    ):
        """
        Updates multiple users across multiple projects.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-PATCH/

        Args:
            projects (list[dict]): List of project dictionaries
            users (list[dict]): List of user dictionaries
            products (list[dict], optional): List of product access dictionaries

        Returns:
            None

        Example:
            ```python
            # Get all active projects
            projects = acc.projects.get_all_active_projects()

            # Define users to update
            users = [
                {"email": "user@example.com"},
                {"email": "anotheruser@example.com"}
            ]

            # Update users across all projects
            acc.project_users.patch_project_users(
                projects=projects,
                users=users,
                products=AccProjectUsersApi.productadmin
            )
            ```
        """
        # Use the provided products or the default if None.
        if products is None:
            products = productmember  # assuming productmember is defined globally

        # Build a dictionary of users keyed by email.
        user_dict = {user.get("email"): user for user in users if user.get("email")}

        for project in projects:
            project_id = project.get("id")
            if not project_id:
                continue  # Skip projects without an id

            # Assume self.get_all returns a list of project user dictionaries.
            project_users = self.get_all(project_id)
            project_user_dict = {
                pu.get("email"): pu for pu in project_users if pu.get("email")
            }

            for email, user in user_dict.items():
                if email in project_user_dict:
                    pu = project_user_dict[email]
                    # Retrieve the access level from the first product in the user's dictionary
                    user_products = user.get("products", [])
                    user_access = (
                        user_products[0].get("access")
                        if user_products and isinstance(user_products, list)
                        else None
                    )

                    # Check if any of the project user's products need updating
                    if any(
                        prod.get("key") == "projectAdministration"
                        and prod.get("access") != user_access
                        for prod in pu.get("products", [])
                    ):
                        print(
                            f"patching user {email} to project {project.get('jobNumber', 'unknown')}"
                        )
                        try:
                            self.patch_user(
                                project_id, pu.get("id"), {"products": products}
                            )
                        except Exception:
                            time.sleep(60)
                            self.patch_user(
                                project_id, pu.get("id"), {"products": products}
                            )
                    else:
                        print(
                            f"user {email} already patched to project {project.get('jobNumber', 'unknown')}"
                        )

    def delete_user(self, project_id: str, target_user_id: str):
        """
        Deletes a user from a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-DELETE/

        Args:
            project_id (str): The project UUID
            target_user_id (str): The ID of the user to delete

        Returns:
            bool: True if the deletion was successful

        Example:
            ```python
            # Delete a single user from a project
            acc.project_users.delete_user(
                project_id="your_project_uuid",
                target_user_id="user_uuid"
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users/{target_user_id}"
        headers = self._get_headers()

        response = requests.delete(url, headers=headers)
        self._handle_error_response(response)

        return True

    def delete_users(self, project_id: str, users: list[dict]):
        """
        Deletes multiple users from a project.

        Args:
            project_id (str): The project UUID
            users (list[dict]): List of user dictionaries containing email addresses

        Returns:
            None

        Example:
            ```python
            # Delete multiple users from a project
            users_to_remove = [
                {"email": "user1@example.com"},
                {"email": "user2@example.com"}
            ]
            acc.project_users.delete_users(
                project_id="your_project_uuid",
                users=users_to_remove
            )
            ```
        """
        user_emails_set = set([user.get("email") for user in users])
        project_users = self.get_users(project_id)
        users_to_delete = [
            pu for pu in project_users if pu.get("email") in user_emails_set
        ]

        for user in users_to_delete:
            print(f"Deleting user {user.get('email')} from project {project_id}")
            try:
                self.delete_user(project_id, user.get("id"))
            except:
                time.sleep(60)
                self.delete_user(project_id, user.get("id"))
