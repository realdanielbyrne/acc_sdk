# Data Connector API

The `AccDataConnectorApi` class provides methods to initiate and manage bulk data downloads from Autodesk Construction Cloud (ACC). This API allows you to create data extraction requests, manage extraction jobs, and download the resulting data files.
This API requires a 3-legged token with the `data:read` and `data:write` scopes.

## Create a Data Request

Create a new data extraction request specifying which projects and service groups to include.

```python
# Create a one-time data extraction request
request_data = {
    "description": "My Data Extract",
    "isActive": True,
    "scheduleInterval": "ONE_TIME",
    "effectiveFrom": "2023-06-06T00:00:00.000Z",
    "serviceGroups": ["admin", "issues"],
    "projectIdList": ["project_uuid1", "project_uuid2"]
}
data_request = acc.data_connector.post_request(data=request_data)

# Create a recurring data extraction request
recurring_request = {
    "description": "Weekly Data Extract",
    "isActive": True,
    "scheduleInterval": "WEEKLY",
    "effectiveFrom": "2023-06-06T00:00:00.000Z",
    "serviceGroups": ["admin", "issues", "photos"],
    "projectIdList": ["project_uuid1", "project_uuid2"],
    "sendEmail": True
}
data_request = acc.data_connector.post_request(data=recurring_request)
```

The `post_request` method supports various parameters:

- `description`: A description of the data request
- `isActive`: Whether the request is active
- `scheduleInterval`: Frequency of extraction (ONE_TIME, DAILY, WEEKLY, MONTHLY)
- `effectiveFrom`: Start date for the request
- `serviceGroups`: List of service groups to include (admin, issues, photos, etc.)
- `projectIdList`: List of project IDs to include (up to 50)
- `sendEmail`: Whether to send notification emails

## Get Data Requests

Retrieve data requests with optional filtering and pagination.

```python
# Get all data requests
requests = acc.data_connector.get_requests()

# Get requests with pagination and sorting
requests = acc.data_connector.get_requests(
    limit=10,
    offset=0,
    sort="desc",
    sort_fields="createdAt,-updatedAt"
)

# Get requests with filtering
requests = acc.data_connector.get_requests(
    projectId="project_uuid",
    isActive=True,
    scheduleInterval="ONE_TIME"
)

# Get requests with date range filtering
requests = acc.data_connector.get_requests(
    createdAt="2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z"
)
```

## Get a Specific Data Request

Retrieve details of a specific data request by ID.

```python
request = acc.data_connector.get_request(request_id="request_uuid")
print(f"Request description: {request['description']}")
print(f"Service groups: {', '.join(request['serviceGroups'])}")
```

## Update a Data Request

Modify an existing data request's attributes.

```python
update_data = {
    "description": "Updated Data Extract",
    "isActive": False,
    "serviceGroups": ["admin", "issues", "photos"]
}
updated_request = acc.data_connector.patch_request(
    request_id="request_uuid",
    data=update_data
)
```

## Delete a Data Request

Remove a data request that is no longer needed.

```python
success = acc.data_connector.delete_request(request_id="request_uuid")
if success:
    print("Request successfully deleted")
```

## Get Extraction Jobs

Retrieve information about data extraction jobs with optional filtering.

```python
# Get all jobs
jobs = acc.data_connector.get_jobs()

# Get jobs for a specific project
jobs = acc.data_connector.get_jobs(project_id="project_uuid")

# Get jobs with pagination, sorting, and filtering
jobs = acc.data_connector.get_jobs(
    limit=10,
    offset=0,
    sort="desc",
    sort_fields="createdAt,-completedAt",
    status="complete",
    completionStatus="success"
)

# Get jobs with date range filtering
jobs = acc.data_connector.get_jobs(
    createdAt="2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z"
)
```

## Get Jobs for a Specific Request

Retrieve all jobs associated with a particular data request.

```python
# Get all jobs for a specific request
jobs = acc.data_connector.get_jobs_by_request(
    request_id="request_uuid"
)

# Get jobs with pagination and sorting
jobs = acc.data_connector.get_jobs_by_request(
    request_id="request_uuid",
    limit=10,
    offset=0,
    sort="desc"
)
```

## Get a Specific Job

Retrieve details of a specific extraction job by ID.

```python
job = acc.data_connector.get_job(job_id="job_uuid")
print(f"Job status: {job['status']}")
print(f"Completion status: {job['completionStatus']}")
```

## Download Extracted Data

Get a signed URL for downloading a specific file from a job's data extract.

```python
# Get a signed URL for downloading a specific file
file_info = acc.data_connector.get_job_data(
    job_id="job_uuid",
    file_name="admin_companies.csv"
)
print(f"File: {file_info['name']}, Size: {file_info['size']} bytes")
print(f"Download URL (valid for 60 seconds): {file_info['signedUrl']}")

# To download the file using the signed URL:
import requests
response = requests.get(file_info['signedUrl'])
with open(file_info['name'], 'wb') as f:
    f.write(response.content)
```
