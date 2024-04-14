import logging
#https://prometheus.io/docs/introduction/faq/#how-to-feed-logs-into-prometheus

def get_logger(name, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add filehandler
    fh = logging.FileHandler('logs.log')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
