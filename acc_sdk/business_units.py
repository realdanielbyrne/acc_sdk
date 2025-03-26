from calendar import c
import requests
from .base import AccBase


class AccBusinessUnitsApi:
    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/hq/v1/accounts/:account_id/business_units_structure"
        self.base = base

    def get_business_units(self)->list[dict]:
        """
        Query all the business units in a specific BIM 360 account.
        Authorization must be Bearer <token>, where <token> is obtained via a two-legged OAuth flow.
        The GET method requires the account:read scope, and the Authentication Context	
        is app only.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/business_units_structure-GET/

        Returns:
            list[dict]: An array of business units associated with the account_id                
        """
        token = f"Bearer {self.base.get_2leggedToken()}"
        headers = {"Authorization": token}
        url = self.base_url.replace(":account_id", self.base.account_id)

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            return content.get("business_units", [])
        else:
            error = response.json().get('errors')
            if error:
                print(error)
            detail = response.json().get('detail')
            if detail:
                print(detail)
            response.raise_for_status()

    def update_business_units(self, business_units:list[dict])->list[dict]:
        """
        Creates or redefines the business units of a specific BIM 360 account.
        Authorization must be Bearer <token>, where <token> is obtained via a two-legged OAuth flow.
        The PUT method requires the account:write scope, and the Authentication Context is app only.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/business_units_structure-PUT/
            
        Args:
            business_units (dict): The business units to create or redefine. Each business unit
            must have a unique name, and optional id, parent_id, and description fields.
            If Id is specified and already existing, the existing business unit will be replaced
            with the provided attributes. If ID specified and not already existing, a new business 
            unit will be created with the id. If Id unspecified, a new business unit will be created
            with a server-generated id.

        Returns:
            list[dict]: An array of created or modified business units.
        """
        token = f"Bearer {self.base.get_2leggedToken()}"
        headers = {"Authorization": token,
                   "Content-Type": "application/json"}
        url = self.base_url.replace(":account_id", self.base.account_id)

        response = requests.put(url, headers=headers, json=business_units)
        if response.status_code == 200:
            content = response.json()
            return content
        else:
            error = response.json().get('errors')
            if error:
                print(error)
            detail = response.json().get('detail')
            if detail:
                print(detail)
            response.raise_for_status()