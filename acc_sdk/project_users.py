# accapi/project_users.py
import requests
from .base import AccBase
import time


class AccProjectUsersApi:
    '''
    This class provides methods to interact with the project users endpoint of the Autodesk Construction Cloud API.
    The class provides methods to get, add, update, and delete users in a project as well as bulk implementations of these methods.
    
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
        created_user = acc.project_users.add_user(project_id="your_project_uuid", user=new_user)
        ```
    '''

    productadmin = [
                    {
                        "key": "projectAdministration",
                        "access": "administrator"
                    },
                    {
                        "key": "designCollaboration",
                        "access": "administrator"
                    },
                    {
                        "key": "build",
                        "access": "administrator"
                    },
                    {
                        "key": "cost",
                        "access": "administrator"
                    },
                    {
                        "key": "modelCoordination",
                        "access": "administrator"
                    },
                    {
                        "key": "docs",
                        "access": "administrator"
                    },
                    {
                        "key": "insight",
                        "access": "administrator"
                    },
                    {
                        "key": "takeoff",
                        "access": "administrator"
                    }
                    ]

    productmember = [
                    {
                        "key": "projectAdministration",
                        "access": "none"
                    },
                    {
                        "key": "designCollaboration",
                        "access": "member"
                    },
                    {
                        "key": "build",
                        "access": "member"
                    },
                    {
                        "key": "cost",
                        "access": "member"
                    },
                    {
                        "key": "modelCoordination",
                        "access": "member"
                    },
                    {
                        "key": "docs",
                        "access": "member"
                    },
                    {
                        "key": "insight",
                        "access": "member"
                    },
                    {
                        "key": "takeoff",
                        "access": "member"
                    }
                    ]  
    
    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/construction/admin"
        self.base = base
        self.user_id = self.base.user_info.get('uid')

    def get_users(self, project_id:str, query_params=None, follow_pagination=False):
        """
        Retrieves information about a filtered subset of users in the specified project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projectsprojectId-users-GET/

        Args:
            project_id (str): Project UUID
            query_params (dict, optional): One of the filters described in the official documentation.
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
        token = f"Bearer {self.base.get_private_token()}"

        base_url = f"{self.base_url}/v1/projects/{project_id}/users"
        headers = {"Authorization": token, "User-Id": self.user_id}
        all_users = []
        next_url = base_url

        if query_params is None:
            query_params = {}
            
        # add limit, offset to query_params if they dont exist
        if query_params.get('limit') is None:
            query_params['limit'] = 200
        if query_params.get('offset') is None:
            query_params['offset'] = 0
        
        
        while next_url:
            response = requests.get(next_url, headers=headers, params=query_params)
            if response.status_code != 200:
                response.raise_for_status()

            data = response.json()            
            all_users.extend(data["results"])

            next_url = data["pagination"].get("nextUrl") if follow_pagination else None

            # Clear query parameters for subsequent requests using the pagination URL
            query_params = None

        # foreach user in all_users, add user['uid'] = user['autodeskId']
        for user in all_users:
            user["sub"] = user["uid"] = user["autodeskId"]
        
        return all_users

    def get_user(self, project_id:str, user_id:str, fields:list[str]=[])->dict:
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
        token = f"Bearer {self.base.get_private_token()}"

        url = f"{self.base_url}/v1/projects/{project_id}/users/{user_id}"
        headers = {"Authorization": token}
        query_params = {"fields": fields}
        response = requests.get(url, headers=headers, params=query_params)

        if response.status_code == 200:
            user = response.json()
            user["sub"] = user["uid"] = user["autodeskId"]
            return user
        else:
            response.raise_for_status()

    def add_user(self, project_id:str, user: dict)->dict:
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
            created_user = acc.project_users.add_user(
                project_id="your_project_uuid",
                user=new_user
            )
            
            # Add a user with admin access
            admin_user = {
                "email": "admin@example.com",
                "products": AccProjectUsersApi.productadmin
            }
            created_admin = acc.project_users.add_user(
                project_id="your_project_uuid",
                user=admin_user
            )
            ```
        """
        url = f"{self.base_url}/v1/projects/{project_id}/users"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/json",
            "User-Id": self.user_id,
        }

        if user.get("email") is None:
            raise ValueError("Email is required")
        if user.get("products") is None:
            raise ValueError("Products is required")

        modified_user = {"email": user.get("email"), "products": user.get("products")}
        if user.get("roleIds"):
            modified_user["roleIds"] = user.get("roleIds")

        response = requests.post(url, headers=headers, json=modified_user, timeout=100)
        response.raise_for_status()

        return response.json()
        
    def import_users(self, project_id:str, users: list[dict]):
        """
        Imports a list of users into a project.
        
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-v2-projects-project-Id-users-import-POST/
        
        Args:
            project_id (str): A project UUID
            users (list[dict]): A list of user dictionaries, each containing email and products keys.

        Returns:
            None

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
            acc.project_users.import_users(
                project_id="your_project_uuid",
                users=users_to_import
            )
            ```
        """
        token = f"Bearer {self.base.get_private_token()}"

        url = f"{self.base_url}/v2/projects/{project_id}/users:import"
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Id": self.user_id
        }

        if len(users) == 0:
            print("No users to import")
            return

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
                response.raise_for_status()

    def patch(self, project_id:str, target_user_id:str, data:dict):
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
            updated_user = acc.project_users.patch(
                project_id="your_project_uuid",
                target_user_id="user_uuid",
                data=update_data
            )
            ```
        """
        token = f"Bearer {self.base.get_private_token()}"

        url = f"{self.base_url}/v1/projects/{project_id}/users/{target_user_id}"
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Id": self.user_id,
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def patch_project_users(self, projects: list[dict], users: list[dict], products: list[dict] = None):
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
        user_dict = {user.get('email'): user for user in users if user.get('email')}
        
        for project in projects:
            project_id = project.get('id')
            if not project_id:
                continue  # Skip projects without an id
            
            # Assume self.get_all returns a list of project user dictionaries.
            project_users = self.get_all(project_id)
            project_user_dict = {pu.get('email'): pu for pu in project_users if pu.get('email')}
            
            for email, user in user_dict.items():
                if email in project_user_dict:
                    pu = project_user_dict[email]
                    # Retrieve the access level from the first product in the user's dictionary
                    user_products = user.get('products', [])
                    user_access = user_products[0].get('access') if user_products and isinstance(user_products, list) else None

                    # Check if any of the project user's products need updating
                    if any(prod.get('key') == 'projectAdministration' and prod.get('access') != user_access
                        for prod in pu.get('products', [])):
                        print(f"patching user {email} to project {project.get('jobNumber', 'unknown')}")
                        try:
                            self.patch(project_id, pu.get('id'), {'products': products})
                        except Exception:
                            time.sleep(60)
                            self.patch(project_id, pu.get('id'), {'products': products})
                    else:
                        print(f"user {email} already patched to project {project.get('jobNumber', 'unknown')}")


    def delete(self, project_id:str, target_user_id:str):
        """
        Deletes a user from a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-DELETE/

        Args:
            project_id (str): The project UUID
            target_user_id (str): The ID of the user to delete

        Returns:
            None

        Example:
            ```python
            # Delete a single user from a project
            acc.project_users.delete(
                project_id="your_project_uuid",
                target_user_id="user_uuid"
            )
            ```
        """
        token = f"Bearer {self.base.get_private_token()}"

        url = f"{self.base_url}/v1/projects/{project_id}/users/{target_user_id}"

        headers = {"Authorization": token, 
                   "User-Id": self.user_id}

        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return True
        else:
            response.raise_for_status()

    def delete_users(self, project_id:str, users:list[dict]):
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
        user_emails_set = set([user.get('email') for user in users])
        project_users = self.get_users(project_id)
        users_to_delete = [pu for pu in project_users if pu.get('email') in user_emails_set]

        for user in users_to_delete:
            print(f"Deleting user {user.get('email')} from project {project_id}")
            try:
                self.delete(project_id, user.get('id'))
            except:
                time.sleep(60)
                self.delete(project_id, user.get('id'))

