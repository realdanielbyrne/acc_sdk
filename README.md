# Autodesk Construction Cloud SDK

## Introduction
The Autodesk Construction Cloud, ACC, API for Python helps developers create applications that leverage
ACC API. This API grew out of my company's need to automate certain aspects of ACC that are not currently
supported by the ACC web application. The API is a work in progress and will be updated with more services
as the features are implemented. I am working on adding more services to the `ACC` class, but you can also
contribute to the project by adding more services.

I've currently implemented the following APIs:

- The Account Admin API automates creating and managing projects, assigning and managing project users, and managing 
 member and partner company directories with teh following APIs:

    - The Projects API provides methods to create, read, update, and delete projects. 
    - The Accoount Users API allows you to add and update groups of users to your account.
    - The Business Units API allows you to createe, update, or get business units in your account.
    - The Companies API provides methods to manage companies, such as adding and updating companies.
    - The Project Users API provides methods to manage project users, such as adding, updating, deleting, and patching permissions for users on a project.

- The Forms API provides methods to securely create forms from a template, fill out, modify, and retrieve form data.
- The Sheets API provides methods to manage sheets and version sets, as well as uploading, publishing, and exporting sheets as pdfs.
- The Authentication helper class provides methods to authenticate with the ACC using the OAuth2 2-legged 
 client credential flow and/or the 3-legged authorization code flows. This class also maintains
 the validity of the Bearer tokens, by refreshing the tokens as they expire, and manages both 2-legged and 
 3-legged tokens at the same time to give you full access to the API services.

- The Data Management API allows you to manage files and folders in the project. You can upload, download, and
 delete files, create folders, and move files between folders. The API also provides access to the data stored
 in the ACC Data Management module.

- The User Profile API provides an endpoint for gathering profile information from the logged in user.

## Contributing

This project is a work in progress and will be updated with more services as the features are implemented. I am 
working on adding more services to the `ACC` class, but you can also contribute to the project by helping me add
more services.

To contribute to the project, please follow the steps below:

1. Fork the repository
2. Clone the repository
3. Create a new branch
4. Make your changes
5. Push your changes to your fork
6. Create a pull request


The following services are planned for future implementation:

- The AutoSpecs API 
- The Assets API 
- The Cost Management API 
- The Data Connector API 
- The Files (Document Management) API
- The Issues API 
- The Model Coordination API 
- The Locations API 
- The Photos API 
- The Relationships API 
- The RFIs API (beta) 
- The Submittals API 
- The Takeoff API 


## Installation

```bash
pip install acc_sdk
poetry install
```

## Authentication

To use the ACC API, you need to create an instance of the `ACC` class. The `ACC` class provides access to the various
services provided by the ACC API.  However, first you need to authenticate with the ACC API. 

The ACC API uses the OAuth2 2 legged client credential flow and/or the 3 legged authorization code flow. Various API services require
one or the other flows. The Authentication OAuth helper class provides the necessary methods to

- Authenticate with the ACC API using either 
    - 2 legged client credential flow 
    - 3 legged authorization code flow 
- Maintains the validity of the Bearer tokens, by refreshing the tokens as they expire
- Manages both 2-legged and 3-legged tokens at the same time to give you full access to the API services

The following code snippet shows how to authenticate with the ACC API using the 2 legged client credential flow.

```python
import os
from accapi import Authentication, Acc
from dotenv import load_dotenv
load_dotenv()

# Load your environment variables
ACCOUNT_ID = os.environ.get('AUTODESK_ACCOUNT_ID')
CLIENT_ID =  os.environ.get('AUTODESK_CLIENT_ID_WEB_APP'),
CLIENT_SECRET =  os.environ.get('AUTODESK_CLIENT_SECRET_WEB_APP')
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

# Define the scopes
scopes = [
            "user-profile:read",
            "user:read",
            "user:write",
            "viewables:read",
            "data:read",
            "data:write",
            "data:create",
            "data:search",
            "bucket:create",
            "bucket:read",
            "bucket:update",
            "bucket:delete",
            "code:all",
            "account:read",
            "account:write"
            ] 

# Initalize the class 
auth_client = Authentication(
    session={}, 
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, 
    admin_email="youremail@adomain.com"
    )  

# Request the 2 legged token
auth_client.request_2legged_token(scopes=scopes)
assert auth_client._session["accapi_2legged"]
```

The following code snippet shows how to authenticate with the ACC API using the 3 legged authorization code flow.

```python
import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from accapi import Authentication, Acc
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SESSION_KEY") # Required for session usage
CLIENT_ID = os.environ.get("AUTODESK_CLIENT_ID_WEB_APP")
CLIENT_SECRET = os.environ.get("AUTODESK_CLIENT_SECRET_WEB_APP")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
CALLBACK_URL = "http://127.0.0.1:5000/callback"
ACCOUNT_ID = os.environ.get("AUTODESK_ACCOUNT_ID")
SCOPES = [
    "user-profile:read",
    "user:read",
    "user:write",
    "viewables:read",
    "data:read",
    "data:write",
    "data:create",
    "account:read",
    "account:write",
]
@app.route("/", methods=["GET"])
def index():
    session.clear()
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """Called from form submission on index.html. Initiates OAuth2 flow.
        Redirects to callback URL if successful, or an error message if not.
    """
    email = request.form.get("email")
    session["user_email"] = email
    auth = Authentication(session,CLIENT_ID,CLIENT_SECRET, session["user_email"], CALLBACK_URL)
    
    authorization_url = auth.get_authorization_url(scopes=SCOPES)
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    """Second step in the OAuth2 flow. Exchanges auth code for access token.
        Redirects to dashboard if successful, or an error message if not.
    """
    code = request.args.get("code")
    if not code:
        return "No authorization code received.", 400

    # Rebuild the Authentication object from the session
    auth = Authentication(session,CLIENT_ID,CLIENT_SECRET, session["user_email"], CALLBACK_URL)
    token_data = auth.request_authcode_access_token(code=code, scopes=SCOPES)
    if not token_data:
        return "Failed to exchange code for token", 400

    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """ Final destination of 3 legged Authenticatin flow. """
    
    # Rebuild the Authentication object from the session
    auth = Authentication(session,CLIENT_ID,CLIENT_SECRET, session["user_email"], CALLBACK_URL)

    # Build an ACC instance (accapi) with the user’s authentication context
    acc = Acc(auth_client=auth, account_id=ACCOUNT_ID)
    return render_template("dashboard.html")

def run():
    app.run(debug=True)
    
if __name__ == "__main__":
    run()

```


## Initialization

Once you have authenticated with the ACC API, you can create an instance of the `ACC` class. The `ACC` class provides access to the various services provided by the ACC API. 
The account id is an optional argument. If you do not provide the account id, the class will attempt to get the Account Id from the 2-legged token.  Not providing the account
id will not limit the services you can access if you have both the 2-legged and 3-legged tokens and the appropriate scopes.


```python
from accapi import Acc
acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)
```

The account id is an optional argument. If you do not provide the account id, the class will attempt to get the Account Id from the 2-legged token.  Not providing the account
id will not limit the APIs you can access. Best is to provide both 2-legged and 3-legged tokens in the Authentication class with and the appropriate scopes so that
you can access all the APIs.


## Making API Requests

Making API requests is simple. You can access the various services provided by the ACC API by calling the appropriate method on the `ACC` class. The following code snippets shows a few common examples of making API calls with the library.

### Managing Projects

The `AccProjectsApi` provides methods to manage projects within Autodesk Construction Cloud (ACC), including creating new projects, fetching project details, and updating project information.

#### Get All Active Projects

Gets all projects that are active in the account.

```python
projects = acc.projects.get_all_active_projects()
```

#### Get Active Projects With Pagination

Gets all projects that are active in the account but limits the number of projects returned.

```python
projects = acc.projects.get_active_projects(filter_params={'limit': 10, 'offset': 0})
```

#### Get All Projects

Gets all projects in the account.

```python
projects = acc.projects.get_projects()
```

#### Get Limited Project Details

Get Projects and limit the metadata fields returned.
```python
projects = acc.projects.get_projects(filter_params={'fields':"accountId,name,jobNumber"})
print(projects[0])
```

#### Get Projects Filtered 

Here we show how to get active projects with a specific status, and limit the metadata fields returned.

```python
active_build_projects_params = {    
    'fields': 'name,jobNumber,type,status',    
    'filter[status]': 'active',
    'filterTextMatch': 'equals'
}
projects = acc.projects.get_projects(filter_params=active_build_projects_params)
```

#### Create a project

Creates a new project. You can create the project directly,
or clone it from a project template.

The project dictionary needs at least name and type fields defined,l and the 
name must be unique even among deleted projects since they are not actually deleted.

```python
test_project = {
        "jobNumber": "9999W",
        "name": "My unique project name",        
        "type": "Wall Construction",        
        "latitude": "34.7749",
        "longitude": "-125.4194",
        "timezone":"America/Chicago"
}
new_project = acc.projects.post_project(test_project)
```

#### Create a list of projects

```python
def get_active_projects():
  jobs_dict = get_active_jobs_from_your_db()
  
  # map project types to template ids
  template_mapping = {
    'ProjectType1': {'projectId': 'c506442f-0ba5-4d9d-9ff8-70e0b02935b1'},
    'ProjectType2': {'projectId': '38c0c641-d6ba-4772-873d-7740c5bdf8f1'},
    'ProjectType3': {'projectId': '5758b3a0-36a4-41e9-8143-8fde80419eb6'},
    'ProjectType4': {'projectId': '636cfcf8-cd99-4086-af74-4c7384653d40'}
  }
  for project in result:
    project['template'] = template_mapping.get(project['type'])
  
  return result

def create_projects(projects):
  if projects is None or len(projects) == 0:
    return
  for project in projects:
    project['id'] = acc.projects.post_project(project)        
  return projects

jobs = get_active_projects()
new_projects = create_projects(jobs)
```

### Managing Account Users

The `AccAccountUsersApi` provides comprehensive methods to manage users within your Autodesk Construction Cloud (ACC) account, including fetching user details, searching users, creating new users, bulk importing users, and updating user status or associations.

#### Get All Account Users

Retrieve a complete list of users associated with the account.

```python
users = acc.account_users.get_users()
print(users)
```

#### Get User by Email

Fetch details of a specific user using their email address.

```python
user_email = "user@example.com"
user = acc.account_users.get_user_by_email(user_email)
print(user)
```

#### Search Users by Name

Search for users within the account by their name.

```python
users_named_daniel = acc.account_users.get_users_search(name="Daniel")
print(users_named_daniel)
```

#### Create a Single User

Add a new user to the account by providing at least an email and a company ID.

```python
new_user = {
    "email": "newuser@example.com",
    "company_id": "company123"
}
created_user = acc.account_users.post_user(new_user)
print(created_user)
```

#### Bulk Import Users

Import multiple users at once by providing a list of user details.

```python
users_to_import = [
    {"email": "user1@example.com", "company_id": "company123"},
    {"email": "user2@example.com", "company_id": "company123"},
]
import_result = acc.account_users.post_users(users_to_import)
print(import_result)
```

#### Update User Status or Company Association

Modify an existing user's status or assign them to a different company.

```python
updated_user = acc.account_users.patch_user(
    user_email="existinguser@example.com",
    status="active",
    company_id="newcompany123"
)
print(updated_user)
```

### Managing Project Users

The `AccProjectUsersApi` provides extensive methods to manage users within your Autodesk Construction Cloud (ACC) projects, including retrieving user details, adding new users individually or in bulk, updating permissions, and removing users.

#### Get Users from a Project

Retrieve all or a filtered subset of users from a specific project.

```python
project_id = "your_project_uuid"
users = acc.project_users.get_users(project_id)
print(users)
```

To paginate through results or apply filters:

```python
filtered_users = acc.project_users.get_users(project_id, query_params={"limit": 50}, follow_pagination=True)
```

#### Get Detailed User Information

Fetch detailed information for a specific user in a project.

```python
user_info = acc.project_users.get_user(project_id="your_project_uuid", user_id="user_uuid")
print(user_info)
```

#### Add a Single User to a Project

Add a new user by specifying their email and product access.

```python
new_user = {
    "email": "user@example.com",
    "products": AccProjectUsersApi.productmember
}
created_user = acc.project_users.add_user(project_id="your_project_uuid", user=new_user)
print(created_user)
```

#### Import Users to a Project (Bulk)

Efficiently add multiple users at once. Provide a list of users with their email and desired products.

```python
bulk_users = [
    {"email": "user1@example.com", "products": AccProjectUsersApi.productmember},
    {"email": "user2@example.com", "products": AccProjectUsersApi.productadmin}
]

acc.project_users.import_users(project_id="your_project_uuid", users=bulk_users)
```

#### Update User Permissions

Update permissions or product access for a specific user.

```python
update_data = {"products": AccProjectUsersApi.productadmin}
updated_user = acc.project_users.patch(project_id="your_project_uuid", target_user_id="user_uuid", data=update_data)
print(updated_user)
```

#### Batch Update Users Across Multiple Projects

Apply product or permission updates to multiple users across several projects.

```python
projects = acc.projects.get_all_active_projects()
users = [
    {"email": "user@example.com", "products": AccProjectUsersApi.productadmin},
    {"email": "anotheruser@example.com", "products": AccProjectUsersApi.productmember}
]

acc.project_users.patch_project_users(projects=projects, users=users)
```

#### Delete a User from a Project

Remove an individual user from a specific project.

```python
acc.project_users.delete(project_id="your_project_uuid", target_user_id="user_uuid")
```

#### Bulk Delete Users from a Project

Remove multiple users by specifying their email addresses.

```python
users_to_remove = [
    {"email": "user1@example.com"},
    {"email": "user2@example.com"}
]

acc.project_users.delete_users(project_id="your_project_uuid", users=users_to_remove)
```


### Managing Forms

The `AccFormsApi` provides methods to interact with forms within Autodesk Construction Cloud (ACC), allowing users to retrieve, create, and modify form data.

#### Retrieve Forms

Fetch forms from a project with optional filtering and pagination.

```python
forms = acc.forms.get_forms(project_id="your_project_id", limit=10)
print(forms)
```

#### Retrieve Form Templates

Get available form templates for a project.

```python
templates = acc.forms.get_templates(project_id="your_project_id")
print(templates)
```

#### Get Forms from the Past 30 Days

Fetch forms created within the last 30 days.

```python
recent_forms = acc.forms.get_forms_for_past30(project_id="your_project_id")
print(recent_forms)
```

#### Create a New Form

Create a form based on a template.

```python
form_data = {"customValues": {"field1": "value1"}}
new_form = acc.forms.post_form(project_id="your_project_id", template_id="template_id", data=form_data)
print(new_form)
```

#### Update Form Details

Update existing form details.

```python
update_data = {"customValues": {"field1": "updated_value"}}
updated_form = acc.forms.patch_form(project_id="your_project_id", template_id="template_id", form_id="form_id", data=update_data)
print(updated_form)
```

#### Update Form Fields

Batch update form fields, both tabular and non-tabular.

```python
batch_data = {"customValues": {"field1": "new_value"}}
updated_fields = acc.forms.put_form(project_id="your_project_id", form_id="form_id", data=batch_data)
print(updated_fields)
```

### Using the Sheets API

The `AccSheetsApi` class provides methods to manage sheets, version sets, uploads, exports, and collections within Autodesk Construction Cloud (ACC). 
Ensure your `Authentication` instance has a 3-legged token with scopes `data:read` and `data:write` to use these methods.

Below are the main functionalities, along with usage examples:

#### Managing Version Sets

Version sets group sheets by their issuance date.

**Create a Version Set**

```python
from datetime import datetime
version_set = acc.sheets.create_version_set(
    project_id="your_project_id",
    issuance_date="2024-03-25",
    name="Version Set 1"
)
```

**Get All Version Sets**

```python
version_sets = acc.sheets.get_version_sets(project_id="your_project_id")
```

**Update a Version Set**

```python
acc.sheets.patch_version_set(
    project_id="your_project_id",
    version_set_id="version_set_id",
    issuance_date="2024-03-26",
    name="Updated Version Set"
)
```

**Delete a Version Set**

```python
acc.sheets.delete_version_set(
    project_id="your_project_id",
    version_set_id="version_set_id"
)
```

#### Uploading Sheets

Upload sheets to Autodesk using Object Storage Service (OSS).

**Upload PDF to Autodesk**

```python
bucket_key, object_key = acc.sheets.upload_file_to_autodesk("project_id", "sheet.pdf")
signed_url_info = acc.sheets.get_signed_s3_upload(bucket_key, object_key)
status_code = acc.sheets.upload_pdf_to_signed_url(signed_url_info["url"], "path/to/sheet.pdf")
upload_response = acc.sheets.complete_s3_upload(bucket_key, object_key, signed_url_info["uploadKey"])
```

#### Managing Sheets

**Retrieve Sheets**

```python
sheets = acc.sheets.get_sheets(project_id="your_project_id", follow_pagination=True)
```

**Batch Update Sheets**

```python
updated_sheets = acc.sheets.batch_update_sheets(
    project_id="your_project_id",
    ids=["sheet_id_1", "sheet_id_2"],
    updates={"versionSetId": "new_version_set_id"}
)
```

**Batch Delete Sheets**

```python
acc.sheets.batch_delete_sheets(
    project_id="your_project_id",
    ids=["sheet_id_1", "sheet_id_2"]
)
```

#### Exporting Sheets

Export sheets as PDF files.

**Create Export Job**

```python
export_job = acc.sheets.export_sheets(
    project_id="your_project_id",
    options={"outputFileName": "sheets_export.pdf"},
    sheets=["sheet_id_1", "sheet_id_2"]
)
```

**Check Export Status**

```python
export_status = acc.sheets.get_export_status(
    project_id="your_project_id",
    export_id=export_job["id"]
)
```

#### Managing Collections

Collections organize sheets within a project.

**Retrieve All Collections**

```python
collections = acc.sheets.get_collections(project_id="your_project_id", follow_pagination=True)
```

**Retrieve a Specific Collection**

```python
collection = acc.sheets.get_collection(
    project_id="your_project_id",
    collection_id="collection_id"
)
```

## Required Scopes and Token Types

The scopes and token types needed by API:

- AccProjectUsersApi
    - Requires the `data:read` scope for GET and `data:write` scope for POST and PATCH
    - Requires either a 2-legged or 3-legged token
- AccProjectsApi
    - Requires the `account:read` scope for GET and `account:write` scope for POST and PATCH
    - Requires either a 2-legged or 3-legged token
- AccSheetsApi
    - Requires the `data:read` and `data:write` scopes
    - Requires a 3-legged token
- AccDataManagementApi
    - Requires the `data:read` and `data:write` scopes
- AccBusinessUnitsApi
    - Requires the `account:read` and `account:write` scopes
    - Requires either a 2-legged token
- AccCompaniesApi 
    - Requires the `account:read` and `account:write` scopes
    - Requires a 2-legged token for POST and PATCH requests, and a 2 or 3-legged token for GET requests.
- AccFormsApi 
    - Requires the `data:read` and `data:write` scopes and a 3-legged token
    - Requires a 3-legged token
- AccAccountUsersApi
    - Requires the `account:read` and `account:write` scopes
- AccSheetsApi
    - Requires the `data:read` and `data:write` scopes
    - Requires a 3-legged token
- AccUserProfileApi
    - Requires the `user-profile:read` scope
    - Requires a 3-legged token

