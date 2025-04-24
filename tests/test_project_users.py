import unittest
from unittest.mock import patch, MagicMock
from acc_sdk.project_users import AccProjectUsersApi
from acc_sdk.base import AccBase


class TestAccProjectUsersApi(unittest.TestCase):

    def setUp(self):
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.get_private_token.return_value = "mock_token"
        self.mock_base.user_info = {"uid": "mock_user_id"}
        self.api = AccProjectUsersApi(base=self.mock_base)

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

    @patch("acc_sdk.project_users.requests.post")
    def test_add_user(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_user_id"}
        mock_post.return_value = mock_response

        new_user = {
            "email": "user@example.com",
            "products": AccProjectUsersApi.productmember,
        }
        response = self.api.add_user(project_id="mock_project_id", user=new_user)

        self.assertEqual(response["id"], "new_user_id")
        mock_post.assert_called_once()

    @patch("acc_sdk.project_users.requests.delete")
    def test_delete_user(self, mock_delete):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        result = self.api.delete(
            project_id="mock_project_id", target_user_id="mock_user_id"
        )

        self.assertTrue(result)
        mock_delete.assert_called_once()


if __name__ == "__main__":
    unittest.main()
