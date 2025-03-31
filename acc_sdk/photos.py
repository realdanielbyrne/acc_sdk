import requests
from .base import AccBase

class AccPhotosApi:
    """
    API for interacting with photos in Autodesk Construction Cloud.
    This API requires a 3-legged token with the data:read scope.
    """

    def __init__(self, base: AccBase):
        self.base = base
        self.base_url = "https://developer.api.autodesk.com/photos/v1"

    def get_photo(self, project_id: str, photo_id: str, include: list = None) -> dict:
        """
        Return a single media (photo or video) from a project.

        Args:
            project_id (str): Unique identifier of the project.
            photo_id (str): Unique identifier of the media.
            include (list, optional): Extra fields to be returned for each Photo Object. 
                                   Will always be: signedUrls.

        Returns:
            dict: The photo object containing:
                - id (str): The ID of the media
                - title (str): Title of the media
                - description (str): Description of the media
                - mediaType (str): The type of the media (NORMAL, INFRARED, PHOTOSPHERE, VIDEO)
                - type (str): The type of object this media was added with
                - createdAt (str): Creation timestamp in ISO 8601 format
                - createdBy (str): The actor that created the media
                - updatedAt (str): Last update timestamp in ISO 8601 format
                - updatedBy (str): The actor that last updated the media
                - takenAt (str): When the media was captured
                - latitude (float): Latitude in decimal degrees
                - longitude (float): Longitude in decimal degrees
                - size (int): Filesize in bytes
                - isPublic (bool): If true, visible to everyone
                - locked (bool): If true, cannot be deleted or edited
                - urls (dict): URLs to the media's assets
                - signedUrls (dict, optional): Short-lived URLs to the media's assets

        Raises:
            Exception: If the request fails or returns an error status code.

        Example:
            ```python
            # Get a photo with basic information
            photo = acc.photos.get_photo(
                project_id="your_project_id",
                photo_id="your_photo_id"
            )
            
            # Get a photo with signed URLs
            photo = acc.photos.get_photo(
                project_id="your_project_id",
                photo_id="your_photo_id",
                include=["signedUrls"]
            )

            ```

        Official Documentation:
            https://aps.autodesk.com/en/docs/acc/v1/reference/http/photos-getphoto-GET/
        """
        url = f"{self.base_url}/projects/{project_id}/photos/{photo_id}"
        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}"
        }
        
        # Build query parameters
        params = {}
        if include:
            params["include"] = ",".join(include)
            
        response = self.base.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_filtered_photos(self, project_id: str, filter_params: dict = None, include: list = None) -> dict:
        """
        Get a filtered list of photos from a project.

        Args:
            project_id (str): Unique identifier of the project.
            filter_params (dict, optional): Dictionary of filter parameters. Can include:
                - limit (int): Maximum number of photos to return
                - offset (int): Number of photos to skip
                - sortBy (str): Field to sort by (e.g., "createdAt", "takenAt")
                - sortOrder (str): Sort order ("asc" or "desc")
                - mediaType (list): List of media types to filter by
                - type (list): List of object types to filter by
                - createdBy (list): List of creator IDs to filter by
                - takenAt (dict): Date range filter for when photos were taken
                - createdAt (dict): Date range filter for when photos were created
                - updatedAt (dict): Date range filter for when photos were updated
                - isPublic (bool): Filter by public/private status
                - locked (bool): Filter by locked status
            include (list, optional): Extra fields to be returned for each Photo Object. 
                                   Will always be: signedUrls.

        Returns:
            dict: Response containing:
                - data (list): List of photo objects
                - meta (dict): Metadata about the response including:
                    - total (int): Total number of photos matching the filter
                    - limit (int): Maximum number of photos returned
                    - offset (int): Number of photos skipped

        Raises:
            Exception: If the request fails or returns an error status code.

        Example:
            ```python
            # Get all photos with pagination
            photos = acc.photos.get_filtered_photos(
                project_id="your_project_id",
                filter_params={
                    "limit": 50,
                    "offset": 0,
                    "sortBy": "createdAt",
                    "sortOrder": "desc"
                }
            )
            
            # Get photos with filters
            photos = acc.photos.get_filtered_photos(
                project_id="your_project_id",
                filter_params={
                    "mediaType": ["NORMAL", "VIDEO"],
                    "type": ["FIELD-REPORT", "ISSUE"],
                    "isPublic": True,
                    "takenAt": {
                        "start": "2024-01-01T00:00:00Z",
                        "end": "2024-03-20T23:59:59Z"
                    }
                },
                include=["signedUrls"]
            )
            ```

        Official Documentation:
            https://aps.autodesk.com/en/docs/acc/v1/reference/http/photos-getfilteredphotos-POST/
        """
        url = f"{self.base_url}/projects/{project_id}/photos/filter"
        headers = {
            "Authorization": f"Bearer {self.base.get_3leggedToken()}"
        }
        
        # Build request body
        body = {}
        if filter_params:
            body.update(filter_params)
            
        # Build query parameters
        params = {}
        if include:
            params["include"] = ",".join(include)
            
        response = self.base.post(url, json=body, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    