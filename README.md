# AccSdk - Autodesk Construction Cloud Software Development Kit

The Autodesk Construction Cloud SDK, AccSdk, is a Python SDK that helps developers
create applications that leverage the [Autodesk Construction Cloud API](https://aps.autodesk.com/developer/overview/autodesk-construction-cloud).

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

AccSdk currently implements the following Autodesk Construction Cloud APIs:

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
- The Data Connector API provides methods to initiate and manage bulk data downloads which can then be used in analysis tools like PowerBI and Tableau.

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

## Basic Usage

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

Making API requests is simple. You can access the various services provided by the ACC API by calling the appropriate method on the `ACC` class. Detailed documentation for each API is available in separate files.

### API Documentation

For detailed usage instructions and examples, please refer to the following documentation files:

- [Authentication API](docs/authentication.md) - Authentication with OAuth 2.0 flows
- [Photos API](docs/photos_api.md) - Interact with photos and media
- [Projects API](docs/projects_api.md) - Manage projects
- [Account Users API](docs/account_users_api.md) - Manage account users
- [Project Users API](docs/project_users_api.md) - Manage project users
- [Forms API](docs/forms_api.md) - Work with forms and templates
- [Sheets API](docs/sheets_api.md) - Manage sheets, version sets, and collections
- [User Profile API](docs/user_profile_api.md) - Access user profile information
- [Business Units API](docs/business_units_api.md) - Manage business units
- [Companies API](docs/companies_api.md) - Manage companies
- [Data Connector API](docs/data_connector_api.md) - Bulk data extraction

## Required Scopes and Token Types

Each API requires specific scopes and token types. Below is a summary of the requirements:

| API | Required Scopes | Token Type |
|-----|----------------|------------|
| AccProjectUsersApi | `data:read` for GET, `data:write` for POST/PATCH | 2-legged or 3-legged |
| AccProjectsApi | `account:read` for GET, `account:write` for POST/PATCH | 2-legged or 3-legged |
| AccSheetsApi | `data:read`, `data:write` | 3-legged only |
| AccDataManagementApi | `data:read`, `data:write` | 2-legged or 3-legged |
| AccBusinessUnitsApi | `account:read`, `account:write` | 2-legged only |
| AccCompaniesApi | `account:read`, `account:write` | 2-legged for POST/PATCH, 2 or 3-legged for GET |
| AccFormsApi | `data:read`, `data:write` | 3-legged only |
| AccAccountUsersApi | `account:read`, `account:write` | 2-legged or 3-legged |
| AccUserProfileApi | `user-profile:read` | 3-legged only |
| AccPhotosApi | `data:read` | 3-legged only |
| AccDataConnectorApi | `data:read`, `data:write` | 3-legged only |

For more details on each API's requirements, refer to the individual documentation files.

## Running Unit Tests

If you have cloned this repository from GitHub, you can run the unit tests to ensure everything is working as expected. Note that the PyPI package does not include the `tests` directory, so this step is only applicable for the cloned repository.

### Prerequisites

- Ensure you have installed all dependencies by running:

```bash
poetry install
```

- Verify that you have Python installed (version 3.8 or higher is recommended).

### Running Tests

To run the unit tests, use the following command:

```bash
poetry run pytest tests/
```

This will execute all the test cases in the `tests` directory and provide a summary of the results.

### Running Specific Tests

If you want to run a specific test file, you can specify the path to the test file. For example:

```bash
poetry run pytest tests/test_account_users.py
```

### Viewing Detailed Test Output

To view detailed output during test execution, use the `-v` flag:

```bash
poetry run pytest -v tests/
```

### Running Tests with Coverage

To check the test coverage, you can use the `pytest-cov` plugin. Install it if not already installed:

```bash
poetry add --dev pytest-cov
```

Then run the tests with coverage:

```bash
poetry run pytest --cov=acc_sdk tests/
```

This will display a coverage report in the terminal.

## License

This project is licensed under the MIT License - see below for details:

```text
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
