import requests
from .authentication import Authentication

class AccBase:
    def __init__(self, 
                auth_client: Authentication,
                account_id = None                
            ):
        """
        Initializes the AccBase class.

        Args:
            auth_client (Authentication): An instance of the Authentication class
            which contains valid Bearer tokens, either 2-legged, 3-legged, or both.
            account_id (str, optional): The account ID.  Soem API calls require an account ID,
            but it can be derived from a 2-legged token, and thus is optional.

        """
        
        self.auth_client = auth_client
        self.company_id = None

        self.account_id = account_id
        self.hub_id = "b."+self.account_id if self.account_id else None
        
        if self.account_id is None and self.get_private_token():                
            self.hub_id, self.account_id = self.get_account_id()    
            if not self.account_id:
                print("Warning: Account ID is required for some API calls.")
            
        self.admin_email = auth_client.admin_email
        if self.admin_email and self.get_2leggedToken():
            self.user_info = self.get_user_by_email(self.admin_email)
            self.company_id = self.user_info.get('company_id')
            self.account_id = self.user_info.get('account_id')
        
        if self.account_id and not self.company_id:
            self.company_id = self.get_company_id()

        # get token holder user info
        if self.get_3leggedToken():
            self.user_info = self.auth_client.get_user_info()
            
    def get_user_by_email(self, email)->dict:
        """Get a user by email address.

        Args:
            email (str): The email address to lookup the user by

        Returns:
            dict: The user object
        """
        if email == None:
            raise Exception("Email is required")
        
        headers = {"Content-Type": "application/json", 
                   "Authorization": f"Bearer {self.get_2leggedToken()}"}
        response = requests.get(
            f"https://developer.api.autodesk.com/hq/v1/accounts/{self.account_id}/users/search?email={email}&limit=1",
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
            None

    def get_2leggedToken(self):
        """Look for a 2legged token in the auth_client._session dictionary

        Returns:
            str: Bearer token
        """
        return self.auth_client.get_2legged_token()
        
    def get_3leggedToken(self):
        """Look for a 3legged token in the auth_client._session dictionary

        Returns:
            str: Bearer token
        """
        return self.auth_client.get_3legged_token()

    def get_private_token(self):
        """
        Get the private token from the auth_client.

        Returns:
            str: Bearer token
        """
        return self.get_2leggedToken() if self.get_2leggedToken() else self.get_3leggedToken()
                    
    def get_company_id(self):
        """
        Get the company ID from the account ID.

        Returns:
            str: Company ID
        """
        headers = {"Authorization": f"Bearer {self.get_private_token()}"}
        response = requests.get(
            f"https://developer.api.autodesk.com/construction/admin/v1/accounts/{self.account_id}/companies", 
            headers=headers
        )

        if response.status_code == 200:
            return response.json()["results"][0]["id"]
        else:
            return None

    def _get_hub_id(self):
        """
        Get the hub ID from the private token.

        Returns:
            str: The hub ID
        """
        headers = { "Authorization": f"Bearer {self.get_private_token()}" }
        response = requests.get(
            "https://developer.api.autodesk.com/project/v1/hubs", headers=headers
        )

        if response.status_code == 200:
            return response.json()["data"][0]["id"]
        else:
            return None

    def get_account_id(self):
        """Get the account ID from the hub ID.

        Returns:
            list[str]: The hub ID and account ID
        """
        hub_id = self._get_hub_id()        
        if hub_id:
            return hub_id, hub_id.split("b.")[1]
        else:
            return None

    