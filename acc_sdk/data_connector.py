import requests
from .base import AccBase


class AccDataConnectorApi:
    """
    This class provides methods to initiate and manage bulk data downloads from Autodesk Construction Cloud.

    Example:
        ```python
        from accapi import Acc
        acc = Acc(auth_client=auth_client, account_id=ACCOUNT_ID)

        # Create a data request
        request_data = {
            "description": "My Data Extract",
            "isActive": True,
            "scheduleInterval": "ONE_TIME",
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "serviceGroups": ["admin", "issues"],
            "projectIdList": ["project_uuid1", "project_uuid2"]
        }
        data_request = acc.data_connector.post_request(account_id="account_uuid", data=request_data)
        ```
    """

    def __init__(self, base: AccBase):
        self.base = base
        self.base_address = "https://developer.api.autodesk.com/data-connector/v1"

    ###########################################################################
    # Requests
    ###########################################################################

    def delete_request(self, account_id=None, request_id=None):
        """
        Deletes the specified data request created earlier by the authenticated user.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-requestId-DELETE/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            request_id (str): The ID of the data request to delete.

        Returns:
            bool: True if the request was successfully deleted.

        Example:
            ```python
            # Delete a specific data request by ID
            success = acc.data_connector.delete_request(request_id="ce9bc188-1e18-11eb-adc1-0242ac120002")
            if success:
                print("Request successfully deleted")
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not request_id:
            raise Exception("Request ID is required")

        url = f"{self.base_address}/accounts/{account_id}/requests/{request_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            return True
        else:
            response.raise_for_status()

    def get_request(self, account_id=None, request_id=None):
        """
        Returns information about a specified data request created earlier by the authenticated user.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-requestId-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            request_id (str): The ID of the data request to retrieve.

        Returns:
            dict: The data request object with detailed information.

        Example:
            ```python
            # Get a specific data request by ID
            request = acc.data_connector.get_request(request_id="ce9bc188-1e18-11eb-adc1-0242ac120002")
            print(f"Request description: {request['description']}")
            print(f"Service groups: {', '.join(request['serviceGroups'])}")
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not request_id:
            raise Exception("Request ID is required")

        url = f"{self.base_address}/accounts/{account_id}/requests/{request_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_requests(
        self,
        account_id=None,
        sort=None,
        limit=20,
        offset=0,
        sort_fields=None,
        **filters,
    ):
        """
        Returns an array of data requests that the authenticated user has created in the specified account.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            sort (str, optional): The sort order of returned data connector objects.
                Possible values: "asc" (earliest to latest date), "desc" (latest to earliest date).
            limit (int, optional): The number of data connector objects to return. Default: 20.
            offset (int, optional): The number of data objects to skip. Default: 0.
            sort_fields (str, optional): Comma-separated names of fields by which to sort the returned data requests.
                Prepend any field with a hyphen (-) to sort in descending order.
                Possible values: isActive, accountId, createdBy, createdByEmail, createdAt, updatedBy,
                updatedAt, scheduleInterval, reoccuringInterval, effectiveFrom, effectiveTo, startDate, endDate.
            **filters: Additional filters to apply to the request. Use the format filter_field=value.
                Possible filter fields: projectId, createdAt, updatedAt, scheduleInterval, reocurringInterval,
                effectiveFrom, effectiveTo, isActive, startDate, endDate.
                For date ranges, use the format "2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z".

        Returns:
            dict: A dictionary containing pagination information and an array of data request objects.

        Example:
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
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        url = f"{self.base_address}/accounts/{account_id}/requests"

        # Build query parameters
        params = {}

        if sort:
            params["sort"] = sort

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        if sort_fields:
            params["sortFields"] = sort_fields

        # Add filters
        for key, value in filters.items():
            params[f"filter[{key}]"] = value

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def post_request(self, account_id=None, data=None):
        """
        Creates a data request for an authenticated user. The user can optionally limit the request to one project.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-POST/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            data (dict): The data request object. Required fields vary based on scheduleInterval.
                For ONE_TIME requests:
                - description (str, optional): User-entered description
                - isActive (bool, optional): Request active status (default: true)
                - scheduleInterval (str): Must be "ONE_TIME"
                - effectiveFrom (str): ISO 8601 datetime when job execution begins
                - serviceGroups (list[str]): Service groups to extract data from
                - projectId (str, optional): Legacy single project ID
                - projectIdList (list[str], optional): List of up to 50 project IDs
                - callbackUrl (str, optional): URL to call when job completes
                - sendEmail (bool, optional): Send notification email (default: true)
                - startDate (str, optional): ISO 8601 start date for data extraction
                - endDate (str, optional): ISO 8601 end date for data extraction
                - dateRange (str, optional): Timeframe for data extraction
                - projectStatus (str, optional): Types of projects to include (default: "all")

                For recurring requests (DAY, WEEK, MONTH, YEAR):
                - All ONE_TIME fields plus:
                - reoccuringInterval (int): Number of interval units between jobs
                - effectiveTo (str): ISO 8601 datetime when schedule ends

        Returns:
            dict: The created data request object.

        Example:
            ```python
            # Create a one-time data request
            one_time_request = {
                "description": "My Company Data Extract",
                "isActive": True,
                "scheduleInterval": "ONE_TIME",
                "effectiveFrom": "2023-06-06T00:00:00.000Z",
                "serviceGroups": ["admin", "issues"],
                "projectIdList": ["project_uuid1", "project_uuid2"],
                "callbackUrl": "https://api.mycompany.com/autodesk/jobinfo",
                "sendEmail": True,
                "startDate": "2023-06-06T00:00:00.000Z",
                "endDate": "2023-06-06T12:00:00.000Z"
            }
            request = acc.data_connector.post_request(data=one_time_request)

            # Create a recurring data request
            recurring_request = {
                "description": "Weekly Data Extract",
                "scheduleInterval": "WEEK",
                "reoccuringInterval": 2,
                "effectiveFrom": "2023-06-06T00:00:00.000Z",
                "effectiveTo": "2023-12-31T23:59:59.999Z",
                "serviceGroups": ["all"],
                "projectStatus": "active"
            }
            request = acc.data_connector.post_request(data=recurring_request)
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not data:
            raise Exception("Request data is required")

        # Validate required fields based on scheduleInterval
        if "scheduleInterval" not in data:
            raise Exception("scheduleInterval is required")

        if "effectiveFrom" not in data:
            raise Exception("effectiveFrom is required")

        if "serviceGroups" not in data or not data["serviceGroups"]:
            raise Exception("At least one service group is required")

        # Validate recurring schedule requirements
        if data["scheduleInterval"] != "ONE_TIME":
            if (
                "reoccuringInterval" not in data
                or not isinstance(data["reoccuringInterval"], int)
                or data["reoccuringInterval"] <= 0
            ):
                raise Exception(
                    "reoccuringInterval must be a positive integer for recurring schedules"
                )

            if "effectiveTo" not in data:
                raise Exception("effectiveTo is required for recurring schedules")

        url = f"{self.base_address}/accounts/{account_id}/requests"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()

    def patch_request(self, account_id=None, request_id=None, data=None):
        """
        Updates the attributes of an existing data request created earlier by the authenticated user.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-requestId-PATCH/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            request_id (str): The ID of the data request to update.
            data (dict): The data request attributes to update. Only specify the attributes you want to update.
                Possible attributes include:
                - isActive (bool): The request active status.
                - description (str): User-entered description.
                - scheduleInterval (str): ONE_TIME, DAY, WEEK, MONTH, or YEAR.
                - reoccuringInterval (int): Number of interval units between jobs.
                - effectiveFrom (str): ISO 8601 datetime when job execution begins.
                - effectiveTo (str): ISO 8601 datetime when schedule ends.
                - serviceGroups (list[str]): Service groups to extract data from.
                - callbackUrl (str): URL to call when job completes.
                - sendEmail (bool): Send notification email.
                - projectIdList (list[str]): List of up to 50 project IDs.
                - startDate (str): ISO 8601 start date for data extraction.
                - endDate (str): ISO 8601 end date for data extraction.
                - dateRange (str): Timeframe for data extraction.
                - projectStatus (str): Types of projects to include.

        Returns:
            dict: The updated data request object.

        Example:
            ```python
            # Update a data request
            update_data = {
                "description": "Updated Data Extract",
                "isActive": False,
                "serviceGroups": ["admin", "issues", "photos"]
            }
            updated_request = acc.data_connector.patch_request(
                request_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
                data=update_data
            )
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not request_id:
            raise Exception("Request ID is required")

        if not data:
            raise Exception("Update data is required")

        url = f"{self.base_address}/accounts/{account_id}/requests/{request_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
            "Content-Type": "application/json",
        }

        response = requests.patch(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    ###########################################################################
    # Jobs
    ###########################################################################

    def get_jobs(
        self,
        account_id=None,
        sort=None,
        limit=20,
        offset=0,
        project_id=None,
        sort_fields=None,
        **filters,
    ):
        """
        Returns an array of Data Connector jobs spawned by requests from the authenticated user.
        The user must have project administrator or executive overview permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-jobs-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            sort (str, optional): The sort order of returned data connector objects.
                Possible values: "asc" (earliest to latest date), "desc" (latest to earliest date).
            limit (int, optional): The number of data connector objects to return. Default: 20.
            offset (int, optional): The number of data objects to skip. Default: 0.
            project_id (str, optional): Project ID to filter the returned Data Connector objects.
            sort_fields (str, optional): Comma-separated names of fields by which to sort the returned jobs.
                Prepend any field with a hyphen (-) to sort in descending order.
                Possible values: projectId, createdBy, createdByEmail, createdAt, status,
                completionStatus, startedAt, completedAt, startDate, endDate.
            **filters: Additional filters to apply to the request. Use the format filter_field=value.
                Possible filter fields: projectId, createdAt, status, completionStatus,
                startedAt, completedAt, startDate, endDate.
                For date ranges, use the format "2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z".

        Returns:
            dict: A dictionary containing pagination information and an array of job objects.

        Example:
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
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        url = f"{self.base_address}/accounts/{account_id}/jobs"

        # Build query parameters
        params = {}

        if sort:
            params["sort"] = sort

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        if project_id:
            params["projectId"] = project_id

        if sort_fields:
            params["sortFields"] = sort_fields

        # Add filters
        for key, value in filters.items():
            params[f"filter[{key}]"] = value

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_job(self, account_id=None, job_id=None):
        """
        Returns information about a specified job that was spawned by a data request created by the authenticated user.
        The user must have project administrator or executive overview permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-jobs-jobId-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            job_id (str): The ID of the job to retrieve information for.

        Returns:
            dict: The job object with detailed information including ID, request ID, account ID, project ID,
                  creation details, status, completion status, progress, and date ranges.

        Example:
            ```python
            # Get a specific job by ID
            job = acc.data_connector.get_job(job_id="ce9bc188-1e18-11eb-adc1-0242ac120002")
            print(f"Job status: {job['status']}")
            print(f"Completion status: {job['completionStatus']}")
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not job_id:
            raise Exception("Job ID is required")

        url = f"{self.base_address}/accounts/{account_id}/jobs/{job_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def delete_job(self, account_id=None, job_id=None):
        """
        Cancels the specified running job spawned by a data request created by the authenticated user.
        The user must have project administrator or executive overview permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-jobs-jobId-DELETE/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            job_id (str): The ID of the job to cancel.

        Returns:
            bool: True if the job was successfully cancelled.

        Example:
            ```python
            # Cancel a running job by ID
            success = acc.data_connector.delete_job(job_id="ce9bc188-1e18-11eb-adc1-0242ac120002")
            if success:
                print("Job successfully cancelled")
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not job_id:
            raise Exception("Job ID is required")

        url = f"{self.base_address}/accounts/{account_id}/jobs/{job_id}"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            return True
        else:
            response.raise_for_status()

    def get_jobs_by_request(
        self, account_id=None, request_id=None, sort=None, limit=20, offset=0
    ):
        """
        Returns an array of data connector jobs associated with a request that was created by the authenticated user.
        The user must have project administrator or executive overview permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-requests-requestId-jobs-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            request_id (str): The ID of the data request to retrieve jobs for.
            sort (str, optional): The sort order of returned data connector objects.
                Possible values: "asc" (earliest to latest date), "desc" (latest to earliest date).
            limit (int, optional): The number of data connector objects to return. Default: 20.
            offset (int, optional): The number of data objects to skip. Default: 0.

        Returns:
            dict: A dictionary containing pagination information and an array of job objects.

        Example:
            ```python
            # Get all jobs for a specific request
            jobs = acc.data_connector.get_jobs_by_request(
                request_id="ce9bc188-1e18-11eb-adc1-0242ac120002"
            )

            # Get jobs with pagination and sorting
            jobs = acc.data_connector.get_jobs_by_request(
                request_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
                limit=10,
                offset=0,
                sort="desc"
            )
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not request_id:
            raise Exception("Request ID is required")

        url = f"{self.base_address}/accounts/{account_id}/requests/{request_id}/jobs"

        # Build query parameters
        params = {}

        if sort:
            params["sort"] = sort

        if limit is not None:
            params["limit"] = limit

        if offset is not None:
            params["offset"] = offset

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    ###########################################################################
    # Data
    ###########################################################################

    def get_job_data_listing(self, account_id=None, job_id=None):
        """
        Returns an array of information about the files contained within the data extract created by a specified job.
        The job must be spawned by a data request that was created by the authenticated user.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-jobs-jobId-data-listing-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            job_id (str): The ID of the job to retrieve data listing for.

        Returns:
            list: An array of file information objects, each containing name, createdAt, and size.

        Example:
            ```python
            # Get data listing for a specific job
            data_listing = acc.data_connector.get_job_data_listing(job_id="ce9bc188-1e18-11eb-adc1-0242ac120002")
            for file_info in data_listing:
                print(f"File: {file_info['name']}, Size: {file_info['size']} bytes, Created: {file_info['createdAt']}")
            ```
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not job_id:
            raise Exception("Job ID is required")

        url = f"{self.base_address}/accounts/{account_id}/jobs/{job_id}/data-listing"

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_job_data(self, account_id=None, job_id=None, file_name=None):
        """
        Returns a signed URL that you can contact to retrieve a single specified file from a specified job's data extract.
        The user must have executive overview or project administrator permissions.

        https://aps.autodesk.com/en/docs/acc/v1/reference/http/data-connector-jobs-jobId-data-name-GET/

        Args:
            account_id (str, optional): The account ID. If not provided, uses the account ID from the base class.
            job_id (str): The ID of the job to retrieve data from.
            file_name (str): The name of the file to retrieve from the data extract.

        Returns:
            dict: An object containing the file size, name, and a signed URL for downloading the file.
                 The signed URL is valid for 60 seconds.

        Example:
            ```python
            # Get a signed URL for downloading a specific file from a job's data extract
            file_info = acc.data_connector.get_job_data(
                job_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
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
        """
        if not account_id:
            account_id = self.base.account_id

        if not account_id:
            raise Exception("Account ID is required")

        if not job_id:
            raise Exception("Job ID is required")

        if not file_name:
            raise Exception("File name is required")

        url = (
            f"{self.base_address}/accounts/{account_id}/jobs/{job_id}/data/{file_name}"
        )

        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
