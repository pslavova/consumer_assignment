import uuid
import logging
from flask import (
    g, Flask, jsonify, request
)
from werkzeug.exceptions import HTTPException
from marshmallow import Schema, fields

from constants import CONSUMER_GROUP_CONTEXT_KEY

# creating the Flask app
rest_api_app = Flask(__name__)

consumer_schema_err_msg = "Provided data does not match requirements. " \
    + "The body should contain json data like the following: {'consumer_id': '<host>:<port>'}. " \
    + "<host> and <port> are the connection details to use for consumer's Rest Apis."

class ConsumerSchema(Schema):
    consumer_id = fields.String(required=True)

@rest_api_app.post('/register')
def register():
    # expected format {"consumer_id": "consumer_host_address:consumer_port"}
    consumer_id = "undefined"
    try:
        if not request.is_json:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response
        data = request.get_json(force=True)
        try:
            validate_consumer_data(json_request_data=data)
        except Exception as ex:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response

        consumer_id = data.get("consumer_id")
        print(rest_api_app)
        consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)

        consumer_group.add_consumer(consumer_id)

        response = jsonify(
            message=f"Consumer with id {consumer_id} is registered."
        )
        return response
    except Exception as ex:
        uuid_ref = str(uuid.uuid4())
        logging.exception(f"Failed to add consumer to Redis list for consumer id {consumer_id}. Ref: {uuid_ref}", ex)
        error_message = f"Failed to register consumer! Use Ref for details: {uuid_ref}"
        response = jsonify({"error": error_message})
        response.status_code = 500
        return response

@rest_api_app.post('/unregister')
def unregister():
    # expected format {"consumer_id": "consumer_host_address:consumer_port"}
    consumer_id = "undefined"
    try:
        if not request.is_json:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response
        data = request.get_json(force=True)
        try:
            validate_consumer_data(json_request_data=data)
        except:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response

        consumer_id = data.get("consumer_id")

        consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)

        consumer_group.remove_consumer(consumer_id)

        response = jsonify(
            message=f"Consumer with id {consumer_id} is unregistered."
        )
        return response
    except Exception as ex:
        uuid_ref = str(uuid.uuid4())
        logging.exception(f"Failed to remove consumer from Redis list for consumer id {consumer_id}. Ref: {uuid_ref}", ex)
        error_message = f"Failed to unregister consumer! Use Ref for details: {uuid_ref}"

        response = jsonify({"error": error_message})
        response.status_code = 500
        return response

@rest_api_app.post('/checkMembership')
def check_membership():
    # expected format {"consumer_id": "consumer_host_address:consumer_port"}
    consumer_id = "undefined"
    try:
        if not request.is_json:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response
        data = request.get_json(force=True)
        try:
            validate_consumer_data(json_request_data=data)
        except:
            response = jsonify({"error": consumer_schema_err_msg})
            response.status_code = 400
            return response

        consumer_id = data.get("consumer_id")

        consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)

        is_member = consumer_group.check_consumer_membership(consumer_id)

        response = jsonify(
           {"is_member": is_member}
        )
        if is_member:
            response.status_code = 200
        else:
            response.status_code = 404
        return response
    except Exception as ex:
        uuid_ref = str(uuid.uuid4())
        logging.exception(f"Failed to remove consumer from Redis list for consumer id {consumer_id}. Ref: {uuid_ref}", ex)
        error_message = f"Failed to unregister consumer! Use Ref for details: {uuid_ref}"
        response.data = jsonify({"error": error_message})
        response.status_code = 500
        print(response)
        return response

@rest_api_app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    print(response)
    # replace the body with JSON
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

def validate_consumer_data(json_request_data):
    schema = ConsumerSchema()
    schema.load(json_request_data)