import logging

logfile = 'logs.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(logfile, encoding='utf-8')
basic_formatter = logging.Formatter('%(asctime)s : [%(levelname)s] : %(message)s')
file_handler.setFormatter(basic_formatter)
logger.addHandler(file_handler)
print('INIT LOGGING')
