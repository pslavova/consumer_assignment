import requests
import logging

class ConsumerGroupClient:
    def __init__(self, host: str, port: int):
        self.consumer_group_app_url = f"http://{host}:{port}"

    def register(self, id: str) -> None:
        url = f"{self.consumer_group_app_url}/register"
        payload = { "consumer_id": id }
        headers = { "Content-Type": "application/json" }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Successfully registered to consumers group.")
        else:
            error_msg = f"Failed to register to consumers group. Status Code: {response.status_code}; " \
                        + f"Response content: {response.content}"
            raise Exception(error_msg)

    def unregister(self, id: str) -> None:
        url = f"{self.consumer_group_app_url}/unregister"
        payload = { "consumer_id": id }
        headers = { "Content-Type": "application/json" }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Successfully unregistered from consumers group.")
        else:
            error_msg = f"Failed to unregister from consumers group. Status Code: {response.status_code}; " \
                        + f"Response content: {response.content}"
            raise Exception(error_msg)

    def check_membership(self, id: str) -> bool:
        url = f"{self.consumer_group_app_url}/checkMembership"
        payload = { "consumer_id": id }
        headers = { "Content-Type": "application/json" }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("Consumer is already registered to consumer group.")
            return True
        else:
            logging.info("Consumer is not found in consumer group.")
            return False