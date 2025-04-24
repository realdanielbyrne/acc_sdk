# Companies API

The `AccCompaniesApi` class provides methods to manage companies within your Autodesk Construction Cloud (ACC) account.
This API requires a 2-legged token with the `account:read` scope for GET requests and `account:write` scope for POST and PATCH requests.

## Get All Companies

Retrieve a list of companies in your account with optional filtering and pagination.

```python
# Get all companies with default pagination (20 items per page)
companies = acc.companies.get_companies()

# Get companies with custom filters
filtered_companies = acc.companies.get_companies(
    filter_name="Construction Co",
    filter_trade="Concrete",
    limit=50,
    offset=0
)
```

## Get Company by ID

Fetch details of a specific company using its ID.

```python
company = acc.companies.get_company(company_id="your_company_id")
print(company)
```

## Update Company Details

Modify an existing company's information.

```python
update_data = {
    "name": "Updated Company Name",
    "trade": "Concrete",
    "phone": "(503)623-1525"
}
updated_company = acc.companies.update_company(
    account_id="your_account_id",
    company_id="your_company_id",
    data=update_data
)
print(updated_company)
```

## Update Company Image

Upload or update a company's logo or image.

```python
# Update company image with auto-detected MIME type
updated_company = acc.companies.update_company_image(
    account_id="your_account_id",
    company_id="your_company_id",
    file_path="path/to/company_logo.png"
)

# Update company image with specific MIME type
updated_company = acc.companies.update_company_image(
    account_id="your_account_id",
    company_id="your_company_id",
    file_path="path/to/company_logo.png",
    mime_type="image/png"
)
```
