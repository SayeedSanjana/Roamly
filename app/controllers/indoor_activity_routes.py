from flask import Blueprint, jsonify
from services.indoor_activity_scraper_service import scrape_indoor_activities # type: ignore

indoor_activity_controller = Blueprint('indoor_activity_controller', __name__)

@indoor_activity_controller.route('/indoor-activities', methods=['GET'])
def get_indoor_activities():
    data = scrape_indoor_activities()
    return jsonify(data)
