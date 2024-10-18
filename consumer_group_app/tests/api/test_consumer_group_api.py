import pytest

from unittest.mock import patch, MagicMock

from api.consumer_group_api import rest_api_app
from constants import CONSUMER_GROUP_CONTEXT_KEY

@pytest.fixture
def client():
    with rest_api_app.test_client() as client:
        mock = MagicMock()
        setattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY, mock)
        yield client

def test_register_success(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.add_consumer.return_value = True

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/register', json=data)

    assert response.status_code == 200
    assert b"Consumer with id localhost:5000 is registered." in response.data
    mock_consumer_group.add_consumer.assert_called_once_with("localhost:5000")

def test_register_invalid_json(client):
    response = client.post('/register', data='not a json')

    assert response.status_code == 400
    assert b"Provided data does not match requirements" in response.data

def test_register_validation_failure(client):
    with patch('api.consumer_group_api.validate_consumer_data', side_effect=Exception("Validation error")):
        data = {"consumer_id": "localhost:5000"}
        response = client.post('/register', json=data)

        assert response.status_code == 400
        assert b"Provided data does not match requirements" in response.data

def test_register_internal_error(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.add_consumer.side_effect = Exception("Some error")

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/register', json=data)

    assert response.status_code == 500
    assert b"Failed to register consumer! Use Ref for details:" in response.data

def test_unregister_success(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.remove_consumer.return_value = True

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/unregister', json=data)

    assert response.status_code == 200
    assert b"Consumer with id localhost:5000 is unregistered." in response.data
    mock_consumer_group.remove_consumer.assert_called_once_with("localhost:5000")

def test_unregister_invalid_json(client):
    response = client.post('/unregister', data='not a json')

    assert response.status_code == 400
    assert b"Provided data does not match requirements" in response.data

def test_unregister_validation_failure(client):
    with patch('api.consumer_group_api.validate_consumer_data', side_effect=Exception("Validation error")):
        data = {"consumer_id": "localhost:5000"}
        response = client.post('/unregister', json=data)

        assert response.status_code == 400
        assert b"Provided data does not match requirements" in response.data

def test_unregister_internal_error(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.remove_consumer.side_effect = Exception("Some error")

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/unregister', json=data)

    assert response.status_code == 500
    assert b"Failed to unregister consumer! Use Ref for details:" in response.data

def test_check_membership_success(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.check_consumer_membership.return_value = True

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/checkMembership', json=data)

    assert response.status_code == 200
    assert b'"is_member":true' in response.data

def test_check_membership_not_found(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.check_consumer_membership.return_value = False

    data = {"consumer_id": "localhost:5000"}
    response = client.post('/checkMembership', json=data)

    assert response.status_code == 404
    assert b'"is_member":false' in response.data

def test_check_membership_invalid_json(client):
    response = client.post('/checkMembership', data='not a json')

    assert response.status_code == 400
    assert b"Provided data does not match requirements" in response.data

def test_check_membership_validation_failure(client):
    with patch('api.consumer_group_api.validate_consumer_data', side_effect=Exception("Validation error")):
        data = {"consumer_id": "localhost:5000"}
        response = client.post('/checkMembership', json=data)

        assert response.status_code == 400
        assert b"Provided data does not match requirements" in response.data

def test_check_membership_internal_error(client):
    mock_consumer_group = getattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY)
    mock_consumer_group.check_consumer_membership.side_effect = Exception("Some error")

    data = {"consumer_id": "localhost:5000"}
    response = client.post("/checkMembership", json=data)

    assert response.status_code == 500
    assert b"Failed to check for membership! Use Ref for details:" in response.data
