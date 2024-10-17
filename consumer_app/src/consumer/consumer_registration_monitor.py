import logging
import time

from consumer_group.consumer_group_client import ConsumerGroupClient

# TODO move to config.properties
CHECK_INTERVAL_IN_MINUTES = 5

class ConsumerRegistrationMonitor:
    def __init__(self, group_app_host: str, group_app_port: int, consumer_id: str):
        self.group_app_client = ConsumerGroupClient(group_app_host, group_app_port)
        self.consumer_id = consumer_id

    def run_monitoring(self):
        while True:
            try:
                if not self.group_app_client.check_membership(self.consumer_id):
                    self.group_app_client.register(self.consumer_id)
            except Exception as ex:
                error_msg = f"Exception raised in registration monitoring flow. Will try again in {CHECK_INTERVAL_IN_MINUTES} minutes"
                logging.exception(error_msg, ex)

            time.sleep(CHECK_INTERVAL_IN_MINUTES * 60)
