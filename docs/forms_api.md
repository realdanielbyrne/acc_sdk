# Forms API

The `AccFormsApi` provides methods to interact with forms within Autodesk Construction Cloud (ACC), allowing users to retrieve, create, and modify form data.

## Retrieve Forms

Fetch forms from a project with optional filtering and pagination.

```python
forms = acc.forms.get_forms(project_id="your_project_id", limit=10)
print(forms)
```

## Retrieve Form Templates

Get available form templates for a project.

```python
templates = acc.forms.get_templates(project_id="your_project_id")
print(templates)
```

## Get Forms from the Past 30 Days

Fetch forms created within the last 30 days.

```python
recent_forms = acc.forms.get_forms_for_past30(project_id="your_project_id")
print(recent_forms)
```

## Create a New Form

Create a form based on a template.

```python
form_data = {"customValues": {"field1": "value1"}}
new_form = acc.forms.post_form(project_id="your_project_id", template_id="template_id", data=form_data)
print(new_form)
```

## Update Form Details

Update existing form details.

```python
update_data = {"customValues": {"field1": "updated_value"}}
updated_form = acc.forms.patch_form(project_id="your_project_id", template_id="template_id", form_id="form_id", data=update_data)
print(updated_form)
```

## Update Form Fields

Batch update form fields, both tabular and non-tabular.

```python
batch_data = {"customValues": {"field1": "new_value"}}
updated_fields = acc.forms.put_form(project_id="your_project_id", form_id="form_id", data=batch_data)
print(updated_fields)
```
