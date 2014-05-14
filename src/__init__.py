import logging
logger = logging.getLogger("tektronix")
level = logging.DEBUG
logger.setLevel(level)
# stream output
format = "%(asctime)s [%(name)s:%(levelname)s]: %(message)s"
ch = logging.StreamHandler()
ch.setLevel(level)
formatter = logging.Formatter(format)
ch.setFormatter(formatter)
logger.addHandler(ch)
# create file handler which logs even debug messages
#fh = logging.FileHandler('spam.log')
#fh.setLevel(logging.DEBUG)
#fh.setFormatter(formatter)
#logger.addHandler(fh)
from tektronix import *
