import uuid
import logging
from flask import (
    g, Flask, jsonify, request
)
from marshmallow import Schema, fields

from constants import CONSUMER_CONTEXT_KEY

# creating the Flask app
rest_api_app = Flask(__name__)

message_schema_err_msg = "Provided data does not match requirements. " \
    + "The body should contain json data like the following: {'consumer_id': '<host>:<port>'}. " \
    + "<host> and <port> are the connection details to use for consumer's Rest Apis."

class MessageSchema(Schema):
    message_id = fields.String(required=True)

@rest_api_app.post('/processMessage')
def process_message():
    # expected format {"message_id": "some guid"}
    data = None
    try:
        if not request.is_json:
            response = jsonify({"error": message_schema_err_msg})
            response.status_code = 400
            return response
        data = request.get_json(force=True)
        try:
            validate_consumer_data(json_request_data=data)
        except Exception as ex:
            response = jsonify({"error": message_schema_err_msg})
            response.status_code = 400
            return response

        consumer = getattr(rest_api_app, CONSUMER_CONTEXT_KEY)
        consumer.process_msg(data)

        response = jsonify(
            message = f"Message with id {data.get('message_id')} was processed successfully."
        )
        return response
    except Exception as ex:
        uuid_ref = str(uuid.uuid4())
        logging.error(f"Failed to process message: {data}. Ref: {uuid_ref}")
        logging.exception(ex)
        error_message = f"Failed to process message! Use Ref for details: {uuid_ref}"
        response = jsonify({"error": error_message})
        response.status_code = 400
        return response

@rest_api_app.get('/health')
def health():
    response = jsonify(message=f"Application is running")
    return response

def validate_consumer_data(json_request_data):
    schema = MessageSchema()
    schema.load(json_request_data)