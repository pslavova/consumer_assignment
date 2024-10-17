import logging
import redis
import threading
import random

from redis.client import PubSub
from typing import List

class ConsumersGroup:
    # TODO this class should be singleton!!!

    MSGS_CHANNEL_NAME = "messages:published"
    CONSUMERS_LIST_NAME = "consumer:ids"

    def __init__(self, group_members_max_count: int, redis_host: str, redis_port: int):
        self._lock = threading.Lock()
        self.group_members_max_count = group_members_max_count
        try:
            self.redis_con_pool = redis.ConnectionPool(host=redis_host, port=redis_port)
        except redis.ConnectionError as ex:
            logging.exception("Failed to connect to Redis server", ex)
            raise RuntimeError(ex)

    def add_consumer(self, id: str) -> bool:
        with self._lock, \
            redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            items_count = connection.llen(ConsumersGroup.CONSUMERS_LIST_NAME)
            if items_count < self.group_members_max_count:
                id_index = connection.lpos(ConsumersGroup.CONSUMERS_LIST_NAME, id)
                if id_index == None:
                    connection.lpush(ConsumersGroup.CONSUMERS_LIST_NAME, id)
                return True
            else:
                raise Exception(f"Consumer with id {id} cannot be added to the group, because max capacity is reached!")

    def remove_consumer(self, id: str) -> bool:
        with self._lock, \
            redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            removed_items_count = connection.lrem(ConsumersGroup.CONSUMERS_LIST_NAME, count=0, value=id)
            return True if removed_items_count > 0 else False

    def check_consumer_membership(self, id: str) -> bool:
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            try:
                id_index = connection.lpos(name=ConsumersGroup.CONSUMERS_LIST_NAME, value=id)
                return True if id_index != None else False
            except Exception as ex:
                logging.exception(f"Failed to check for item in list {ConsumersGroup.CONSUMERS_LIST_NAME}", ex)
                return False

    def get_all_consumers(self) -> List[str]:
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            return [item.decode() for item in connection.lrange(ConsumersGroup.CONSUMERS_LIST_NAME, 0, -1)]

    def get_consumer(self) -> str:
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            items_count = connection.llen(ConsumersGroup.CONSUMERS_LIST_NAME)
            index = random.randint(0, items_count - 1)
            consumer_id = connection.lindex(ConsumersGroup.CONSUMERS_LIST_NAME, index)
            return consumer_id.decode()

    def subscribe_to_channel(self) -> PubSub:
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            pubsub = connection.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(ConsumersGroup.MSGS_CHANNEL_NAME)
            return pubsub

    def unsubscribe_from_channel(self) -> None:
        with redis.Redis(connection_pool=self.redis_con_pool, decode_responses=True) as connection:
            pubsub = connection.pubsub(ignore_subscribe_messages=True)
            pubsub.unsubscribe()
