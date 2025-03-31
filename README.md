# AccSdk - Autodesk Construction Cloud Software Development Kit

[![PyPI version](https://badge.fury.io/py/acc_sdk.svg)](https://badge.fury.io/py/acc_sdk)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Introduction

The Autodesk Construction Cloud SDK, AccSdk, is a software development kit for Python that helps developers
create applications that leverage the [Autodesk Construction Cloud API](https://aps.autodesk.com/developer/overview/autodesk-construction-cloud).
This SDK grew out of my company's need to automate certain aspects of ACC that are not currently supported by the
[ACC web application](https://acc.autodesk.com/).

Autodesk publishes and maintains an extensive collection of APIs that allow you to automate and integrate across all of their platform
products, ACC being one of their newer offerings. The official documentation for the ACC API can be found at
[Autodesk Construction Cloud API](https://aps.autodesk.com/developer/overview/autodesk-construction-cloud). This package
also supports a subset of the [Data Management API](https://aps.autodesk.com/developer/overview/data-management-api),
which provides access to the data stored in the ACC Files module. Please refer to the original documentation for extensive details
on the API endpoints and their usage.

This package is not an official Autodesk product, but rather a community-driven effort to provide an alternative
interface to the ACC API. Specifically, I've used this package to automate setting up hundreds of jobs and users in
ACC when the company I work for first adopted the platform. We also use this package on an ongoing basis to automate adding
new hires and managing bulk user updates to large numbers of projects. For instance, when someone gets promoted, we upgrade
their project level permissions and possibly add them to a larger subset of the overall projects. I've also used this package in an automation script
that creates new projects in ACC as new projects get created in an adjacent ERP application. There are many more uses. Feel free to contribute to the project
by adding more services or features, and/or sending me a message if you have any questions or suggestions for future enhancements.

## Features

Acc_sdk currently implements the following Autodesk Construction Cloud APIs:

- The Account Users API allows you to add and update groups of users to your account.
- The Authentication API provides methods to authenticate with the ACC using the OAuth2 2-legged and/or the 3-legged flows.
 This class also maintains the validity of the Bearer tokens by refreshing the tokens as they expire, and manages both
 2-legged and 3-legged tokens at the same time to give you full access to the API services.
- The Business Units API allows you to create, update, or get business units in your account.
- The Companies API provides methods to manage companies, such as adding and updating companies.
- The Data Management API allows you to manage files and folders in the project. You can upload, download, and
 delete files, create folders, and move files between folders. The API also provides access to the data stored
 in the ACC Data Management module.
- The Forms API provides methods to securely create forms from a template, fill out, modify, and retrieve form data.
- The Project Users API provides methods to manage project users, such as adding, updating, deleting, and patching permissions for users on a project.
- The Projects API provides methods to create, read, update, and delete projects.
- The Sheets API provides methods to manage sheets and version sets, as well as uploading, publishing, and exporting sheets as PDFs.
- The User Profile API provides a method for gathering profile information from the logged-in user.
- The Photos API provides methods to retrieve and search for photos.

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
- The Relationships API
- The RFIs API (beta)
- The Submittals API
- The Takeoff API

## Installation

```bash
pip install acc_sdk
poetry install
```

## Usage

### Authentication

The first step in using the AccSdk, you need to create an instance of the `ACC` class. The `ACC` class provides access to the various
services provided by the ACC API.  However, first you need to authenticate with the ACC API.

The AccSdk Authentication module implements methods to use the the OAuth2 2-legged and 3-legged authentication processes, and it
manages the tokens and their liftimes. The Authentication module class provides the necessary methods to

- Authenticate with the ACC API using
  - 2 legged OAuth Client Credential flow
  - 3 legged OAuth Authorization Code flow
- Maintain the validity of tokens, by refreshing them as they expire
- Manage both 2-legged and 3-legged tokens concurrently to give you full access to the API services
- Revoke tokens
- Introspect tokens to check their validity
- Logout of the 3-legged session
- Get the user profile of the 3-legged token holder
- Get the OpenID Connect Discovery Document
- Get the APIs supported scopes

The initialization of the `Authentication` class requires the following parameters:

- `session`: A Flask session or a Python dictionary that is used to store the tokens and other session-related data.
- `client_id`: The Client ID of your application. This is provided by Autodesk when you register your application.  
- `client_secret`: The client secret of your application. This is also provided by Autodesk when you register your application. Optional if you are using PKCE.
- `admin_email`: The email address of the token holder user. Optional for 2-legged. Used for user_impersonation.
- `callback_url`: The callback URL that Autodesk will redirect to after the user has authenticated. Required for the 3-legged flow.
- `login_url`: The login URL for the 3-legged flow. This is the URL that Autodesk will redirect to after the user has authenticated. Optional.

The following code snippet shows how to authenticate with the ACC API using the 2 legged client credential flow.

```python
import os
from accapi import Authentication # Authentication Module for managing the authentication process and tokens
from accapi import Acc

from dotenv import load_dotenv # for optionally loading environment variables from .env file
load_dotenv()

# Load your environment variables
ACCOUNT_ID = os.environ.get('AUTODESK_ACCOUNT_ID')
CLIENT_ID =  os.environ.get('AUTODESK_CLIENT_ID_WEB_APP'),
CLIENT_SECRET =  os.environ.get('AUTODESK_CLIENT_SECRET_WEB_APP')
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")


auth_client = Authentication( session={}, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, admin_email="youremail@adomain.com")  

# Define the scopes you want your token holder to have, 

scopes = [
            "user-profile:read",
            "viewables:read",
            "data:read",
            "data:write",
            "account:read",
            "account:write"
            ] 

# Optionaly query the OpenID Connect Discovery Document to get the API's supported scopes
scopes = auth_client.get_oidc_spec()
scopes = [scope for scope in scopes if scope.startswith("data") or scope.startswith("account") or scope.startswith("user-profile")]

# Request the 2 legged token
auth_client.request_2legged_token(scopes=scopes)
assert auth_client._session["accapi_2legged"]
```

The following code snippet shows a simplified example on how to authenticate using the 3 legged authorization code flow.

```python
import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from accapi import Authentication, Acc
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SESSION_KEY") 
CLIENT_ID = os.environ.get("AUTODESK_CLIENT_ID_WEB_APP")
CLIENT_SECRET = os.environ.get("AUTODESK_CLIENT_SECRET_WEB_APP")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
CALLBACK_URL = "http://127.0.0.1:5000/callback"
ACCOUNT_ID = os.environ.get("AUTODESK_ACCOUNT_ID")
SCOPES = [ "user-profile:read","user:read","user:write","viewables:read","data:read","data:write","data:create","account:read","account:write"]

@app.route("/", methods=["GET"])
def index():    
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """
    Called from form submission on index.html. Initiates OAuth2 flow.
    Redirects to callback URL if successful, or an error message if not.
    """
    email = request.form.get("email")
    session["user_email"] = email
    auth = Authentication(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, session["user_email"], CALLBACK_URL)
    
    authorization_url = auth.get_authorization_url(scopes=SCOPES)
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    """
    Second step in the OAuth2 flow. Exchanges auth code for access token.
    Redirects to dashboard if successful, or an error message if not.
    """
    code = request.args.get("code")
    if not code:
        return "No authorization code received.", 400

    # Rebuild the Authentication object from the session to retain the same user context 
    auth = Authentication(session,CLIENT_ID,CLIENT_SECRET, session["user_email"], CALLBACK_URL)

    # Exchange the code for an access token
    token_data = auth.request_authcode_access_token(code=code, scopes=SCOPES)
    if not token_data:
        return "Failed to exchange code for token", 400

    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """ Final destination of 3 legged Authenticatin flow. """
    
    # Rebuild the Authentication object from the session to retain the same user context 
    auth = Authentication(session,CLIENT_ID,CLIENT_SECRET, session["user_email"], CALLBACK_URL)

    # Build an ACC instance (accapi) with the user's authentication context
    acc = Acc(auth_client=auth, account_id=ACCOUNT_ID)
    return render_template("dashboard.html")

def run():
    app.run(debug=True)
    
if __name__ == "__main__":
    run()

```

### Initialization

Once you have authenticated with the ACC API, you can create an instance of the `ACC` class. The `ACC` class provides access to the various services provided by the ACC API. The account id is an optional argument. If you do not provide the account id, the class will attempt to get the Account Id from the 2-legged token.  Not providing the account id will not limit the services you can access if you have both the 2-legged and 3-legged tokens and the appropriate scopes.

```python
from accapi import Acc
acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)
```

The account id is an optional argument. If you do not provide the account id, the class will attempt to get the Account Id from the 2-legged token.  Not providing the account
id will not limit the APIs you can access. Best is to provide both 2-legged and 3-legged tokens in the Authentication class with and the appropriate scopes so that
you can access all the APIs.

## Making API Requests

Making API requests is simple. You can access the various services provided by the ACC API by calling the appropriate method on the `ACC` class. The following code snippets shows a few common examples of making API calls with the library.

### Using the Photos API

The `AccPhotosApi` class provides methods to interact with photos and media in Autodesk Construction Cloud (ACC).
This API requires a 3-legged token with the `data:read` scope.

#### Get a Single Photo

Retrieve details of a specific photo or video from a project.

```python
# Get basic photo information
photo = acc.photos.get_photo(
    project_id="your_project_id",
    photo_id="your_photo_id"
)
print(f"Photo title: {photo['title']}")
print(f"Description: {photo['description']}")

# Get photo with signed URLs for direct access
photo = acc.photos.get_photo(
    project_id="your_project_id",
    photo_id="your_photo_id",
    include=["signedUrls"]
)
print(f"File URL: {photo['signedUrls']['fileUrl']}")
print(f"Thumbnail URL: {photo['signedUrls']['thumbnailUrl']}")
```

#### Get Filtered Photos

Retrieve a filtered list of photos from a project with various filtering options and pagination support.

```python
# Get all photos with pagination
photos = acc.photos.get_filtered_photos(
    project_id="your_project_id",
    filter_params={
        "limit": 50,
        "offset": 0,
        "sortBy": "createdAt",
        "sortOrder": "desc"
    },
    follow_pagination=True  # Get all results
)

# Get photos with specific filters
photos = acc.photos.get_filtered_photos(
    project_id="your_project_id",
    filter_params={
        "mediaType": ["NORMAL", "VIDEO"],
        "type": ["FIELD-REPORT", "ISSUE"],
        "isPublic": True,
        "takenAt": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-03-20T23:59:59Z"
        }
    },
    include=["signedUrls"]
)
```

The `get_filtered_photos` method supports various filter parameters:
- `limit` and `offset` for pagination
- `sortBy` and `sortOrder` for sorting results
- `mediaType` to filter by type (NORMAL, INFRARED, PHOTOSPHERE, VIDEO)
- `type` to filter by object type
- `createdBy` to filter by creator
- Date range filters for `takenAt`, `createdAt`, and `updatedAt`
- `isPublic` and `locked` status filters

The response includes:
- `data`: List of photo objects with details like title, description, media type, creation date, etc.
- `meta`: Metadata including total count and pagination information
- Optional `signedUrls` for direct access to media files

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

### Using the User Profile API

The `AccUserProfileApi` class provides methods to retrieve information about the authenticated user in Autodesk Construction Cloud (ACC).
This API requires a 3-legged token with the `user-profile:read` scope.

#### Get User Information

Retrieve basic information about the authenticated user.

```python
user_info = acc.user_profile.get_user_info()
print(user_info)
```

The response includes details such as:

- User ID
- Email address
- Name
- Preferred language
- Picture URL
- Other OpenID Connect standard claims

### Using the Business Units API

The `AccBusinessUnitsApi` class provides methods to manage business units within your Autodesk Construction Cloud (ACC) account.
This API requires a 2-legged token with the `account:read` and `account:write` scopes.

#### Get All Business Units

Retrieve all business units in your account.

```python
business_units = acc.business_units.get_business_units()
print(business_units)
```

#### Get Business Unit by ID

Fetch details of a specific business unit using its ID.

```python
business_unit = acc.business_units.get_business_unit(business_unit_id="your_business_unit_id")
print(business_unit)
```

#### Create a Business Unit

Create a new business unit in your account.

```python
new_business_unit = {
    "name": "New Business Unit",
    "description": "Description of the business unit"
}
created_unit = acc.business_units.post_business_unit(new_business_unit)
print(created_unit)
```

#### Update a Business Unit

Modify an existing business unit's details.

```python
update_data = {
    "name": "Updated Business Unit Name",
    "description": "Updated description"
}
updated_unit = acc.business_units.patch_business_unit(
    business_unit_id="your_business_unit_id",
    data=update_data
)
print(updated_unit)
```

### Using the Companies API

The `AccCompaniesApi` class provides methods to manage companies within your Autodesk Construction Cloud (ACC) account.
This API requires a 2-legged token with the `account:read` scope for GET requests and `account:write` scope for POST and PATCH requests.

#### Get All Companies

Retrieve a list of companies in your account with optional filtering and pagination.

```python
# Get all companies with default pagination (20 items per page)
companies = acc.companies.get_companies()

# Get companies with custom filters
filtered_companies = acc.companies.get_companies(
    filter_name="Construction Co",
    filter_trade="Concrete",
    limit=50,
    offset=0
)
```

#### Get Company by ID

Fetch details of a specific company using its ID.

```python
company = acc.companies.get_company(company_id="your_company_id")
print(company)
```

#### Update Company Details

Modify an existing company's information.

```python
update_data = {
    "name": "Updated Company Name",
    "trade": "Concrete",
    "phone": "(503)623-1525"
}
updated_company = acc.companies.update_company(
    account_id="your_account_id",
    company_id="your_company_id",
    data=update_data
)
print(updated_company)
```

#### Update Company Image

Upload or update a company's logo or image.

```python
# Update company image with auto-detected MIME type
updated_company = acc.companies.update_company_image(
    account_id="your_account_id",
    company_id="your_company_id",
    file_path="path/to/company_logo.png"
)

# Update company image with specific MIME type
updated_company = acc.companies.update_company_image(
    account_id="your_account_id",
    company_id="your_company_id",
    file_path="path/to/company_logo.png",
    mime_type="image/png"
)
```

### Using the Authentication API

The `Authentication` class provides comprehensive methods to manage authentication with the Autodesk Construction Cloud (ACC) API. It supports both 2-legged and 3-legged OAuth flows, token management, and various authentication-related operations.

#### Initialize Authentication

Create a new instance of the Authentication client with your credentials.

```python
auth_client = Authentication(
    client_id="your_client_id",
    client_secret="your_client_secret",
    admin_email="admin@example.com",  # Optional, for 2-legged user impersonation
    session={},  # Flask session or dictionary to store tokens
    callback_url="http://your-app/callback",  # Required for 3-legged flow
    logout_url="http://your-app/logout"  # Optional, for logout redirect
)
```

#### 2-Legged Authentication

Obtain a client credentials token for server-to-server operations.

```python
scopes = [
    "data:read",
    "data:write",
    "account:read",
    "account:write"
]
token = auth_client.request_2legged_token(scopes=scopes)
```

#### 3-Legged Authentication

The 3-legged authentication process involves multiple steps:

1. First, generate the authorization URL that the user will visit:

```python
# Define the scopes needed for your application
scopes = [
    "user-profile:read",
    "data:read",
    "data:write",
    "account:read",
    "account:write"
]

# Get the authorization URL
auth_url = auth_client.get_authorization_url(scopes=scopes)
```

2. The user visits the authorization URL and authenticates with Autodesk. Upon successful authentication, Autodesk redirects the user to your callback URL with an authorization code.

3. In your callback handler, exchange the authorization code for access and refresh tokens:

```python
# Exchange the authorization code for tokens
token_data = auth_client.request_authcode_access_token(
    code=request.args.get("code"),  # The code from the callback
    scopes=scopes
)
```

4. When the access token expires, use the refresh token to obtain a new access token:

```python
# Refresh the token with optional subset of scopes
new_token = auth_client.request_private_refresh_token(
    scopes=["data:read", "data:write"]  # Optional subset of original scopes
)
```

For a complete example of implementing 3-legged authentication in a web application, see the Flask example in the Authentication section above.

#### Token Management

Manage and validate your authentication tokens.

```python
# Check if a token is valid
is_valid = auth_client.is_authorized("accapi_3legged")

# Get remaining time until token expiration
expires_in = auth_client.expires_in("accapi_3legged")

# Revoke a token
auth_client.revoke_private_token("accapi_3legged")

# Clear all tokens from session
auth_client.clear_all_tokens()
```

#### User Profile Information

Retrieve information about the authenticated user.

```python
# Get user profile information
user_info = auth_client.get_user_info()
print(user_info)
```

#### Token Types and Scopes

The Authentication class supports various token types and scopes:

- **2-Legged Tokens**: For server-to-server operations
- **3-Legged Tokens**: For user-specific operations
- **Public Tokens**: Without client secret (PKCE flow)
- **Private Tokens**: With client secret

Common scopes include:

- `user-profile:read`: Access user profile information
- `data:read` and `data:write`: Access project data
- `account:read` and `account:write`: Manage account settings
- `viewables:read`: Access viewable files

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
  - Requires a 2-legged token
- AccCompaniesApi
  - Requires the `account:read` and `account:write` scopes
  - Requires a 2-legged token for POST and PATCH requests, and a 2 or 3-legged token for GET requests
- AccFormsApi
  - Requires the `data:read` and `data:write` scopes
  - Requires a 3-legged token
- AccAccountUsersApi
  - Requires the `account:read` and `account:write` scopes
- AccSheetsApi
  - Requires the `data:read` and `data:write` scopes
  - Requires a 3-legged token
- AccUserProfileApi
  - Requires the `user-profile:read` scope
  - Requires a 3-legged token

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 Daniel Byrne

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
