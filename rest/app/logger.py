from app.client import redisClient

import logging
import platform

logKey = "{}.rest".format(platform.node())

class RedisHandler(logging.Handler):
    def emit(self, record):
        formatted = self.format(record)
        redisClient.lpush('logging', f"{formatted}")

formatter = logging.Formatter(f'{logKey}.%(levelname)s: %(asctime)s - %(message)s')
