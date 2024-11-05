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

    return data_routes
