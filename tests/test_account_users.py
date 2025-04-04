import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the parent directory to the path so we can import the acc_sdk module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_sdk.account_users import AccAccountUsersApi
from acc_sdk.base import AccBase


class TestAccAccountUsersApi(unittest.TestCase):
    def setUp(self):
        # Create a mock AccBase instance
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.account_id = "test_account_id"
        self.mock_base.company_id = "test_company_id"
        self.mock_base.get_2leggedToken.return_value = "test_token"
        self.mock_base.user_info = {"uid": "test_user_id"}

        # Create an instance of AccAccountUsersApi with the mock base
        self.api = AccAccountUsersApi(self.mock_base)

        # Set the user_id attribute
        self.api.user_id = "test_user_id"

    @patch("requests.get")
    def test_get_user_by_id(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "status": "active",
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_user_by_id("test_user_id")

        # Verify the result
        self.assertEqual(result["id"], "test_user_id")
        self.assertEqual(result["name"], "Test User")
        self.assertEqual(result["email"], "test@example.com")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/test_user_id",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
            },
        )

    @patch("requests.get")
    def test_get_user_by_id_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("User not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_user_by_id("nonexistent_user_id")

    @patch("requests.get")
    def test_get_user_by_email(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "test_user_id",
                "name": "Test User",
                "email": "test@example.com",
                "status": "active",
                "uid": "test_uid",
            }
        ]
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_user_by_email("test@example.com")

        # Verify the result
        self.assertEqual(result["id"], "test_user_id")
        self.assertEqual(result["name"], "Test User")
        self.assertEqual(result["email"], "test@example.com")
        self.assertEqual(result["autodeskId"], "test_uid")
        self.assertEqual(result["sub"], "test_uid")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/search?email=test@example.com&limit=1",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
            },
        )

    @patch("requests.get")
    def test_get_user_by_email_not_found(self, mock_get):
        # Set up the mock response for user not found
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_user_by_email("nonexistent@example.com")

        # Verify the result is None
        self.assertIsNone(result)

    @patch("requests.get")
    def test_get_user_by_email_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_user_by_email("test@example.com")

    def test_get_user_by_email_no_email(self):
        # Call the method with None email and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.get_user_by_email(None)

        self.assertEqual(str(context.exception), "Email is required")

    @patch("requests.get")
    def test_get_users(self, mock_get):
        # Set up the mock responses for pagination
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [
            {"id": "user1", "name": "User 1", "email": "user1@example.com"},
            {"id": "user2", "name": "User 2", "email": "user2@example.com"},
        ]

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [
            {"id": "user3", "name": "User 3", "email": "user3@example.com"}
        ]

        mock_response3 = MagicMock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = []

        # Set up the mock to return different responses on subsequent calls
        mock_get.side_effect = [mock_response1, mock_response2, mock_response3]

        # Call the method
        result = self.api.get_users()

        # Verify the result
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["id"], "user1")
        self.assertEqual(result[1]["id"], "user2")
        self.assertEqual(result[2]["id"], "user3")

        # Verify the requests were made correctly
        self.assertEqual(mock_get.call_count, 3)

        # Verify that the URL and headers are correct
        for call in mock_get.call_args_list:
            args, kwargs = call
            self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
            self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_token")
            self.assertEqual(
                args[0], f"{self.api.base_url}/accounts/test_account_id/users"
            )

    @patch("requests.get")
    def test_get_users_with_params(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "user1", "name": "User 1", "email": "user1@example.com"}
        ]

        # Set up the mock to return empty list on second call to end pagination
        mock_empty_response = MagicMock()
        mock_empty_response.status_code = 200
        mock_empty_response.json.return_value = []

        mock_get.side_effect = [mock_response, mock_empty_response]

        # Call the method with parameters
        result = self.api.get_users(
            sort="name", fields="id,name,email", limit=50, offset=10
        )

        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "user1")

        # Verify the request was made correctly
        _, kwargs = mock_get.call_args_list[0]
        self.assertEqual(kwargs["params"]["sort"], "name")
        self.assertEqual(kwargs["params"]["field"], "id,name,email")
        # Note: The method ignores the provided limit and offset and uses its own pagination

    @patch("requests.get")
    def test_get_users_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_users()

    @patch("requests.get")
    def test_get_users_search(self, mock_get):
        # Set up the mock responses for pagination
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [
            {"id": "user1", "name": "John Doe", "email": "john@example.com"},
            {"id": "user2", "name": "John Smith", "email": "smith@example.com"},
        ]

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = []

        # Set up the mock to return different responses on subsequent calls
        mock_get.side_effect = [mock_response1, mock_response2]

        # Call the method with search parameters
        result = self.api.get_users_search(name="John", partial=True, operator="OR")

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "user1")
        self.assertEqual(result[1]["id"], "user2")

        # Verify the requests were made correctly
        self.assertEqual(mock_get.call_count, 2)

        # Verify that the URL and headers are correct
        for call in mock_get.call_args_list:
            args, kwargs = call
            self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
            self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_token")
            self.assertEqual(
                args[0], f"{self.api.base_url}/accounts/test_account_id/users/search"
            )

            # Verify search parameters
            self.assertEqual(kwargs["params"]["name"], "John")
            self.assertEqual(kwargs["params"]["partial"], True)
            self.assertEqual(kwargs["params"]["operator"], "OR")

    @patch("requests.get")
    def test_get_users_search_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_users_search(name="John")

    @patch("requests.post")
    def test_post_user(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "new_user_id",
            "name": "New User",
            "email": "new@example.com",
            "company_id": "test_company_id",
            "status": "active",
        }
        mock_post.return_value = mock_response

        # Test data
        user_data = {"name": "New User", "email": "new@example.com"}

        # Call the method
        result = self.api.post_user(user_data)

        # Verify the result
        self.assertEqual(result["id"], "new_user_id")
        self.assertEqual(result["name"], "New User")
        self.assertEqual(result["email"], "new@example.com")
        self.assertEqual(result["company_id"], "test_company_id")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
                "User-Id": "test_user_id",
            },
            json={
                "name": "New User",
                "email": "new@example.com",
                "company_id": "test_company_id",
            },
        )

    @patch("requests.post")
    def test_post_user_with_company_id(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "new_user_id",
            "name": "New User",
            "email": "new@example.com",
            "company_id": "custom_company_id",
            "status": "active",
        }
        mock_post.return_value = mock_response

        # Test data with custom company_id
        user_data = {
            "name": "New User",
            "email": "new@example.com",
            "company_id": "custom_company_id",
        }

        # Call the method
        result = self.api.post_user(user_data)

        # Verify the result
        self.assertEqual(result["company_id"], "custom_company_id")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
                "User-Id": "test_user_id",
            },
            json=user_data,
        )

    def test_post_user_no_email(self):
        # Test data without email
        user_data = {"name": "New User"}

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.post_user(user_data)

        self.assertEqual(str(context.exception), "User email is required at a minimum.")

    def test_post_user_no_company_id(self):
        # Set up the mock base without company_id
        self.mock_base.company_id = None

        # Test data without company_id
        user_data = {"name": "New User", "email": "new@example.com"}

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.post_user(user_data)

        self.assertEqual(str(context.exception), "Company ID is required")

    @patch("requests.post")
    @patch("acc_sdk.account_users.AccAccountUsersApi.get_user_by_email")
    def test_post_user_already_exists(self, mock_get_user, mock_post):
        # Set up the mock response for conflict
        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_post.return_value = mock_response

        # Set up the mock for get_user_by_email
        mock_get_user.return_value = {
            "id": "existing_user_id",
            "name": "Existing User",
            "email": "existing@example.com",
            "company_id": "test_company_id",
            "status": "active",
        }

        # Test data
        user_data = {"name": "Existing User", "email": "existing@example.com"}

        # Call the method
        result = self.api.post_user(user_data)

        # Verify the result
        self.assertEqual(result["id"], "existing_user_id")
        self.assertEqual(result["name"], "Existing User")
        self.assertEqual(result["email"], "existing@example.com")

        # Verify get_user_by_email was called
        mock_get_user.assert_called_once_with("existing@example.com")

    @patch("requests.post")
    def test_post_users(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": 2,
            "failure": 0,
            "success_items": [
                {"id": "user1", "name": "User 1", "email": "user1@example.com"},
                {"id": "user2", "name": "User 2", "email": "user2@example.com"},
            ],
            "failure_items": [],
        }
        mock_post.return_value = mock_response

        # Test data
        users_data = [
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
        ]

        # Call the method
        result = self.api.post_users(users_data)

        # Verify the result
        self.assertEqual(result["success"], 2)
        self.assertEqual(result["failure"], 0)
        self.assertEqual(len(result["success_items"]), 2)

        # Verify the request was made correctly
        expected_data = [
            {
                "name": "User 1",
                "email": "user1@example.com",
                "company_id": "test_company_id",
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "company_id": "test_company_id",
            },
        ]

        mock_post.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/import",
            headers={
                "Content-Type": "application/json",
                "Authorization": "test_token",
                "User-Id": "test_user_id",
            },
            json=expected_data,
        )

    def test_post_users_no_company_id(self):
        # Set up the mock base without company_id
        self.mock_base.company_id = None

        # Test data without company_id
        users_data = [
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
        ]

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.post_users(users_data)

        self.assertEqual(str(context.exception), "Company ID is required.")

    @patch("requests.post")
    def test_post_users_with_custom_company_id(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": 2,
            "failure": 0,
            "success_items": [
                {
                    "id": "user1",
                    "name": "User 1",
                    "email": "user1@example.com",
                    "company_id": "custom_company_id",
                },
                {
                    "id": "user2",
                    "name": "User 2",
                    "email": "user2@example.com",
                    "company_id": "custom_company_id",
                },
            ],
            "failure_items": [],
        }
        mock_post.return_value = mock_response

        # Test data with custom company_id
        users_data = [
            {
                "name": "User 1",
                "email": "user1@example.com",
                "company_id": "custom_company_id",
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "company_id": "custom_company_id",
            },
        ]

        # Call the method
        result = self.api.post_users(users_data)

        # Verify the result
        self.assertEqual(result["success"], 2)
        self.assertEqual(result["success_items"][0]["company_id"], "custom_company_id")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/import",
            headers={
                "Content-Type": "application/json",
                "Authorization": "test_token",
                "User-Id": "test_user_id",
            },
            json=users_data,
        )

    @patch("requests.post")
    def test_post_users_error(self, mock_post):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_post.return_value = mock_response

        # Test data
        users_data = [{"name": "User 1", "email": "user1@example.com"}]

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.post_users(users_data)

    @patch("requests.patch")
    @patch("acc_sdk.account_users.AccAccountUsersApi.get_user_by_email")
    def test_patch_user_status(self, mock_get_user, mock_patch):
        # Set up the mock for get_user_by_email
        mock_get_user.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "status": "inactive",
        }

        # Set up the mock response for patch
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "status": "active",
        }
        mock_patch.return_value = mock_response

        # Call the method
        result = self.api.patch_user(user_email="test@example.com", status="active")

        # Verify the result
        self.assertEqual(result["id"], "test_user_id")
        self.assertEqual(result["status"], "active")

        # Verify get_user_by_email was called
        mock_get_user.assert_called_once_with("test@example.com")

        # Verify the request was made correctly
        mock_patch.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/test_user_id",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
                "User-Id": "test_user_id",
            },
            json={"status": "active"},
        )

    @patch("requests.patch")
    @patch("acc_sdk.account_users.AccAccountUsersApi.get_user_by_email")
    def test_patch_user_company_id(self, mock_get_user, mock_patch):
        # Set up the mock for get_user_by_email
        mock_get_user.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "company_id": "old_company_id",
        }

        # Set up the mock response for patch
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "company_id": "new_company_id",
        }
        mock_patch.return_value = mock_response

        # Call the method
        result = self.api.patch_user(
            user_email="test@example.com", company_id="new_company_id"
        )

        # Verify the result
        self.assertEqual(result["company_id"], "new_company_id")

        # Verify the request was made correctly
        mock_patch.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/test_user_id",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
                "User-Id": "test_user_id",
            },
            json={"company_id": "new_company_id"},
        )

    @patch("requests.patch")
    @patch("acc_sdk.account_users.AccAccountUsersApi.get_user_by_email")
    def test_patch_user_both_fields(self, mock_get_user, mock_patch):
        # Set up the mock for get_user_by_email
        mock_get_user.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "status": "inactive",
            "company_id": "old_company_id",
        }

        # Set up the mock response for patch
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
            "status": "active",
            "company_id": "new_company_id",
        }
        mock_patch.return_value = mock_response

        # Call the method
        result = self.api.patch_user(
            user_email="test@example.com", status="active", company_id="new_company_id"
        )

        # Verify the result
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["company_id"], "new_company_id")

        # Verify the request was made correctly
        mock_patch.assert_called_once_with(
            f"{self.api.base_url}/accounts/test_account_id/users/test_user_id",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_token",
                "User-Id": "test_user_id",
            },
            json={"status": "active", "company_id": "new_company_id"},
        )

    def test_patch_user_invalid_status(self):
        # Call the method with invalid status and expect an exception
        with self.assertRaises(Exception) as context:
            self.api.patch_user(user_email="test@example.com", status="invalid_status")

        self.assertEqual(
            str(context.exception), "Status must be either 'active' or 'inactive'"
        )

    @patch("requests.patch")
    @patch("acc_sdk.account_users.AccAccountUsersApi.get_user_by_email")
    def test_patch_user_error(self, mock_get_user, mock_patch):
        # Set up the mock for get_user_by_email
        mock_get_user.return_value = {
            "id": "test_user_id",
            "name": "Test User",
            "email": "test@example.com",
        }

        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        mock_patch.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.patch_user(user_email="test@example.com", status="active")


if __name__ == "__main__":
    unittest.main()
