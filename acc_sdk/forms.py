# accapi/forms.py
import requests
from datetime import date, timedelta
from .base import AccBase


class AccFormsApi:
    """
    This class provides methods to interact with the Forms endpoint of the Autodesk Construction Cloud API.
    The GET methods require data:read and the POST, PATCH, and PUT methods require data:write scope.

    Token must be Bearer <token>, where <token> is is obtained via a three-legged OAuth flow
    for the GET, POST, PATCH, and PUT methods.

    Example:
        ```python
        from accapi import Acc
        acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)

        # Get all forms in a project
        forms = acc.forms.get_forms(project_id="your_project_id")

        # Create a new form
        new_form = acc.forms.post_form(
            project_id="your_project_id",
            template_id="template_uuid",
            data={"customValues": {"field1": "value1"}}
        )
        ```
    """

    def __init__(self, base: AccBase):
        self.base = base
        self.base_url = "https://developer.api.autodesk.com/construction/forms/v1"

    def _get_headers(self):
        """
        Constructs the headers required for API requests.

        Returns:
            dict: A dictionary containing the headers.
        """
        token = f"Bearer {self.base.get_3leggedToken()}"
        return {"Authorization": token, "Content-Type": "application/json"}

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
            response.raise_for_status()
            data = response.json()

            # Extend the results with the data from this page
            results.extend(data.get("data", []))

            # Get the next URL for pagination
            url = data.get("pagination", {}).get("nextUrl")

            # Clear params for subsequent requests using the pagination URL
            params = None

        return results

    def get_forms(
        self,
        project_id,
        offset=0,
        limit=50,
        ids=None,
        formDateMin=None,
        formDateMax=None,
        updatedAfter=None,
        updatedBefore=None,
        templateId=None,
        statuses=None,
        sortBy=None,
        sortOrder=None,
        locationIds=None,
        follow_pagination=False,
    ) -> list[dict]:
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

        Example:
            ```python
            # Get all forms
            forms = acc.forms.get_forms(project_id="your_project_id")

            # Get forms with pagination
            forms = acc.forms.get_forms(
                project_id="your_project_id",
                follow_pagination=True
            )

            # Get forms filtered by date range
            forms = acc.forms.get_forms(
                project_id="your_project_id",
                formDateMin="2024-01-01T00:00:00Z",
                formDateMax="2024-03-25T23:59:59Z"
            )

            # Get forms by template and status
            forms = acc.forms.get_forms(
                project_id="your_project_id",
                templateId="template_uuid",
                statuses="draft,inReview"
            )
            ```
        """
        if project_id.startswith("b."):
            project_id = project_id[2:]

        url = f"{self.base_url}/projects/{project_id}/forms"
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
            params["locationId"] = locationIds

        headers = self._get_headers()

        if follow_pagination:
            return self._handle_pagination(url, headers, params)

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])

    def get_templates(
        self,
        project_id,
        offset=0,
        limit=50,
        updatedAfter=None,
        updatedBefore=None,
        sortOrder=None,
        follow_pagination=False,
    ) -> list[dict]:
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

        Example:
            ```python
            # Get all templates
            templates = acc.forms.get_templates(project_id="your_project_id")

            # Get templates with pagination
            templates = acc.forms.get_templates(
                project_id="your_project_id",
                follow_pagination=True
            )

            # Get recently updated templates
            templates = acc.forms.get_templates(
                project_id="your_project_id",
                updatedAfter="2024-01-01T00:00:00Z",
                sortOrder="desc"
            )
            ```
        """
        if project_id.startswith("b."):
            project_id = project_id[2:]

        url = f"{self.base_url}/projects/{project_id}/form-templates"
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

        headers = self._get_headers()

        if follow_pagination:
            return self._handle_pagination(url, headers, params)

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("data", [])

    def get_forms_for_past30(self, project_id, **kwargs) -> list[dict]:
        """
        Retrieve forms for a given project that were created within teh past 30 days.

        Args:
            project_id (str): The project ID.
            **kwargs: Additional keyword arguments to pass to the get_forms() method.

        Returns:
            list: A list of forms that were created within the past 30 days.

        Example:
            ```python
            # Get forms from the past 30 days
            recent_forms = acc.forms.get_forms_for_past30(project_id="your_project_id")

            # Get forms from the past 30 days with additional filters
            recent_forms = acc.forms.get_forms_for_past30(
                project_id="your_project_id",
                templateId="template_uuid",
                statuses="completed"
            )
            ```
        """
        today = date.today()
        date_minus_30 = today - timedelta(days=30)

        # Format the date as 'yyyy-mm-dd'
        formDateMin = date_minus_30.strftime("%Y-%m-%d")

        return self.get_forms(project_id, formDateMin=formDateMin, **kwargs)

    def post_form(self, project_id: str, template_id: str, data: dict) -> dict:
        """
        Adds a new form to a project.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-POST/

        Args:
            project_id (str): The project ID from GET forms.
            template_id (str): The form template ID from GET forms.
            data (dict): The form data to create the form.

        Returns:
            dict: The created form object.

        Example:
            ```python
            # Create a new form
            form_data = {
                "customValues": {
                    "field1": "value1",
                    "field2": "value2"
                },
                "tabularValues": {
                    "table1": [
                        {"column1": "value1", "column2": "value2"},
                        {"column1": "value3", "column2": "value4"}
                    ]
                }
            }
            new_form = acc.forms.post_form(
                project_id="your_project_id",
                template_id="template_uuid",
                data=form_data
            )
            print(new_form["id"])  # Print the new form ID
            ```
        """
        url = (
            f"{self.base_url}/projects/{project_id}/form-templates/{template_id}/forms"
        )

        headers = self._get_headers()
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def patch_form(
        self, project_id: str, template_id: str, form_id: str, data: dict
    ) -> dict:
        """
        Updates a form's form details. Note that we do not currently support updating PDF forms.

        To edit a form, it must be in draft or inReview status and the user must have permissions to edit the form.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-formId-PATCH/

        Args:
            project_id (str): The project ID from GET forms.
            template_id (str): The form template ID from GET forms.
            form_id (str): The form ID from GET forms.
            data (dict): The form data split into customValues(non-tabular fields) and tabularValues(tabular fields).

        Returns:
            dict: The updated form object.

        Example:
            ```python
            # Update form details
            update_data = {
                "customValues": {
                    "field1": "updated_value1"
                }
            }
            updated_form = acc.forms.patch_form(
                project_id="your_project_id",
                template_id="template_uuid",
                form_id="form_uuid",
                data=update_data
            )
            print(updated_form["id"])  # Print the updated form ID
            ```
        """
        url = f"{self.base_url}/projects/{project_id}/form-templates/{template_id}/forms/{form_id}"

        headers = self._get_headers()
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def put_form(self, project_id: str, form_id: str, data: dict) -> dict:
        """
        Updates a form's main form fields, both tabular and non-tabular. Note that we do not currently support updating PDF forms.
        To edit form values, the form needs to be in draft status and the user must have permissions to edit the form.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/forms-forms-formId-PUT/

        Args:
            project_id (str): The project ID from GET forms.
            data (dict): The form data split into customValues(non-tabular fields) and tabularValues(tabular fields).

        Returns:
            dict: The form object from the API response.

        Example:
            ```python
            # Batch update form fields
            update_data = {
                "customValues": {
                    "field1": "new_value1",
                    "field2": "new_value2"
                },
                "tabularValues": {
                    "table1": [
                        {"column1": "new_value1", "column2": "new_value2"}
                    ]
                }
            }
            updated_form = acc.forms.put_form(
                project_id="your_project_id",
                form_id="form_uuid",
                data=update_data
            )
            print(updated_form)  # Print the updated form data
            ```
        """
        url = (
            f"{self.base_url}/projects/{project_id}/forms/{form_id}/values:batch-update"
        )

        headers = self._get_headers()
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
