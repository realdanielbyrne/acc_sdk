from re import A
from .base import AccBase
from .account_users import AccAccountUsersApi
from .project_users import AccProjectUsersApi
from .projects import AccProjectsApi
from .sheets import AccSheetsApi
from .data_management import AccDataManagementApi
from .forms import AccFormsApi
from .authentication import Authentication
from .companies import AccCompaniesApi
from .business_units import AccBusinessUnitsApi

# Aggregator class supporting both 2-legged and 3-legged auth.
class Acc:
    def __init__(   self, 
                    auth_client: Authentication,
                    account_id=None):
        """
        Initializes the Acc aggregator.

        Parameters:
            auth_client (Authentication): The authentication client to use.
            account_id (str): The account ID to use. If not provided, the account ID is determined from the auth_client.

        """

        # Initialize the shared base instance.
        self.base = AccBase(auth_client=auth_client, account_id=account_id)
        self.auth_client = auth_client
        
        # Instantiate APIs that work with both token types.        
        self.project_users = AccProjectUsersApi(self.base)
        self.projects = AccProjectsApi(self.base)
        self.sheets = AccSheetsApi(self.base)
        self.data_management = AccDataManagementApi(self.base)      

        # Apis that require 2-legged authorization
        self.account_users = AccAccountUsersApi(self.base)
        self.business_units = AccBusinessUnitsApi(self.base)

        # Requires account:read scope and a 2-legged or 3-legged auth token for GET methods
        # Requires account:write scope and a 2-legged auth token for POST and PATCH methods
        self.companies = AccCompaniesApi(self.base)

        # Apis that require 3-legged authorization
        self.forms = AccFormsApi(self.base) 
        self.user_profiles = AccAccountUsersApi(self.base)
    
    def get_forms(self, project_id, **forms_kwargs)->list[dict]:
        """
        get_forms extension to get forms along with user names and email addresses
        of the users who created the forms.

        Args:
            project_id (str): The project ID.
            **forms_kwargs: Additional keyword arguments to pass to the get_forms() method.

        Returns:
            list: A list of forms along with user names and email addresses of the users who created the forms.
        """
        # Retrieve the form templates for the project.
        forms = self.forms.get_forms(project_id, **forms_kwargs)

        # Extract the createdBy field the forms and create a list of only unique names
        user_names = []
        for form in forms:
            user_name = form.get("createdBy")
            if user_name not in user_names:
                user_names.append(user_name)

        # get user names from the user ids using the project_users api
        project_users = self.project_users.get_users(project_id, query_params={"filter['autodeskId']": user_names,"fields":['email','name','autodeskId']})

        # update forms with user names and email addresses matched by form.createdBy = project_user.autodeskId
        for form in forms:
            userId = form.get("createdBy")
            for project_user in project_users:
                if userId == project_user.get("autodeskId"):
                    form["createdByName"] = project_user.get("name")
                    form["createdByEmail"] = project_user.get("email")
                    break

        return forms

    def get_forms_for_past30(self, project_id, **forms_kwargs)->list[dict]:
        """
        get_forms_for_past30 extension to get forms along with user names and email addresses
        of the users who created the forms that were created within the past 30 days.

        Args:
            project_id (str): The project ID.
            **forms_kwargs: Additional keyword arguments to pass to the get_forms() method.

        Returns:
            list: A forms entered over the past 30 days.
        
        """
        forms = self.forms.get_forms_for_past30(project_id, **forms_kwargs)
        
        # Extract the createdBy field the forms and create a list of only unique names
        user_names = []
        for form in forms:
            user_name = form.get("createdBy")
            if user_name not in user_names:
                user_names.append(user_name)

        # get user names from the user ids using the project_users api
        project_users = self.project_users.get_users(
            project_id, 
            query_params={"filter['autodeskId']": user_names,"fields":['email','name','autodeskId']})

        # update forms with user names and email addresses matched by form.createdBy = project_user.autodeskId
        for form in forms:
            userId = form.get("createdBy")
            for project_user in project_users:
                if userId == project_user.get("autodeskId"):
                    form["createdByName"] = project_user.get("name")
                    form["createdByEmail"] = project_user.get("email")
                    break

        return forms

    def get_forms_all_active_projects(self, **forms_kwargs):
        """
        get_forms_all_projects extension to get forms along with user names and email addresses
        of the users who created the forms for all projects.

        Args:
            **forms_kwargs: Additional keyword arguments to pass to the get_forms() method.
        
        """
        projects = self.projects.get_all_active_projects()
        all_forms = []
        for project in projects:
            forms = self.get_forms(project.get("id"), **forms_kwargs)
            all_forms.extend(forms)
        return all_forms

    def get_forms_all_active_projects_last30(self, **forms_kwargs):
        """
        get_forms_all_projects_last30 extension to get forms along with user names and email addresses
        of the users who created the forms for all projects that were created within the past 30 days.

        Args:
            **forms_kwargs: Additional keyword arguments to pass to the get_forms() method.
        
        """
        projects = self.projects.get_all_active_projects()
        all_forms = []
        for project in projects:
            forms = self.get_forms_for_past30(project.get("id"), **forms_kwargs)
            all_forms.extend(forms)
        return all_forms
        
    
        
