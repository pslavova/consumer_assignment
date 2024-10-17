import configparser
import os.path
import logging
from dataclasses import dataclass

@dataclass
class Configs:
    redis_host: str
    redis_port: int
    max_consumer_group_size: int

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
        consumer_props = {}
    else:
        properties_config = configparser.RawConfigParser()
        properties_config.read(args.configFilePath)

        redis_props = dict(properties_config.items('redis')) if properties_config.has_section('redis') else {}
        consumer_props = dict(properties_config.items('consumers')) if properties_config.has_section('consumers') else {}

    configs: Configs = Configs(
        redis_host=get_property(args.redisServerHost, redis_props.get("host"), "localhost", str),
        redis_port=get_property(args.redisServerPort, redis_props.get("port"), "6379", int),
        max_consumer_group_size=get_property(args.maxConsumerGroupSize, consumer_props.get("max_consumer_group_size"), "5", int),
    )

    return configs