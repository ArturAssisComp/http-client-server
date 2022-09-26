from threading import Thread
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
client_logger = logging.getLogger('client_logger')
basic_logger = logging.getLogger('basic_logger')

class Client(object):
    def __init__(self):
        pass

    def connect(self, host:str, port:int, message:str, encoding='utf-8', timeout=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            extra = {'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname()), 'dst_hostname':host, 'dst_port':port}
            s.settimeout(timeout)
            client_logger.info("Connecting...", extra=extra)
            s.connect((host, port))
            client_logger.info(f"Sending message:\n/***request***/\n{message}\n/*************/", extra=extra)
            s.sendall(message.encode(encoding))
            client_logger.info(f"Waiting for response...", extra=extra)
            data = s.recv(BUFFER_SIZE)
        client_logger.info(f"Received:\n/***response***/\n{repr(data)}\n/**************/", extra=extra)



if __name__=='__main__':
    
    # Example 1: Connect google
    # my_client = Client()
    # my_client.connect("www.google.com", 80, "GET /robots.txt HTTP/1.1\r\n\r\n", timeout=10)

    # Example 2: Parallel connection to server
    # my_client_1 = Client()
    # my_client_2 = Client()
    # Thread(target=my_client_1.connect, args=("127.0.1.1", 14000, "Temporario 1"), kwargs={'timeout': 10}).start()
    # Thread(target=my_client_1.connect, args=("127.0.1.1", 14000, "Temporario 2"), kwargs={'timeout': 10}).start()

    # Example 3: Connect localhost
    my_client = Client()
    my_client.connect("localhost", 14000, "GET /robots.txt HTTP/1.1\r\n\r\n", timeout=10)
