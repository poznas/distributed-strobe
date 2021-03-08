import logging

LOG_FMT = '%(asctime)s %(levelname)s {%(process)s-%(thread)s} %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FMT)

logger = logging.getLogger('dev')
