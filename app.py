import random
import re
from datetime import date

import requests
from flask import Flask, url_for, render_template, request, session, redirect, flash, jsonify, current_app
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
app.secret_key = '5fd22f708895fd5e1b05a04b8d21e7377db75a2bf3176cfd758c9189ed315165'
# In-memory storage for users and clients
in_memory_users = {}
user_clients = {}


# Function to extract company name using Regex
def extract_company_name(accelerator_name):
    match = re.search(r"Your (.+)", accelerator_name)
    if match:
        return match.group(1).replace(" ", "")  # Remove spaces from the company name
    return None


# Function to get the company logo or a random one if not found
def get_company_logo(company_name):
    # Get the full path of the logos folder in the static directory
    logos_folder = os.path.join(current_app.root_path, 'static', 'img', 'logos')

    # If company_name is provided, check for its logo
    if company_name:
        logo_filename = f"{company_name}.png"
        logo_path = os.path.join(logos_folder, logo_filename)
        if os.path.exists(logo_path):
            # Return the URL for the company's logo
            return url_for('static', filename=f'img/logos/{logo_filename}')

    # If company logo is not found, select a random logo from the folder
    logos = os.listdir(logos_folder)
    if logos:
        random_logo = random.choice(logos)
        return url_for('static', filename=f'img/logos/{random_logo}')

    # If no logos are available, return a default logo image (optional)
    return url_for('static', filename='img/logos/default.png')


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


# Route to fetch cards from the external API using user session data
@app.route("/api/get_cards", methods=["POST", "GET"])
@login_required
def get_cards():
    # Define the URL for the external API (localhost:8000)
    external_api_url = "http://localhost:8000/recommend/get_recommendations"

    # Get user's data from the session
    company_name = session.get('company_name', 'Unknown Company')
    implemented_products = session.get('implemented_products', [])
    unimplemented_products = session.get('unimplemented_products', [])
    industry = session.get('industry', 'Unknown Industry')
    custom_industry = session.get('custom_industry', None)
    program_start_date = session.get('program_start_date', date.today().strftime('%Y-%m-%d'))
    company_size = session.get('company_size', 1)
    location = session.get('location', 'Unknown Location')
    company_description = session.get('company_description', '')
    current_challenges = session.get('current_challenges', [])

    # If custom industry is specified, use that instead of the selected industry
    if custom_industry:
        industry = custom_industry

    # Example data to send in the POST request using session data
    payload = {
        "company_name": company_name,
        "implemented_products": implemented_products+unimplemented_products,
        "implemented_products_is_implemented": [True] * len(implemented_products) + [False] * len(unimplemented_products),
        "industry": industry,
        "program_start_date": program_start_date,
        "company_size": company_size,
        "location": location,
        "Optional Company Description": company_description,
        "current_challenges": current_challenges,
        "number_of_recommendations": 5
    }

    try:
        # Send the request to the external API
        response = requests.post(external_api_url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON data
            recommendations = response.json().get('recommendations', [])

            # Format the recommendations into card data for the frontend
            cards = []
            for i, rec in enumerate(recommendations):
                # Extract company name from accelerator name
                company_name = extract_company_name(rec["accelerator"])

                # Find the appropriate image or get a random one
                image_url = get_company_logo(company_name) if company_name else get_company_logo(None)

                # Append the card data
                cards.append({
                    "id": str(i + 1),
                    "title": rec["accelerator"],
                    "imageUrl": image_url,
                    "description": rec["description"],
                    "type":rec["accelerator"].split(" ")[0],
                })

            return jsonify({"cards": cards})
        else:
            # If the external API request fails, return an error message
            return jsonify({"error": "Failed to fetch cards from external API."}), 500

    except Exception as e:
        # Catch any exceptions during the request
        print(f"Error fetching cards: {e}")
        return jsonify({"error": "An error occurred while fetching cards."}), 500


# Route to handle swipe actions
@app.route("/api/swipe", methods=["POST"])
@login_required
def swipe():
    data = request.json
    action = data.get("action")  # 'like' or 'dislike'
    card_id = data.get("card_id")  # Identifier for the card
    user_id = session.get("user")

    if not action or not card_id:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    # Hash the user_id (or use another identifier)
    user_hash = hashlib.sha256(user_id.encode()).hexdigest()

    # Prepare the record to insert into MongoDB
    record = {
        'user_id_hash': user_hash,
        'card_id': card_id,
        'action': action,
        'timestamp': datetime.utcnow()  # Add timestamp for tracking
    }

    # Insert the record into MongoDB
    try:
        users_collection.insert_one(record)
    except Exception as e:
        print(f"Error saving swipe to MongoDB: {e}")
        return jsonify({"status": "error", "message": "Error saving swipe to database"}), 500

    # Send swipe data to external server (localhost:8000)
    external_api_url = "http://localhost:8000/api/swipe"
    payload = {
        "user_id": user_hash,  # Send the hashed user ID
        "card_id": card_id,
        "action": action
    }

    try:
        # Send the request to the external server
        response = requests.post(external_api_url, json=payload)

        # Check if the external API request was successful
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Swipe recorded and forwarded successfully"}), 200
        else:
            print(f"Error sending swipe to external server: {response.status_code}, {response.text}")
            return jsonify({"status": "error", "message": "Failed to send swipe to external server"}), 500

    except Exception as e:
        print(f"Error sending swipe to external server: {e}")
        return jsonify({"status": "error", "message": "Error occurred while sending swipe to external server"}), 500



@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    else:
        kinde_client = user_clients.get(session.get("user"))
        if kinde_client and kinde_client.is_authenticated():
            data = {"current_year": date.today().year}
            data.update(get_authorized_data(kinde_client))
            return render_template("home.html", user=in_memory_users.get(session.get("user")))
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

# app.py

@app.route("/quiz")
@login_required
def quiz():
    if not session.get("user"):
        return redirect(url_for("login"))

    else:
        kinde_client = user_clients.get(session.get("user"))
        if kinde_client and kinde_client.is_authenticated():
            data = {"current_year": date.today().year}
            data.update(get_authorized_data(kinde_client))
            return render_template("swipe_quiz.html", user=in_memory_users.get(session.get("user")))
    return render_template("logged_out.html")


@app.route("/loading")
@login_required
def loading():
    return render_template("loading.html", user=in_memory_users.get(session.get("user")))

@app.route("/decisions")
@login_required
def decisions():
    return render_template("decisions.html", user=in_memory_users.get(session.get("user")))

@app.route("/results")
@login_required
def results():
    return render_template("gallery.html", user=in_memory_users.get(session.get("user")))



@app.route("/company_assessment", methods=["GET", "POST"])
def company_assessment():
    form = CompanyForm()

    if request.method == "POST" and form.validate_on_submit():
        # Store form data in session
        session['company_name'] = form.company_name.data
        session['implemented_products'] = form.implemented_products.data
        session['unimplemented_products'] = form.unimplemented_products.data
        session['industry'] = form.industry.data
        session['custom_industry'] = form.custom_industry.data if form.industry.data == 'other' else None
        session['program_start_date'] = form.program_start_date.data.strftime('%Y-%m-%d')
        session['company_size'] = form.company_size.data
        session['location'] = form.location.data
        session['company_description'] = form.company_description.data
        session['current_challenges'] = form.current_challenges.data

        # Flash success message
        flash('Company assessment submitted successfully!', 'success')

        # Redirect to the quiz page
        return redirect(url_for('quiz'))

    return render_template("company_assessment.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session.get("user")
    user_data = in_memory_users.get(user_id, {})
    return render_template("dashboard.html", **user_data, user=in_memory_users.get(user_id))

# Additional routes and functionalities as needed

if __name__ == '__main__':
    app.run(debug=True)
