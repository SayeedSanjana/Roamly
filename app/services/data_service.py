import pandas as pd
from app.models.restaurant_schema import RestaurantSchema
from app.models.dummy_users_schema import DummyUserVisitsSchema
from app.models.indoor_activities_schema import IndoorActivitiesSchema
from app.models.outdoor_activities_schema import OutdoorActivitiesSchema

class DataService:
    def __init__(self, db):
        self.db = db
        self.restaurant_schema = RestaurantSchema()
        self.dummy_user_visits_schema = DummyUserVisitsSchema()
        self.indoor_activities_schema = IndoorActivitiesSchema()
        self.outdoor_activities_schema = OutdoorActivitiesSchema()

    def load_data(self):
        # Load CSV files
        dummy_user_visits = pd.read_csv('dummy_user_visits.csv',encoding='latin1')
        indoor_activities = pd.read_csv('indoor_activities.csv',encoding='latin1')
        outdoor_activities = pd.read_csv('outdoor_activities.csv',encoding='latin1')
        restaurants = pd.read_csv('restaurants.csv',encoding='latin1')

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
            'Rating': 'rating'
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

        return {"message": "Data insertion completed successfully!"}
