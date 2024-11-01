import requests
import csv
import time

from config import Config

# Replace 'YOUR_API_KEY' with your actual Yelp API key
HEADERS = {'Authorization': f'Bearer {Config.YELP_API_KEY}'}
SEARCH_ENDPOINT = 'https://api.yelp.com/v3/businesses/search'

# Parameters
LOCATION = 'Montreal, QC'
CATEGORIES = 'restaurants'
LIMIT = 50  # Maximum number of results per request
TOTAL_RESULTS = 500  # Total number of results desired

def fetch_restaurants():
    all_restaurants = []
    for offset in range(0, TOTAL_RESULTS, LIMIT):
        params = {
            'location': LOCATION,
            'categories': CATEGORIES,
            'limit': LIMIT,
            'offset': offset
        }
        response = requests.get(SEARCH_ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            all_restaurants.extend(data.get('businesses', []))
            # Respect Yelp's rate limit
            time.sleep(1)
        else:
            print(f"Error: {response.status_code}")
            break
    return all_restaurants

def save_to_csv(restaurants, filename='restaurants.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'City', 'State', 'Zip Code', 'Latitude', 'Longitude', 'Cuisine Type', 'Review Count', 'Rating'])
        for restaurant in restaurants:
            name = restaurant.get('name', '')
            location = restaurant.get('location', {})
            address = ' '.join(location.get('display_address', []))
            city = location.get('city', '')
            state = location.get('state', '')
            zip_code = location.get('zip_code', '')
            coordinates = restaurant.get('coordinates', {})
            latitude = coordinates.get('latitude', '')
            longitude = coordinates.get('longitude', '')
            categories = [category['title'] for category in restaurant.get('categories', [])]
            cuisine_type = ", ".join(categories)
            review_count = restaurant.get('review_count', 0)
            rating = restaurant.get('rating', 0)
            writer.writerow([name, address, city, state, zip_code, latitude, longitude, cuisine_type, review_count, rating])

if __name__ == '__main__':
    restaurants = fetch_restaurants()
    save_to_csv(restaurants)
    print(f"Saved {len(restaurants)} restaurants to 'restaurants.csv'")
