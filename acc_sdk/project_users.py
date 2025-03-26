# accapi/project_users.py
import requests
from .base import AccBase
import time


class AccProjectUsersApi:
    '''
    This class provides methods to interact with the project users endpoint of the Autodesk Construction Cloud API.
    The class provides methods to get, add, update, and delete users in a project as well as bulk implementaitons of these methods.
    
    Token must be Bearer <token>, where <token> is is obtained via either or with two-legged or three-legged oauth flow.
    The GET methods require account:read and the POST, PATCH, and DELETE methods require account:write scopes.
    The POST, PATCH, and DELETE methods require the User-Id header to be set to the user's ID when two-legged authentication
    is used.    
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
            fields (list[str], optional): List of user fiuelds to return.

        Returns:
            dict: Detailed project user dictionary.
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
            project_id (str): _description_the UUID of the project.
            user (dict): A user dictionary including a minimum of email and products keys.

        Returns:
            dict: user dictionary    
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
        Updates a user in a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-PATCH/
        
        Args:
            project_id (str): A project UUID
            target_user_id (str): ID of user to update
            data (dict): User data to update  

        Returns:
            dict: a user dictionary
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
        Patch users in a project using dictionaries.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-PATCH/
        
        Args:
            projects (list[dict]): A list of project dictionaries.
            users (list[dict]): A list of user dictionaries.
            products (list[dict], optional): A list of product dictionaries. Defaults to productmember.
        
        Returns:
            None
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
        Removes the specified user from a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projects-project-Id-users-userId-DELETE/
        
        Args:
            project_id (str): A project UUID
            target_user_id (str): The ID of the user to remove from the project.

        Returns:
            None
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
        Deletes a list of users from a project.

        Args:
            project_id (str): A project UUID
            users (list[dict]): A list of user dictionaries with user e-mails to delete from the project.
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

