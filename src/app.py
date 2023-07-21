import base64
import json
import logging
import os
import time
from io import BytesIO

import redis
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request
from nsfw_detector import predict

# Maximum number of images that can be processed at once
MAX_IMAGES = 100

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Connect to Redis
r = redis.Redis(host='nsfw_redis', port=6379, db=0,
                decode_responses=True, password=os.environ.get('REDIS_PASS'))

model_path = './models/v1-2-0/saved_model.h5'
if os.path.isfile(model_path):
    print("File exists")
else:
    print("File does not exist or is a directory")
# Load the pre-trained model
model = predict.load_model('./models/v1-2-0/saved_model.h5')


@app.before_request
def check_api_key():
    """
    Middleware that checks for an API key in the request headers before processing a request.
    If the key is not present or incorrect, the request is aborted.
    """
    api_key = request.headers.get('key', '')
    if os.environ.get('API_KEY', ''):
        if not api_key:
            abort(401, 'API Key required')
        elif not api_key == os.environ.get('API_KEY', ''):
            abort(401, 'Invalid API Key')


@app.route('/', methods=['POST'])
def detect():
    """
    Detects the NSFW level of a list of images.
    """
    try:
        start_time = time.time()  # Record the start time

        images = request.json.get('images')

        all_predictions = {}
        for image in images:
            input_start_time = time.time()

            buffer = image['buffer']
            image_hash = image['hash']

            # Check if Redis has a key with that hash
            if image_hash and r.exists(image_hash):
                # If so, use that data
                prediction = json.loads(r.get(image_hash))
            else:
                # Buffer is base64 encoded, decode into bytes
                file_bytes = base64.b64decode(buffer)
                # Convert bytes to a file-like object
                file = BytesIO(file_bytes)
                # Compute the predictions
                prediction = predict.classify(model, file)

                # Store the prediction in Redis
                if image_hash:
                    r.set(image_hash, json.dumps(prediction))

            input_end_time = time.time()
            logger.debug(
                "Time for processing image with hash '%s': %f seconds", image_hash, (input_end_time - input_start_time))

            all_predictions[image_hash] = prediction

        end_time = time.time()  # Record the end time
        logger.debug(
            "Total time for detect function: %f seconds", (end_time - start_time))

        return jsonify({"predictions": all_predictions})

    except Exception as e:
        logger.error("Error in detect function: %s", e)
        return jsonify({"error": "An error occurred during NSFW detection. Please check your input and try again."}), 500


@app.route('/help', methods=['GET'])
def help():
    """
    Returns a dictionary containing information about the API.
    """
    help_info = {
        'endpoints': {
            '/': {
                'method': 'POST',
                'description': 'Classify the NSFW level of images. Takes a list of items as input, each with a buffer and hash field. The buffer should contain the base64 encoded image. The hash is used for caching results in Redis to avoid recalculation. Returns a dictionary mapping hashes to classification results.',
            },
            '/test': {
                'method': 'GET',
                'description': 'Test endpoint to check if the API is working. Returns a success message.',
            },
            '/healthcheck': {
                'method': 'GET',
                'description': 'Healthcheck endpoint to verify the service status. Returns a status message.',
            },
            '/help': {
                'method': 'GET',
                'description': 'This help endpoint providing information about the API.'
            },
        },
    }
    return jsonify({"Help": help_info})


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Simple way to check if this service is running.
    """
    return jsonify({"status": "healthy"})


try:
    port = os.environ['VIRTUAL_PORT']
    if os.environ.get('API_KEY'):
        logger.info("Starting server on port %s in private mode", port)
    else:
        logger.info("Starting server on port %s in public mode", port)
    if os.environ['FLASK_ENV'] == 'development':
        app.run(host='0.0.0.0', port=port)
except Exception as e:
    logger.error("Error starting server: %s", e)
