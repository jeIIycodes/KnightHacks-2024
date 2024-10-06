# blueprints/routes.py

from flask import Blueprint, request, jsonify, current_app, Response
from werkzeug.utils import secure_filename
import hashlib
import csv
import os
from io import StringIO
from AiPredictor.db import users_collection, test_connection
database_bp = Blueprint('database', __name__,url_prefix="/db")

@database_bp.route('/')
def index():
    return "Welcome to the Flask App!"

@database_bp.route('/test_db')
def test_db():

    if test_connection():
        return "Database connection successful!", 200
    else:
        return "Database connection failed!", 500

@database_bp.route('/submit', methods=['POST'])
def submit():
    # Determine if the request contains JSON or form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Extract and validate form data
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    # Hash the username
    username_hash = hashlib.sha256(username.encode()).hexdigest()

    # Process 'implemented' boolean
    implemented = data.get('implemented', 'false').lower() in ('true', '1', 'yes')

    # Extract other fields
    accelerators = data.get('accelerators', '')
    category = data.get('category', '')
    industry = data.get('industry', '')
    company_size = data.get('company_size', '')  # Optional
    challenges = data.get('challenges')

    # Handle challenges - accept comma-separated string or list
    if isinstance(challenges, str):
        challenges = [c.strip() for c in challenges.split(',') if c.strip()]
    elif isinstance(challenges, list):
        challenges = [str(c).strip() for c in challenges if str(c).strip()]
    else:
        challenges = []

    # Prepare the record to insert into MongoDB
    record = {
        'username_hash': username_hash,
        'implemented': implemented,
        'accelerators': accelerators,
        'category': category,
        'industry': industry,
        'company_size': company_size if company_size else None,
        'challenges': challenges
    }

    # Insert the record into MongoDB
    try:
        users_collection.insert_one(record)
        return jsonify({'message': 'Data submitted successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@database_bp.route('/export_csv')
def export_csv():
    try:
        # Fetch all records
        records = users_collection.find()

        # Create a StringIO object to write CSV data into memory
        csvfile = StringIO()
        fieldnames = ['username_hash', 'implemented', 'accelerators', 'category',
                      'industry', 'company_size', 'challenges', 'files']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            # Prepare the record to write
            row = {
                'username_hash': record.get('username_hash'),
                'implemented': record.get('implemented'),
                'accelerators': record.get('accelerators'),
                'category': record.get('category'),
                'industry': record.get('industry'),
                'company_size': record.get('company_size') if record.get('company_size') else '',
                'challenges': ','.join(record.get('challenges', [])),
                'files': ','.join(record.get('files', []))
            }
            writer.writerow(row)

        # Reset the pointer to the beginning
        csvfile.seek(0)

        return Response(
            csvfile.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=export.csv"}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
