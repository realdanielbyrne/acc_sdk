# Sheets API

The `AccSheetsApi` class provides methods to manage sheets, version sets, uploads, exports, and collections within Autodesk Construction Cloud (ACC).
Ensure your `Authentication` instance has a 3-legged token with scopes `data:read` and `data:write` to use these methods.

Below are the main functionalities, along with usage examples:

## Managing Version Sets

Version sets group sheets by their issuance date.

### Create a Version Set

```python
from datetime import datetime
version_set = acc.sheets.create_version_set(
    project_id="your_project_id",
    issuance_date="2024-03-25",
    name="Version Set 1"
)
```

### Get All Version Sets

```python
version_sets = acc.sheets.get_version_sets(project_id="your_project_id")
```

### Update a Version Set

```python
acc.sheets.patch_version_set(
    project_id="your_project_id",
    version_set_id="version_set_id",
    issuance_date="2024-03-26",
    name="Updated Version Set"
)
```

### Delete a Version Set

```python
acc.sheets.delete_version_set(
    project_id="your_project_id",
    version_set_id="version_set_id"
)
```

## Uploading Sheets

Upload sheets to Autodesk using Object Storage Service (OSS).

```python
bucket_key, object_key = acc.sheets.upload_file_to_autodesk("project_id", "sheet.pdf")
signed_url_info = acc.sheets.get_signed_s3_upload(bucket_key, object_key)
status_code = acc.sheets.upload_pdf_to_signed_url(signed_url_info["url"], "path/to/sheet.pdf")
upload_response = acc.sheets.complete_s3_upload(bucket_key, object_key, signed_url_info["uploadKey"])
```

## Managing Sheets

### Retrieve Sheets

```python
sheets = acc.sheets.get_sheets(project_id="your_project_id", follow_pagination=True)
```

### Batch Update Sheets

```python
updated_sheets = acc.sheets.batch_update_sheets(
    project_id="your_project_id",
    ids=["sheet_id_1", "sheet_id_2"],
    updates={"versionSetId": "new_version_set_id"}
)
```

### Batch Delete Sheets

```python
acc.sheets.batch_delete_sheets(
    project_id="your_project_id",
    ids=["sheet_id_1", "sheet_id_2"]
)
```

## Exporting Sheets

Export sheets as PDF files.

### Create Export Job

```python
export_job = acc.sheets.export_sheets(
    project_id="your_project_id",
    options={"outputFileName": "sheets_export.pdf"},
    sheets=["sheet_id_1", "sheet_id_2"]
)
```

### Check Export Status

```python
export_status = acc.sheets.get_export_status(
    project_id="your_project_id",
    export_id=export_job["id"]
)
```

## Managing Collections

Collections organize sheets within a project.

### Retrieve All Collections

```python
collections = acc.sheets.get_collections(project_id="your_project_id", follow_pagination=True)
```

### Retrieve a Specific Collection

```python
collection = acc.sheets.get_collection(
    project_id="your_project_id",
    collection_id="collection_id"
)
```
