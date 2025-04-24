# Photos API

The `AccPhotosApi` class provides methods to interact with photos and media in Autodesk Construction Cloud (ACC).
This API requires a 3-legged token with the `data:read` scope.

## Get a Single Photo

Retrieve details of a specific photo or video from a project.

```python
# Get basic photo information
photo = acc.photos.get_photo(
    project_id="your_project_id",
    photo_id="your_photo_id"
)
print(f"Photo title: {photo['title']}")
print(f"Description: {photo['description']}")

# Get photo with signed URLs for direct access
photo = acc.photos.get_photo(
    project_id="your_project_id",
    photo_id="your_photo_id",
    include=["signedUrls"]
)
print(f"File URL: {photo['signedUrls']['fileUrl']}")
print(f"Thumbnail URL: {photo['signedUrls']['thumbnailUrl']}")
```

## Get Filtered Photos

Retrieve a filtered list of photos from a project with various filtering options and pagination support.

```python
# Get all photos with pagination
photos = acc.photos.get_filtered_photos(
    project_id="your_project_id",
    filter_params={
        "limit": 50,
        "offset": 0,
        "sortBy": "createdAt",
        "sortOrder": "desc"
    },
    follow_pagination=True  # Get all results
)

# Get photos with specific filters
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

The `get_filtered_photos` method supports various filter parameters:

- `limit` and `offset` for pagination
- `sortBy` and `sortOrder` for sorting results
- `mediaType` to filter by type (NORMAL, INFRARED, PHOTOSPHERE, VIDEO)
- `type` to filter by object type
- `createdBy` to filter by creator
- Date range filters for `takenAt`, `createdAt`, and `updatedAt`
- `isPublic` and `locked` status filters

The response includes:

- `data`: List of photo objects with details like title, description, media type, creation date, etc.
- `meta`: Metadata including total count and pagination information
- Optional `signedUrls` for direct access to media files
