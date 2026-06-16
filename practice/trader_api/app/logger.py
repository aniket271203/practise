import logging
import sys

def setup_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    ConsoleHandler=logging.StreamHandler(sys.stdout)
    ConsoleHandler.setLevel(logging.DEBUG)
    
    FileHandler=logging.FileHandler('trader.log')
    FileHandler.setLevel(logging.INFO)
    
    formatter=logging.Formatter(
        " %(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%D"
    )
    
    FileHandler.setFormatter(formatter)
    ConsoleHandler.setFormatter(formatter)
    
    logger.addHandler(ConsoleHandler)
    logger.addHandler(FileHandler)
    
    return logger
