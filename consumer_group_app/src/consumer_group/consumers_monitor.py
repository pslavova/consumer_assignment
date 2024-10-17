import logging
import time

from consumer.consumer_client import ConsumerClient
from consumer_group.consumer_group import ConsumersGroup

# TODO move to config.properties
CHECK_INTERVAL_IN_MINUTES = 5

class ConsumerRegistrationMonitor:
    def __init__(self, consumer_group: ConsumersGroup):
        self.consumer_group = consumer_group

    def run_monitoring(self):
        logging.info("Starting consumers health monitoring.")
        while True:
            try:
                logging.info("Checking consumers health.")
                all_consumers = self.consumer_group.get_all_consumers()
                for consumer_id in all_consumers:
                    host, port = consumer_id.split(":")
                    consumer_client = ConsumerClient(host, port)

                    healthy = consumer_client.check_health()

                    if not healthy:
                        logging.info(f"Consumer with id {consumer_id} is not healthy. Removing it from subscribers list.")
                        self.consumer_group.remove_consumer(consumer_id)
            except Exception as ex:
                error_msg = f"Exception raised in consumers monitoring flow. Will try again in {CHECK_INTERVAL_IN_MINUTES} minutes"
                logging.exception(error_msg, ex)

            time.sleep(CHECK_INTERVAL_IN_MINUTES * 60)
