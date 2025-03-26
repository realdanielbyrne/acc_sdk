import requests
import os
from datetime import datetime
from .base import AccBase


class AccSheetsApi:
    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/construction/sheets/v1"
        self.base = base

    ###########################################################################
    # Version Sets
    ###########################################################################
    def create_version_set(self, project_id:str, issuance_date:datetime, name):
        """
        Create version sets
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-sets-POST/

        Args:
            project_id (str): The project id
            issuance_date (datetime): ISO 8601 formatted date string
            name (_type_): The name of the version set (max size 255 characters)

        Returns:
            dict: The created version set
        """
        token = self.base.get_private_token()
        # Validate issuance_date
        try:
            datetime.strptime(issuance_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        # Validate name
        if not (0 < len(name) <= 255) or name.isspace():
            raise ValueError(
                "Invalid name. It should be a non-empty string with a max length of 255 characters."
            )

        # Prepare the data
        data = {"name": name, "issuanceDate": f"{issuance_date}T00:00:00.000Z"}

        # Set the headers
        headers = {"Authorization": token, "Content-Type": "application/json"}

        # API endpoint
        url = f"{self.base_url}/projects/{project_id}/version-sets"

        # Perform the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check the response
        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def get_version_sets(self, project_id:str, query_params=None):
        """
        Get version sets
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-sets-GET/

        Args:
            project_id (str): The project id
            query_params (dict, optional): The query parameters to filter the version sets

        Returns:
            list: An array of version sets
        """
            
        token = self.base.get_private_token()
        # Set the headers
        headers = {"Authorization": token}

        # API endpoint with the project_id
        url = f"{self.base_url}/projects/{project_id}/version-sets"

        # Perform the GET request
        response = requests.get(url, headers=headers, query_params=query_params)

        # Check the response
        if response.status_code == 200:
            version_sets = response.json()["results"]
            print("Version sets retrieved successfully.")
            return version_sets
        else:
            response.raise_for_status()

    def patch_version_set(self, project_id:str, version_set_id:str, issuance_date:datetime, name:str):
        """
        Update a version set
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-sets-versionSetId-PATCH/

        Args:
            project_id (str): The project id
            version_set_id (str): The version set id
            issuance_date (datetime): ISO 8601 formatted date string
            name (str): The name of the version set (max size 255 characters)

        Returns:
            None
        """
        token = self.base.get_private_token()
        # Validate issuance_date
        try:
            datetime.strptime(issuance_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        # Validate name
        if not (0 < len(name) <= 255) or name.isspace():
            raise ValueError(
                "Invalid name. It should be a non-empty string with a max length of 255 characters."
            )

        # Prepare the data
        data = {"name": name, "issuanceDate": f"{issuance_date}T00:00:00.000Z"}

        # Set the headers
        headers = {"Authorization": token, "Content-Type": "application/json"}

        # API endpoint
        url = f"{self.base_url}/projects/{project_id}/version-sets/{version_set_id}"

        # Perform the PATCH request
        response = requests.patch(url, headers=headers, json=data)

        # Check the response
        if response.status_code == 200:
            print("Version set updated successfully.")
        else:
            response.raise_for_status()

    def batch_get_version_sets(self, project_id, ids: list[str]):
        """
        Get multiple version sets by their ids
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-setsbatch-get-POST/

        Args:
            project_id (str): The project id
            ids (list): A list of version set ids

        Returns:
            list: An array of version sets
        """
        
        token = self.base.get_private_token()
        # Validate ids
        if not isinstance(ids, list) or not all(isinstance(id, str) for id in ids):
            raise ValueError("Invalid ids. It should be a list of strings.")

        # Prepare the data
        data = {"ids": ids}

        # Set the headers
        headers = {"Authorization": token, "Content-Type": "application/json"}

        # API endpoint
        url = f"{self.base_url}/projects/{project_id}/version-sets:batch-get"

        # Perform the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check the response
        if response.status_code == 200:
            version_sets = response.json()["results"]
            print("Version sets retrieved successfully.")
            return version_sets
        else:
            response.raise_for_status()

    def delete_version_set(self, project_id, version_set_id):
        """
        Delete a version set
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-setsbatch-delete-POST/

        Args:
            project_id (str): The project id
            version_set_id (str): The version set id

        Returns:
            None
        """
        token = self.base.get_private_token()

        # Set the headers
        headers = {"Authorization": token}

        # API endpoint
        url = f"{self.base_url}/projects/{project_id}/version-sets/{version_set_id}"

        # Perform the DELETE request
        response = requests.delete(url, headers=headers)

        # Check the response
        if response.status_code == 204:
            print("Version set deleted successfully.")
        else:
            response.raise_for_status()

    def batch_delete_version_sets(self, project_id, ids):
        """
        Delete multiple version sets by their ids
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-version-setsbatch-delete-POST/

        Args:
            project_id (str): The project id
            ids (list): A list of version set ids

        Returns:
            None
        """
        token = self.base.get_private_token()
        # Validate ids
        if not isinstance(ids, list) or not all(isinstance(id, str) for id in ids):
            raise ValueError("Invalid ids. It should be a list of strings.")

        # Prepare the data
        data = {"ids": ids}

        # Set the headers
        headers = {"Authorization": token, "Content-Type": "application/json"}

        # API endpoint
        url = f"{self.base_url}/projects/{project_id}/version-sets:batch-delete"

        # Perform the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check the response
        if response.status_code == 204:
            print("Version sets deleted successfully.")
        else:
            response.raise_for_status()

    ###########################################################################
    # Uploads
    ###########################################################################
    def upload_file_to_autodesk(self, project_id, file_name):
        """
        Creates a storage location in the Object Storage Service (OSS) for you to upload the file to. This endpoint is typically used during the process of uploading files to the ACC Sheets tool.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-storage-POST/

        Args:
            project_id (str): The project id
            file_name (str): The name of the file to upload

        Returns:
            tuple: A tuple containing the bucket key and object key
        """
        token = self.base.get_private_token()
        url = f"{self.base_url}/projects/{project_id}/storage"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"fileName": file_name}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 201:
            response.raise_for_status()

        urn = response.json().get("urn")
        if urn:
            parts = urn.split(":")[-1].split("/")
            bucket_key = parts[0]
            object_key = "/".join(parts[1:])
            return bucket_key, object_key
        else:
            raise Exception("URN not found in response")

    def get_signed_s3_upload(self, bucket_key, object_key):
        """
        Get signed S3 upload URL

        Retrieves a signed URL for uploading an object to Autodesk OSS using S3.
        
        Args:
            bucket_key (str): The bucket key.
            object_key (str): The object key.
        
        Returns:
            dict: The JSON response from Autodesk API containing signed URL details.
        """
        token = self.base.get_private_token()
        url = f"https://developer.api.autodesk.com/oss/v2/buckets/{bucket_key}/objects/{object_key}/signeds3upload"
        headers = {"Authorization": token}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def upload_pdf_to_signed_url(self, signed_url, file_path):
        """
        Upload a PDF file to the signed URL

        Validates that the file is a PDF and exists, then uploads the file using a PUT request.
        
        Args:
            signed_url (str): The signed URL to which the file should be uploaded.
            file_path (str): The local path to the PDF file.
        
        Returns:
            int: The HTTP status code of the upload request.
        
        Raises:
            ValueError: If the file is not a PDF.
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are accepted")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as file:
            response = requests.put(signed_url, data=file)

            if response.status_code != 200:
                response.raise_for_status()
        return response.status_code

    def complete_s3_upload(self, bucket_key, object_key, upload_key):
        """
        Complete the S3 upload

        Finalizes the S3 upload process by sending the upload key.
        
        Args:
            bucket_key (str): The bucket key.
            object_key (str): The object key.
            upload_key (str): The upload key received during the upload process.
        
        Returns:
            dict: The JSON response from Autodesk API confirming completion.
        """
        token = self.base.get_private_token()
        url = f"https://developer.api.autodesk.com/oss/v2/buckets/{bucket_key}/objects/{object_key}/signeds3upload"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"uploadKey": upload_key}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def post_uploads(self, project_id, version_set_id, files: list[dict]):
        """
        Create uploads for a version set

        Validates and posts file upload information associated with a version set.
        Each file dictionary must include proper OSS storage details.
        
        Args:
            project_id (str): The project identifier.
            version_set_id (str): The version set identifier.
            files (list[dict]): List of file data dictionaries, each containing:
                                - storageType (should be "OSS")
                                - storageUrn (str)
                                - name (str, maximum 255 characters)
        
        Returns:
            dict: The JSON response from Autodesk API for the upload operation.
        
        Raises:
            ValueError: If file data fails validation.
        """
        token = self.base.get_private_token()
        # Validate files
        for file in files:
            if file.get("storageType") != "OSS":
                raise ValueError('storageType must be "OSS"')
            if not isinstance(file.get("storageUrn"), str):
                raise ValueError("storageUrn must be a string")
            if not isinstance(file.get("name"), str) or len(file["name"]) > 255:
                raise ValueError(
                    "name must be a string with a maximum length of 255 characters"
                )

        url = f"{self.base_url}/projects/{project_id}/uploads"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        payload = {"versionSetId": version_set_id, "files": files}

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 201:
            response.raise_for_status()

        return response.json()

    ###########################################################################
    # Sheets
    ###########################################################################
    def get_sheets(self, project_id:str, user_id = None, query_params=None, follow_pagination=False)->list:
        """
        Retrieves information about the sheets in a project.
        By default, this endpoint only returns sheets with the newest issuance
        date (this includes future issuance dates).

        To return all the sheets in a project, set the currentOnly filter to false.
        To return sheets from a specific version set, use the version set 
        ID filter (filter[versionSetId]).

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-sheets-GET/

        Args:
            project_id (str): The project ID.
            user_id (str, optional): The ID of the user on whose behalf the API request is made.
            query_params (dict, optional): Additional query parameters to filter the sheets.
            follow_pagination (bool, optional): Whether to follow pagination links to retrieve all sheets.

        Returns:
            list: An array of sheets.
        """
        
            
        token = self.base.get_private_token()

        # Set the headers
        headers = {"Authorization": token}
        if user_id:
            headers["x-user-id"] = user_id

        # API endpoint with the project_id
        url = f"{self.base_url}/projects/{project_id}/sheets"

        sheets = []
        while url:
            # Perform the GET request
            response = requests.get(url, headers=headers, query_params=query_params)

            # Check the response
            if response.status_code !=200:
                response.raise_for_status()
            data = response.json()
            sheets.extend(data["results"])
            url = data.get('pagination', {}).get('next') if follow_pagination else None

            # Clear query parameters for subsequent requests using the pagination URL
            query_params = None

        return sheets

    def batch_get_sheets(self, project_id: str, sheet_ids: list) -> list:
        """
        Retrieves a list of sheets by their IDs for a given project.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-sheetsbatch-get-POST/
        Args:
            project_id (str): The UUID of the project.
            sheet_ids (list): A list of sheet UUID strings (max 200 items).

        Returns:
            dict: The 'data' field from the API response.

        Raises:
            HTTPError: If the API request fails.
        """
        url = (
            f"https://developer.api.autodesk.com/construction/sheets/v1/"
            f"projects/{project_id}/sheets:batch-get"
        )
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/json"
        }
        payload = {"ids": sheet_ids}
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code.
        
        # Return only the 'data' field of the response.
        # (Assumes that the API response JSON is wrapped as {"data": ...})
        return response.json()["results"]

    def batch_update_sheets(self, project_id: str, ids: list, updates: dict, user_id = None) -> list:
        """
        Updates a list of sheets for the given project.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-sheetsbatch-update-POST/
        Parameters:
            project_id (str): The UUID of the project. This can be with or without the "b." prefix.
            ids (list): A list of sheet IDs (strings) that need to be updated. Maximum of 200 IDs.
            updates (dict): A dictionary containing the updates to apply.
                            Valid keys include:
                            - "number": str (new sheet number, single sheet update only)
                            - "title": str (new title for the sheet, single sheet update only)
                            - "versionSetId": str (ID of the new version set)
                            - "addTags": list (list of tags to attach to the sheets)
                            - "removeTags": list (list of tags to detach from the sheets)

        Returns:
            list: The "results" field from the API response, which is a list of updated sheet objects.
        
        Raises:
            requests.HTTPError: If the API response status indicates an error.
        """
        if len(ids) > 200:
            raise ValueError("The maximum number of sheet IDs that can be batched is 200.")
        
        token = self.base.get_private_token()
        url = f"{self.base_url}/projects/{project_id}/sheets:batch-update"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if user_id is not None:
            headers["x-user-id"] = user_id
        
        payload = {
            "ids": ids,
            "updates": updates
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  

        data = response.json()
        return data.get("results",[])

    def batch_delete_sheets(self, project_id: str, ids: list, user_id = None) -> list:
        """
        Deletes a list of sheets for the given project.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-sheetsbatch-delete-POST/
        Parameters:
            project_id (str): The UUID of the project. This can be with or without the "b." prefix.
            ids (list): A list of sheet IDs (strings) that need to be updated. Maximum of 200 IDs.

        Returns:
            list: The "results" field from the API response, which is a list of updated sheet objects.
        
        Raises:
            requests.HTTPError: If the API response status indicates an error.
        """
        if len(ids) > 200:
            raise ValueError("The maximum number of sheet IDs that can be batched is 200.")
        
        token = self.base.get_private_token()
        url = f"{self.base_url}/projects/{project_id}/sheets:batch-delete"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if user_id is not None:
            headers["x-user-id"] = user_id
        
        payload = {
            "ids": ids            
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  

    def batch_restore_sheets(self, project_id: str, ids: list, user_id = None) -> list:
        """
        Restores a list of sheets for the given project.
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/sheets-sheetsbatch-restore-POST/
        Parameters:
            project_id (str): The UUID of the project. This can be with or without the "b." prefix.
            ids (list): A list of sheet IDs (strings) that need to be updated. Maximum of 200 IDs.

        Returns:
            list: The "results" field from the API response, which is a list of updated sheet objects.
        
        Raises:
            requests.HTTPError: If the API response status indicates an error.
        """
        if len(ids) > 200:
            raise ValueError("The maximum number of sheet IDs that can be batched is 200.")
        
        token = self.base.get_private_token()
        url = f"{self.base_url}/projects/{project_id}/sheets:batch-restore"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if user_id is not None:
            headers["x-user-id"] = user_id
        
        payload = {
            "ids": ids            
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()          

    ###########################################################################
    # Exports
    ###########################################################################
    def export_sheets(self, project_id: str, options: dict, sheets: list, user_id: str = None) -> dict:
        """
        Creates an export job to generate a downloadable PDF file from published sheets.
        
        Args:
            project_id (str): The UUID of the project. Can be in the format with or without a "b." prefix.
            options (dict): Dictionary containing export options such as outputFileName, standardMarkups,
                            issueMarkups, and photoMarkups.
            sheets (list): A list of sheet UUIDs (max 1000) to include in the export.
            user_id (str, optional): Optional user ID to be sent in the x-user-id header field. 
                                    This can be either the user's ACC ID or Autodesk ID.
        
        Returns:
            dict: A dictionary containing the export job details including the export job ID and status.
            
        Raises:
            requests.HTTPError: If the response from the API indicates an error.
        """
        # Retrieve the OAuth token from the base class.
        token = self.base.get_private_token()

        # Set up the required headers.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Include the x-user-id header if a user_id is provided.
        if user_id:
            headers["x-user-id"] = user_id

        # Construct the endpoint URL using the provided project_id.        
        url = f"{self.base_url}/projects/{project_id}/exports"

        # Create the JSON payload for the POST request.
        payload = {
            "options": options,
            "sheets": sheets
        }

        # Perform the POST request to create the export job.
        response = requests.post(url, json=payload, headers=headers)

        # Check for a successful response (HTTP 202 Accepted).
        if response.status_code == 202:
            return response.json()
        else:
            # Raise an exception if the API call failed.
            response.raise_for_status()

    def get_export_status(self, project_id: str, export_id: str, user_id: str = None) -> dict:
        """
        Retrieves the status and details of a PDF sheet export job, including a signed URL
        for downloading the file when available.
        
        Args:
            project_id (str): The UUID of the project. Can be provided with or without a "b." prefix.
            export_id (str): The UUID of the export job to check the status for.
            user_id (str, optional): Optional user ID to be sent in the x-user-id header field.
                                    This may be the user's ACC ID or Autodesk ID.
        
        Returns:
            dict: A dictionary containing the export job status and, if successful, the signed URL
                within the result.output object, or error details if the export failed.
                
        Raises:
            requests.HTTPError: If the API response indicates an error.
        """
        # Retrieve the OAuth token from the base class.
        token = self.base.get_private_token()

        # Set up headers including optional x-user-id if provided.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        if user_id:
            headers["x-user-id"] = user_id

        # Construct the endpoint URL with project and export IDs.
        url = f"{self.base_url}/projects/{project_id}/exports/{export_id}"

        # Perform the GET request to retrieve export job details.
        response = requests.get(url, headers=headers)

        # Check for a successful response (HTTP 200 OK).
        if response.status_code == 200:
            return response.json()
        else:
            # Raise an exception if the API call failed.
            response.raise_for_status()

    ###########################################################################
    # Collections
    ###########################################################################
    def get_collections(self, project_id, user_id=None, follow_pagination=False, offset=0, limit=None):
        """
        Retrieves all collections for a given project from the Autodesk Sheets API.

        Parameters:
            project_id (str): The project UUID.
            user_id (str, optional): When provided, sent as the 'x-user-id' header.
            follow_pagination (bool, optional): If True, follows pagination links and aggregates all results.
                Defaults to False. When True, the 'offset' and 'limit' parameters are ignored.
            offset (int, optional): The starting index for the results (ignored if follow_pagination is True).
            limit (int, optional): The number of results to return (ignored if follow_pagination is True).

        Returns:
            list: A list of collection objects retrieved from the API.

        Raises:
            requests.exceptions.HTTPError: For non-successful HTTP responses.
        """
        # Retrieve the private token from the base class.
        token = self.base.get_private_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        if user_id is not None:
            headers["x-user-id"] = user_id
   
        url = f"{self.base_url}/projects/{project_id}/collections"
        
        # Set up query parameters only if pagination is not followed.
        params = {}
        if not follow_pagination:
            params["offset"] = offset
            if limit is not None:
                params["limit"] = limit

        # Initial API request.
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Start with the initial results.
        results = data.get("results", [])

        # If follow_pagination is enabled, loop through next links to aggregate all results.
        if follow_pagination:
            pagination = data.get("pagination", {})
            next_url = pagination.get("nextUrl")
            while next_url:
                page_response = requests.get(next_url, headers=headers)
                page_response.raise_for_status()
                page_data = page_response.json()
                results.extend(page_data.get("results", []))
                pagination = page_data.get("pagination", {})
                next_url = pagination.get("nextUrl")

        return results

    def get_collection(self, project_id, collection_id, user_id=None):
        """
        Retrieves a specific collection by its unique ID for the given project from the Autodesk Sheets API.

        Parameters:
            project_id (str): The project UUID.
            collection_id (str): The unique identifier of the collection.
            user_id (str, optional): When provided, sent as the 'x-user-id' header.

        Returns:
            dict: The collection object retrieved from the API.

        Raises:
            requests.exceptions.HTTPError: For non-successful HTTP responses.
        """
        # Retrieve the private token from the base class.
        token = self.base.get_private_token()

        # Setup headers with Authorization and optional x-user-id.
        headers = {
            "Authorization": f"Bearer {token}"
        }
        if user_id is not None:
            headers["x-user-id"] = user_id
        
        url = f"{self.base_url}/projects/{project_id}/collections/{collection_id}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()
