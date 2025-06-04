# %%
import os

from acc_sdk import Acc, Authentication
from acc_sdk.project_users import AccProjectUsersApi

ACCOUNT_ID = os.environ.get("AUTODESK_ACCOUNT_ID")
CLIENT_ID = os.environ.get("AUTODESK_CLIENT_ID_WEB_APP")
CLIENT_SECRET = os.environ.get("AUTODESK_CLIENT_SECRET_WEB_APP")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

TEST_EMAIL = os.environ.get("TEST_EMAIL", "dbyrne@rpmxconstruction.com")
TEST_NAME = os.environ.get("TEST_NAME", "Daniel Byrne")
TEST_CO = os.environ.get("TEST_CO", "RPM xConstruction")
TEST_PROJECT_ID = os.environ.get(
    "TEST_PROJECT_ID", "159e6860-d922-471a-96bc-732e6899c82f"
)

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
    "account:write",
]

def test_2legged_integration_test():
    # %% get 2 legged token test
    auth_client = Authentication(
        session={},
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        admin_email=ADMIN_EMAIL,
    )

    auth_client.request_2legged_token(scopes=scopes)
    assert auth_client._session["accapi_2legged"]

    # %%
    acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)

    ############################################
    # Companies
    ############################################
    # %%
    companies = acc.companies.get_companies()
    print(companies[:5])

    ############################################
    # Account Users
    ############################################
    # %% get_users test
    users = acc.account_users.get_users()
    print(users[:5])
    assert users.__len__() > 0

    # %% test values
    test_email = TEST_EMAIL
    test_name = TEST_NAME
    test_co = TEST_CO

    # %% get_user_by_email test
    testuser = acc.account_users.get_user_by_email(test_email)
    print(f"user: {testuser}")
    assert testuser is not None
    assert testuser["email"] == test_email

    # %% get_user_by_id test
    testuserid = testuser["id"]

    testuser = {}
    testuser = acc.account_users.get_user_by_id(testuserid)
    print(f"userid: {testuser['id']}, testid: {testuserid}")
    assert testuser["id"] == testuserid

    # %% get_users_search email test
    test_user = {}
    users = acc.account_users.get_users_search(email=test_email)
    testuser = users[0]
    assert testuser["email"] == test_email
    assert testuser["name"] == test_name
    assert testuser["company_name"] == test_co

    # %% get_users_search name test
    test_user = {}
    users = acc.account_users.get_users_search(name=test_name)
    testuser = users[0]
    assert testuser["email"] == test_email
    assert testuser["name"] == test_name
    assert testuser["company_name"] == test_co

    # %% get_users_search company_name test
    test_user = {}
    users = acc.account_users.get_users_search(company_name=test_co)
    testuser = users[0]
    assert testuser["company_name"] == test_co

    ############################################
    # Projects
    ############################################
    # %% get_projects test
    projects = acc.projects.get_projects()
    print(projects[:5])
    assert projects.__len__() > 0

    # %% get projects fields test
    projects = acc.projects.get_projects(
        filter_params={"fields": "accountId,name,jobNumber"}
    )
    print(projects[0])
    assert projects[0].keys().__len__() == 4

    # %% get projects filter test
    active_build_projects_params = {
        "fields": "name,jobNumber,type,status",
        "filter[status]": "active",
        "filterTextMatch": "equals",
    }
    projects = acc.projects.get_projects(filter_params=active_build_projects_params)
    assert projects[0].keys().__len__() == 5
    assert projects[0]["status"] == "active"

    # %% get_project by id test
    test_project = acc.projects.get_project(TEST_PROJECT_ID)
    print(f"test_project['id']: {test_project['id']}")
    assert test_project["id"] == TEST_PROJECT_ID

    ############################################
    # Project Users
    ############################################
    # %% import project users test

    users = [
        {
            "email": TEST_EMAIL,
            "products": AccProjectUsersApi.productadmin,
        }
    ]
    retval = acc.project_users.post_import_users(TEST_PROJECT_ID, users)
    assert retval

    # %% get user by email test
    test_user = acc.project_users.get_user_by_email(
        project_id=TEST_PROJECT_ID, email=test_email
    )
    print(f"test_user['email']: {test_user['email']}")
    assert test_user["email"] == test_email

    # %% delete users from a project test
    ret = acc.project_users.delete_users(TEST_PROJECT_ID, users)
    assert ret
    test_user = acc.project_users.get_user_by_email(
        project_id=TEST_PROJECT_ID, email=test_email
    )
    assert test_user is None

    # %% add users to a project test
    user = acc.project_users.post_user(
        project_id=TEST_PROJECT_ID,
        user={"email": test_email, "products": AccProjectUsersApi.productmember},
    )
    assert user["email"] == test_email

    # %% patch project user test
    user = acc.project_users.patch_user(
        project_id=TEST_PROJECT_ID,
        user_email=test_email,
        data={"products": AccProjectUsersApi.productmember},
    )

    assert user["email"] == test_email
    assert user["products"] == AccProjectUsersApi.productmember
