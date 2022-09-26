from audioop import add
from http import server
from threading import Thread
from time import sleep
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

    def accept(self, server_port:int, encoding='utf-8', timeout=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('',server_port))
            s.listen() # Parameters could be an int32 with number of max connections, or nothing to do this automatically
            extra = {'hostname': socket.gethostname(), 'ip': socket.gethostbyname(socket.gethostname())}
            s.settimeout(timeout)
            # server_logger.info("Connecting...", extra=extra)
            print (extra)
            while True:
                conn_socket, addr = s.accept()
                Thread(target=self.answer, args=(conn_socket,addr,)).start()
            # client_logger.info(f"Sending message:\n/***request***/\n{message}\n/*************/", extra=extra)
            # s.sendall(message.encode(encoding))
            # client_logger.info(f"Waiting for response...", extra=extra)
            # data = s.recv(BUFFER_SIZE)
        # client_logger.info(f"Received:\n/***response***/\n{repr(data)}\n/**************/", extra=extra)

    def answer(self, conn_socket:socket.socket, addr:tuple):
        sentence = conn_socket.recv(BUFFER_SIZE).decode('utf-8')
        # Retorna a mesma mensagem após 0.5s
        sleep(0.5)
        conn_socket.sendall(sentence.encode('utf-8'))
        print("Mensagem Enviada")


if __name__=='__main__':
    my_server = Server()
    my_server.accept(14000)
