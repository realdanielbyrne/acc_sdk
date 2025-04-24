import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add the parent directory to the path so we can import the acc_sdk module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acc_sdk.photos import AccPhotosApi
from acc_sdk.base import AccBase


class TestAccPhotosApi(unittest.TestCase):
    def setUp(self):
        # Create a mock AccBase instance
        self.mock_base = MagicMock(spec=AccBase)
        self.mock_base.get_3leggedToken.return_value = "test_token"

        # Create an instance of AccPhotosApi with the mock base
        self.api = AccPhotosApi(self.mock_base)

    @patch("requests.get")
    def test_get_photo_basic(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "photo123",
            "title": "Test Photo",
            "description": "A test photo",
            "mediaType": "NORMAL",
            "type": "ISSUE",
            "createdAt": "2024-01-01T12:00:00Z",
            "createdBy": "user123",
            "updatedAt": "2024-01-02T12:00:00Z",
            "updatedBy": "user123",
            "takenAt": "2024-01-01T11:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "size": 1024000,
            "isPublic": True,
            "locked": False,
            "urls": {
                "thumbnail": "https://example.com/thumbnail.jpg",
                "full": "https://example.com/full.jpg"
            }
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.api.get_photo(project_id="project123", photo_id="photo123")

        # Verify the result
        self.assertEqual(result["id"], "photo123")
        self.assertEqual(result["title"], "Test Photo")
        self.assertEqual(result["mediaType"], "NORMAL")
        self.assertEqual(result["type"], "ISSUE")
        self.assertEqual(result["latitude"], 37.7749)
        self.assertEqual(result["longitude"], -122.4194)

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/photo123",
            params={},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.get")
    def test_get_photo_with_include(self, mock_get):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "photo123",
            "title": "Test Photo",
            "mediaType": "NORMAL",
            "urls": {
                "thumbnail": "https://example.com/thumbnail.jpg",
                "full": "https://example.com/full.jpg"
            },
            "signedUrls": {
                "thumbnail": "https://example.com/signed-thumbnail.jpg",
                "full": "https://example.com/signed-full.jpg"
            }
        }
        mock_get.return_value = mock_response

        # Call the method with include parameter
        result = self.api.get_photo(
            project_id="project123", 
            photo_id="photo123", 
            include=["signedUrls"]
        )

        # Verify the result
        self.assertEqual(result["id"], "photo123")
        self.assertEqual(result["title"], "Test Photo")
        self.assertIn("signedUrls", result)
        self.assertEqual(result["signedUrls"]["thumbnail"], "https://example.com/signed-thumbnail.jpg")

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/photo123",
            params={"include": "signedUrls"},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.get")
    def test_get_photo_error(self, mock_get):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Photo not found")
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_photo(project_id="project123", photo_id="nonexistent")

    @patch("requests.post")
    def test_get_filtered_photos_basic(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "photo123",
                    "title": "Test Photo 1",
                    "mediaType": "NORMAL"
                },
                {
                    "id": "photo456",
                    "title": "Test Photo 2",
                    "mediaType": "VIDEO"
                }
            ],
            "meta": {
                "total": 2,
                "limit": 50,
                "offset": 0
            }
        }
        mock_post.return_value = mock_response

        # Call the method
        result = self.api.get_filtered_photos(project_id="project123")

        # Verify the result
        self.assertEqual(len(result["data"]), 2)
        self.assertEqual(result["data"][0]["id"], "photo123")
        self.assertEqual(result["data"][1]["id"], "photo456")
        self.assertEqual(result["meta"]["total"], 2)

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/filter",
            json={},
            params={},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.post")
    def test_get_filtered_photos_with_filters(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "photo123",
                    "title": "Test Photo 1",
                    "mediaType": "NORMAL",
                    "isPublic": True
                }
            ],
            "meta": {
                "total": 1,
                "limit": 10,
                "offset": 0
            }
        }
        mock_post.return_value = mock_response

        # Define filter parameters
        filter_params = {
            "limit": 10,
            "offset": 0,
            "sortBy": "createdAt",
            "sortOrder": "desc",
            "mediaType": ["NORMAL"],
            "isPublic": True
        }

        # Call the method with filter parameters
        result = self.api.get_filtered_photos(
            project_id="project123",
            filter_params=filter_params
        )

        # Verify the result
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], "photo123")
        self.assertEqual(result["data"][0]["mediaType"], "NORMAL")
        self.assertEqual(result["data"][0]["isPublic"], True)
        self.assertEqual(result["meta"]["limit"], 10)

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/filter",
            json=filter_params,
            params={},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.post")
    def test_get_filtered_photos_with_include(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "photo123",
                    "title": "Test Photo 1",
                    "signedUrls": {
                        "thumbnail": "https://example.com/signed-thumbnail.jpg"
                    }
                }
            ],
            "meta": {
                "total": 1,
                "limit": 50,
                "offset": 0
            }
        }
        mock_post.return_value = mock_response

        # Call the method with include parameter
        result = self.api.get_filtered_photos(
            project_id="project123",
            include=["signedUrls"]
        )

        # Verify the result
        self.assertEqual(len(result["data"]), 1)
        self.assertIn("signedUrls", result["data"][0])
        self.assertEqual(
            result["data"][0]["signedUrls"]["thumbnail"], 
            "https://example.com/signed-thumbnail.jpg"
        )

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/filter",
            json={},
            params={"include": "signedUrls"},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.post")
    def test_get_filtered_photos_with_date_filters(self, mock_post):
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "photo123",
                    "title": "Test Photo 1",
                    "takenAt": "2024-01-15T12:00:00Z"
                }
            ],
            "meta": {
                "total": 1,
                "limit": 50,
                "offset": 0
            }
        }
        mock_post.return_value = mock_response

        # Define filter parameters with date range
        filter_params = {
            "takenAt": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z"
            }
        }

        # Call the method with filter parameters
        result = self.api.get_filtered_photos(
            project_id="project123",
            filter_params=filter_params
        )

        # Verify the result
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["data"][0]["id"], "photo123")
        self.assertEqual(result["data"][0]["takenAt"], "2024-01-15T12:00:00Z")

        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            f"{self.api.base_url}/projects/project123/photos/filter",
            json=filter_params,
            params={},
            headers={"Authorization": "Bearer test_token"}
        )

    @patch("requests.post")
    def test_get_filtered_photos_error(self, mock_post):
        # Set up the mock response for an error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("Bad request")
        mock_post.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception):
            self.api.get_filtered_photos(project_id="project123")


if __name__ == "__main__":
    unittest.main()
