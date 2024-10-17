import logging
import redis

from datetime import datetime
from typing import Dict

class Consumer:
    MSGS_STREAM_NAME = "messages:processed"

    def __init__(self, redis_host: str, redis_port: int, service_host: str, service_port: int):
        try:
            self.id = f"{service_host}:{service_port}"
            self.redis_con_pool = redis.ConnectionPool(host=redis_host, port=redis_port)
        except redis.ConnectionError as ex:
            logging.exception("Failed to connect to Redis server", ex)
            raise RuntimeError(ex)

    def process_msg(self, msg: Dict[str, str]) -> Dict[str, str]:
        logging.info(f"Processing msg with id {msg.get("message_id")}")
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            enriched_msg = {
                            "subscriber_id": self.id,
                            "message_id": msg.get("message_id"),
                            "processing_time": datetime.now().strftime(format="%y-%m-%d'T'%H:%M:%S")
                        }
            connection.xadd(Consumer.MSGS_STREAM_NAME, enriched_msg)

