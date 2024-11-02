import os

class Config:
    # Secret key for session management and security (set this in your environment)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-default-secret-key'

    # MongoDB connection URI (set this in your environment)
    MONGO_URI = os.environ.get('MONGO_URI') or 'your-default-mongo-uri'

    # Yelp API Key (set this in your environment)
    YELP_API_KEY = os.environ.get('YELP_API_KEY') or 'your-default-yelp-api-key'
