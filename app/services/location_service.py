from geopy.geocoders import Nominatim
from app.models.location_schema import LocationSchema  # type: ignore
from marshmallow import ValidationError
from bson.objectid import ObjectId
# import logging

# logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG for detailed logs

class LocationService:
    def __init__(self, db):
        self.db = db
        self.geolocator = Nominatim(user_agent="Roamly")
        self.location_schema = LocationSchema()

    def set_current_location(self, user_id, latitude, longitude):
        """
        Automatically sets the user's current location.
        Only latitude and longitude are required.
        """
        try:
            # Validate latitude and longitude using the unified schema
            self.location_schema.load({"latitude": latitude, "longitude": longitude})
        except ValidationError as err:
            return {"error": err.messages}, 400

        try:
            # Reverse geocode the latitude and longitude into an address
            location = self.geolocator.reverse((latitude, longitude), language='en')
            if location:
                address_data = {
                    "user_id": ObjectId(user_id),
                    "latitude": latitude,
                    "longitude": longitude,
                    "formatted_address": location.address
                }

                # Save or update location
                existing_location = self.db.addresses.find_one({"user_id": ObjectId(user_id)})
                if existing_location:
                    self.db.addresses.update_one({"user_id": ObjectId(user_id)}, {"$set": address_data})
                    return {"message": "Location updated", "address_id": str(existing_location['_id'])}, 200
                else:
                    address_id = self.db.addresses.insert_one(address_data).inserted_id
                    return {"message": "Location created", "address_id": str(address_id)}, 201
            else:
                return {"error": "Unable to detect location"}, 500
        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500

    def set_manual_location(self, user_id, data):
        """
        Allows the user to manually set their location.
        Full validation for manual location entry.
        """
        # logging.debug("Services"+user_id)
        try:
            # Validate the full manual location using the unified schema
            validated_data = self.location_schema.load(data)
        except ValidationError as err:
            return {"error": err.messages}, 400

        try:
            # Extract the manual location details
            latitude = validated_data['latitude']
            longitude = validated_data['longitude']
            street = validated_data['street']
            city = validated_data['city']
            state = validated_data['state']
            country = validated_data['country']
            postal_code = validated_data['postal_code']

            address_data = {
                "user_id": ObjectId(user_id),
                "latitude": latitude,
                "longitude": longitude,
                "street": street,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code,
                "formatted_address": f"{street}, {city}, {state}, {country}, {postal_code}"
            }

            # Save or update the manual location
            existing_location = self.db.addresses.find_one({"user_id": ObjectId(user_id)})
            if existing_location:
                self.db.addresses.update_one({"user_id": ObjectId(user_id)}, {"$set": address_data})
                return {"message": "Manual location updated", "address_id": str(existing_location['_id'])}, 200
            else:
                address_id = self.db.addresses.insert_one(address_data).inserted_id
                return {"message": "Manual location created", "address_id": str(address_id)}, 201
        except Exception as e:
            return {"error": f"Internal server error: {str(e)}"}, 500
