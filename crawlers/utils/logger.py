import logging

def log_setup(log_to_console=True):
    logger = logging.getLogger("TiktokAPI")
    return logger

logger = log_setup()
