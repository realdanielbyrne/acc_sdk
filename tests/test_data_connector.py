import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the parent directory to the path so we can import the acc_sdk module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_sdk.data_connector import AccDataConnectorApi
from acc_sdk.base import AccBase


class TestAccDataConnectorApi(unittest.TestCase):
    def setUp(self):
        # Create a mock AccBase instance
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.account_id = "test_account_id"
        self.mock_base.get_private_token.return_value = "test_token"
        self.mock_base.get_3leggedToken.return_value = "test_token"

        # Create an instance of AccDataConnectorApi with the mock base
        self.api = AccDataConnectorApi(self.mock_base)

    @patch("requests.post")
    def test_post_request(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "description": "Test Data Extract",
            "isActive": True,
            "accountId": "test_account_id",
            "serviceGroups": ["admin", "issues"],
        }
        mock_post.return_value = mock_response

        # Test data for a one-time request
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "ONE_TIME",
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "serviceGroups": ["admin", "issues"],
        }

        # Call the method
        result = self.api.post_request(data=test_data)

        # Verify the result
        self.assertEqual(result["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002")
        self.assertEqual(result["description"], "Test Data Extract")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json",
            },
            json=test_data,
        )

    @patch("requests.post")
    def test_post_request_with_account_id(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "description": "Test Data Extract",
            "isActive": True,
            "accountId": "custom_account_id",
            "serviceGroups": ["admin", "issues"],
        }
        mock_post.return_value = mock_response

        # Test data for a one-time request
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "ONE_TIME",
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "serviceGroups": ["admin", "issues"],
        }

        # Call the method with a custom account ID
        result = self.api.post_request(account_id="custom_account_id", data=test_data)

        # Verify the result
        self.assertEqual(result["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/requests",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json",
            },
            json=test_data,
        )

    @patch("requests.post")
    def test_post_request_validation(self, mock_post):
        # Test missing scheduleInterval
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "serviceGroups": ["admin", "issues"],
        }

        with self.assertRaises(Exception) as context:
            self.api.post_request(data=test_data)
        self.assertTrue("scheduleInterval is required" in str(context.exception))

        # Test missing effectiveFrom
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "ONE_TIME",
            "serviceGroups": ["admin", "issues"],
        }

        with self.assertRaises(Exception) as context:
            self.api.post_request(data=test_data)
        self.assertTrue("effectiveFrom is required" in str(context.exception))

        # Test missing serviceGroups
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "ONE_TIME",
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
        }

        with self.assertRaises(Exception) as context:
            self.api.post_request(data=test_data)
        self.assertTrue(
            "At least one service group is required" in str(context.exception)
        )

        # Test recurring schedule without reoccuringInterval
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "WEEK",
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "effectiveTo": "2023-12-31T23:59:59.999Z",
            "serviceGroups": ["admin", "issues"],
        }

        with self.assertRaises(Exception) as context:
            self.api.post_request(data=test_data)
        self.assertTrue(
            "reoccuringInterval must be a positive integer" in str(context.exception)
        )

        # Test recurring schedule without effectiveTo
        test_data = {
            "description": "Test Data Extract",
            "isActive": True,
            "scheduleInterval": "WEEK",
            "reoccuringInterval": 2,
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "serviceGroups": ["admin", "issues"],
        }

        with self.assertRaises(Exception) as context:
            self.api.post_request(data=test_data)
        self.assertTrue(
            "effectiveTo is required for recurring schedules" in str(context.exception)
        )

    @patch("requests.get")
    def test_get_requests_basic(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "description": "Test Data Extract",
                    "isActive": True,
                    "accountId": "test_account_id",
                    "serviceGroups": ["admin", "issues"],
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_requests()

        # Verify the result
        self.assertEqual(result["pagination"]["totalResults"], 1)
        self.assertEqual(
            result["results"][0]["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002"
        )
        self.assertEqual(result["results"][0]["description"], "Test Data Extract")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_requests_with_account_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "description": "Test Data Extract",
                    "isActive": True,
                    "accountId": "custom_account_id",
                    "serviceGroups": ["admin", "issues"],
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.get_requests(account_id="custom_account_id")

        # Verify the result
        self.assertEqual(result["results"][0]["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/requests",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_requests_with_pagination_and_sorting(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 10, "offset": 5, "totalResults": 100},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "description": "Test Data Extract",
                    "isActive": True,
                    "accountId": "test_account_id",
                    "serviceGroups": ["admin", "issues"],
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with pagination and sorting parameters
        result = self.api.get_requests(
            limit=10, offset=5, sort="desc", sort_fields="createdAt,-updatedAt"
        )

        # Verify the result
        self.assertEqual(result["pagination"]["limit"], 10)
        self.assertEqual(result["pagination"]["offset"], 5)
        self.assertEqual(result["pagination"]["totalResults"], 100)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests",
            headers={"Authorization": "Bearer test_token"},
            params={
                "limit": 10,
                "offset": 5,
                "sort": "desc",
                "sortFields": "createdAt,-updatedAt",
            },
        )

    @patch("requests.get")
    def test_get_requests_with_filters(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "description": "Test Data Extract",
                    "isActive": True,
                    "accountId": "test_account_id",
                    "projectId": "test_project_id",
                    "scheduleInterval": "ONE_TIME",
                    "serviceGroups": ["admin", "issues"],
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with filters
        result = self.api.get_requests(
            projectId="test_project_id", isActive=True, scheduleInterval="ONE_TIME"
        )

        # Verify the result
        self.assertEqual(result["results"][0]["projectId"], "test_project_id")
        self.assertEqual(result["results"][0]["scheduleInterval"], "ONE_TIME")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests",
            headers={"Authorization": "Bearer test_token"},
            params={
                "limit": 20,
                "offset": 0,
                "filter[projectId]": "test_project_id",
                "filter[isActive]": True,
                "filter[scheduleInterval]": "ONE_TIME",
            },
        )

    @patch("requests.get")
    def test_get_requests_with_date_range_filter(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "description": "Test Data Extract",
                    "isActive": True,
                    "accountId": "test_account_id",
                    "createdAt": "2023-01-15T12:00:00.000Z",
                    "serviceGroups": ["admin", "issues"],
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a date range filter
        date_range = "2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z"
        result = self.api.get_requests(createdAt=date_range)

        # Verify the result
        self.assertEqual(result["results"][0]["createdAt"], "2023-01-15T12:00:00.000Z")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0, "filter[createdAt]": date_range},
        )

    @patch("requests.get")
    def test_get_requests_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_requests()

    @patch("requests.get")
    def test_get_request(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "description": "Test Data Extract",
            "isActive": True,
            "accountId": "test_account_id",
            "projectId": None,
            "projectIdList": '[ "project_uuid1", "project_uuid2" ]',
            "createdBy": "USER123",
            "createdByEmail": "user@example.com",
            "createdAt": "2023-06-06T00:00:00.000Z",
            "updatedBy": "USER123",
            "updatedAt": "2023-06-06T00:00:00.000Z",
            "scheduleInterval": "ONE_TIME",
            "reoccuringInterval": None,
            "effectiveFrom": "2023-06-06T00:00:00.000Z",
            "effectiveTo": "2023-06-12T00:00:00.000Z",
            "lastQueuedAt": None,
            "serviceGroups": ["admin", "issues"],
            "callbackUrl": "https://api.example.com/callback",
            "sendEmail": True,
            "startDate": "2023-06-06T00:00:00.000Z",
            "endDate": "2023-06-06T12:00:00.000Z",
            "dateRange": "LAST_MONTH",
            "projectStatus": "active",
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_request(request_id="ce9bc188-1e18-11eb-adc1-0242ac120002")

        # Verify the result
        self.assertEqual(result["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002")
        self.assertEqual(result["description"], "Test Data Extract")
        self.assertEqual(result["serviceGroups"], ["admin", "issues"])

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.get")
    def test_get_request_with_account_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "description": "Test Data Extract",
            "accountId": "custom_account_id",
            "serviceGroups": ["admin", "issues"],
        }
        mock_get.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.get_request(
            account_id="custom_account_id",
            request_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
        )

        # Verify the result
        self.assertEqual(result["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/requests/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.get")
    def test_get_request_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Request not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_request(request_id="nonexistent-request-id")

    def test_get_request_missing_request_id(self):
        # Call the method without a request ID and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.get_request()

        self.assertEqual(str(context.exception), "Request ID is required")

    @patch("requests.delete")
    def test_delete_request(self, mock_delete):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Call the method
        result = self.api.delete_request(
            request_id="ce9bc188-1e18-11eb-adc1-0242ac120002"
        )

        # Verify the result
        self.assertTrue(result)

        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.delete")
    def test_delete_request_with_account_id(self, mock_delete):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.delete_request(
            account_id="custom_account_id",
            request_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
        )

        # Verify the result
        self.assertTrue(result)

        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/requests/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.delete")
    def test_delete_request_error(self, mock_delete):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Request not found")
        mock_delete.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.delete_request(request_id="nonexistent-request-id")

    def test_delete_request_missing_request_id(self):
        # Call the method without a request ID and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.delete_request()

        self.assertEqual(str(context.exception), "Request ID is required")

    @patch("requests.get")
    def test_get_jobs_by_request_basic(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "projectId": None,
                    "projectIdList": '[ "project_uuid1", "project_uuid2" ]',
                    "createdBy": "USER123",
                    "createdByEmail": "user@example.com",
                    "createdAt": "2023-06-06T00:00:00.000Z",
                    "status": "complete",
                    "completionStatus": "success",
                    "startedAt": "2023-06-06T00:10:00.000Z",
                    "completedAt": "2023-06-06T00:29:40.000Z",
                    "sendEmail": True,
                    "progress": 100,
                    "lastDownloadedBy": "user@example.com",
                    "lastDownloadedAt": "2023-06-07T00:00:00.000Z",
                    "startDate": "2023-06-06T00:00:00.000Z",
                    "endDate": "2023-06-06T12:00:00.000Z",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_jobs_by_request(
            request_id="a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e"
        )

        # Verify the result
        self.assertEqual(result["pagination"]["totalResults"], 1)
        self.assertEqual(
            result["results"][0]["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002"
        )
        self.assertEqual(result["results"][0]["status"], "complete")
        self.assertEqual(result["results"][0]["completionStatus"], "success")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests/a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_jobs_by_request_with_account_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "custom_account_id",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.get_jobs_by_request(
            account_id="custom_account_id",
            request_id="a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
        )

        # Verify the result
        self.assertEqual(result["results"][0]["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/requests/a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_jobs_by_request_with_pagination_and_sorting(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 10, "offset": 5, "totalResults": 100},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with pagination and sorting parameters
        result = self.api.get_jobs_by_request(
            request_id="a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
            limit=10,
            offset=5,
            sort="desc",
        )

        # Verify the result
        self.assertEqual(result["pagination"]["limit"], 10)
        self.assertEqual(result["pagination"]["offset"], 5)
        self.assertEqual(result["pagination"]["totalResults"], 100)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/requests/a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 10, "offset": 5, "sort": "desc"},
        )

    @patch("requests.get")
    def test_get_jobs_by_request_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_jobs_by_request(request_id="nonexistent-request-id")

    def test_get_jobs_by_request_missing_request_id(self):
        # Call the method without a request ID and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.get_jobs_by_request()

        self.assertEqual(str(context.exception), "Request ID is required")

    @patch("requests.get")
    def test_get_jobs_basic(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "projectId": None,
                    "projectIdList": '[ "project_uuid1", "project_uuid2" ]',
                    "createdBy": "USER123",
                    "createdByEmail": "user@example.com",
                    "createdAt": "2023-06-06T00:00:00.000Z",
                    "status": "complete",
                    "completionStatus": "success",
                    "startedAt": "2023-06-06T00:10:00.000Z",
                    "completedAt": "2023-06-06T00:29:40.000Z",
                    "sendEmail": True,
                    "progress": 100,
                    "lastDownloadedBy": "user@example.com",
                    "lastDownloadedAt": "2023-06-07T00:00:00.000Z",
                    "startDate": "2023-06-06T00:00:00.000Z",
                    "endDate": "2023-06-06T12:00:00.000Z",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_jobs()

        # Verify the result
        self.assertEqual(result["pagination"]["totalResults"], 1)
        self.assertEqual(
            result["results"][0]["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002"
        )
        self.assertEqual(result["results"][0]["status"], "complete")
        self.assertEqual(result["results"][0]["completionStatus"], "success")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_jobs_with_account_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "custom_account_id",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.get_jobs(account_id="custom_account_id")

        # Verify the result
        self.assertEqual(result["results"][0]["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0},
        )

    @patch("requests.get")
    def test_get_jobs_with_project_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "projectId": "test_project_id",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a project ID
        result = self.api.get_jobs(project_id="test_project_id")

        # Verify the result
        self.assertEqual(result["results"][0]["projectId"], "test_project_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={"limit": 20, "offset": 0, "projectId": "test_project_id"},
        )

    @patch("requests.get")
    def test_get_jobs_with_pagination_and_sorting(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 10, "offset": 5, "totalResults": 100},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with pagination and sorting parameters
        result = self.api.get_jobs(
            limit=10,
            offset=5,
            sort="desc",
            sort_fields="createdAt,-completedAt",
        )

        # Verify the result
        self.assertEqual(result["pagination"]["limit"], 10)
        self.assertEqual(result["pagination"]["offset"], 5)
        self.assertEqual(result["pagination"]["totalResults"], 100)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={
                "limit": 10,
                "offset": 5,
                "sort": "desc",
                "sortFields": "createdAt,-completedAt",
            },
        )

    @patch("requests.get")
    def test_get_jobs_with_filters(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "status": "complete",
                    "completionStatus": "success",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with filters
        result = self.api.get_jobs(
            status="complete",
            completionStatus="success",
        )

        # Verify the result
        self.assertEqual(result["results"][0]["status"], "complete")
        self.assertEqual(result["results"][0]["completionStatus"], "success")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={
                "limit": 20,
                "offset": 0,
                "filter[status]": "complete",
                "filter[completionStatus]": "success",
            },
        )

    @patch("requests.get")
    def test_get_jobs_with_date_range_filter(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pagination": {"limit": 20, "offset": 0, "totalResults": 1},
            "results": [
                {
                    "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
                    "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
                    "accountId": "test_account_id",
                    "createdAt": "2023-01-15T12:00:00.000Z",
                    "status": "complete",
                }
            ],
        }
        mock_get.return_value = mock_response

        # Call the method with a date range filter
        date_range = "2023-01-01T00:00:00.000Z..2023-01-31T23:59:59.999Z"
        result = self.api.get_jobs(createdAt=date_range)

        # Verify the result
        self.assertEqual(result["results"][0]["createdAt"], "2023-01-15T12:00:00.000Z")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs",
            headers={"Authorization": "Bearer test_token"},
            params={
                "limit": 20,
                "offset": 0,
                "filter[createdAt]": date_range,
            },
        )

    @patch("requests.get")
    def test_get_jobs_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_jobs()

    @patch("requests.get")
    def test_get_job(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
            "accountId": "test_account_id",
            "projectId": None,
            "projectIdList": '[ "ffffffff-1f51-4b26-a6b7-6ac0639cb138", "aaaaaaaa-1f51-4b26-a6b7-6ac0639cb138" ]',
            "createdBy": "ABCDEFGHI",
            "createdByEmail": "joe.user@mycompany.com",
            "createdAt": "2020-11-06T19:09:40.106Z",
            "status": "complete",
            "completionStatus": "success",
            "startedAt": "2020-11-06T19:10:00.106Z",
            "completedAt": "2020-11-06T19:29:40.106Z",
            "sendEmail": True,
            "progress": 100,
            "lastDownloadedBy": "joe.user@mycompany.com",
            "lastDownloadedAt": "2021-11-06T19:09:40.106Z",
            "startDate": "2023-06-06T00:00:00.000Z",
            "endDate": "2023-06-06T12:00:00.000Z",
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_job(job_id="ce9bc188-1e18-11eb-adc1-0242ac120002")

        # Verify the result
        self.assertEqual(result["id"], "ce9bc188-1e18-11eb-adc1-0242ac120002")
        self.assertEqual(result["requestId"], "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["completionStatus"], "success")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.get")
    def test_get_job_with_account_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "ce9bc188-1e18-11eb-adc1-0242ac120002",
            "requestId": "a5a8e90f-3dbe-4b08-9b8e-16e8049ce31e",
            "accountId": "custom_account_id",
            "status": "complete",
            "completionStatus": "success",
        }
        mock_get.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.get_job(
            account_id="custom_account_id",
            job_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
        )

        # Verify the result
        self.assertEqual(result["accountId"], "custom_account_id")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/jobs/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.get")
    def test_get_job_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Job not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_job(job_id="nonexistent-job-id")

    def test_get_job_missing_job_id(self):
        # Call the method without a job ID and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.get_job()

        self.assertEqual(str(context.exception), "Job ID is required")

    @patch("requests.delete")
    def test_delete_job(self, mock_delete):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Call the method
        result = self.api.delete_job(job_id="ce9bc188-1e18-11eb-adc1-0242ac120002")

        # Verify the result
        self.assertTrue(result)

        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            f"{self.api.base_address}/accounts/test_account_id/jobs/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.delete")
    def test_delete_job_with_account_id(self, mock_delete):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        # Call the method with a custom account ID
        result = self.api.delete_job(
            account_id="custom_account_id",
            job_id="ce9bc188-1e18-11eb-adc1-0242ac120002",
        )

        # Verify the result
        self.assertTrue(result)

        # Verify the request was made correctly
        mock_delete.assert_called_once_with(
            f"{self.api.base_address}/accounts/custom_account_id/jobs/ce9bc188-1e18-11eb-adc1-0242ac120002",
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("requests.delete")
    def test_delete_job_error(self, mock_delete):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Job not found")
        mock_delete.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.delete_job(job_id="nonexistent-job-id")

    def test_delete_job_missing_job_id(self):
        # Call the method without a job ID and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.delete_job()

        self.assertEqual(str(context.exception), "Job ID is required")


if __name__ == "__main__":
    unittest.main()
