from audioop import add
from email.policy import HTTP
from http import server
from http.client import HTTPResponse
from threading import Thread
from time import sleep
from datetime import datetime
from contextlib import contextmanager
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

    def accept(self, host:str, server_port:int, base_dir:str, encoding='utf-8', timeout=None):
        extra = {'server_hostname': socket.gethostname(), 'server_ip': socket.gethostbyname(socket.gethostname()), 'server_port':server_port, 'client_host':"", 'client_port':""}
        self.dir = os.path.join(script_dir, base_dir)
        self.encoding = encoding
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host,server_port))
            s.listen() # Parameters could be an int32 with number of max connections, or nothing to do this automatically
            s.settimeout(timeout)
            server_logger.info("Starting server...", extra=extra)
            while True:
                server_logger.info("Waiting for connections:", extra=extra)
                conn_socket, addr = s.accept()
                tmp_extra = extra.copy()
                tmp_extra['client_host'] = addr[0]
                tmp_extra['client_port'] = int(addr[1])
                server_logger.info(f"Connection accepted", extra=tmp_extra)
                Thread(target=self.response, args=(conn_socket,addr,), kwargs={'logging_extra_info':tmp_extra}).start()

    def response(self, conn_socket:socket.socket, addr:tuple, logging_extra_info=None):
        if logging_extra_info is None:
            logging_extra_info = {'server_hostname': socket.gethostname(), 'server_ip': socket.gethostbyname(socket.gethostname()), 'server_port':"", 'client_host':"", 'client_port':""}

        sentence = conn_socket.recv(BUFFER_SIZE).decode(self.encoding)
        server_logger.info(f"Parsing received content.", extra=logging_extra_info)
        # Parser TODO
        # Here, we check for the possibility of a 400 response

        # Se file encontrado
        sentence_file = "simplepage.html"
        server_logger.info(f"File requested: {sentence_file}", extra=logging_extra_info)
        with open_handling_error(self.dir + '/' + sentence_file, "r", logging_extra_info=logging_extra_info) as (f, status):
            if status == 200:
                HTTPcontent = f.read().encode(self.encoding)
                HTTPheader = 'HTTP/1.1 200 OK\r\n'

            elif status == 404:
                HTTPcontent = "".encode(self.encoding)
                HTTPheader = 'HTTP/1.1 400 Not Found\r\n'
            HTTPheader += 'Date: {}\r\n'.format(datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z"))
            HTTPheader += 'Content-type: {}; charset={}\r\n'.format('text/html', self.encoding)
            HTTPheader += 'Content-lenght: {}\r\n'.format(len(HTTPcontent))
            HTTPheader += '\r\n\r\n'
            HTTPheader = HTTPheader.encode(self.encoding)
            HTTPresponse = HTTPheader + HTTPcontent
            server_logger.info(f"Response header created: \n/***response***/\n{HTTPheader}\n/*************/", extra=logging_extra_info)
            conn_socket.sendall(HTTPresponse)
            server_logger.info(f"Response sent", extra=logging_extra_info)

        server_logger.info(f"Closing thread", extra=logging_extra_info)

@contextmanager
def open_handling_error(*args, **kwargs):
    f = None
    try:
        f = open(*args)
        yield f, 200 
    except OSError as e:
        server_logger.error(f"File can not be opened\n{e}", extra=kwargs['logging_extra_info'])
        yield None, 404
    finally:
        if f is not None:
            f.close()


if __name__=='__main__':
    my_server = Server()
    my_server.accept('localhost', 14000, '../../data')
