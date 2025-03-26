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
        """
        headers = { "Authorization": f"Bearer {self.base.get_3leggedToken()}" }
        response = requests.get(
            f"{self.baseAddress}/userinfo",
            headers=headers
        )

        response.raise_for_status()
        return response.json()
        