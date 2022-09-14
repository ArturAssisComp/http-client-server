import socket
import logging
import sys
import os
# Add path to logger_config file
script_dir    = os.path.dirname(__file__)
rel_path      = ".."
abs_file_path = os.path.join(script_dir, rel_path)
sys.path.append(abs_file_path)
import logger_config


BUFFER_SIZE = 2048
server_logger = logging.getLogger('server_logger')
basic_logger = logging.getLogger('basic_logger')


class Server(object):
    def __init__(self):
        pass



if __name__=='__main__':
    pass
