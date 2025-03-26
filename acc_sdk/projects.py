import requests
from .base import AccBase

class AccProjectsApi:
    '''
    This class provides methods to interact with the project endpoint of the Autodesk Construction Cloud API.
    The get methods require account:read and the post, and patch methods require account:write scopes.

    Token must be Bearer <token>, where <token> is is obtained via either a two-legged or three-legged OAuth flow
    for the GET and POST methods.  The Patch method requires a 2-legged token.
    '''    
    def __init__(self, base: AccBase):
        self.base_url = "https://developer.api.autodesk.com/construction/admin/v1"
        self.base = base
        self.user_id = self.base.user_info.get('uid')

    def get_project(self, project_id):
        """
        Get a project by project ID.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-projectsprojectId-GET/

        Args:
            project_id (str): The project ID to lookup the project by.

        Returns:
            dict: project object
        """
        token = f"Bearer {self.base.get_private_token()}"

        headers = {"Authorization": token}
        url = f"https://developer.api.autodesk.com/construction/admin/v1/projects/{project_id}"

        response = requests.get(url, headers=headers)
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

    def get_projects(self, filter_params:dict=None, follow_pagination:bool=False)->list[dict]:
        """
        Get a list of projects in an account. You can also use this endpoint to filter out the list of projects by setting the filter parameters.   

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/admin-accounts-accountidprojects-GET/

        Args:
            filter_params (dict, optional): Filter parameters to apply to the query.
            follow_pagination (bool, optional): If True, follow pagination links to get all projects.

        Returns:
            list: The list of projects (results array) from the API response.
        """        
        token = f"Bearer {self.base.get_private_token()}"

        # if filter_params contains fields, and fields contains ID, then remove ID from fields
        if filter_params is not None and filter_params.get('fields') != None:
            fields = filter_params.get('fields').split(',')
            fields = [field.strip() for field in fields]
            if 'id' in fields:
                fields.remove('id')
                filter_params['fields'] = ','.join(fields)

        url = f"{self.base_url}/accounts/{self.base.account_id}/projects"

        headers = {"Authorization": token, "User-Id": self.user_id}

        projects = []
        while url:
            response = requests.get(url, headers=headers, params=filter_params)
            if response.status_code != 200:
                errors = response.json().get('errors') if response.json().get('errors') else response.json().get('detail')
                if errors:
                    print(errors)                
                response.raise_for_status()

            data = response.json()
            projects.extend(data.get("results",{}))
            
            url = data["pagination"].get("nextUrl") if follow_pagination else None

            # clear filter_params for subsequent requests using the pagination URL
            filter_params = None

        return projects

    def get_active_projects(self, filter_params:dict=None, follow_pagination:bool=False):
        """Get all active projects in the account.

        Args:
            filter_params (str, optional): Filter parameters to apply to the query. 
            follow_pagination (bool, optional): If True, follow pagination links to get all projects.

        Returns:
            list: a list of active projects filtered by the filter parameters.
        """
        if filter_params is None:
            filter_params = {}
        filter_params['filter[status]'] = 'active'
        return self.get_projects(filter_params, follow_pagination)

    def get_all_active_projects(self, filter_params:dict=None):
        """Get all active projects in the account.

        Args:
            filter_params (str, optional): Filter parameters to apply to the query.            

        Returns:
            list: a list of active projects filtered by the filter parameters.
        """        
        if filter_params is None:
            filter_params = {}
        filter_params['filter[status]'] = 'active'
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
        """
        token = f"Bearer {self.base.get_private_token()}"

        if project.get("name") == None:
            raise Exception("Missing required parameter 'name'")
        if project.get("type") == None:            
            raise Exception("Missing required parameter 'type'")

        headers = {
            "Content-Type": "application/json",
            "Authorization": token,
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
            errors = response.json().get('errors') if response.json().get('errors') else response.json().get('detail')
            if errors:                
                [print(error) for error in errors]
            job = self.get_projects(filter_params={'filter[jobNumber]': project['jobNumber']})
            return job[0]
        else:
            errors = response.json().get('errors') if response.json().get('errors') else response.json().get('detail')
            if errors:                
                [print(error) for error in errors]
            response.raise_for_status()

