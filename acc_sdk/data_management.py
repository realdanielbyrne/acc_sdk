import requests
import json
from .base import AccBase


class AccDataManagementApi:
    def __init__(self, base: AccBase):
        self.base = base

    ###########################################################################
    # Hubs
    ###########################################################################
    def get_hubs(self, user_id: str = None, filter_id:list[str]=None,filter_name:list[str] = None, filter_extension_type:list[str] = None)->list[dict]:
        """
        Get a list of hubs accessible to the authenticated user.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-GET/
        
        Args:
            user_id (str, optional): The id of the user context to execute the API call in.
            filter_id (list[str], optional): A list of hub IDs to filter the results by.
            filter_name (list[str], optional): A list of hub names to filter the results by.
            filter_extension_type (list[str], optional): A list of hub extension types to filter the results by.            

        Returns:
            list[dict]: A list of hubs accessible to the authenticated user or to 
            the user_id.
        """
        url = "https://developer.api.autodesk.com/project/v1/hubs"
        headers = {"Authorization:": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_id:
            params["filter[id]"] = filter_id
        if filter_name:
            params["filter[name]"] = filter_name
        if filter_extension_type:
            params["filter[extension.type]"] = filter_extension_type
            
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            hubs_data = response.json().get("data", [])
            return hubs_data
        response.raise_for_status()

    def get_hub(self, hub_id: str, user_id: str = None)->dict:
        """
        Get the details of a specific hub.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-GET/

        Args:
            hub_id (str): The unique identifier of the hub. Account Id is the same as the hub_id without the 'b.' prefix.
            user_id (str, optional): The id of the user context to execute the API call in.

        Returns:
            dict: The details of the hub.
        """ 
        
        url = f"https://developer.api.autodesk.com/project/v1/hubs/:{hub_id}"
        headers = {"Authorization:": f"Bearer {self.base.get_private_token()}"}

        if user_id:
            headers["x-user-id"] = user_id

        if not hub_id.startswith("b."):
            hub_id = "b." + hub_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            hub_data = response.json().get("data", {})
            return hub_data            
        response.raise_for_status()

    ###########################################################################
    # Projects
    ###########################################################################
    def get_projects(self, hub_id: str, user_id: str = None, follow_pagination = False, query_params:dict = None)->list[dict]:
        """
        Get a list of projects in a hub.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-GET/
        
        Args:
            hub_id (str): The unique identifier of the hub or the acc account id.
            user_id (str, optional): The id of the user context to execute the API call in.

        Returns:
            list[dict]: A list of projects in the hub.            
        """
        
        if not hub_id.startswith("b."):
            hub_id = "b." + hub_id
            
        base_url = f"https://developer.api.autodesk.com/project/v1/hubs/:{hub_id}/projects"
                
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        if query_params is None:
            query_params = {}

        all_results = []
        while base_url:
            response = requests.get(base_url, headers=headers, params=query_params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            if response.status_code != 200:
                response.raise_for_status()

            all_results.extend(data.get("data", {}))

            # Check for the next link in the pagination
            base_url = None
            if "links" in data and "next" in data["links"] and follow_pagination:
                base_url = (
                    "https://developer.api.autodesk.com" + data["links"]["next"]["href"]
                )
                # Clear query params after the first request to follow the next link properly
                query_params = {}

            if "links" in data and "next" in data["links"] and not follow_pagination:
                all_results.append(data["links"]["next"])

        return all_results

    def get_project(self, hub_id: str, project_id: str, user_id=None)->dict:
        """
        Returns a specific project in a hub.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-project_id-GET/
        Args:
            hub_id (str): The unique identifier of the hub.
            project_id (str): The unique identifier of the project.
            user_id (str, optional): The id of the user context to execute the API call in.

        Returns:
            dict: The proiect object.
        """

        if not hub_id.startswith("b."):
            hub_id = "b." + hub_id
        if not project_id.startswith("b."):
            project_id = "b." + project_id
        url = f"https://developer.api.autodesk.com/project/v1/hubs/:{hub_id}/projects/:{project_id}"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            project_data = response.json()['data']
            return project_data
                    
        response.raise_for_status()

    def get_hub_from_project(self, hub_id: str, project_id: str, user_id=None)->dict:
        """
        Get the hub information from a specific project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-project_id-hub-GET/
        Args:
            hub_id (str): The unique identifier of the hub.
            project_id (str): The unique identifier of the project.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the hub details.
        """
        
        if not hub_id.startswith("b."):
            hub_id = "b." + hub_id
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/project/v1/hubs/:{hub_id}/projects/:{project_id}/hub"        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            hub_data = response.json().get("data", {})
            return hub_data
            
        response.raise_for_status()

    def get_project_top_folders(self, hub_id: str, project_id: str, user_id=None, excludeDeleted:bool = False, projectFilesOnly:bool=False )->list[dict]:
        """
        Returns the details of the highest level folders the user has access to for a given project. 
        The user must have at least read access to the folders.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/hubs-hub_id-projects-project_id-topFolders-GET/

        Args:
            hub_id (str): The unique identifier of the hub.
            project_id (str): The unique identifier of the project.
            user_id (str, optional): The id of the user context to execute the API call in. 

        Returns:
            list[dict]: A list of top folders in the project.
        """
        if hub_id == None or project_id == None:
            raise Exception("Hub ID and Project ID are required")

        if not hub_id.startswith("b."):
            hub_id = "b." + hub_id
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/project/v1/hubs/:{hub_id}/projects/:{project_id}/topFolders"

        params = {}
        if excludeDeleted:
            params["excludeDeleted"] = excludeDeleted
        if projectFilesOnly:
            params["projectFilesOnly"] = projectFilesOnly            
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            folder_data = response.json().get("data", [])
            return folder_data
            
        response.raise_for_status()

    def get_project_download(self, project_id, download_id, user_id=None)->dict:
        """
        Returns the details for a specific download.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-downloads-download_id-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            download_id (str): The download id.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the download details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/downloads/:{download_id}"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {})
        response.raise_for_status()

    def get_project_job(self, project_id: str, job_id: str, user_id=None)->dict:
        """
        Returns the job_id object.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-jobs-job_id-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            job_id (str): The unique identifier of the job.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the job_id object.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/jobs/:{job_id}"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {})
        response.raise_for_status()

    def create_project_download(self, project_id: str, version_id: str, file_type, user_id=None)->dict:
        """
        Request the creation of a new download for a specific and supported file type. The fileType specified
        in the POST body needs to be contained in the list of supported file types returned by the 
        GET projects/:project_id/versions/:version_id/downloadFormats endpoint for the specified version_id.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            file_type: The file type for the download.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the download creation details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/downloads"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}", 
                   "Content-Type": "application/vnd.api+json"}
        if user_id:
            headers["x-user-id"] = user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "downloads",
                "attributes": {"format": {"fileType": file_type}},
                "relationships": {
                    "source": {"data": {"type": "versions", "id": version_id}}
                },
            },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def create_project_storage_loc(self, project_id: str, data_type, data_id, data_name, user_id=None)->dict:
        """
        Creates a storage location in the OSS where data can be uploaded to.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-storage-POST/
        
        Args:
            project_id (str): The unique identifier of the project.
            data_type: The type of the target data. Must be 'folders' or 'items'.
            data_id: The identifier for the target data.
            data_name (str): Displayable name of the resource.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the storage location details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = (
            f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/storage"
        )
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}",
                   "Content-Type": "application/vnd.api+json"}
        if user_id:
            headers["x-user-id"] = user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "objects",
                "attributes": {"name": data_name},
                "relationships": {
                    "target": {"data": {"type": data_type, "id": data_id}}
                },
            },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    ###########################################################################
    # Folders
    ###########################################################################
    def get_folder_details(self, project_id, folder_id, if_modified_since:str= None, user_id=None)->dict:
        """
        Returns the folder by ID for any folder within a given project. All folders or sub-folders within a
        project are associated with their own unique ID, including the root folder.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-GET/

        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.        
            if_modified_since (str, optional): The date and time to check if the resource has been modified since.
            user_id (str, optional): The id of the user context to execute the API call in.

        Returns:
            dict: A dictionary containing the folder details.
        """
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/folders/{folder_id}"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id
        if if_modified_since:
            headers["If-Modified-Since"] = if_modified_since

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", {})
        elif response.status_code == 304:
            print("Resource has not been modified since the last request.")
            return None
        else:
            print(
                f"Failed to retrieve folder details. Status code: {response.status_code}"
            )
            return None

    def get_folder_contents(
        self,
        project_id: str,
        folder_id,
        filter_type=None,
        filter_id=None,
        filter_extension_type=None,
        filter_last_modified_time_rollup=None,
        page_number=None,
        page_limit=None,
        include_hidden=False,
        user_id=None
    )->list[dict]:
        """
        Retrieve the contents of a folder in a project.
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id: The unique identifier of the folder.
            filter_type (optional): Filter by type.
            filter_id (optional): Filter by id.
            filter_extension_type (optional): Filter by extension type.
            filter_last_modified_time_rollup (optional): Filter by last modified time rollup.
            page_number (int, optional): The page number for pagination.
            page_limit (int, optional): The number of items per page.
            include_hidden (bool, optional): Flag to include hidden items.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            list[dict]: A list of folder contents.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/contents"

        
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/json",
        }
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_type:
            params["filter[type]"] = filter_type
        if filter_id:
            params["filter[id]"] = filter_id
        if filter_extension_type:
            params["filter[extension.type]"] = filter_extension_type
        if filter_last_modified_time_rollup:
            params["filter[lastModifiedTimeRollup]"] = filter_last_modified_time_rollup
        if page_number is not None:
            params["page[number]"] = page_number
        if page_limit is not None:
            params["page[limit]"] = page_limit
        if include_hidden:
            params["includeHidden"] = "true"
        else:
            params["includeHidden"] = "false"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_folder_parent(self, project_id: str, folder_id: str, user_id=None)->dict:
        """
        Retrieve the parent folder of a specific folder in a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-parent-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the parent folder details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/parent"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}", 
                   "Content-Type": "application/vnd.api+json"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def get_folder_resource_refs(
        self,
        project_id: str,
        folder_id: str,
        user_id=None,
        filter_ref_type=None,
        filter_ref_id=None,
        filter_ext_type=None,
        filter_last_modified_time_rollup=None,
        page_number=None,
        page_limit=None,
    )->list[dict]:
        """
        Retrieve resource references for a folder in a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-refs-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            user_id (str, optional): The id of the user context to execute the API call in.
            filter_ref_type (optional): Filter by reference type.
            filter_ref_id (optional): Filter by reference id.
            filter_ext_type (optional): Filter by extension type.
            filter_last_modified_time_rollup (optional): Filter by last modified time rollup.
            page_number (int, optional): The page number for pagination.
            page_limit (int, optional): The number of items per page.
        
        Returns:
            list[dict]: A list of resource references for the folder.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/refs"
        token = f"Bearer {self.base.get_private_token()}"
        headers = {"Authorization": token, "Content-Type": "application/vnd.api+json"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_ref_type:
            params["filter[type]"] = filter_ref_type
        if filter_ref_id:
            params["filter[id]"] = filter_ref_id
        if filter_ext_type:
            params["filter[extension.type]"] = filter_ext_type
        if filter_last_modified_time_rollup:
            params["filter[lastModifiedTimeRollup]"] = filter_last_modified_time_rollup
        if page_number:
            params["page[number]"] = page_number
        if page_limit:
            params["page[limit]"] = page_limit

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_folder_links(self, project_id: str, folder_id: str, user_id=None)->list[dict]:
        """
        Retrieve a collection of links for a specific folder.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-relationships-links-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing folder link information.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/relationships/links"

        headers = {"Authorization": self.base.get_private_token()}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_folder_relationship_refs(
        self,
        project_id: str,
        folder_id: str,
        user_id=None,
        filter_ref_type=None,
        filter_ref_id=None,
        filter_ext_type=None,
        filter_type=None,
        filter_direction=None,
    )->list[dict]:
        """
        Retrieve custom relationship references for a folder.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-relationships-refs-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            user_id (str, optional): The id of the user context to execute the API call in.
            filter_ref_type (optional): Filter by reference type.
            filter_ref_id (optional): Filter by reference id.
            filter_ext_type (optional): Filter by extension type.
            filter_type (optional): Filter by type.
            filter_direction (optional): Filter by direction of relationship.
        
        Returns:
            list[dict]: A dictionary containing relationship references.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/relationships/refs"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_ref_type:
            params["filter[refType]"] = filter_ref_type
        if filter_ref_id:
            params["filter[refId]"] = filter_ref_id
        if filter_ext_type:
            params["filter[extension.type]"] = filter_ext_type
        if filter_type:
            params["filter[type]"] = filter_type
        if filter_direction:
            params["filter[direction]"] = filter_direction

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def get_folder_serarch(
        self,
        project_id: str,
        folder_id: str,
        user_id=None,
        page_number=None,
        filter=None,
    ):
        """
        Search for content within a folder.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-search-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            user_id (str, optional): The id of the user context.
            page_number (int, optional): The page number for pagination.
            filter (optional): Filter criteria for the search.
        
        Returns:
            list[dict]: A dictionary containing the search results.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/search"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter:
            params["filter"] = filter
        if page_number:
            params["page[number]"] = page_number

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def create_folder(self, project_id:str, folder_name:str, parent_folder_id:str, copyFrom:str = None)->dict:
        """
        Creates a new folder. To delete and restore folders, use the PATCH projects/:project_id/folders/:folder_id endpoint.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-POST/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_name (str): The name of the new folder.
            parent_folder_id (str): The unique identifier of the parent folder.
        
        Returns:
            dict: A dictionary containing the details of the created folder.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = (
            f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders"
        )
        
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "folders",
                "attributes": {
                    "name": folder_name,
                    "extension": {
                        "type": "folders:autodesk.core:Folder",
                        "version": "1.0",
                    },
                },
                "relationships": {
                    "parent": {"data": {"type": "folders", "id": parent_folder_id}}
                },
            },
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def add_folder_reference(self, project_id: str, folder_id:str, version_id:str, extension_type:str, extension_version:str)->None:
        """
        Add a reference to a version within a folder.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-relationships-refs-POST/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            version_id (str): The unique identifier of the version.
            extension_type (str): The extension type for the reference.
            extension_version (str): The version of the extension.
        
        Returns:
            None
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}/relationships/refs"
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "versions",
                "id": version_id,
                "meta": {
                    "extension": {"type": extension_type, "version": extension_version}
                },
            },
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            print("Reference added successfully.")
        else:
            response.raise_for_status()

    def rename_folder(self, project_id: str, folder_id: str, new_name: str, user_id:str=None)-> dict:
        """
        Rename a folder within a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-PATCH/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder.
            new_name (str): The new name for the folder.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the folder details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }
        if user_id:
            headers["x-user-id"] = user_id
        
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "folders",
                "id": folder_id,
                "attributes": {"name": new_name},
            },
        }

        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def delete_folder(self, project_id: str, folder_id: str, user_id:str=None)-> dict:
        """
        Delete (hide) a folder within a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-PATCH/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder to delete.
            
        
        Returns:
            dict: A dictionary containing the folder details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}"

        headers = {
            "Authorization": self.base.get_private_token(),
            "Content-Type": "application/vnd.api+json",
        }
        if user_id:
            headers["x-user-id"] = user_id
        
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "folders",
                "id": folder_id,
                "attributes": {"hidden": True},
            },
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def restore_folder(self, project_id: str, folder_id: str, user_id:str=None)->dict:
        """
        Restore a previously deleted (hidden) folder within a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-folders-folder_id-PATCH/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_id (str): The unique identifier of the folder to restore.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing the folder details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/folders/:{folder_id}"
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",            
        }
        if user_id:
            headers["x-user-id"] = user_id
        
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "folders",
                "id": folder_id,
                "attributes": {"hidden": False},
            },
        }
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    ###########################################################################
    # Items
    ###########################################################################
    def get_item(
        self,
        project_id: str,
        item_id: str,
        include_path_in_project: bool = False,
        user_id=None,
    )->dict:
        """
        Retrieve metadata for a specific item in a project.
        
        Items represent documents, design files, drawings, spreadsheets, etc.
        The most recent version (tip) of the item is assumed to be the first element in the included array.
        
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            include_path_in_project (bool, optional): Flag to include the path of the item in the project.
            user_id (str, optional): The id of the user context to execute the API call in.
        
        Returns:
            dict: A dictionary containing item metadata and the most recent version.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}"
        
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id
            
        response = requests.get(
            url,
            headers=headers,
            params={"includePathInProject": include_path_in_project},
        )

        if response.status_code == 200:
            data = response.json()
            metadata = data.get("data")
            included = data.get("included", [])

            # Assuming the most recent version is the first in the 'included' array
            most_recent_version = included[0] if included else None

            return {"metadata": metadata, "most_recent_version": most_recent_version}
        else:
            response.raise_for_status()

    def get_items_parent_folder(self, project_id: str, item_id: str, user_id=None)->dict:
        """
        Retrieve the parent folder for a specific item within a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-parent-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            user_id (str, optional): The id of the user executing the API call.
        
        Returns:
            dict: A dictionary containing the parent folder details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/:{project_id}/items/:{item_id}/parentFolder"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def get_resource_relationships(self, project_id: str, item_id: str, user_id=None, filters=None)->list[dict]:
        """
        Fetches resources that have a custom relationship with the given item_id in a project.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-refs-GET/

        Args:
            project_id (str): unique identifier of the project
            item_id (str): unique identifier of the item            
            user_id (str, optional): the id of the user context to execute the API call in
            filters (dict, optional): filters for the request

        Returns:
            dict, response JSON from the API
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/refs"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    params[f"filter[{key}]"] = ",".join(value)
                else:
                    params[f"filter[{key}]"] = value

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_item_links(self, project_id: str, item_id: str, user_id=None)->list[dict]:
        """
        Returns a collection of links for the given item_id. Custom relationships can be established between an item and 
        other external resources residing outside the data domain service. A link’s href defines the target URI to access a resource.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-relationships-links-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            user_id (str, optional): The user context identifier.
        
        Returns:
            list[dict]: A list of dictionaries containing relationship link details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/relationships/links"
        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_item_relationships(self, project_id: str, item_id: str, user_id=None, filter_ref_type=None)->list[dict]:
        """
        Retrieve custom relationship references for a specific item.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-relationships-refs-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            user_id (str, optional): The user context identifier.
            filter_ref_type (optional): Filter by reference type.
        
        Returns:
            list[dict]: A list of dictionaries containing custom relationship data.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/relationships/refs"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_ref_type:
            params["filter[meta.refType]"] = filter_ref_type

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_tip_version(self, project_id: str, item_id: str, user_id=None)->dict:
        """
        Retrieve the tip (most recent) version of a specific item.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-tip-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            user_id (str, optional): The user context identifier.
        
        Returns:
            dict: A dictionary containing the tip version details.
        """
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/tip"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    def get_item_versions(self, project_id: str, item_id: str, user_id=None, filters=None)->list[dict]:
        """
        Retrieve all versions of a specified item within a project by iterating through all pages.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-versions-GET/
        
        Args:
            project_id (str}: ID of the project
            item_id {str): ID of the item        
            user_id (str, optional): ID of the user context to execute the API call in
            filters (list[dict], optional): Dictionary of filters to apply

        Returns:
            lsit[dict]: List of all versions
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/versions"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id
        params = {}

        if filters:
            for key, value in filters.items():
                params[f"filter[{key}]"] = value

        all_versions = []
        while url:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                response.raise_for_status()
            data = response.json()
            all_versions.extend(data["data"])

            # Check if there is a next page
            url = data["links"].get("next", {}).get("href")

            # Clear params to avoid reapplying filters to subsequent pages
            params = {}

        return all_versions

    def create_item(
        self,
        project_id: str,
        folder_urn,
        file_name,
        storage_urn,
        x_user_id=None,
        copy_from=None,
    )->dict:
        """
        Create a new item (file) in a project, including its first version.
        
        Prior to invoking this method, a storage location should be created and file uploaded.
        For additional versions, use the 'create_version' method.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-POST/
        
        Args:
            project_id (str): The unique identifier of the project.
            folder_urn: The unique identifier of the parent folder.
            file_name (str): The name of the file.
            storage_urn: The unique identifier of the storage location.
            x_user_id (str, optional): The user context identifier.
            copy_from (optional): Reference for copying an existing item.
        
        Returns:
            dict: A dictionary containing the created item details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }

        if x_user_id:
            headers["x-user-id"] = x_user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "items",
                "attributes": {
                    "displayName": file_name,
                    "extension": {"type": "items:autodesk.core:File", "version": "1.0"},
                },
                "relationships": {
                    "tip": {"data": {"type": "versions", "id": "1"}},
                    "parent": {"data": {"type": "folders", "id": folder_urn}},
                },
            },
            "included": [
                {
                    "type": "versions",
                    "id": "1",
                    "attributes": {
                        "name": file_name,
                        "extension": {
                            "type": "versions:autodesk.core:File",
                            "version": "1.0",
                        },
                    },
                    "relationships": {
                        "storage": {"data": {"type": "objects", "id": storage_urn}}
                    },
                }
            ],
        }

        params = {}
        if copy_from:
            params["copyFrom"] = copy_from

        response = requests.post(
            url, headers=headers, params=params, data=json.dumps(data)
        )

        if response.status_code == 201:
            json_data = response.json()
            ret = {'data': json_data.get('data', {}), 'included': json_data.get('included', []), 'meta': json_data.get('meta', {})}
            return ret
            
        else:
            response.raise_for_status()

    def create_item_relationship(
        self, project_id, item_id, resource_type, resource_id, user_id=None
    ):
        """
        Create a custom relationship between an item and another resource.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-relationships-refs-POST/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            resource_type (str): The type of the resource to relate.
            resource_id (str): The unique identifier of the related resource.
            user_id (str, optional): The user context identifier.
        
        Returns:
            None
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}/relationships/refs"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }

        if user_id:
            headers["x-user-id"] = user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": resource_type,
                "id": resource_id,
                "meta": {
                    "extension": {
                        "type": "auxiliary:autodesk.core:Attachment",
                        "version": "1.0",
                    }
                },
            },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 204:
            print("Successful creation of a reference between two resources.")
        else:
            response.raise_for_status()

    def update_item_properties(self, project_id, item_id, user_id=None, attributes={})->dict:
        """
        UUpdates the properties of the given item_id object. Note that updating the displayName of an
        item is not supported for BIM 360 Docs or ACC items. Instead, use the 
        POST projects/:project_id/versions endpoint.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-items-item_id-PATCH/
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            user_id (str, optional): The user context identifier.
            attributes (dict): A dictionary of attributes to update.
        
        Returns:
            dict: A dictionary containing the updated item properties.
        """

        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/items/{item_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }
        if user_id:
            headers["x-user-id"] = user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {"type": "items", "id": item_id, "attributes": attributes},
        }

        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("data", {})

    ###########################################################################
    # Versions
    ###########################################################################
    def get_version(self, project_id, version_id, user_id=None)->dict:
        """
        Retrieve details of a specific version of an item.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-versions-version_id-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            user_id (str, optional): The user context identifier.
        
        Returns:
            dict: A dictionary containing version details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
        }
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_json = response.json().get("data", {})
        else:
            response.raise_for_status()

        return response_json.get("data", {})

    def get_version_download_formats(self, project_id, version_id, user_id=None)->list[str]:
        """
        Retrieve a list of file formats available for download for a specific version.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/projects-project_id-versions-version_id-downloadFormats-GET/
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            user_id (str, optional): The user context identifier.
        
        Returns:
            list: A list of file format strings.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/downloadFormats"
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
        }
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            formats = data.get("data", {}).get("attributes", {}).get("formats", [])
            return [format_info["fileType"] for format_info in formats]
        else:
            response.raise_for_status()

    def get_version_downloads(self, project_id, version_id, user_id=None)->list[dict]:
        """
        Retrieve the list of downloads available for a specific version.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            user_id (str, optional): The user context identifier.
        
        Returns:
            list: A list containing download details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/downloads"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
        }
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_item_version(self, project_id: str, version_id, user_id=None):
        """
        Retrieve the item associated with a specific version.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            user_id (str, optional): The user context identifier.
        
        Returns:
            dict: A dictionary containing the item details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/item"

        headers = {"Authorization": self.base.get_private_token()}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_version_resources(
        self,
        project_id: str,
        version_id,
        filter_type=None,
        filter_id=None,
        filter_extension_type=None,
        user_id=None,
    ):
        """
        Retrieve custom-related resources for a specific version.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            filter_type (list, optional): List of types to filter resources.
            filter_id (list, optional): List of IDs to filter resources.
            filter_extension_type (list, optional): List of extension types to filter resources.
            user_id (str, optional): The user context identifier.
        
        Returns:
            list: A list containing custom-related resource details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/refs"
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/json",
        }
        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_type:
            params["filter[type]"] = ",".join(filter_type)
        if filter_id:
            params["filter[id]"] = ",".join(filter_id)
        if filter_extension_type:
            params["filter[extension.type]"] = ",".join(filter_extension_type)

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_version_links(self, project_id: str, version_id, user_id=None):
        """
        Retrieve the relationship links for a specific version.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            user_id (str, optional): The user context identifier.
        
        Returns:
            list: A list of link data related to the version.
        """
        # A link’s href defines the target URI to access a resource.
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/relationships/links"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}
        if user_id:
            headers["x-user-id"] = user_id

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def get_version_relationships(
        self,
        project_id: str,
        version_id,
        user_id=None,
        filter_type=None,
        filter_id=None,
        filter_refType=None,
        filter_direction=None,
        filter_extension_type=None,
    ):
        """
        Retrieve custom relationship details for a specific version.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id: The unique identifier of the version.
            user_id (str, optional): The user context identifier.
            filter_type (optional): Filter by type.
            filter_id (optional): Filter by identifier.
            filter_refType (optional): Filter by reference type.
            filter_direction (optional): Filter by relationship direction.
            filter_extension_type (optional): Filter by extension type.
        
        Returns:
            list: A list of custom relationship details for the version.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/relationships/refs"

        headers = {"Authorization": f"Bearer {self.base.get_private_token()}"}

        if user_id:
            headers["x-user-id"] = user_id

        params = {}
        if filter_type:
            params["filter[type]"] = filter_type
        if filter_id:
            params["filter[id]"] = filter_id
        if filter_refType:
            params["filter[refType]"] = filter_refType
        if filter_direction:
            params["filter[direction]"] = filter_direction
        if filter_extension_type:
            params["filter[extension.type]"] = filter_extension_type

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            response.raise_for_status()

    def create_version(
        self,
        project_id,
        item_id,
        storage_id,
        file_name,
        version_number="1.0",
        x_user_id=None,
        copy_from=None,
        workflow=None,
        workflow_attribute=None,
    ):
        """
        Create a new version for an item in a project.
        
        Args:
            project_id (str): The unique identifier of the project.
            item_id (str): The unique identifier of the item.
            storage_id (str): The identifier of the storage location.
            file_name (str): The name of the version/file.
            version_number (str, optional): The version number (default "1.0").
            x_user_id (str, optional): The user context identifier.
            copy_from (optional): Identifier for copying from an existing version.
            workflow (optional): Workflow identifier, if applicable.
            workflow_attribute (optional): Additional workflow attributes, if any.
        
        Returns:
            dict: A dictionary containing details of the created version.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = (
            f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions"
        )

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }

        if x_user_id:
            headers["x-user-id"] = x_user_id

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "versions",
                "attributes": {
                    "name": file_name,
                    "extension": {
                        "type": "versions:autodesk.core:File",
                        "version": version_number,
                    },
                },
                "relationships": {
                    "item": {"data": {"type": "items", "id": item_id}},
                    "storage": {"data": {"type": "objects", "id": storage_id}},
                },
            },
        }

        if workflow:
            data["meta"] = {"workflow": workflow}
            if workflow_attribute:
                data["meta"]["workflowAttribute"] = workflow_attribute

        if copy_from:
            url += f"?copyFrom={copy_from}"

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            ret = {'data': response.json().get('data', {}), 'included': response.json().get('included', []), 'meta': response.json().get('meta', {})}
            return ret
            
        else:
            response.raise_for_status()

    def create_custom_version_relationship(
        self,
        project_id,
        version_id,
        related_resource_id,
        extension_type,
        extension_version,
    ):
        """
        Create a custom relationship between a version and a related resource.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            related_resource_id (str): The unique identifier of the related resource.
            extension_type (str): The extension type of the relationship.
            extension_version (str): The extension version.
        
        Returns:
            None
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}/relationships/refs"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }

        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "versions",
                "id": related_resource_id,
                "meta": {
                    "extension": {"type": extension_type, "version": extension_version}
                },
            },
        }

        response = requests.post(url, headers=headers, json=data)
        if response == 204:
            print("Relationship created successfully")
            return
        else:
            response.raise_for_status()

    def rename_version(self, project_id, version_id, new_name)->dict:
        """
        Rename a specific version of an item.
        
        Args:
            project_id (str): The unique identifier of the project.
            version_id (str): The unique identifier of the version.
            new_name (str): The new name for the version.
        
        Returns:
            dict: A dictionary containing the updated version details.
        """
        if not project_id.startswith("b."):
            project_id = "b." + project_id

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/versions/{version_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json",
        }
        
        data = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "versions",
                "id": version_id,
                "attributes": {"name": new_name},
            },
        }

        response = requests.patch(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("data", {})
        else:
            response.raise_for_status()

    ###########################################################################
    # Commands
    ###########################################################################

    def check_permission(self, project_id, required_actions, resources, user_id=None):
        """
        Check if a user has permission to perform specified actions on specified resources.

        Parameters:
            project_id (str): The unique identifier of the project. For BIM 360 Docs, add a "b." prefix if needed.
            required_actions (list): List of actions to check for. Valid actions include:
                "read", "view", "download", "collaborate", "write", "create", "upload",
                "updateMetaData", "delete", "admin", "share".
            resources (list): List of resource dictionaries. Each dictionary should have:
                - "type": one of "folders", "items", or "versions"
                - "id": the URN of the resource, e.g. "urn:adsk.wipprod:dm.folder:..."
            user_id (str, optional): For two-legged calls, you can optionally specify the x-user-id header.

        Returns:
            dict: The JSON response from the API call.

        """
        token = self.base.get_private_token()
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }
        if user_id:
            headers["x-user-id"] = user_id

        payload = {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.core:CheckPermission",
                        "version": "1.0.0",
                        "data": {
                            "requiredActions": required_actions
                        }
                    }
                },
                "relationships": {
                    "resources": {
                        "data": resources
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception if the request failed
        return response.json()        
        
    def list_refs(self, project_id, versions, x_user_id=None):
        """
        Retrieve custom relationships between specified versions and other resources using the Autodesk ListRefs API.
        https://aps.autodesk.com/en/docs/data/v2/reference/http/ListRefs/
        Parameters:
            project_id (str): The unique project identifier. For BIM 360 Docs, the project ID should be prefixed with "b.".
            token (str): The OAuth bearer token. Must be a valid token string.
            versions (list of str): List of version URNs for which to retrieve relationships. Maximum 50 versions allowed.
            x_user_id (str, optional): User ID to limit the API call to act on behalf of a specific user.
        
        Returns:
            dict: The JSON data response from the API containing the relationships.
        
        """
        if len(versions) > 50:
            raise ValueError("You can retrieve relationships for up to 50 versions only.")

        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        
        headers = {
            "Authorization": f"Bearer {self.base.get_private_token()}",
            "Content-Type": "application/vnd.api+json"
        }
        
        if x_user_id:
            headers["x-user-id"] = x_user_id

        payload = {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.core:ListRefs",
                        "version": "1.0.0"
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [{"type": "versions", "id": ver} for ver in versions]
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
        
        return response.json().get("data", {})

    def list_items(self, project_id: str, item_ids: list, include_path_in_project: bool = True) -> dict:
        """
        Retrieves metadata for up to 50 specified items from the Autodesk Data Management API.
        
        Args:
            project_id (str): The unique identifier of the project.
                For BIM 360 Docs, prefix the project ID with 'b.' if required.
            item_ids (list): List of item URNs (as strings) for which to retrieve metadata.
            include_path_in_project (bool): Option to include path in project metadata. Defaults to True.
        
        Returns:
            dict: Parsed JSON response from the API containing item metadata.
        
        Raises:
            requests.HTTPError: If the response status code indicates an error.
        """
        # Retrieve the bearer token from the base class
        token = self.base.get_private_token()
        
        # Construct the endpoint URL by injecting the project_id
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }
        
        # Construct the payload based on the API documentation
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.core:ListItems",
                        "version": "1.1.0",
                        "data": {"includePathInProject": include_path_in_project}
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [{"type": "items", "id": item_id} for item_id in item_ids]
                    }
                }
            }
        }
        
        # Make the POST request to the endpoint
        response = requests.post(url, headers=headers, json=payload)
        
        # Raise an exception for non-200 responses
        response.raise_for_status()
        
        # Return the JSON response
        return response.json().get("data", {})

    def publish_model(self, project_id, resource_urns)->dict:
        """
        Publishes the latest version of a C4R model to BIM 360 Docs.

        Args:
            project_id (str): The unique identifier of the project (include the "b." prefix).
            resource_urns (list of str): A list of resource URNs to be published.

        Returns:
            dict: The 'data' field from the API response.
        """
        import requests

        token = self.base.get_private_token()
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }

        payload = {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.bim360:C4RModelPublish",
                        "version": "1.0.0"
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [{"type": "items", "id": urn} for urn in resource_urns]
                    }
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError if the response was an error.
        return response.json().get('data',{})

    def publish_without_links(self, project_id: str, resource_urn: str) -> dict:
        """
        Publishes the latest version of a C4R model without the links to BIM 360 Docs.

        Args:
            project_id (str): The unique identifier for the project. For BIM 360 Docs,
                            this should be prefixed with 'b.' if required.
            resource_urn (str): The URN of the resource (item) to be published.

        Returns:
            dict: The 'data' field from the API response.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        # Retrieve the token from the base class.
        token = self.base.get_private_token()
        
        # Construct the endpoint URL.
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        
        # Set up the required headers.
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }
        
        # Create the payload as per the API documentation.
        payload = {
            "jsonapi": {
                "version": "1.0"
            },
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.bim360:C4RPublishWithoutLinks",
                        "version": "1.0.0"
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [
                            {
                                "type": "items",
                                "id": resource_urn
                            }
                        ]
                    }
                }
            }
        }
        
        # Make the POST request.
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors.
        
        # Return only the 'data' field from the response.
        return response.json().get("data")

    def get_publish_model_job(self, project_id, item_id):
        """
        Verifies whether a C4R model needs to be published to BIM 360 Docs.
        
        Parameters:
            project_id (str): The project identifier. For BIM 360 Docs, include the "b." prefix.
            item_id (str): The resource id (e.g., "urn:adsk.wip:dm.file:...").
        
        Returns:
            dict or None: The 'data' field from the API response. This can be a dict with job details or None if the data is null.
        
        Raises:
            HTTPError: If the API request returns an unsuccessful status code.
        """
        # Retrieve the OAuth token from the base class
        token = self.base.get_private_token()
        
        # Construct the endpoint URL using the provided project_id
        url = f"https://developer.api.autodesk.com/data/v1/projects/{project_id}/commands"
        
        # Set the required request headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json"
        }
        
        # Build the JSON payload following the API specification
        payload = {
            "jsonapi": {"version": "1.0"},
            "data": {
                "type": "commands",
                "attributes": {
                    "extension": {
                        "type": "commands:autodesk.bim360:C4RModelGetPublishJob",
                        "version": "1.0.0"
                    }
                },
                "relationships": {
                    "resources": {
                        "data": [
                            {"type": "items", "id": item_id}
                        ]
                    }
                }
            }
        }
        
        # Execute the POST request to the Autodesk API endpoint
        response = requests.post(url, headers=headers, json=payload)
        
        # Raise an exception for HTTP errors (e.g., 400, 403, 404)
        response.raise_for_status()
        
        # Return only the 'data' field from the response
        return response.json().get("data")
        
