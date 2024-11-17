import pandas as pd
from app.models.restaurant_schema import RestaurantSchema
from app.models.dummy_users_schema import DummyUserVisitsSchema
from app.models.indoor_activities_schema import IndoorActivitiesSchema
from app.models.outdoor_activities_schema import OutdoorActivitiesSchema
from app.models.transportation_schema import TransportationSchema


class DataService:
    def __init__(self, db):
        self.db = db
        self.restaurant_schema = RestaurantSchema()
        self.dummy_user_visits_schema = DummyUserVisitsSchema()
        self.indoor_activities_schema = IndoorActivitiesSchema()
        self.outdoor_activities_schema = OutdoorActivitiesSchema()
        self.transportation_schema = TransportationSchema()

    def load_data(self):
        # Load CSV files
        dummy_user_visits = pd.read_csv('dummy_user_visits.csv', encoding='latin1')
        indoor_activities = pd.read_csv('indoor_activities.csv', encoding='latin1')
        outdoor_activities = pd.read_csv('outdoor_activities.csv', encoding='latin1')
        restaurants = pd.read_csv('restaurants.csv', encoding='latin1')
        transportation = pd.read_csv('transportation.csv', encoding='latin1')

        # Rename columns to match schema field names
        restaurants = restaurants.rename(columns={
            'Name': 'name',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Zip Code': 'zip_code',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Cuisine Type': 'cuisine_type',
            'Review Count': 'review_count',
            'Rating': 'rating',
            'Foodtime': 'food_time'
        })

        dummy_user_visits = dummy_user_visits.rename(columns={
            'User': 'user',
            'Category': 'category',
            'Place': 'place',
            'Address': 'address',
            'Detail': 'detail',
            'Rating': 'rating'
        })

        indoor_activities = indoor_activities.rename(columns={
            'Name': 'name',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Zip Code': 'zip_code',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Rating': 'rating',
            'Category': 'category'
        })

        outdoor_activities = outdoor_activities.rename(columns={
            'Name': 'name',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Zip Code': 'zip_code',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Rating': 'rating',
            'Category': 'category'
        })

        transportation = transportation.rename(columns={
            'Name': 'name',
            'Address': 'address',
            'City': 'city',
            'State': 'state',
            'Zip Code': 'zip_code',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Category': 'category',
            'Review Count': 'review_count',
            'Rating': 'rating'
        })

        # Function to validate and insert data
        def insert_data(collection, data, schema):
            valid_data = []
            for record in data:
                errors = schema.validate(record)
                if not errors:
                    valid_data.append(record)
                else:
                    print(f"Validation errors for record {record}: {errors}")

            if valid_data:
                self.db[collection].insert_many(valid_data)
                print(f"Inserted {len(valid_data)} records into {collection}")

        # Insert data into MongoDB
        insert_data("dummy_user_visits", dummy_user_visits.to_dict('records'), self.dummy_user_visits_schema)
        insert_data("indoor_activities", indoor_activities.to_dict('records'), self.indoor_activities_schema)
        insert_data("outdoor_activities", outdoor_activities.to_dict('records'), self.outdoor_activities_schema)
        insert_data("restaurants", restaurants.to_dict('records'), self.restaurant_schema)
        insert_data("transportation", transportation.to_dict('records'), self.transportation_schema)

        return {"message": "Data insertion completed successfully!"}

    def serialize_object_id(self, data):
        if isinstance(data, list):
            for item in data:
                if "_id" in item:
                    item["_id"] = str(item["_id"])
        elif isinstance(data, dict) and "_id" in data:
            data["_id"] = str(data["_id"])
        return data

    def get_all_restaurants(self):
        data = list(self.db.restaurants.find({}, {
            "_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
            "latitude": 1, "longitude": 1, "cuisine_type": 1, "review_count": 1, "rating": 1, "food_time": 1
        }))
        return self.serialize_object_id(data)

    def get_all_indoor_activities(self):
        data = list(self.db.indoor_activities.find({}, {
            "_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
            "latitude": 1, "longitude": 1, "category": 1, "rating": 1
        }))
        return self.serialize_object_id(data)

    def get_all_outdoor_activities(self):
        data = list(self.db.outdoor_activities.find({}, {
            "_id": 1, "name": 1, "address": 1, "city": 1, "state": 1, "zip_code": 1,
            "latitude": 1, "longitude": 1, "category": 1, "rating": 1
        }))
        return self.serialize_object_id(data)

    def get_cuisines(self):
        cuisines = self.db.restaurants.distinct("cuisine_type")
        return sorted(list(set(cuisines)))  # Ensure unique values

    def get_indoor_categories(self):
        categories = self.db.indoor_activities.distinct("category")
        return sorted(list(set(categories)))  # Ensure unique values

    def get_outdoor_categories(self):
        categories = self.db.outdoor_activities.distinct("category")
        return sorted(list(set(categories)))  # Ensure unique values