# accapi/forms.py
import requests
from datetime import date, timedelta
from .base import AccBase

class AccFormsApi:
    '''
    This class provides methods to interact with the Forms endpoint of the Autodesk Construction Cloud API.
    The GET methods require data:read and the POST, PATCH, and PUT methods require data:write scope.

    Token must be Bearer <token>, where <token> is is obtained via a three-legged OAuth flow
    for the GET, POST, PATCH, and PUT methods.
    '''       
    def __init__(self, base: AccBase):
        self.base = base        
        self.base_url = "https://developer.api.autodesk.com/construction/forms/v1"

    def get_forms(self, project_id, offset=0, limit=50, ids=None, formDateMin=None,
                  formDateMax=None, updatedAfter=None, updatedBefore=None, templateId=None,
                  statuses=None, sortBy=None, sortOrder=None, locationIds=None, follow_pagination=False)->list[dict]:
        """
        Returns a paginated list of forms in a project. Forms are sorted by updatedAt, most recent first.
        Returns up to 50 forms per page unless follow_pagination is True.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-GET/

        Args:
            project_id (str): The project ID.
            offset (int): The number of records to skip (defaults to 0).
            limit (int): The number of records per page (defaults to 50, maximum is 50).
            ids (str, optional): A comma-separated list of form IDs to filter by.
            formDateMin (str, optional): ISO 8601 datetime to filter forms created after this time.
            formDateMax (str, optional): ISO 8601 datetime to filter forms created before this time.
            updatedAfter (str, optional): ISO 8601 datetime to filter forms updated after this time.
            updatedBefore (str, optional): ISO 8601 datetime to filter forms updated before this time.
            templateId (str, optional): The form template ID to filter by.
            statuses (str, optional): A comma-separated list of statuses to filter by.
            sortBy (str, optional): The field to sort the forms by.
            sortOrder (str, optional): The sort order ('asc' or 'desc').
            locationIds (str, optional): A comma-separated list of location IDs to filter by.
            follow_pagination (bool, optional): Whether to follow pagination links.

        Returns:
            list: A list of forms in the project.
        """        
        # Remove the "b." prefix if present.
        if project_id.startswith("b."):
            project_id = project_id[2:]
        
        # Build the initial URL
        url = f"{self.base_url}/projects/{project_id}/forms"
        
        # Build the query parameters dictionary
        params = {
            "offset": offset,
            "limit": limit,
        }
        if limit > 50:
            raise ValueError("The maximum limit is 50.")
        
        if ids is not None:
            params["ids"] = ids
        if formDateMin is not None:
            params["formDateMin"] = formDateMin
        if formDateMax is not None:
            params["formDateMax"] = formDateMax
        if updatedAfter is not None:
            params["updatedAfter"] = updatedAfter
        if updatedBefore is not None:
            params["updatedBefore"] = updatedBefore
        if templateId is not None:
            params["templateId"] = templateId
        if statuses is not None:
            params["statuses"] = statuses
        if sortBy is not None:
            params["sortBy"] = sortBy
        if sortOrder is not None:
            params["sortOrder"] = sortOrder
        if locationIds is not None:
            # Autodesk expects multiple location parameters as individual query parameters.
            params["locationId"] = locationIds

        headers = {"Authorization": f"Bearer {self.base.get_3leggedToken()}"}

        all_forms = []        
        current_params = params

        while url:
            response = requests.get(url, headers=headers, params=current_params)
            response.raise_for_status()
            json_data = response.json()

            # Extend the list with the forms data from this page.
            all_forms.extend(json_data.get("data", []))

            # Get pagination info
            pagination = json_data.get("pagination", {})
            url = pagination.get("nextUrl") if follow_pagination else None

            # For subsequent requests, use the next_url which already includes query parameters.
            current_params = {}

        return all_forms

    def get_templates(self, project_id, offset=0, limit=50, updatedAfter=None,
                      updatedBefore=None, sortOrder=None, follow_pagination=False)->list[dict]:
        """
        Retrieve all form templates for a given project by following pagination.
        
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-form-templates-GET/
        
        Args:
            project_id (str): The project ID (will remove a leading "b." if present).
            offset (int): Number of records to skip (defaults to 0).
            limit (int): Number of records per page (defaults to 50, maximum is 50).
            updatedAfter (str, optional): ISO 8601 datetime to filter templates updated after this time.
            updatedBefore (str, optional): ISO 8601 datetime to filter templates updated before this time.
            sortOrder (str, optional): Sort order for the templates ('asc' or 'desc').

        Returns:
            list: A list of all form templates for the specified project.
        """
        # Remove the "b." prefix from the project_id if it exists.
        if project_id.startswith("b."):
            project_id = project_id[2:]

        # Build the initial URL for the form templates endpoint.
        url = f"{self.base_url}/projects/{project_id}/form-templates"

        # Build the query parameters.
        params = {
            "offset": offset,
            "limit": limit,
        }
        if limit > 50:
            raise ValueError("The maximum limit is 50.")
        if updatedAfter is not None:
            params["updatedAfter"] = updatedAfter
        if updatedBefore is not None:
            params["updatedBefore"] = updatedBefore
        if sortOrder is not None:
            params["sortOrder"] = sortOrder

        headers = {"Authorization": f"Bearer {self.base.get_3leggedToken()}"}

        all_templates = []        
        current_params = params

        while url:
            response = requests.get(url, headers=headers, params=current_params)
            response.raise_for_status()
            json_data = response.json()

            # Add the templates from this page to the list.
            all_templates.extend(json_data.get("data", []))

            # Follow the pagination link if available.
            pagination = json_data.get("pagination", {})
            url = pagination.get("nextUrl") if follow_pagination else None
            if not url:
                break

            current_params = {}

        return all_templates

    def get_forms_for_past30(self, project_id, **kwargs)->list[dict]:
        """
        Retrieve forms for a given project that were created within teh past 30 days.

        Args:
            project_id (str): The project ID.
            **kwargs: Additional keyword arguments to pass to the get_forms() method.

        Returns:
            list: A list of forms that were created within the past 30 days.            
        """
        today = date.today()
        date_minus_30 = today - timedelta(days=30)

        # Format the date as 'yyyy-mm-dd'
        formDateMin = date_minus_30.strftime('%Y-%m-%d')

        return self.get_forms(project_id, formDateMin=formDateMin, **kwargs)

    def post_form(self, project_id:str, template_id:str, data:dict)->dict:
        """
        Adds a new form to a project.
        
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-POST/

        Args:
            project_id (str): The project ID from GET forms.
            template_id (str): The form template ID from GET forms.
            data (dict): The form data to create the form.

        """
        url = f"{self.base_url}/projects/{project_id}/form-templates/{template_id}/forms"

        headers = {"Authorization": f"Bearer {self.base.get_3leggedToken()}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def patch_form(self, project_id:str, template_id:str, form_id:str, data:dict)->dict:
        """
        Updates a form’s form details. Note that we do not currently support updating PDF forms.

        To edit a form, it must be in draft or inReview status and the user must have permissions to edit the form.
        
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-formId-PATCH/

        Args:
            project_id (str): The project ID from GET forms.            
            template_id (str): The form template ID from GET forms.
            form_id (str): The form ID from GET forms.
            data (dict): The form data split into customValues(non-tabular fields) and tabularValues(tabular fields).

        """
        url = f"{self.base_url}/projects/{project_id}/form-templates/{template_id}/forms/{form_id}"

        headers = {"Authorization":f"Bearer {self.base.get_3leggedToken()}", 
                   "Content-Type": "application/json"}
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def put_form(self, project_id:str, form_id:str, data:dict)->dict:
        """
        Updates a form’s main form fields, both tabular and non-tabular. Note that we do not currently support updating PDF forms.
        To edit form values, the form needs to be in draft status and the user must have permissions to edit the form. 
        
        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-formId-PUT/

        Args:
            project_id (str): The project ID from GET forms.            
            data (dict): The form data split into customValues(non-tabular fields) and tabularValues(tabular fields).

        Returns:
            dict: The form object from the API response.
        """
        url = f"{self.base_url}/projects/{project_id}/forms/{form_id}/values:batch-update"

        headers = {"Authorization":f"Bearer {self.base.get_3leggedToken()}", 
                   "Content-Type": "application/json"}
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()