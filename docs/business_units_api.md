# Business Units API

The `AccBusinessUnitsApi` class provides methods to manage business units within your Autodesk Construction Cloud (ACC) account.
This API requires a 2-legged token with the `account:read` and `account:write` scopes.

## Get All Business Units

Retrieve all business units in your account.

```python
business_units = acc.business_units.get_business_units()
print(business_units)
```

## Get Business Unit by ID

Fetch details of a specific business unit using its ID.

```python
business_unit = acc.business_units.get_business_unit(business_unit_id="your_business_unit_id")
print(business_unit)
```

## Create a Business Unit

Create a new business unit in your account.

```python
new_business_unit = {
    "name": "New Business Unit",
    "description": "Description of the business unit"
}
created_unit = acc.business_units.post_business_unit(new_business_unit)
print(created_unit)
```

## Update a Business Unit

Modify an existing business unit's details.

```python
update_data = {
    "name": "Updated Business Unit Name",
    "description": "Updated description"
}
updated_unit = acc.business_units.patch_business_unit(
    business_unit_id="your_business_unit_id",
    data=update_data
)
print(updated_unit)
```
