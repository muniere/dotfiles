import logging

DEBUG = 10
EXEC = 15
INFO = 20
WARN = 30
ERROR = 40

logging.addLevelName(DEBUG, "DEBUG")
logging.addLevelName(EXEC, "EXEC")
logging.addLevelName(INFO, "INFO")
logging.addLevelName(WARN, "WARN")
logging.addLevelName(ERROR, "ERROR")
