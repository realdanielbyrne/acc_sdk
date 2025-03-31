import requests
from .base import AccBase


class AccUserProfileApi:
    def __init__(self,base: AccBase):
        self.baseAddress = "https://api.userprofile.autodesk.com"
        self.base = base

    def get_user_info(self):
        """
        Fetches basic information for the given authenticated user. Only supports 3-legged access tokens.
        https://aps.autodesk.com/en/docs/profile/v1/reference/profile/oidcuserinfo/
        
        Returns:
            dict: User information

        Example:
            ```python
            user_info = acc.userprofile.get_user_info()
            print(user_info)
            ```
        """
        token = self.base.get_private_token()
        headers = { "Authorization": f"Bearer {token}" }
        response = requests.get(
            f"{self.baseAddress}/userinfo",
            headers=headers
        )

        response.raise_for_status()
        return response.json()
        