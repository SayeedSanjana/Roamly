import requests
import csv
import time
from config import Config

HEADERS = {'Authorization': f'Bearer {Config.YELP_API_KEY}'}
SEARCH_ENDPOINT = 'https://api.yelp.com/v3/businesses/search'

# Parameters
LOCATION = 'Montreal, QC'
# Categories for outdoor activities
CATEGORIES = 'hiking,parks,beaches,gardens,zoos,golf,fishing,boating,campgrounds,skiresorts,horsebackriding,outdooradventures,rockclimbing,sports_clubs,bikerentals'  
LIMIT = 50  # Maximum number of results per request
TOTAL_RESULTS = 500  # Total number of results desired

def fetch_outdoor_activities():
    all_activities = []
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
            businesses = data.get('businesses', [])
            all_activities.extend(businesses)
            time.sleep(1)  # Respect Yelp's rate limit
        else:
            print(f"Error: {response.status_code} - {response.text}")
            break
    return all_activities

def save_to_csv(activities, filename='outdoor_activities.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Address', 'City', 'State', 'Zip Code', 'Latitude', 'Longitude', 'Rating', 'Category'])
        for activity in activities:
            name = activity.get('name', '')
            location = activity.get('location', {})
            address = ' '.join(location.get('display_address', []))
            city = location.get('city', '')
            state = location.get('state', '')
            zip_code = location.get('zip_code', '')
            coordinates = activity.get('coordinates', {})
            latitude = coordinates.get('latitude', '')
            longitude = coordinates.get('longitude', '')
            rating = activity.get('rating', 0)
            # Collect and format the categories
            categories = [category['title'] for category in activity.get('categories', [])]
            category = ", ".join(categories)
            writer.writerow([name, address, city, state, zip_code, latitude, longitude, rating, category])

if __name__ == '__main__':
    activities = fetch_outdoor_activities()
    save_to_csv(activities)
    print(f"Saved {len(activities)} outdoor activities to 'outdoor_activities.csv'")
