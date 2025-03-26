import requests
import os
import mimetypes
from .base import AccBase


class AccCompaniesApi:
    '''
    This class provides methods to interact with the project users endpoint of the Autodesk Construction Cloud API.
    
    Authentication must be Bearer <token>, where <token> is obtained via either a two-legged or three-legged OAuth flow.    
    The GET methods require account:read scope and either a 2-legged or 3-legged auth token, and the POST and PATCH methods
    require account:write scope and a 2-legged auth token.

    '''
    def __init__(self, base: AccBase):
        self.base = base
        self.user_id = self.base.user_info.get('uid')

    def get_companies(self, user_id=None, filter_name=None, filter_trade=None, filter_erpId=None, filter_taxId=None, 
                      filter_updatedAt=None, orFilters=None, filterTextMatch=None, sort=None, fields=None, limit=20, offset=0):
        """ 
        Returns a list of companies in an account. You can also use this endpoint to 
        filter out the list of companies by setting the filter parameters.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/companies-GET/
        
        Args:
            user_id (str, optional): The ID of a user on whose behalf your request is acting.
            filter_name (str, optional): Filter companies by name.
            filter_trade (str, optional): Filter companies by trade.
            filter_erpId (str, optional): Filter companies by ERP Id.
            filter_taxId (str, optional): Filter companies by tax Id.
            filter_updatedAt (str, optional): Filter companies by updated at date range.
            orFilters (list or str, optional): List of fields to apply an “or” operator.
            filterTextMatch (str, optional): How to match text fields (e.g. contains, startsWith, etc.).
            sort (list or str, optional): List of fields to sort by.
            fields (list or str, optional): List of fields to return in the response.
            limit (int, optional): The number of resources to return. Defaults to 20.
            offset (int, optional): The number of resources to skip. Defaults to 0.

        Returns:
            list: The list of companies (results array) from the API response.
        """
        token = f"Bearer {self.base.get_2leggedToken()}"
            
        headers = {"Authorization": token,
                   "user_id": self.user_id}
        
        # Replace :accountId in the base URL
        url = f"https://developer.api.autodesk.com/construction/admin/v1/accounts/{self.base.account_id}/companies"
        
        # Build the query parameters
        params = {}
        if filter_name is not None:
            params["filter[name]"] = filter_name
        if filter_trade is not None:
            params["filter[trade]"] = filter_trade
        if filter_erpId is not None:
            params["filter[erpId]"] = filter_erpId
        if filter_taxId is not None:
            params["filter[taxId]"] = filter_taxId
        if filter_updatedAt is not None:
            params["filter[updatedAt]"] = filter_updatedAt
        if orFilters is not None:
            params["orFilters"] = ",".join(orFilters) if isinstance(orFilters, list) else orFilters
        if filterTextMatch is not None:
            params["filterTextMatch"] = filterTextMatch
        if sort is not None:
            params["sort"] = ",".join(sort) if isinstance(sort, list) else sort
        if fields is not None:
            params["fields"] = ",".join(fields) if isinstance(fields, list) else fields

        # Always include limit and offset
        params["limit"] = limit
        params["offset"] = offset

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            content = response.json()
            # Only return the "results" array to the caller.
            return content.get("results", [])
        else:
            error = response.json().get('errors')
            if error:
                print(error)
            detail = response.json().get('detail')
            if detail:
                print(detail)
            response.raise_for_status()

    def get_company(self, company_id):
        """ 
        Returns a single company in an account.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/companies-:company_id-GET/
        
        Args:
            company_id (str): The ID of the company to retrieve.

        Returns:
            dict: The company object from the API response.        
        """
        token = f"Bearer {self.base.get_private_token()}"
            
        headers = {"Authorization": token,
                   "User-Id": self.user_id}
        
        url = f"https://developer.api.autodesk.com/hq/v1/accounts/{self.base.account_id}/companies/{company_id}"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            return content
        else:
            response.raise_for_status()

    def update_company(self, account_id, company_id, data, region=None):
        """
        Update the specified attributes of a partner company using Autodesk's API.
        
        This method implements the PATCH request to update a company. It builds the URL
        optionally using the legacy endpoint for EMEA/EU regions, sets the necessary
        headers, and sends the JSON payload containing the update details.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/companies-:company_id-PATCH/
        
        Args:
            account_id (str): The account ID (UUID) for the company.
            company_id (str): The company ID (UUID).
            data (dict): A dictionary containing the update attributes. For example:
                {
                    "name": "Autodesk",
                    "trade": "Concrete",
                    "phone": "(503)623-1525"
                }
            region (str, optional): The region where the service is located ("US" or "EMEA").
                If set to "EU" or "EMEA", the legacy endpoint is used.
        
        Returns:
            dict: A dictionary representing the updated company data.
        
        Raises:
            requests.HTTPError: If the HTTP request returns a status code indicating an error.
        """
        # Retrieve OAuth token
        token = self.base.get_2leggedToken()
        
        # Set headers required by the API
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # If a region is specified, add it to headers and adjust the endpoint if necessary.
        if region:
            headers["Region"] = region
            # For EMEA or EU, use the legacy endpoint URL.
            if region.upper() in ["EU", "EMEA"]:
                url = f"https://developer.api.autodesk.com/hq/v1/regions/eu/accounts/{account_id}/companies/{company_id}"
            else:
                url = f"https://developer.api.autodesk.com/hq/v1/accounts/{account_id}/companies/{company_id}"
        else:
            url = f"https://developer.api.autodesk.com/hq/v1/accounts/{account_id}/companies/{company_id}"
        
        # Send the PATCH request with the JSON data
        response = requests.patch(url, json=data, headers=headers)
        
        # Raise an exception if the request was unsuccessful
        if response.status_code != 200:
            response.raise_for_status()
        
        # Return the updated company details as a JSON object
        return response.json()

    def update_company_image(self, account_id, company_id, file_path, region=None, mime_type=None):
        """
        Update or create a partner company's image using Autodesk's API.
        
        This method sends a PATCH request to update a company image. It constructs the correct URL
        (using the legacy endpoint for "EU" or "EMEA" regions if applicable), and uploads the image
        file using multipart/form-data.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/companies-:company_id-image-PATCH/
        
        Args:
            account_id (str): The account ID (UUID) for the company.
            company_id (str): The company ID (UUID).
            file_path (str): Path to the image file to be uploaded.
            region (str, optional): The region where the service is located ("US" or "EMEA"). If set to "EU" or "EMEA",
                the legacy endpoint is used.
            mime_type (str, optional): The MIME type of the image file (e.g., "image/png"). If not provided, it will
                be auto-detected based on the file extension.
        
        Returns:
            dict: A dictionary representing the updated company data.
        
        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        # Retrieve OAuth token
        token = self.base.get_2leggedToken()
        
        # Set the Authorization header (do not manually set Content-Type for multipart requests)
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Construct the correct endpoint URL based on region
        if region:
            headers["Region"] = region
            if region.upper() in ["EU", "EMEA"]:
                url = f"https://developer.api.autodesk.com/hq/v1/regions/eu/accounts/{account_id}/companies/{company_id}/image"
            else:
                url = f"https://developer.api.autodesk.com/hq/v1/accounts/{account_id}/companies/{company_id}/image"
        else:
            url = f"https://developer.api.autodesk.com/hq/v1/accounts/{account_id}/companies/{company_id}/image"
        
        # Auto-detect MIME type if not provided
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
        
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file_obj:
            # The file is sent in a multipart form under the key "chunk"
            files = {
                "chunk": (file_name, file_obj, mime_type)
            }
            response = requests.patch(url, headers=headers, files=files)
        
        # Raise an exception for non-successful responses
        if response.status_code != 200:
            response.raise_for_status()
        
        return response.json()
