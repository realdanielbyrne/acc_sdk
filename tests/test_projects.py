import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to the path so we can import the acc_sdk module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_sdk.projects import AccProjectsApi
from acc_sdk.base import AccBase


class TestAccProjectsApi(unittest.TestCase):
    def setUp(self):
        # Create a mock AccBase instance
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.account_id = "test_account_id"
        self.mock_base.get_private_token.return_value = "mock_token"
        self.mock_base.user_info = {"uid": "mock_user_id"}

        # Create an instance of AccProjectsApi with the mock base
        self.api = AccProjectsApi(base=self.mock_base)

        # Set the user_id attribute
        self.api.user_id = "mock_user_id"

    @patch("acc_sdk.projects.requests.get")
    def test_get_project(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_project_id",
            "name": "Test Project",
            "type": "Wall Construction",
            "jobNumber": "12345",
            "status": "active",
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_project(project_id="test_project_id")

        # Verify the result
        self.assertEqual(result["id"], "test_project_id")
        self.assertEqual(result["name"], "Test Project")
        self.assertEqual(result["type"], "Wall Construction")
        self.assertEqual(result["status"], "active")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/projects/test_project_id",
            headers={"Authorization": "Bearer mock_token"},
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_projects(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "project1",
                    "name": "Project 1",
                    "type": "Wall Construction",
                    "status": "active",
                },
                {
                    "id": "project2",
                    "name": "Project 2",
                    "type": "Building Construction",
                    "status": "active",
                },
            ],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_projects()

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[1]["id"], "project2")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=None,
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_projects_with_filter_params(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"id": "project1", "name": "Project 1", "status": "active"}],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Define filter parameters
        filter_params = {"fields": "id,name,status", "filter[status]": "active"}

        # Call the method with filter parameters
        result = self.api.get_projects(filter_params=filter_params)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[0]["status"], "active")
        self.assertEqual(set(result[0].keys()), {"id", "name", "status"})

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=filter_params,
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_projects_with_pagination(self, mock_get):
        # Set up the mock responses for pagination
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "results": [{"id": "project1", "name": "Project 1"}],
            "pagination": {"nextUrl": "https://example.com/next-page"},
        }

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "results": [{"id": "project2", "name": "Project 2"}],
            "pagination": {"nextUrl": None},
        }

        # Configure the mock to return different responses on consecutive calls
        mock_get.side_effect = [first_response, second_response]

        # Call the method with pagination enabled
        result = self.api.get_projects(follow_pagination=True)

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[1]["id"], "project2")

        # Verify the requests were made correctly
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=None,
        )
        mock_get.assert_any_call(
            "https://example.com/next-page",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=None,
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_active_projects(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"id": "project1", "name": "Project 1", "status": "active"}],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_active_projects()

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[0]["status"], "active")

        # Verify the request was made correctly with the active status filter
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params={"filter[status]": "active"},
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_active_projects_with_filter_params(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "project1",
                    "name": "Project 1",
                    "status": "active",
                    "type": "Wall Construction",
                }
            ],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Define filter parameters
        filter_params = {
            "fields": "name,status,type",
            "filter[type]": "Wall Construction",
        }

        # Call the method with filter parameters
        result = self.api.get_active_projects(filter_params=filter_params)

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[0]["status"], "active")
        self.assertEqual(result[0]["type"], "Wall Construction")

        # Verify the request was made correctly with both filters
        expected_params = {
            "fields": "name,status,type",
            "filter[type]": "Wall Construction",
            "filter[status]": "active",
        }
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=expected_params,
        )

    @patch("acc_sdk.projects.requests.get")
    def test_get_all_active_projects(self, mock_get):
        # Set up the mock responses for pagination
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "results": [{"id": "project1", "name": "Project 1", "status": "active"}],
            "pagination": {"nextUrl": "https://example.com/next-page"},
        }

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "results": [{"id": "project2", "name": "Project 2", "status": "active"}],
            "pagination": {"nextUrl": None},
        }

        # Configure the mock to return different responses on consecutive calls
        mock_get.side_effect = [first_response, second_response]

        # Call the method
        result = self.api.get_all_active_projects()

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "project1")
        self.assertEqual(result[1]["id"], "project2")
        self.assertEqual(result[0]["status"], "active")
        self.assertEqual(result[1]["status"], "active")

        # Verify the requests were made correctly
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params={"filter[status]": "active"},
        )
        mock_get.assert_any_call(
            "https://example.com/next-page",
            headers={"Authorization": "Bearer mock_token", "User-Id": "mock_user_id"},
            params=None,
        )

    @patch("acc_sdk.projects.requests.post")
    def test_post_project(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 202  # Note: API returns 202 for successful creation
        mock_response.json.return_value = {
            "id": "new_project_id",
            "name": "New Project",
            "type": "Wall Construction",
            "jobNumber": "12345",
            "status": "active",
        }
        mock_post.return_value = mock_response

        # Define a new project
        new_project = {
            "name": "New Project",
            "type": "Wall Construction",
            "jobNumber": "12345",
        }

        # Call the method
        result = self.api.post_project(new_project)

        # Verify the result
        self.assertEqual(result["id"], "new_project_id")
        self.assertEqual(result["name"], "New Project")
        self.assertEqual(result["type"], "Wall Construction")
        self.assertEqual(result["jobNumber"], "12345")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/projects",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer mock_token",
                "User-Id": "mock_user_id",
            },
            json=new_project,
        )

    @patch("acc_sdk.projects.requests.post")
    def test_post_project_missing_required_fields(self, mock_post):
        # Define an incomplete project
        incomplete_project = {"jobNumber": "12345"}

        # Verify that an exception is raised for missing name
        with self.assertRaises(Exception) as context:
            self.api.post_project(incomplete_project)
        self.assertIn("Missing required parameter 'name'", str(context.exception))

        # Add name but still missing type
        incomplete_project["name"] = "New Project"

        # Verify that an exception is raised for missing type
        with self.assertRaises(Exception) as context:
            self.api.post_project(incomplete_project)
        self.assertIn("Missing required parameter 'type'", str(context.exception))

        # Verify that no API call was made
        mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
