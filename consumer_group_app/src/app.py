import argparse
import logging
import json
import threading
import time
import atexit

from pathlib import Path
from redis.client import PubSub
from config_parser import Configs, load_configs
from api.consumer_group_api import rest_api_app
from consumer_group.consumers_monitor import ConsumerRegistrationsMonitor
from consumer_group.consumer_group import ConsumersGroup
from consumer.consumer_client import ConsumerClient
from constants import CONSUMER_GROUP_CONTEXT_KEY

logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

TOTAL_PROCESSED_MESSAGES: int = 0
TOTAL_FAILED_MESSAGES: int = 0

PRINT_STATS_PERIOD_IN_MINUTES = 3

consumer_group: ConsumersGroup = None

def start_flask_app(consumer_group: ConsumersGroup):
    # set the consumer group in the context so that it can be extracted and used in the api
    setattr(rest_api_app, CONSUMER_GROUP_CONTEXT_KEY, consumer_group)

    logging.info("Starting Flask App...")
    rest_api_app.run(debug = False)

def listen_for_messages(pubsub: PubSub, consumer_group: ConsumersGroup):
    global TOTAL_PROCESSED_MESSAGES
    global TOTAL_FAILED_MESSAGES

    logging.info("Starting MSG listener...")
    for msg in pubsub.listen():
        try:
            msg_data = json.loads(msg["data"].decode())
            consumer_id = consumer_group.get_consumer()
            consumer_host, consumer_port = (consumer_id.split(":"))
            consumer_client = ConsumerClient(consumer_host, consumer_port)
            logging.info(f"Sending msg '{msg_data}' to consumer with id: {consumer_id}")
            consumer_client.process_msg(msg_data)
            TOTAL_PROCESSED_MESSAGES += 1
        except Exception as ex:
            logging.exception(f"Failed to process message: {msg}", ex)
            TOTAL_FAILED_MESSAGES += 1

def print_statistics():
    global TOTAL_PROCESSED_MESSAGES
    global TOTAL_FAILED_MESSAGES
    global PRINT_STATS_PERIOD_IN_MINUTES

    logging.info("Starting Statistics Reporter ...")
    while True:
        time.sleep(PRINT_STATS_PERIOD_IN_MINUTES * 60)
        msg = f"Total messages processed: {TOTAL_PROCESSED_MESSAGES}; Total messages failed: {TOTAL_FAILED_MESSAGES}"
        logging.info(msg)

def release_resources_on_exit(consumer_group: ConsumersGroup):
    logging.info("Unsubscribing from channel...")
    consumer_group.unsubscribe_from_channel()

def run():
    logging.info("Starting Consumer Group application.")
    src_folder_path = Path(__file__).parent
    parser = argparse.ArgumentParser("Run Message Distributor Application(Handling of subscription groups)")
    parser.add_argument("--redisServerHost", required=False,
                        help="Provide Redis server host to connect to. Value should be IP address or hostname.")
    parser.add_argument("--redisServerPort", required=False,
                        help="Provide Redis server port to connect to.")
    parser.add_argument("--maxConsumerGroupSize", required=False,
                        help="Maximum allowed size of the consumer group.")
    parser.add_argument("--configFilePath", default=f"{src_folder_path}/../config/config.properties",
                        help="Location of the properties files with application configurations.")

    args = parser.parse_args()
    configs: Configs = load_configs(args)

    logging.info("Initializing consumer group.")
    consumer_group = ConsumersGroup(configs.max_consumer_group_size, configs.redis_host, configs.redis_port)

    logging.info("Subscribing consumer group to Redis channel.")
    pubsub = consumer_group.subscribe_to_channel()

    flask_thread = threading.Thread(name="FlaskApp", target=start_flask_app,
                                    kwargs={"consumer_group":consumer_group})
    flask_thread.start()

    msg_processor_thread = threading.Thread(name="MessageListener", target=listen_for_messages,
                                            kwargs={"pubsub":pubsub, "consumer_group":consumer_group})
    msg_processor_thread.start()

    consumers_monitor = ConsumerRegistrationsMonitor(consumer_group=consumer_group)
    consumers_monitoring_thread = threading.Thread(name= "ConsumersMonitoring", target=consumers_monitor.run_monitoring)
    consumers_monitoring_thread.start()

    printStats_thread = threading.Thread(name="StatisticsReporter", target=print_statistics)
    printStats_thread.start()

    atexit.register(release_resources_on_exit, consumer_group)

if __name__ == '__main__':
    run()