import requests
import csv
import os
from marshmallow import ValidationError
from app.models.restaurant_schema import RestaurantSchema

class RestaurantScrapperService:
    BASE_URL = "https://api.yelp.com/v3/businesses/search"

    def __init__(self, api_key, csv_filename='restaurants.csv'):
        self.api_key = api_key
        self.restaurant_schema = RestaurantSchema()
        self.directory = os.path.join(os.path.dirname(__file__), 'restaurant_data')
        
        # Ensure the directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Define the full path to the CSV file
        self.csv_file_path = os.path.join(self.directory, csv_filename)

    def get_total_available_restaurants(self, location="Montreal, QC", term="restaurants"):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            params = {"location": location, "term": term, "limit": 1}
            response = requests.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            total_results = data.get("total", 0)
            print(f"Total number of businesses available: {total_results}")
            return min(total_results, 1000)  # Yelp API cap at 1,000 results
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
            return 0

    def get_restaurants(self, location="Montreal, QC", term="restaurants"):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        restaurants = []
        offset = 0
        limit = 50
        total_results = self.get_total_available_restaurants(location, term)

        try:
            while offset < total_results:
                params = {"location": location, "term": term, "limit": limit, "offset": offset}
                response = requests.get(self.BASE_URL, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                businesses = data.get("businesses", [])

                if not businesses:
                    break  # No more businesses to fetch

                for business in businesses:
                    try:
                        name = business.get("name", "Unknown")
                        rating = business.get("rating", 0.0)
                        location_data = business.get("location", {})
                        address = location_data.get("address1", "No address provided")
                        city = location_data.get("city", "Unknown")
                        state = location_data.get("state", "Unknown")
                        postal_code = location_data.get("zip_code", "Unknown")
                        country = location_data.get("country", "Unknown")
                        coordinates = business.get("coordinates", {})
                        longitude = coordinates.get("longitude", 0.0)
                        latitude = coordinates.get("latitude", 0.0)

                        restaurant_data = {
                            "name": name,
                            "rating": rating,
                            "address": address,
                            "city": city,
                            "state": state,
                            "postal_code": postal_code,
                            "country": country,
                            "longitude": longitude,
                            "latitude": latitude
                        }

                        self.restaurant_schema.load(restaurant_data)
                        restaurants.append(restaurant_data)
                    except ValidationError as ve:
                        print(f"Validation error: {ve}")
                        continue

                offset += limit  # Increment the offset by the limit
                self.write_to_csv(restaurants)
                restaurants.clear()  # Clear the list to free memory

            return {"message": f"Data fetching and storage completed. Total records fetched: {total_results}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def write_to_csv(self, data):
        file_exists = os.path.isfile(self.csv_file_path)
        with open(self.csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)


    def get_total_available_restaurants(self, location="Montreal, QC", term="restaurants"):
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            # Make an initial request to get the total number of results
            params = {
                "location": location,
                "term": term,
                "limit": 1  # Only request 1 item to get the total count
            }
            response = requests.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the total number of results
            total_results = data.get("total", 0)
            print(f"Total number of businesses available: {total_results}")  # This prints the total number

            # Return the total number, capped at 1,000 due to Yelp API limits
            return min(total_results, 1000)
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
            return 0
