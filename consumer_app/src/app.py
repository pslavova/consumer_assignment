import argparse
import logging
import threading
import atexit

from pathlib import Path
from config_parser import Configs, load_configs
from api.consumer_api import rest_api_app
from consumer.consumer import Consumer
from consumer.consumer_registration_monitor import ConsumerRegistrationMonitor
from consumer_group.consumer_group_client import ConsumerGroupClient
from constants import CONSUMER_CONTEXT_KEY

logging.basicConfig(format='%(asctime)s %(levelname)s %(threadName)s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

consumer: Consumer = None

def start_flask_app(api_host: str, api_port: int, consumer: Consumer):
    # set the consumer object in the context so that it can be extracted and used in the api
    setattr(rest_api_app, CONSUMER_CONTEXT_KEY, consumer)

    logging.info("Starting Flask App...")
    rest_api_app.run(host=api_host, port=api_port, debug = False)

def release_resources_on_exit(group_app_host: str, group_app_port: int, consumer: Consumer):
    logging.info("Unregister from consumer group...")
    group_app_client = ConsumerGroupClient(group_app_host, group_app_port)
    group_app_client.unregister(id=consumer.id)

def run():
    logging.info("Starting consumer application.")
    src_folder_path = Path(__file__).parent
    parser = argparse.ArgumentParser("Run Message Consumer Application(Handling of msgs)")
    parser.add_argument("--redisServerHost", required=False,
                        help="Provide Redis server host to connect to. Value should be IP address or hostname.")
    parser.add_argument("--redisServerPort", required=False,
                        help="Provide Redis server port to connect to.")
    parser.add_argument("--consumerGroupAppHost", required=False,
                        help="Provide server host address for the Consumer Group Application. Value should be IP address or hostname.")
    parser.add_argument("--consumerGroupAppPort", required=False,
                        help="Provide server port for the Consumer Group Application.")
    parser.add_argument("--restApiHost", required=False,
                        help="Hostname/IP on which the Rest Api Service will be started.")
    parser.add_argument("--restApiPort", required=False,
                        help="Port on which the Rest Api Service will be started.")
    parser.add_argument("--configFilePath", default=f"{src_folder_path}/../config/config.properties",
                        help="Location of the properties files with application configurations.")

    args = parser.parse_args()

    logging.info("Loading application configurations.")
    configs: Configs = load_configs(args)

    logging.info("Initializing consumer.")
    consumer = Consumer(
        redis_host=configs.redis_host,
        redis_port=configs.redis_port,
        service_host=configs.rest_api_host,
        service_port=configs.rest_api_port
        )

    logging.info("Initializing and starting Rest Api service.")
    flask_thread = threading.Thread(name="FlaskApp", target=start_flask_app,
                                    kwargs={
                                        "consumer":consumer,
                                        "api_host":configs.rest_api_host,
                                        "api_port":configs.rest_api_port
                                    })
    flask_thread.start()

    logging.info("Initializing and starting consumers registrations monitoring.")
    monitor = ConsumerRegistrationMonitor(group_app_host=configs.consumer_group_app_host,
                                          group_app_port=configs.consumer_group_app_port,
                                          consumer_id=consumer.id)
    registration_monitoring_thread = threading.Thread(name="ConsumerRegistrationMonitoring",
                                                      target=monitor.run_monitoring)
    registration_monitoring_thread.start()

    atexit.register(release_resources_on_exit,
                    configs.consumer_group_app_host,
                    configs.consumer_group_app_port,
                    consumer)

if __name__ == '__main__':
    run()