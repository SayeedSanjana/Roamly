import os
import sys
import requests
import csv
import time

# Add the Roamly root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Config  # Correct import path

# Replace 'YOUR_API_KEY' with your actual Yelp API key
HEADERS = {'Authorization': f'Bearer {Config.YELP_API_KEY}'}
SEARCH_ENDPOINT = 'https://api.yelp.com/v3/businesses/search'

# Parameters
LOCATION = 'Montreal, QC'
CATEGORIES = ['publictransport', 'parking', 'bikerentals']  # Transportation-related categories
LIMIT = 50  # Maximum number of results per request
TOTAL_RESULTS = 500  # Total number of results desired

def fetch_transportation(category):
    all_transportation = []
    for offset in range(0, TOTAL_RESULTS, LIMIT):
        params = {
            'location': LOCATION,
            'categories': category,
            'limit': LIMIT,
            'offset': offset
        }
        response = requests.get(SEARCH_ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            all_transportation.extend(data.get('businesses', []))
            # Respect Yelp's rate limit
            time.sleep(1)
        else:
            print(f"Error: {response.status_code}")
            break
    return all_transportation

def save_to_csv(data, filename='transportation.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'City', 'State', 'Zip Code', 'Latitude', 'Longitude', 'Category', 'Review Count', 'Rating'])
        for item in data:
            name = item.get('name', '')
            location = item.get('location', {})
            address = ' '.join(location.get('display_address', []))
            city = location.get('city', '')
            state = location.get('state', '')
            zip_code = location.get('zip_code', '')
            coordinates = item.get('coordinates', {})
            latitude = coordinates.get('latitude', '')
            longitude = coordinates.get('longitude', '')
            categories = [category['title'] for category in item.get('categories', [])]
            category_type = ", ".join(categories)
            review_count = item.get('review_count', 0)
            rating = item.get('rating', 0)
            writer.writerow([name, address, city, state, zip_code, latitude, longitude, category_type, review_count, rating])

if __name__ == '__main__':
    all_transportation = []
    for category in CATEGORIES:
        print(f"Fetching data for category: {category}")
        transportation = fetch_transportation(category)
        all_transportation.extend(transportation)
    
    save_to_csv(all_transportation, filename='transportation.csv')
    print(f"Saved {len(all_transportation)} transportation locations to 'transportation.csv'")
