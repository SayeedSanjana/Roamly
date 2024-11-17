from flask import Blueprint, jsonify, request
from app.services.data_service import DataService

def create_data_routes(db):
    data_routes = Blueprint('data', __name__)
    data_service = DataService(db)

    @data_routes.route('/load_data', methods=['POST'])
    def load_data():
        try:
            # Call the data service to load data
            response = data_service.load_data()
            return jsonify(response), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @data_routes.route('/get_restaurants', methods=['GET'])
    def get_restaurants():
        data = data_service.get_all_restaurants()
        return jsonify(data), 200

    @data_routes.route('/get_indoor_activities', methods=['GET'])
    def get_indoor_activities():
        data = data_service.get_all_indoor_activities()
        return jsonify(data), 200

    @data_routes.route('/get_outdoor_activities', methods=['GET'])
    def get_outdoor_activities():
        data = data_service.get_all_outdoor_activities()
        return jsonify(data), 200

    @data_routes.route('/get_cuisines', methods=['GET'])
    def get_cuisines():
        data = data_service.get_cuisines()
        return jsonify(data), 200

    @data_routes.route('/get_indoor_categories', methods=['GET'])
    def get_indoor_categories():
        data = data_service.get_indoor_categories()
        return jsonify(data), 200

    @data_routes.route('/get_outdoor_categories', methods=['GET'])
    def get_outdoor_categories():
        data = data_service.get_outdoor_categories()
        return jsonify(data), 200

    return data_routes
