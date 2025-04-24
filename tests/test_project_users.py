import unittest
from unittest.mock import patch, MagicMock
from acc_sdk.project_users import AccProjectUsersApi
from acc_sdk.base import AccBase
import requests


class TestAccProjectUsersApi(unittest.TestCase):

    def setUp(self):
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.get_private_token.return_value = "mock_token"
        self.mock_base.user_info = {"uid": "mock_user_id"}
        self.api = AccProjectUsersApi(base=self.mock_base)

    def test_get_headers(self):
        # Test without content type
        headers = self.api._get_headers()
        self.assertEqual(headers["Authorization"], "Bearer mock_token")
        self.assertEqual(headers["User-Id"], "mock_user_id")
        self.assertNotIn("Content-Type", headers)

        # Test with content type
        headers = self.api._get_headers(include_content_type=True)
        self.assertEqual(headers["Authorization"], "Bearer mock_token")
        self.assertEqual(headers["User-Id"], "mock_user_id")
        self.assertEqual(headers["Content-Type"], "application/json")

    @patch("acc_sdk.project_users.requests.get")
    def test_handle_pagination(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"autodeskId": "user1"}],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Test pagination handling
        results = self.api._handle_pagination(
            url="https://example.com/api",
            headers={"Authorization": "Bearer token"},
            params={"limit": 50},
            follow_pagination=True,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["uid"], "user1")
        mock_get.assert_called_once()

    def test_handle_error_response(self):
        # Test successful response
        mock_response = MagicMock()
        mock_response.status_code = 200

        # This should not raise an exception
        self.api._handle_error_response(mock_response)

        # Test error response
        mock_error_response = MagicMock()
        mock_error_response.status_code = 400
        mock_error_response.json.return_value = {"errors": ["Error message"]}
        mock_error_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Error"
        )

        # This should raise an HTTPError
        with self.assertRaises(requests.HTTPError):
            self.api._handle_error_response(mock_error_response)

    @patch("acc_sdk.project_users.requests.get")
    def test_get_users(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"autodeskId": "user1"}],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        users = self.api.get_users(project_id="mock_project_id")

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["uid"], "user1")
        mock_get.assert_called_once()

        # Verify headers
        called_headers = mock_get.call_args[1]["headers"]
        self.assertEqual(called_headers["Authorization"], "Bearer mock_token")
        self.assertEqual(called_headers["User-Id"], "mock_user_id")

    @patch("acc_sdk.project_users.requests.post")
    def test_post_user(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_user_id"}
        mock_post.return_value = mock_response

        new_user = {
            "email": "user@example.com",
            "products": AccProjectUsersApi.productmember,
        }
        response = self.api.post_user(project_id="mock_project_id", user=new_user)

        self.assertEqual(response["id"], "new_user_id")
        mock_post.assert_called_once()

        # Verify headers
        called_headers = mock_post.call_args[1]["headers"]
        self.assertEqual(called_headers["Authorization"], "Bearer mock_token")
        self.assertEqual(called_headers["User-Id"], "mock_user_id")
        self.assertEqual(called_headers["Content-Type"], "application/json")

    @patch("acc_sdk.project_users.requests.delete")
    def test_delete_user(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = self.api.delete_user(
            project_id="mock_project_id", target_user_id="mock_user_id"
        )

        self.assertTrue(result)
        mock_delete.assert_called_once()

        # Verify headers
        called_headers = mock_delete.call_args[1]["headers"]
        self.assertEqual(called_headers["Authorization"], "Bearer mock_token")
        self.assertEqual(called_headers["User-Id"], "mock_user_id")


if __name__ == "__main__":
    unittest.main()
