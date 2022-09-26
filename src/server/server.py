from audioop import add
from email.policy import HTTP
from http import server
from http.client import HTTPResponse
from threading import Thread
from time import sleep
from datetime import datetime
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
        extra = {'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname()), 'dst_hostname':"", 'dst_port':0}
        self.dir = base_dir
        self.encoding = encoding
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host,server_port))
            s.listen() # Parameters could be an int32 with number of max connections, or nothing to do this automatically
            s.settimeout(timeout)
            # server_logger.info("Connecting...", extra=extra)
            print (extra)
            while True:
                conn_socket, addr = s.accept()
                Thread(target=self.response, args=(conn_socket,addr,)).start()
            # client_logger.info(f"Sending message:\n/***request***/\n{message}\n/*************/", extra=extra)
            # s.sendall(message.encode(encoding))
            # client_logger.info(f"Waiting for response...", extra=extra)
            # data = s.recv(BUFFER_SIZE)
        # client_logger.info(f"Received:\n/***response***/\n{repr(data)}\n/**************/", extra=extra)

    def response(self, conn_socket:socket.socket, addr:tuple):
        sentence = conn_socket.recv(BUFFER_SIZE).decode(self.encoding)
        # Parser TODO

        # Se file encontrado
        sentence_file = "simplepage.html"
        with open(self.dir + '/' + sentence_file, "r") as f:
            HTTPcontent = f.read().encode(self.encoding)
            HTTPheader = 'HTTP/1.1 200 OK\r\n'
            HTTPheader += 'Date: {}\r\n'.format(datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z"))
            HTTPheader += 'Content-type: {}; charset={}\r\n'.format('text/html', self.encoding)
            HTTPheader += 'Content-lenght: {}\r\n'.format(HTTPcontent)
            HTTPheader += '\r\n\r\n'
            HTTPheader = HTTPheader.encode(self.encoding)
            HTTPresponse = HTTPheader + HTTPcontent

            conn_socket.sendall(HTTPresponse)


if __name__=='__main__':
    my_server = Server()
    my_server.accept('localhost', 14000, '../data')
