import configparser
import os.path
import logging
from dataclasses import dataclass

@dataclass
class Configs:
    redis_host: str
    redis_port: int
    rest_api_host: str
    rest_api_port: int
    consumer_group_app_host: str
    consumer_group_app_port: int

def get_property(args_value: str, config_file_value: str, default_value: str, prop_type: type):
    if args_value:
        return prop_type(args_value)
    elif config_file_value:
        return prop_type(config_file_value)
    else:
        return prop_type(default_value)

def load_configs(args):
    if not os.path.isfile(args.configFilePath):
        logging.warn(f"Config file is not found: {args.configFilePath}")
        redis_props = {}
        rest_api_props = {}
        consumer_group_app_props = {}
    else:
        properties_config = configparser.RawConfigParser()
        properties_config.read(args.configFilePath)

        redis_props = dict(properties_config.items('redis')) if properties_config.has_section('redis') else {}
        rest_api_props = dict(properties_config.items('rest_api')) if properties_config.has_section('rest_api') else {}
        consumer_group_app_props = dict(properties_config.items('consumer_group_app')) \
            if properties_config.has_section('consumer_group_app') else {}

    configs: Configs = Configs(
        redis_host=get_property(args.redisServerHost, redis_props.get("host"), "localhost", str),
        redis_port=get_property(args.redisServerPort, redis_props.get("port"), "6379", int),

        rest_api_host=get_property(args.restApiHost, rest_api_props.get("host"), "127.0.0.1", str),
        rest_api_port=get_property(args.restApiPort, rest_api_props.get("port"), "5001", int),

        consumer_group_app_host=get_property(args.consumerGroupAppHost, consumer_group_app_props.get("host"), "127.0.0.1", str),
        consumer_group_app_port=get_property(args.consumerGroupAppPort, consumer_group_app_props.get("port"), "5000", int),
    )

    return configs