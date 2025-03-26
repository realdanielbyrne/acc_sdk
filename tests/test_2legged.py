#%%
from acc_sdk import Acc, Authentication
import os
from flask import session
from urllib.parse import urlencode

ACCOUNT_ID = os.environ.get('AUTODESK_ACCOUNT_ID')
CLIENT_ID =  os.environ.get('AUTODESK_CLIENT_ID_WEB_APP')
CLIENT_SECRET =  os.environ.get('AUTODESK_CLIENT_SECRET_WEB_APP')
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
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

#%% get 2 legged token test
auth_client = Authentication(
    session={}, 
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, 
    admin_email=ADMIN_EMAIL
    )  

auth_client.request_2legged_token(scopes=scopes)
assert auth_client._session["accapi_2legged"]

#%%
acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)



#%%
companies = acc.companies.get_companies()
print(companies[:5])

#%% get_users test
users = acc.account_users.get_users()
print(users[:5])
assert users.__len__() > 0


#%% test values
test_email = "dbyrne@rpmxconstruction.com"
test_name="Daniel Byrne"
test_co="RPM xConstruction"

#%% get_user_by_email test
testuser = acc.account_users.get_user_by_email(test_email)
print(f"user: {testuser}")
assert testuser["email"] == test_email

# %% get_user_by_id test
testuserid = testuser["id"]

testuser = {}
testuser = acc.account_users.get_user_by_id(testuserid)
print(f"userid: {testuser["id"]}, testid: {testuserid}")
assert testuser["id"] == testuserid 

#%% get_users_search email test
test_user={}
users = acc.account_users.get_users_search(email=test_email)
testuser = users[0]
assert testuser["email"] == test_email
assert testuser["name"] == test_name
assert testuser["company_name"] == test_co

#%% get_users_search name test
test_user={}
users = acc.account_users.get_users_search(name=test_name)
testuser = users[0]
assert testuser["email"] == test_email
assert testuser["name"] == test_name
assert testuser["company_name"] == test_co

#%% get_users_search company_name test
test_user={}
users = acc.account_users.get_users_search(company_name=test_co)
testuser = users[0]
assert testuser["company_name"] == test_co


#%% get_projects test
projects = acc.projects.get_projects()
print(projects[:5])
assert projects.__len__() > 0


#%% get projects fields test
projects = acc.projects.get_projects(filter_params={'fields':"accountId,name,jobNumber"})
print(projects[0])
assert projects[0].keys().__len__() == 4

#%% get projects filter test
active_build_projects_params = {    
    'fields': 'name,jobNumber,type,status',    
    'filter[status]': 'active',
    'filterTextMatch': 'equals'
}
projects = acc.projects.get_projects(filter_params=active_build_projects_params)
assert projects[0].keys().__len__() == 5
assert projects[0]["status"] == "active"

# %% get_project by id test
test_project_id = "c9db5232-8c07-42a8-8b5e-974e3667a0e3"
test_project = acc.projects.get_project(test_project_id)
print(f"test_project['id']: {test_project['id']}")
assert test_project["id"] == test_project_id

#%% import project users test
from acc_sdk.project_users import AccProjectUsersApi
users = [
  {'email': 'ngrider@rpmxconstruction.com','products': AccProjectUsersApi.productadmin},
  {'email': 'rjames@rpmxconstruction.com','products': AccProjectUsersApi.productadmin},
]
acc.project_users.import_users(test_project_id,users)

# %% delete users from a project test
acc.project_users.delete_users(test_project_id,users)

#%% import project users test
from acc_sdk.project_users import AccProjectUsersApi
users = [
  {'email': 'ngrider@rpmxconstruction.com','products': AccProjectUsersApi.productadmin},
  {'email': 'rjames@rpmxconstruction.com','products': AccProjectUsersApi.productadmin},
]
acc.project_users.import_users(test_project_id,users)

