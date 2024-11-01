from flask import Blueprint, jsonify, request
from app.services.restaurant_scraper_service import RestaurantScrapperService

def create_restaurant_routes():
    # Create a Blueprint for the restaurant routes
    restaurant_routes = Blueprint('restaurant', __name__)
    yelp_service = RestaurantScrapperService(api_key="ns_jKI1H3xq-Fc9niFvxDcrKfskmIQGw49of0nUEmn2N9MU9zqBK_YuDeqLAzfHL0KntgQ29tQ5eyMdyquuU7EKF5GHweOPkOxti4MV8HgDx_0MPA-1BNS2IsIgkZ3Yx")  # Replace with your Yelp API key

    @restaurant_routes.route('/list', methods=['GET'])
    def get_restaurants():
        try:
            # Get pagination parameters from the request
            offset = int(request.args.get('offset', 0))  # Default to 0
            limit = int(request.args.get('limit', 50))  # Default to 50

            print(f"Request received with offset: {offset}, limit: {limit}")  # Debugging print

            # Fetch restaurant data
            result = yelp_service.get_restaurants(location="Montreal", term="restaurants")
            if "error" in result:
                print(f"Error from yelp_service: {result['error']}")
                return jsonify({"error": result["error"]}), 500

            print(f"Data fetched successfully with offset: {offset}")  # Debugging print

            # Implement pagination
            paginated_data = result[offset:offset + limit]
            return jsonify({
                "offset": offset,
                "limit": limit,
                "total": len(result),
                "restaurants": paginated_data
            }), 200
        except Exception as e:
            print(f"An error occurred: {str(e)}")  # Print the error for debugging
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

        

    @restaurant_routes.route('/total', methods=['GET'])
    def get_total_restaurants():
        """
        Returns the total number of available restaurants for Montreal.
        """
        try:
            # Call the method from the service to get the total number of restaurants
            total_count = yelp_service.get_total_available_restaurants(location="Montreal", term="restaurants")
            return jsonify({"total": total_count}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    return restaurant_routes
