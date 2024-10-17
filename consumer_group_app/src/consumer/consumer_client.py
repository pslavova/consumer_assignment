import requests
import logging

from typing import Dict

class ConsumerClient:

    def __init__(self, host: str, port: str):
        self.consumer_app_url = f"http://{host}:{port}"


    def check_health(self) -> bool:
        url = f"{self.consumer_app_url}/health"
        try:
            response = requests.get(url)
            return True if response.status_code == 200 else False
        except:
            return False


    def process_msg(self, msg: Dict) -> None:
        url = f"{self.consumer_app_url}/processMessage"

        headers = { "Content-Type": "application/json" }
        response = requests.post(url, headers=headers, json=msg)
        if response.status_code == 200:
            logging.debug(f"Message {msg} was processed successfully.")
        else:
            error_msg = f"Failed to process msg. Status Code: {response.status_code}; " \
                        + f"Response content: {response.content}"
            raise Exception(error_msg)