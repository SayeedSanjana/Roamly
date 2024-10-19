import logging
from flask import Flask

app = Flask(__name__)

# # Set up basic logging configuration first
# logging.basicConfig(level=logging.INFO)  # Adjust this as needed for your app

# # Disable PyMongo debug logging by setting the logger level to CRITICAL
# logging.getLogger('pymongo').setLevel(logging.CRITICAL)
# logging.getLogger('pymongo.topology').setLevel(logging.CRITICAL)

# # Optionally, disable Flask's built-in logging configuration
# app.logger.disabled = True
# log = logging.getLogger('werkzeug')
# log.disabled = True

if __name__ == '__main__':
    app.run(debug=True)
