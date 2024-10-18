import pytest

from unittest.mock import patch
from consumer.consumer_client import ConsumerClient

@pytest.fixture
def consumer_client():
    return ConsumerClient(host="127.0.0.1", port="5001")

def test_check_health_success(consumer_client):
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        assert consumer_client.check_health() is True

def test_check_health_failure(consumer_client):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        assert consumer_client.check_health() is False

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        assert consumer_client.check_health() is False

def test_process_msg_success(consumer_client):
    msg = {"key": "value"}
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        consumer_client.process_msg(msg)
        mock_post.assert_called_once_with(
            f"{consumer_client.consumer_app_url}/processMessage",
            headers={"Content-Type": "application/json"},
            json=msg
        )

def test_process_msg_failure(consumer_client):
    msg = {"key": "value"}
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.content = b"Bad Request"

        with pytest.raises(Exception) as exc_info:
            consumer_client.process_msg(msg)

        assert "Failed to process msg" in str(exc_info.value)
