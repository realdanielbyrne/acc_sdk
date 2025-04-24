import unittest
from unittest.mock import patch, MagicMock
from acc_sdk.forms import AccFormsApi
from acc_sdk.base import AccBase


class TestAccFormsApi(unittest.TestCase):
    def setUp(self):
        # Create a mock AccBase instance
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.get_3leggedToken.return_value = "mock_token"

        # Create an instance of AccFormsApi with the mock base
        self.api = AccFormsApi(base=self.mock_base)

    @patch("acc_sdk.forms.requests.get")
    def test_get_forms(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "form1", "name": "Form 1"},
                {"id": "form2", "name": "Form 2"},
            ],
            "pagination": {"nextUrl": None},
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_forms(project_id="test_project_id")

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "form1")
        self.assertEqual(result[1]["id"], "form2")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/projects/test_project_id/forms",
            headers=self.api._get_headers(),
            params={"offset": 0, "limit": 50},
        )

    @patch("acc_sdk.forms.requests.get")
    def test_get_forms_with_pagination(self, mock_get):
        # Set up the mock responses for pagination
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "data": [{"id": "form1", "name": "Form 1"}],
            "pagination": {"nextUrl": "https://example.com/next-page"},
        }

        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "data": [{"id": "form2", "name": "Form 2"}],
            "pagination": {"nextUrl": None},
        }

        # Configure the mock to return different responses on consecutive calls
        mock_get.side_effect = [first_response, second_response]

        # Call the method with pagination enabled
        result = self.api.get_forms(
            project_id="test_project_id", follow_pagination=True
        )

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "form1")
        self.assertEqual(result[1]["id"], "form2")

        # Verify the requests were made correctly
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(
            f"{self.api.base_url}/projects/test_project_id/forms",
            headers=self.api._get_headers(),
            params={"offset": 0, "limit": 50},
        )
        mock_get.assert_any_call(
            "https://example.com/next-page",
            headers=self.api._get_headers(),
            params=None,
        )

    @patch("acc_sdk.forms.requests.post")
    def test_post_form(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_form_id", "name": "New Form"}
        mock_post.return_value = mock_response

        # Define form data
        form_data = {"customValues": {"field1": "value1"}}

        # Call the method
        result = self.api.post_form(
            project_id="test_project_id", template_id="template_id", data=form_data
        )

        # Verify the result
        self.assertEqual(result["id"], "new_form_id")
        self.assertEqual(result["name"], "New Form")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/projects/test_project_id/form-templates/template_id/forms",
            headers=self.api._get_headers(),
            json=form_data,
        )

    @patch("acc_sdk.forms.requests.patch")
    def test_patch_form(self, mock_patch):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "updated_form_id",
            "name": "Updated Form",
        }
        mock_patch.return_value = mock_response

        # Define update data
        update_data = {"customValues": {"field1": "updated_value1"}}

        # Call the method
        result = self.api.patch_form(
            project_id="test_project_id",
            template_id="template_id",
            form_id="form_id",
            data=update_data,
        )

        # Verify the result
        self.assertEqual(result["id"], "updated_form_id")
        self.assertEqual(result["name"], "Updated Form")

        # Verify the request was made correctly
        mock_patch.assert_called_once_with(
            f"{self.api.base_url}/projects/test_project_id/form-templates/template_id/forms/form_id",
            headers=self.api._get_headers(),
            json=update_data,
        )

    @patch("acc_sdk.forms.requests.put")
    def test_put_form(self, mock_put):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "updated_form_id",
            "customValues": {"field1": "new_value1"},
        }
        mock_put.return_value = mock_response

        # Define update data
        update_data = {"customValues": {"field1": "new_value1"}}

        # Call the method
        result = self.api.put_form(
            project_id="test_project_id", form_id="form_id", data=update_data
        )

        # Verify the result
        self.assertEqual(result["id"], "updated_form_id")
        self.assertEqual(result["customValues"]["field1"], "new_value1")

        # Verify the request was made correctly
        mock_put.assert_called_once_with(
            f"{self.api.base_url}/projects/test_project_id/forms/form_id/values:batch-update",
            headers=self.api._get_headers(),
            json=update_data,
        )


if __name__ == "__main__":
    unittest.main()
