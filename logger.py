import logging
import sys
from multiprocessing import Queue

from logging_loki import LokiQueueHandler

# https://prometheus.io/docs/introduction/faq/#how-to-feed-logs-into-prometheus

loki_logs_handler = LokiQueueHandler(
    Queue(-1),
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "fastapi"},
    version="1",
)


def get_logger(name, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger("uvicorn.access")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('logs.log')

    # set fromatters
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # set level
    stream_handler.setLevel(level)
    file_handler.setLevel(level)

    # add handlers to the logger
    logger.handlers = [stream_handler, file_handler, loki_logs_handler]

    return logger
