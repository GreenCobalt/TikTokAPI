import logging

logging.basicConfig(filename='/var/log/tiktokapi.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def log_setup(log_to_console=True):
    logger = logging.getLogger("TiktokAPI")
    return logger

logger = log_setup()
