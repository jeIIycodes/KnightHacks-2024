# db.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from AiPredictor.config import Config

# Initialize MongoDB client
client = MongoClient(
    Config.MONGO_URI,
    server_api=ServerApi('1'),  # Specify server API version
    maxPoolSize=50,
    connect=True  # Enable connection pooling
)

# Access the desired database
db = client.get_database('knighthacks2024')  # Replace with your database name

# Access the desired collection
users_collection = db.get_collection('accelerator_logs')  # Replace with your collection name

# Function to test the database connection
def test_connection():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False
