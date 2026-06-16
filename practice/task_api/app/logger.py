import logging
import sys

def setup_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    ConsoleHandler=logging.StreamHandler(sys.stdout)
    ConsoleHandler.setLevel(logging.DEBUG)
    FileHandler=logging.FileHandler('tasks_api.log')
    FileHandler.setLevel(logging.INFO)
    
    formatter=logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(messages)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    FileHandler.setFormatter(formatter)
    ConsoleHandler.setFormatter(formatter)
    
    logger.addHandler(ConsoleHandler)
    logger.addHandler(FileHandler)
    
    return logger