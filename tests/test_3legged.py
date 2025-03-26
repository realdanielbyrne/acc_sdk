import os
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from acc_sdk import Authentication  # or your import
from acc_sdk import Acc  
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SESSION_KEY") # Required for session usage
CLIENT_ID = os.environ.get("AUTODESK_CLIENT_ID_WEB_APP")
CLIENT_SECRET = os.environ.get("AUTODESK_CLIENT_SECRET_WEB_APP")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
CALLBACK_URL = "http://127.0.0.1:5000/callback"
ACCOUNT_ID = os.environ.get("AUTODESK_ACCOUNT_ID")
SCOPES = [
    "user-profile:read",
    "user:read",
    "user:write",
    "viewables:read",
    "data:read",
    "data:write",
    "data:create",
    "data:search",
    "account:read",
    "account:write",
]

@app.route("/", methods=["GET"])
def index():
    session.clear()
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    """Called from form submission on index.html. Initiates OAuth2 flow.

    Returns:
        Redirect to callback URL if successful, or an error message if not.
    """
    email = request.form.get("email")
    session["user_email"] = email
    auth = Authentication(
        session=session,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        callback_url=CALLBACK_URL,
        admin_email=session["user_email"]
    )
    authorization_url = auth.get_authorization_url(scopes=SCOPES)
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    """Second step in the OAuth2 flow. Exchanges auth code for access token.

    Returns:
        Redirect to dashboard if successful, or an error message if not.
    """
    code = request.args.get("code")
    if not code:
        return "No authorization code received.", 400

    auth = Authentication(
        session=session,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        callback_url=CALLBACK_URL,
        admin_email=session["user_email"]
    )
    token_data = auth.request_authcode_access_token(code=code, scopes=SCOPES)
    if not token_data:
        return "Failed to exchange code for token", 400

    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    """
    Display a list of projects in the sidebar,
    plus placeholders for forms/templates in the main view.
    """
    # Reconstruct Authentication, pass session as token storage
    auth = Authentication(
        session=session,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        callback_url=CALLBACK_URL,
        admin_email=session["user_email"]
    )

    # Build an ACC instance (accapi) with the user’s authentication context
    acc = Acc(auth_client=auth, account_id=ACCOUNT_ID)

    # Retrieve user’s projects
    active_build_projects_params = {    
        'fields': 'name,jobNumber,type',    
        'filterTextMatch': 'equals'
    }
    projects = acc.projects.get_all_active_projects(filter_params=active_build_projects_params)
        
    return render_template(
            "dashboard.html",
            projects=projects
    )

@app.route("/get_project_data", methods=["POST"])
def get_project_data():
    """
    Called via js fetch to retrieve forms and templates for a specific project.
    Returns JSON for front-end usage.

    Returns:
        JSON response with forms and templates for the project.
    """
    project_id = request.form.get("project_id")

    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400

    # Reconstruct Authentication & ACC in the user’s session context
    auth = Authentication(
        session=session,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        callback_url=CALLBACK_URL,
        admin_email=session["user_email"]
    )
    acc = Acc(auth_client=auth, account_id=ACCOUNT_ID)

    # Query forms and form templates
    forms = acc.get_forms(project_id)    
    data = {
        "forms": forms        
    }
    return jsonify(data)

def run():
    app.run(debug=True)
    
if __name__ == "__main__":
    run()
