# config.py

import os


class Config:
    # Replace with your actual MongoDB URI
    MONGO_URI = "mongodb+srv://admin:qodQoeC444Pk9AT2@knighthacks2024.tvjpc.mongodb.net/?retryWrites=true&w=majority&appName=knighthacks2024"

    # Directory to save uploaded files
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    # Ensure the upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Secret key for session management (replace with a strong secret in production)
    SECRET_KEY = '1348e9a78a52e9898d04a1f828945591e4086e25ff92c925faf073749cfbb11a'
