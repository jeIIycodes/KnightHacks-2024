from datetime import date
from flask import Flask, url_for, render_template, request, session, redirect, flash
from flask_session import Session
from functools import wraps

# Import your Kinde authentication and other necessary modules
from kinde_sdk import Configuration, ApiException
from kinde_sdk.kinde_api_client import GrantType, KindeApiClient
from kinde_sdk.apis.tags import users_api
from kinde_sdk.model.user import User

import os

from assessment import CompanyForm

app = Flask(__name__)
app.config.from_object("config")
Session(app)

# In-memory storage for users and clients
in_memory_users = {}
user_clients = {}

# Kinde Configuration
configuration = Configuration(host=app.config["KINDE_ISSUER_URL"])
kinde_api_client_params = {
    "configuration": configuration,
    "domain": app.config["KINDE_ISSUER_URL"],
    "client_id": app.config["CLIENT_ID"],
    "client_secret": app.config["CLIENT_SECRET"],
    "grant_type": app.config["GRANT_TYPE"],
    "callback_url": app.config["KINDE_CALLBACK_URL"],
}
if app.config["GRANT_TYPE"] == GrantType.AUTHORIZATION_CODE_WITH_PKCE:
    kinde_api_client_params["code_verifier"] = app.config["CODE_VERIFIER"]

kinde_client = KindeApiClient(**kinde_api_client_params)

def get_authorized_data(kinde_client):
    user = kinde_client.get_user_details()
    return {
        "id": user.get("id"),
        "given_name": user.get("given_name"),
        "family_name": user.get("family_name"),
        "email": user.get("email"),
        "picture": user.get("picture"),
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    else:
        kinde_client = user_clients.get(session.get("user"))
        if kinde_client and kinde_client.is_authenticated():
            data = {"current_year": date.today().year}
            data.update(get_authorized_data(kinde_client))
            return render_template("home.html", user=data)
    return render_template("logged_out.html")

@app.route("/api/auth/login")
def login():
    return redirect(kinde_client.get_login_url())

@app.route("/api/auth/register")
def register():
    return redirect(kinde_client.get_register_url())

@app.route("/api/auth/kinde_callback")
def callback():
    kinde_client.fetch_token(authorization_response=request.url)
    data = {"current_year": date.today().year}
    data.update(get_authorized_data(kinde_client))
    session["user"] = data.get("id")
    user_clients[data.get("id")] = kinde_client

    user_id = data.get("id")

    if user_id not in in_memory_users:
        in_memory_users[user_id] = data  # Store user data in memory

    if is_new_user(user_id):
        return redirect(url_for("company_assessment"))  # Redirect new users to assessment

    return redirect(url_for("home"))

completed_assessment_users = set()

def is_new_user(user_id):
    return user_id not in completed_assessment_users

@app.route("/api/auth/logout")
def logout():
    user_clients[session.get("user")] = None
    session["user"] = None
    return redirect(
        kinde_client.logout(redirect_to=app.config["LOGOUT_REDIRECT_URL"])
    )

@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html", user=in_memory_users.get(session.get("user")))

@app.route("/loading")
@login_required
def loading():
    return render_template("loading.html", user=in_memory_users.get(session.get("user")))

@app.route("/decisions")
@login_required
def decisions():
    return render_template("decisions.html", user=in_memory_users.get(session.get("user")))

@app.route("/home")
@login_required
def gallery():
    return render_template("gallery.html", user=in_memory_users.get(session.get("user")))

@app.route("/company_assessment", methods=["GET", "POST"])
def company_assessment():
    form = CompanyForm()
    if not session.get("user"):
        return redirect(url_for('index'))

    if form.validate_on_submit():
        company_data = {
            "company_name": form.company_name.data,
            "implemented_products": form.implemented_products.data,
            "industry": form.industry.data,
            "program_start_date": form.program_start_date.data,
            "company_size": form.company_size.data,
            "location": form.location.data,
            "company_description": form.company_description.data,
            "current_challenges": form.current_challenges.data,
        }

        user_id = session.get("user")
        in_memory_users[user_id].update(company_data)
        completed_assessment_users.add(user_id)

        flash('Company information submitted successfully!', 'success')

        return redirect(url_for("dashboard"))

    return render_template("company_assessment.html", form=form, user=in_memory_users.get(session.get("user")))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get("user")
    user_data = in_memory_users.get(user_id, {})
    return render_template("dashboard.html", **user_data, user=in_memory_users.get(user_id))

# Additional routes and functionalities as needed

if __name__ == '__main__':
    app.run(debug=True)
