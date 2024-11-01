import requests
import csv

# Your Yelp API key
API_KEY = 'YOUR_YELP_API_KEY'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}
URL = 'https://api.yelp.com/v3/businesses/search'

# Parameters for the Yelp API request
PARAMS = {
    'location': 'Montreal',
    'categories': 'restaurants',
    'limit': 50,  # Maximum limit per request
}

# Function to fetch restaurants
def fetch_restaurants(offset=0):
    params = PARAMS.copy()
    params['offset'] = offset
    response = requests.get(URL, headers=HEADERS, params=params)
    return response.json().get('businesses', [])

# Collect all restaurants in a list
restaurants = []
offset = 0

while len(restaurants) < 500:
    new_restaurants = fetch_restaurants(offset)
    if not new_restaurants:
        break  # Stop if no more restaurants are returned
    restaurants.extend(new_restaurants)
    offset += 50

# Save the restaurant data to a CSV file
with open('restaurant.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Address', 'City', 'State', 'Zip Code', 'Rating', 'Review Count', 'Longitude', 'Latitude'])

    for restaurant in restaurants:
        name = restaurant.get('name', 'N/A')
        location = restaurant.get('location', {})
        address = location.get('address1', 'N/A').replace(',', '')  # Removing commas
        city = location.get('city', 'N/A')
        state = location.get('state', 'N/A')
        zip_code = location.get('zip_code', 'N/A')
        rating = restaurant.get('rating', 'N/A')
        review_count = restaurant.get('review_count', 'N/A')
        coordinates = restaurant.get('coordinates', {})
        longitude = coordinates.get('longitude', 'N/A')
        latitude = coordinates.get('latitude', 'N/A')

        writer.writerow([name, address, city, state, zip_code, rating, review_count, longitude, latitude])

print("Data saved to restaurant.csv successfully!")
