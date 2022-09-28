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
rel_path      = "../http"
abs_file_path = os.path.join(script_dir, rel_path)
sys.path.append(abs_file_path)
import logger_config
import http_aux as http



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
        return data



if __name__=='__main__':
    if len(sys.argv) <= 1:
        raise RuntimeError(f"Usage: {sys.argv[0]} [url1] [url2] ... [urln]")
    client = Client()
    for arg in sys.argv[1:]:
        basic_logger.info(f"Reading url: {arg}")
        host, port, abs_path = http.parse_url(arg)
        if host is None:
            basic_logger.error("Invalid url")
            continue
        if port is None:
            port = 80
        if abs_path is None:
            abs_path = '/'
        basic_logger.info(f'{host = }, {port = }, {abs_path = }')

        #Build the request:
        request = http.HTTPRequest(abs_path, 'GET').get_str_message()

        #Establish connection:
        data = client.connect(host, int(port), request, timeout=15)
        parsed_response = http.HTTPResponse.parse(data)
        if parsed_response is None:
            basic_logger.error("Invalid response")
            continue

        status_code = parsed_response['status_code']
        reason_phrase = parsed_response['reason_phrase']
        entity_body = parsed_response['entity_body']
        
        basic_logger.info(f"Reading response:")
        basic_logger.info(f"{status_code = }, {reason_phrase}")
        if status_code == '200' and len(entity_body) > 0:
            file_size = int(parsed_response['headers'].get('content_length', -1))
            if abs_path == '/':
                filename = 'index.html'
            else:
                filename = abs_path.split('/')[-1]
            received_file = entity_body.encode()[:file_size]
            basic_logger.info(f"Saving file {filename}")
            with open(filename, "wb") as f:
                f.write(received_file)
            basic_logger.info(f"Saved")







    
