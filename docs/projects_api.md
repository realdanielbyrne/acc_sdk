# Projects API

The `AccProjectsApi` provides methods to manage projects within Autodesk Construction Cloud (ACC), including creating new projects, fetching project details, and updating project information.

## Get All Active Projects

Gets all projects that are active in the account.

```python
projects = acc.projects.get_all_active_projects()
```

## Get Active Projects With Pagination

Gets all projects that are active in the account but limits the number of projects returned.

```python
projects = acc.projects.get_active_projects(filter_params={'limit': 10, 'offset': 0})
```

## Get All Projects

Gets all projects in the account.

```python
projects = acc.projects.get_projects()
```

## Get Limited Project Details

Get Projects and limit the metadata fields returned.

```python
projects = acc.projects.get_projects(filter_params={'fields':"accountId,name,jobNumber"})
print(projects[0])
```

## Get Projects Filtered

Here we show how to get active projects with a specific status, and limit the metadata fields returned.

```python
active_build_projects_params = {
    'fields': 'name,jobNumber,type,status',
    'filter[status]': 'active',
    'filterTextMatch': 'equals'
}
projects = acc.projects.get_projects(filter_params=active_build_projects_params)
```

## Create a project

Creates a new project. You can create the project directly,
or clone it from a project template.

The project dictionary needs at least name and type fields defined, and the
name must be unique even among deleted projects since they are not actually deleted.

```python
test_project = {
        "jobNumber": "9999W",
        "name": "My unique project name",
        "type": "Wall Construction",
        "latitude": "34.7749",
        "longitude": "-125.4194",
        "timezone":"America/Chicago"
}
new_project = acc.projects.post_project(test_project)
```

## Create a list of projects

```python
def get_active_projects():
  jobs_dict = get_active_jobs_from_your_db()

  # map project types to template ids
  template_mapping = {
    'ProjectType1': {'projectId': 'c506442f-0ba5-4d9d-9ff8-70e0b02935b1'},
    'ProjectType2': {'projectId': '38c0c641-d6ba-4772-873d-7740c5bdf8f1'},
    'ProjectType3': {'projectId': '5758b3a0-36a4-41e9-8143-8fde80419eb6'},
    'ProjectType4': {'projectId': '636cfcf8-cd99-4086-af74-4c7384653d40'}
  }
  for project in result:
    project['template'] = template_mapping.get(project['type'])

  return result

def create_projects(projects):
  if projects is None or len(projects) == 0:
    return
  for project in projects:
    project['id'] = acc.projects.post_project(project)
  return projects

jobs = get_active_projects()
new_projects = create_projects(jobs)
```
