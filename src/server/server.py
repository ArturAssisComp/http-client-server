from http import server
from threading import Thread
from time import sleep
from datetime import datetime
from contextlib import contextmanager
import socket
import logging
import sys
import os
import pathlib

# Add path to logger_config file
script_dir    = os.path.dirname(__file__)
rel_path      = ".."
abs_file_path = os.path.join(script_dir, rel_path)
sys.path.append(abs_file_path)
rel_path      = "../http"
abs_file_path = os.path.join(script_dir, rel_path)
sys.path.append(abs_file_path)
import logger_config
import http_aux as http


BUFFER_SIZE = 2048
server_logger = logging.getLogger('server_logger')
basic_logger = logging.getLogger('basic_logger')


class Server(object):
    def __init__(self):
        pass

    def accept(self, host:str, server_port:int, base_dir:str, encoding='utf-8', timeout=None):
        extra = {'server_hostname': socket.gethostname(), 'server_ip': socket.gethostbyname(socket.gethostname()), 'server_port':server_port, 'client_host':"", 'client_port':""}
        
        if pathlib.PurePath(base_dir).is_absolute():
            self.dir = base_dir
        else:
            self.dir = os.path.join(script_dir, base_dir)
        self.encoding = encoding
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host,server_port))
            s.listen() # Parameters could be an int32 with number of max connections, or nothing to do this automatically
            s.settimeout(timeout)
            server_logger.info("Starting server...", extra=extra)
            while True:
                server_logger.info(f"Waiting for connections (dir:{base_dir}):", extra=extra)
                conn_socket, addr = s.accept()
                tmp_extra = extra.copy()
                tmp_extra['client_host'] = addr[0]
                tmp_extra['client_port'] = int(addr[1])
                server_logger.info(f"Connection accepted", extra=tmp_extra)
                Thread(target=self.response, args=(conn_socket,addr,), kwargs={'logging_extra_info':tmp_extra}).start()

    def response(self, conn_socket:socket.socket, addr:tuple, logging_extra_info=None):
        if logging_extra_info is None:
            logging_extra_info = {'server_hostname': socket.gethostname(), 'server_ip': socket.gethostbyname(socket.gethostname()), 'server_port':"", 'client_host':"", 'client_port':""}

        sentence = conn_socket.recv(BUFFER_SIZE)
        server_logger.info(f"Parsing received content.", extra=logging_extra_info)
        # Here, we check for the possibility of a 400 response
        result = http.HTTPRequest.parse(sentence, self.encoding)
        if result is None:
            server_logger.error(f"Bad request (400)", extra=logging_extra_info)
            headers = {
                "Date":f'{datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")}'}
            status_code = 400
            entity_body = None
        else:
            # Se file encontrado
            sentence_file = result['abs_path']
            if sentence_file == '/':
                sentence_file = '/index.html'
            server_logger.info(f"File requested: {sentence_file}", extra=logging_extra_info)
            with open_handling_error(self.dir + sentence_file, "r", logging_extra_info=logging_extra_info) as (f, status):
                if status == 200:
                    status_code = 200
                    entity_body = f.read()
                    HTTPcontent = entity_body[:].encode(self.encoding)
                    headers = {
                        "Date":f'{datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")}',
                        "Content-Type":f"text/html; charset=utf-8",
                        "Content-Length":len(HTTPcontent)}

                elif status == 404:
                    status_code = 404 
                    entity_body = None 
                    headers = {
                        "Date":f'{datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")}'}

        response_msg = http.HTTPResponse(status_code, entity_body=entity_body, headers=headers).get_str_message()
        server_logger.info(f"Response header created: \n/***response***/\n{response_msg}\n/*************/", extra=logging_extra_info) 
        conn_socket.sendall(response_msg.encode(self.encoding)) 
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
    if len(sys.argv) != 4:
        raise RuntimeError(f"Usage: {sys.argv[0]} [host] [port] [dir]")
    my_server = Server()
    host, port, dir_ = sys.argv[1], sys.argv[2], sys.argv[3]
    my_server.accept(host, int(port), dir_)
