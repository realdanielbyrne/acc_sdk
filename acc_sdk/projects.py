import requests
from .base import AccBase


class AccProjectsApi:
    """
    This class provides methods to interact with the project endpoint of the Autodesk Construction Cloud API.
    The get methods require account:read and the post, and patch methods require account:write scopes.

    Token must be Bearer <token>, where <token> is obtained via either a two-legged or three-legged OAuth flow
    for the GET and POST methods. The Patch method requires a 2-legged token.

    Example:
        ```python
        from accapi import Acc
        acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)

        # Get all projects
        projects = acc.projects.get_projects()

        # Create a new project
        new_project = {
            "name": "My Project",
            "type": "Wall Construction",
            "jobNumber": "12345"
        }
        created_project = acc.projects.post_project(new_project)
        ```
    """

    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/construction/admin/v1"
        self.base = base
        self.user_id = self.base.user_info.get("uid")

    def _get_headers(self):
        """
        Constructs the headers required for API requests.

        Returns:
            dict: A dictionary containing the headers.
        """
        token = f"Bearer {self.base.get_private_token()}"
        headers = {"Authorization": token}
        if self.user_id:
            headers["User-Id"] = self.user_id
        return headers

    def _handle_pagination(self, url, headers, params=None):
        """
        Handles pagination for API requests.

        Args:
            url (str): The initial URL for the API request.
            headers (dict): The headers for the API request.
            params (dict, optional): Query parameters for the API request.

        Returns:
            list: A list of results from all pages.
        """
        results = []
        while url:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                errors = response.json().get("errors") or response.json().get("detail")
                if errors:
                    print(errors)
                response.raise_for_status()

            data = response.json()
            results.extend(data.get("results", []))

            # Get the next URL for pagination
            url = data.get("pagination", {}).get("nextUrl")

            # Clear params for subsequent requests using the pagination URL
            params = None

        return results

    def get_project(self, project_id):
        """
        Get a project by project ID.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projectsprojectId-GET/

        Args:
            project_id (str): The project ID to lookup the project by.

        Returns:
            dict: Project object.

        Example:
            ```python
            # Get a specific project by ID
            project = acc.projects.get_project(project_id="your_project_uuid")
            print(project["name"])  # Print project name
            ```
        """
        headers = self._get_headers()
        url = f"{self.base_url}/projects/{project_id}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            errors = response.json().get("errors") or response.json().get("detail")
            if errors:
                print(errors)
            response.raise_for_status()

    def get_projects(
        self, filter_params: dict = None, follow_pagination: bool = False
    ) -> list[dict]:
        """
        Get a list of projects in an account. You can also use this endpoint to filter out the list of projects by setting the filter parameters.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-accounts-accountidprojects-GET/

        Args:
            filter_params (dict, optional): Filter parameters to apply to the query.
            follow_pagination (bool, optional): If True, follow pagination links to get all projects.

        Returns:
            list: The list of projects (results array) from the API response.

        Example:
            ```python
            # Get all projects
            projects = acc.projects.get_projects()

            # Get projects with specific fields
            projects = acc.projects.get_projects(
                filter_params={'fields': "accountId,name,jobNumber"}
            )

            # Get projects with pagination
            projects = acc.projects.get_projects(
                filter_params={'limit': 50},
                follow_pagination=True
            )

            # Get projects with status filter
            active_projects = acc.projects.get_projects(
                filter_params={'filter[status]': 'active'}
            )
            ```
        """
        headers = self._get_headers()
        url = f"{self.base_url}/accounts/{self.base.account_id}/projects"

        if follow_pagination:
            return self._handle_pagination(url, headers, filter_params)

        response = requests.get(url, headers=headers, params=filter_params)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            errors = response.json().get("errors") or response.json().get("detail")
            if errors:
                print(errors)
            response.raise_for_status()

    def get_active_projects(
        self, filter_params: dict = None, follow_pagination: bool = False
    ):
        """
        Get all active projects in the account.

        Args:
            filter_params (dict, optional): Filter parameters to apply to the query.
            follow_pagination (bool, optional): If True, follow pagination links to get all projects.

        Returns:
            list: A list of active projects filtered by the filter parameters.

        Example:
            ```python
            # Get all active projects
            active_projects = acc.projects.get_active_projects()

            # Get active projects with specific fields
            active_projects = acc.projects.get_active_projects(
                filter_params={'fields': "name,jobNumber,type"}
            )

            # Get active projects with pagination
            active_projects = acc.projects.get_active_projects(
                filter_params={'limit': 10},
                follow_pagination=True
            )
            ```
        """
        if filter_params is None:
            filter_params = {}
        filter_params["filter[status]"] = "active"
        return self.get_projects(filter_params, follow_pagination)

    def get_all_active_projects(self, filter_params: dict = None):
        """
        Get all active projects in the account.

        Args:
            filter_params (dict, optional): Filter parameters to apply to the query.

        Returns:
            list: A list of active projects filtered by the filter parameters.

        Example:
            ```python
            # Get all active projects
            active_projects = acc.projects.get_all_active_projects()

            # Get all active projects with specific fields
            active_projects = acc.projects.get_all_active_projects(
                filter_params={'fields': "name,jobNumber,type,status"}
            )

            # Get all active projects with additional filters
            filtered_projects = acc.projects.get_all_active_projects(
                filter_params={
                    'fields': "name,jobNumber,type",
                    'filter[type]': 'Wall Construction'
                }
            )
            ```
        """
        if filter_params is None:
            filter_params = {}
        filter_params["filter[status]"] = "active"
        return self.get_projects(filter_params, follow_pagination=True)

    def post_project(self, project: dict):
        """
        Creates a new project in the specified account. You can create the project directly,
        or clone it from a project template.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-accounts-accountidprojects-POST/

        Args:
            project (dict): A project object to create. Required fields are name and type.
            Name must be unique.

        Returns:
            dict: The created project object.

        Example:
            ```python
            # Create a new project
            new_project = {
                "name": "My Project",
                "type": "Wall Construction",
                "jobNumber": "12345",
                "latitude": "34.7749",
                "longitude": "-125.4194",
                "timezone": "America/Chicago"
            }
            created_project = acc.projects.post_project(new_project)

            # Create a project from a template
            template_project = {
                "name": "Template Project",
                "type": "Wall Construction",
                "jobNumber": "12346",
                "template": {
                    "projectId": "template-uuid"
                }
            }
            created_template_project = acc.projects.post_project(template_project)
            ```
        """
        headers = self._get_headers()

        if project.get("name") is None:
            raise Exception("Missing required parameter 'name'")
        if project.get("type") is None:
            raise Exception("Missing required parameter 'type'")

        headers = {
            "Content-Type": "application/json",
            "Authorization": headers["Authorization"],
            "User-Id": self.user_id,
        }
        response = requests.post(
            f"{self.base_url}/accounts/{self.base.account_id}/projects",
            headers=headers,
            json=project,
        )
        if response.status_code == 202:
            print(f"Project {project['jobNumber']} created")
            content = response.json()
            return content
        elif response.status_code == 409:
            errors = response.json().get("errors") or response.json().get("detail")
            if errors:
                [print(error) for error in errors]
            job = self.get_projects(
                filter_params={"filter[jobNumber]": project["jobNumber"]}
            )
            return job[0]
        else:
            errors = response.json().get("errors") or response.json().get("detail")
            if errors:
                [print(error) for error in errors]
            response.raise_for_status()
