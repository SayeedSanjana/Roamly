from flask import Blueprint, jsonify
from services.restaurant_scraper_service import scrape_restaurants

restaurant_controller = Blueprint('restaurant_controller', __name__)

@restaurant_controller.route('/restaurants', methods=['GET'])
def get_restaurants():
    data = scrape_restaurants()
    return jsonify(data)
