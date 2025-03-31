# accapi/account_users.py
import requests
from .base import AccBase

class AccAccountUsersApi:
    """
    This class provides methods to interact with the account users endpoint of the Autodesk Construction Cloud API.
    
    Authentication must be Bearer <token>, where <token> is obtained via a two-legged OAuth flow.
    The GET methods require account:read scope, and the POST/PATCH methods require account:write scope.

    Example:
        ```python
        from accapi import Acc
        acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)
        
        # Get all users
        users = acc.account_users.get_users()
        
        # Create a new user
        new_user = {
            "email": "user@example.com",
            "company_id": "company_uuid"
        }
        created_user = acc.account_users.post_user(new_user)
        
        # Update user status
        updated_user = acc.account_users.patch_user(
            user_email="user@example.com",
            status="active"
        )
        ```
    """
    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/hq/v1"
        self.base = base
        self.user_id = self.base.user_info.get('uid')

    def get_user_by_id(self, user_id)->dict:
        """
        Get a user by user ID.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-:user_id-GET/

        Args:
            user_id (str): The user ID to lookup the user by.

        Returns:
            dict: user object

        Example:
            ```python
            # Get user by ID
            user = acc.account_users.get_user_by_id("user_uuid")
            ```
        """
        
        headers = {"Content-Type": "application/json", 
                   "Authorization": f"Bearer {self.base.get_2leggedToken()}"}
        response = requests.get(
            f"{self.base_url}/accounts/{self.base.account_id}/users/{user_id}",
            headers=headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_user_by_email(self, email):
        """
        Get a user by email address.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-search-GET/

        Args:
            email (str): The email address to lookup the user by

        Returns:
            dict: user object

        Example:
            ```python
            # Get user by email
            user = acc.account_users.get_user_by_email("user@example.com")
            if user:
                print(f"Found user: {user['name']}")
            else:
                print("User not found")
            ```
        """
        if email == None:
            raise Exception("Email is required")
        
        headers = {"Content-Type": "application/json", 
                   "Authorization": f"Bearer {self.base.get_2leggedToken()}"}
        response = requests.get(
            f"{self.base_url}/accounts/{self.base.account_id}/users/search?email={email}&limit=1",
            headers=headers,
        )

        if response.status_code == 200:
            users = response.json()
            if not users:
                return None
            user = users[0]
            user['autodeskId'] = user['sub'] = user['uid']
            return user
        
        else:
            response.raise_for_status()
            
    def get_users(self, sort=None, fields=None, limit=10, offset=0)->list[dict]:
        """
        Get all users in the account.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-GET/

        Args:
            sort (str, optional): Sort the users by a field. Defaults to None.
            fields (str, optional): Fields to return in the response. Defaults to None.
            limit (int, optional): Limit the number of users to return. Default 10, Max 100.
            offset (int, optional): Offset the number of users to return. Defaults to 0.

        Returns:
            list[dict]: A successful response is an array of users, flat JSON objects 
            with the following attributes:

        Example:
            ```python
            # Get all users
            users = acc.account_users.get_users()
            
            # Get users with specific fields
            users = acc.account_users.get_users(
                fields="name,email,status",
                sort="name"
            )        
            ```
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.base.get_2leggedToken()}",
        }
        url = (
            f"{self.base_url}/accounts/{self.base.account_id}/users"
        )
        params = {"limit": 100, "offset": 0}

        if sort:
            params["sort"] = sort
        if fields:
            params["field"] = fields
        

        all_users = []
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                users = response.json()
                if not users:
                    break
                all_users.extend(users)
                params["offset"] += 100
            else:
                response.raise_for_status()

        return all_users

    def get_users_search(self, **params)->list[dict]:
        """
        Get users by search parameters.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-search-GET/

        Args:
            name (str): User name to match
            email (str): User email to match
            company_name (str): User company to match
            operator (str): Boolean operator to use: OR (default) or AND
            partial (bool): If true (default), perform a fuzzy match
            limit (int): Response array's size
            offset (int): Offset of response array
            sort (str): Comma-separated fields to sort by in ascending order, prepending 
            a field with - sorts in descending order. Invalid fields and whitespaces will be ignored.
            field (str): Comma-separated fields to include in response

            id will always be returned.
            Invalid fields will be ignored.

        Returns:
            list[dict]: a list of user objects matching the search criteria

        Example:
            ```python
            # Search users by name
            users = acc.account_users.get_users_search(
                name="John",
                partial=True
            )
            
            # Search users by company
            company_users = acc.account_users.get_users_search(
                company_name="Construction Co",
                operator="AND"
            )
            
            # Search with multiple criteria
            filtered_users = acc.account_users.get_users_search(
                name="John",
                company_name="Construction Co",
                operator="AND",
                sort="-name"
            )
            ```
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.base.get_2leggedToken()}",
        }
        base_url = f"{self.base_url}/accounts/{self.base.account_id}/users/search"

        params["limit"] = 100
        params["offset"] = 0
        all_users = []
        while True:
            response = response = requests.get(base_url, headers=headers, params=params)

            if response.status_code == 200:
                users = response.json()
                if not users:
                    break
                all_users.extend(users)
                params["offset"] += 100
            else:
                response.raise_for_status()

        return all_users

    def post_user(self, user: dict)->dict:
        """
        Create a user.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-POST/
        
        Args:
            user (dict): the user object to create. Required fields are email and company_id.

        Returns:
            dict: the user object

        Example:
            ```python
            # Create a new user
            new_user = {
                "email": "user@example.com",
                "company_id": "company_uuid",
                "name": "John Doe"
            }
            created_user = acc.account_users.post_user(new_user)
            print(f"Created user: {created_user['name']}")
            
            # Create user with default company
            new_user = {
                "email": "user@example.com",
                "name": "John Doe"
            }
            created_user = acc.account_users.post_user(new_user)
            ```
        """
        if user.get("email") == None:
            raise Exception("User email is required at a minimum.")

        if user.get("company_id") == None and self.base.company_id:
            user["company_id"] = self.base.company_id
        elif user.get("company_id") == None and not self.base.company_id:
            raise Exception("Company ID is required")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.base.get_2leggedToken()}",
            "User-Id": self.user_id
        }
        
        response = requests.post(
            f"{self.base_url}/accounts/{self.base.account_id}/users",
            headers=headers,
            json=user,
        )
        if response.status_code == 201:
            print("User created")
            return response.json()

        elif response.status_code == 409:
            print("User already exists")
            return self.get_user_by_email(user["email"])
        else:
            response.raise_for_status()

    def post_users(self, users: list[dict]):
        """
        Create multiple users.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-import-POST/        

        Args:
            users (list[dict]): a list of user objects to create. Required fields are email and company_id.

        Returns:
            success (int): Import success company count
            failure (int): Import failure company count
            success_items (list[dict]): Array of user objects that were successfully imported
            failure_items (list[dict]): Array of user objects that failed to import, 
            along with content and error information

        Example:
            ```python
            # Import multiple users
            users_to_import = [
                {
                    "email": "user1@example.com",
                    "company_id": "company_uuid",
                    "name": "John Doe"
                },
                {
                    "email": "user2@example.com",
                    "company_id": "company_uuid",
                    "name": "Jane Smith"
                }
            ]
            result = acc.account_users.post_users(users_to_import)
            
            # Check import results
            print(f"Successfully imported: {result['success']} users")
            print(f"Failed to import: {result['failure']} users")
            
            # Print successful imports
            for user in result['success_items']:
                print(f"Created user: {user['name']}")
            
            # Print failed imports
            for failure in result['failure_items']:
                print(f"Failed to import: {failure['email']}")
                print(f"Error: {failure['error']}")
            ```
        """
        for user in users:
            if user.get("company_id") == None and self.base.company_id:
                user["company_id"] = self.base.company_id
            elif user.get("company_id") == None and not self.base.company_id:
                raise Exception("Company ID is required.")

        token = self.base.get_2leggedToken()

        headers = {
            "Content-Type": "application/json",
            "Authorization": token,
            "User-Id": self.user_id,
        }
        response = requests.post(
            f"{self.base_url}/accounts/{self.base.account_id}/users/import",
            headers=headers,
            json=users,
        )

        if response.status_code == 201:
            print("Users created")
            return response.json()
        else:
            response.raise_for_status()

    def patch_user(self, user_email: str, status: str = None, company_id:str = None)->dict:
        """
        Update a user's status or default company.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/users-:user_id-PATCH/

        Args:
            user_email (str): user email
            status (str): status to set the user to. Must be either 'active' or 'inactive'

        Returns:
            dict: The user object

        Example:
            ```python
            # Update user status
            updated_user = acc.account_users.patch_user(
                user_email="user@example.com",
                status="active"
            )
            print(f"Updated user status: {updated_user['status']}")
            
            # Update user's company
            updated_user = acc.account_users.patch_user(
                user_email="user@example.com",
                company_id="new_company_uuid"
            )
            print(f"Updated user company: {updated_user['company_id']}")
            
            # Update both status and company
            updated_user = acc.account_users.patch_user(
                user_email="user@example.com",
                status="inactive",
                company_id="new_company_uuid"
            )
            ```
        """
        if status and status not in ["active", "inactive"]:
            raise Exception("Status must be either 'active' or 'inactive'")
        
        user_id = self.get_user_by_email(user_email)["id"]
        body = {}
        if status:
            body["status"] = status
        if company_id:
            body["company_id"] = company_id
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.base.get_2leggedToken()}",
            "User-Id": self.user_id,
        }
        response = requests.patch(
            f"{self.base_url}/accounts/{self.base.account_id}/users/{user_id}",
            headers=headers,
            json=body,
        )

        if response.status_code == 200:
            print("User updated")
            return response.json()
        else:
            response.raise_for_status()
