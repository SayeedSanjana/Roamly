from flask import Blueprint, jsonify
from services.outdoor_activity_scraper_service import scrape_outdoor_activities # type: ignore

outdoor_activity_controller = Blueprint('outdoor_activity_controller', __name__)

@outdoor_activity_controller.route('/outdoor-activities', methods=['GET'])
def get_outdoor_activities():
    data = scrape_outdoor_activities()
    return jsonify(data)
