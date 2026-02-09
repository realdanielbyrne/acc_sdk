#!/usr/bin/env python3
"""Add or remove a user across active ACC projects, optionally filtered by type.

Usage:
    python manage_project_user.py add user@example.com --role productadmin
    python manage_project_user.py add user@example.com --role productmember --project-type Paving
    python manage_project_user.py remove user@example.com
    python manage_project_user.py remove user@example.com --project-type Excavation
"""

import argparse
import os
import sys
import time

from dotenv import load_dotenv

from acc_sdk import Authentication, Acc
from acc_sdk.project_users import AccProjectUsersApi

ROLE_MAP = {
    "productadmin": AccProjectUsersApi.productadmin,
    "productmember": AccProjectUsersApi.productmember,
}


def fetch_projects(acc, project_type: str | None) -> list[dict]:
    filter_params = {}
    if project_type:
        filter_params["filter[type]"] = project_type

    projects = acc.projects.get_all_active_projects(filter_params=filter_params or None)

    if not projects and project_type:
        print("Server-side filter returned no results, trying client-side filter...")
        all_projects = acc.projects.get_all_active_projects()
        projects = [p for p in all_projects if p.get("type") == project_type]

    return projects or []


def add_user_to_project(acc, project_id: str, email: str, products: list[dict]) -> str:
    existing_user = acc.project_users.get_user_by_email(
        project_id=project_id, email=email
    )
    if existing_user:
        acc.project_users.patch_user(
            project_id=project_id,
            target_user_id=existing_user["id"],
            data={"products": products},
        )
        return "updated"
    else:
        acc.project_users.post_user(
            project_id=project_id,
            user={"email": email, "products": products},
        )
        return "added"


def remove_user_from_project(acc, project_id: str, email: str) -> str:
    existing_user = acc.project_users.get_user_by_email(
        project_id=project_id, email=email
    )
    if existing_user:
        acc.project_users.delete_user(
            project_id=project_id, target_user_id=existing_user["id"]
        )
        return "removed"
    else:
        return "not found"


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Add or remove a user across active ACC projects"
    )
    parser.add_argument(
        "action", choices=["add", "remove"], help="Action to perform"
    )
    parser.add_argument("email", help="Target user email address")
    parser.add_argument(
        "--role",
        choices=["productadmin", "productmember"],
        default="productmember",
        help="Product role to assign when adding (default: productmember)",
    )
    parser.add_argument(
        "--project-type",
        default=None,
        help="Filter projects by type (e.g. Paving, Bridge). Omit for all active projects",
    )
    parser.add_argument("--client-id", default=os.getenv("AUTODESK_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.getenv("AUTODESK_CLIENT_SECRET"))
    parser.add_argument("--admin-email", default=os.getenv("AUTODESK_ADMIN_EMAIL"))
    args = parser.parse_args()

    if not args.client_id or not args.client_secret:
        print(
            "Error: CLIENT_ID and CLIENT_SECRET are required. "
            "Set them in .env or pass via --client-id / --client-secret."
        )
        sys.exit(1)

    print("Authenticating...")
    auth = Authentication(
        client_id=args.client_id,
        client_secret=args.client_secret,
        admin_email=args.admin_email or "",
    )
    auth.request_2legged_token(
        scopes=["account:read", "account:write", "data:read", "data:write"]
    )
    print("Authentication successful.")

    acc = Acc(auth_client=auth)

    type_label = args.project_type or "all"
    print(f"Fetching active projects (type={type_label})...")
    projects = fetch_projects(acc, args.project_type)

    if not projects:
        print(f"No active projects found (type={type_label}).")
        sys.exit(0)

    print(f"Found {len(projects)} project(s).\n")

    products = ROLE_MAP[args.role]
    successes = []
    skipped = []
    failures = []

    for project in projects:
        project_id = project["id"]
        project_name = project.get("name", project_id)
        print(f"Processing: {project_name} ({project_id})")

        try:
            if args.action == "add":
                result = add_user_to_project(acc, project_id, args.email, products)
                print(f"  {result.capitalize()} {args.email} as {args.role}")
                successes.append(project_name)
            else:
                result = remove_user_from_project(acc, project_id, args.email)
                if result == "removed":
                    print(f"  Removed {args.email}")
                    successes.append(project_name)
                else:
                    print(f"  User {args.email} not found, skipping")
                    skipped.append(project_name)
        except Exception as exc:
            print(f"  Error: {exc}")
            failures.append((project_name, str(exc)))

        time.sleep(0.25)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Successful: {len(successes)}/{len(projects)}")
    for name in successes:
        print(f"  [OK] {name}")
    if skipped:
        print(f"Skipped: {len(skipped)}/{len(projects)}")
        for name in skipped:
            print(f"  [SKIP] {name}")
    if failures:
        print(f"Failed: {len(failures)}/{len(projects)}")
        for name, err in failures:
            print(f"  [FAIL] {name}: {err}")


if __name__ == "__main__":
    main()

