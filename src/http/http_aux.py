import re
from datetime import datetime


######Patterns######
#Pattern for abs path:
reserved = r";|/|\?|:|@|&|=|\+"
safe     = r"\$|-|_|\."
extra    = r"!|\*|'|\(|\)|,"
escape   = r"%[a-fA-F0-9][a-fA-F0-9]"

unreserved = f"[a-zA-Z]|[0-9]|({safe})|({extra})"
uchar      = f"({unreserved})|({escape})"
pchar      = f"({uchar})|:|@|&|=|\\+"
fsegment   = f"({pchar})+"
segment    = f"({pchar})*"
param      = f"(({pchar})|/)*"
params     = f"({param})(;({param}))*" 
query      = f"(({uchar})|({reserved}))*"
path       = f"({fsegment})(/({segment}))*"
rel_path   = f"({path})?(;({params}))?(\\?({query}))?"
abs_path   = f"/({rel_path})"

#Pattern for method:
method = "(GET)|(POST)"

#Pattern for URL:
port     = '[0-9]*'
ipv4     = r"([0-9]{1,3}\.){3}([0-9]{1,3})"
hostname = r'(((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6})|(((?!-)[A-Za-z0-9-]{1,63}(?<!-)))' #From: https://www.geeksforgeeks.org/how-to-validate-a-domain-name-using-regular-expression/
host     = f"({ipv4})|({hostname})"
http_URL = f"http://(?P<host>({host}))(:(?P<port>{port}))?(?P<abs_path>{abs_path})?"

#Pattern for headings:
date           = r'(?P<date>Date: )(?P<date_value>.*?)\r\n'
pragma         = r'(?P<pragma>Pragma: )(?P<pragma_value>.*?)\r\n'
general_header = f"({date})|({pragma})"

authorization     = r'(?P<authorization>Authorization: )(?P<authorization_value>.*?)\r\n'
from_             = r'(?P<from>From: )(?P<from_value>.*?)\r\n'
if_modified_since = r'(?P<if_modified_since>If-Modified-Since: )(?P<if_modified_since_value>.*?)\r\n'
referer           = r'(?P<referer>Referer: )(?P<referer_value>.*?)\r\n'
user_agent        = r'(?P<user_agent>User-Agent: )(?P<user_agent_value>.*?)\r\n'
request_header    = f"({authorization})|({from_})|({if_modified_since})|({referer})|({user_agent})"


allow            = r'(?P<allow>Allow: )(?P<allow_value>.*?)\r\n'
content_encoding = r'(?P<content_encoding>Content-Encoding: )(?P<content_encoding_value>.*?)\r\n'
content_length   = r'(?P<content_length>Content-Length: )(?P<content_length_value>[0-9]+)\r\n'
content_type     = r'(?P<content_type>Content-Type: )(?P<content_type_value>.*?)\r\n'
expires          = r'(?P<expires>Expires: )(?P<expires_value>.*?)\r\n'
last_modified    = r'(?P<last_modified>Last-Modified: )(?P<last_modified_value>.*?)\r\n'
entity_header    = f"({allow})|({content_encoding})|({content_length})|({content_type})|({expires})|({last_modified})|(.*?: .*?\\r\\n)"

location = r'(?P<location>Location: )(?P<location_value>.*?)\r\n'
server = r'(?P<server>Server: )(?P<server_value>.*?)\r\n'
www_authenticate = r'(?P<www_authenticate>WWW-Authenticate: )(?P<www_authenticate_value>.*?)\r\n'
response_header = f"({location})|({server})|({www_authenticate})"
#Entity body
entity_body = r'(?P<entity_body>(.|\n)*)'

#Pattern for requests:
request_line   = f"(?P<method>(GET)|(HEAD)|(POST)) (?P<abs_path>{abs_path}) HTTP/(?P<major>[0-9]+)\\.(?P<minor>[0-9]+)\\r\\n"
full_request   = f"({request_line})(({general_header})|({request_header})|({entity_header}))*\\r\\n({entity_body})?"
simple_request = f"(?P<method>GET) (?P<abs_path>{abs_path})\\r\\n"

#Pattern for response:
status_line = r'HTTP/(?P<major>[0-9]+)\.(?P<minor>[0-9]+) (?P<status_code>[0-9]{3}) (?P<reason_phrase>[A-Za-z]+[a-zA-Z ]*)\r\n'
full_response = f"({status_line})(({general_header})|({response_header})|({entity_header}))*\\r\\n({entity_body})?"


####################

class HTTPResponse(object):
    def __init__(self, status_code, reason_phrase=None, entity_body=None, major=1, minor=0, headers=None):
        if not isinstance(status_code, int):
            raise TypeError("status code must be ant int")
        if status_code not in {200, 201, 202, 204, 301, 302, 304, 400, 401, 403, 404, 500, 501, 502, 503}:
            raise ValueError(f"Invalid status code {status_code}")
        self.status_code = status_code
        reason_phrase_dict = {
                    200:"OK",
                    201:"Created",
                    202:"Accepted",
                    204:"No Content",
                    301:"Moved Permanently",
                    302:"Moved Temporarily",
                    304:"Not Modified",
                    400:"Bad Request",
                    401:"Unauthorized",
                    403:"Forbidden",
                    404:"Not Found",
                    500:"Internal Server Error",
                    501:"Not Implemented",
                    502:"Bad Gateway",
                    503:"Service Unavailable"}
        if reason_phrase is None:
            reason_phrase = reason_phrase_dict[status_code]
        self.reason_phrase = reason_phrase
        if entity_body is None:
            entity_body = ""
        self.entity_body = entity_body
        self.major=major
        self.minor=minor
        if headers is None:
            headers = dict()
        self.headers = headers

    def get_str_message(self):
        header_str_builder = []
        for name, value in self.headers.items():
            header_str_builder.append(f"{name}: {value}\r\n")
        response = f'HTTP/{self.major}.{self.minor} {self.status_code} {self.reason_phrase}\r\n{"".join(header_str_builder)}\r\n{self.entity_body}'
        return response





    @staticmethod
    def parse(bytecode, encoding='utf-8'):
        global full_response
        response_str = bytecode.decode(encoding=encoding)
        # Try to parse full response:
        re_full_response = re.compile("^" + full_response)
        match = re_full_response.match(response_str)
        if match:
            status_code = match.group('status_code')
            reason_phrase = match.group('reason_phrase')
            major = match.group('major')
            minor = match.group('minor')
            #Get headers:
            headers = dict()
            date = match.group('date')
            if date:
                headers['date'] = match.group('date_value')
            pragma = match.group('pragma')
            if pragma:
                headers['pragma'] = match.group('pragma_value')
            location = match.group('location')
            if location:
                headers['location'] = match.group('location_value')
            server = match.group('server')
            if server:
                headers['server'] = match.group('server_value')
            www_authenticate = match.group('www_authenticate')
            if www_authenticate:
                headers['www_authenticate'] = match.group('www_authenticate_value')
            allow = match.group('allow')
            if allow:
                headers['allow'] = match.group('allow_value')
            content_encoding = match.group('content_encoding')
            if content_encoding:
                headers['content_encoding'] = match.group('content_encoding_value')
            content_length = match.group('content_length')
            if content_length:
                headers['content_length'] = match.group('content_length_value')
            content_type = match.group('content_type')
            if content_type:
                headers['content_type'] = match.group('content_type_value')
            expires = match.group('expires')
            if expires:
                headers['expires'] = match.group('expires_value')
            last_modified = match.group('last_modified')
            if last_modified:
                headers['last_modified'] = match.group('last_modified_value')

            #Get the entity body:
            entity_body = match.group("entity_body")
            if entity_body is None:
                entity_body = ""
            return {'status_code':status_code, 'reason_phrase':reason_phrase, 'major':major, 'minor':minor, 'headers':headers, 'entity_body':entity_body}
        return None




class HTTPRequest(object):
    def __init__(self, abs_path, method):
        if is_abs_path(abs_path):
            self.abs_path = abs_path 
        else:
            raise ValueError(f"{abs_path} is an invalid abs_path")
        if is_method(method):
            self.method   = method
        else:
            raise ValueError(f"{method} is not a valid method.")

    def get_str_message(self):
        return f"{self.method} {self.abs_path} HTTP/1.0\r\n\r\n"

    #This parser can not handle duplicated headers
    @staticmethod
    def parse(bytecode, encoding='utf-8'):
        global simple_request
        global full_request
        request_str = bytecode.decode(encoding=encoding)
        #Try to parse simple-request
        re_simple_request = re.compile("^" + simple_request + "$")
        match = re_simple_request.match(request_str)
        if match:
            method = match.group('method')
            abs_path = match.group('abs_path')
            major = 0
            minor = 9
            entity_body = ""
            return {'method':method, 'abs_path':abs_path, 'major':major, 'minor':minor, 'headers':dict(), 'entity_body':entity_body}
        #Parse request line:
        re_full_request = re.compile("^" + full_request)
        match = re_full_request.match(request_str)
        if match:
            method = match.group('method')
            abs_path = match.group('abs_path')
            major = match.group('major')
            minor = match.group('minor')
            #Get headers:
            headers = dict()
            date = match.group('date')
            if date:
                headers['date'] = match.group('date_value')
            pragma = match.group('pragma')
            if pragma:
                headers['pragma'] = match.group('pragma_value')
            authorization = match.group('authorization')
            if authorization:
                headers['authorization'] = match.group('authorization_value')
            from_ = match.group('from')
            if from_:
                headers['from'] = match.group('from_value')
            if_modified_since = match.group('if_modified_since')
            if if_modified_since:
                headers['if_modified_since'] = match.group('if_modified_since_value')
            referer = match.group('referer')
            if referer:
                headers['referer'] = match.group('referer_value')
            user_agent = match.group('user_agent')
            if user_agent:
                headers['user_agent'] = match.group('user_agent_value')
            allow = match.group('allow')
            if allow:
                headers['allow'] = match.group('allow_value')
            content_encoding = match.group('content_encoding')
            if content_encoding:
                headers['content_encoding'] = match.group('content_encoding_value')
            content_length = match.group('content_length')
            if content_length:
                headers['content_length'] = match.group('content_length_value')
            content_type = match.group('content_type')
            if content_type:
                headers['content_type'] = match.group('content_type_value')
            expires = match.group('expires')
            if expires:
                headers['expires'] = match.group('expires_value')
            last_modified = match.group('last_modified')
            if last_modified:
                headers['last_modified'] = match.group('last_modified_value')

            #Get the entity body:
            entity_body = match.group("entity_body")
            if entity_body is None:
                entity_body = ""
            return {'method':method, 'abs_path':abs_path, 'major':major, 'minor':minor, 'headers':headers, 'entity_body':entity_body}
        return None




def parse_url(url):
    global http_URL 
    re_agent = re.compile("^" + http_URL + "$")
    match = re_agent.match(url)
    if match:
        host     = match.group('host')
        port     = match.group('port')
        abs_path = match.group('abs_path')
        return (host, port, abs_path)
    return None, None, None




def is_method(strn:str)->bool:
    global method 
    re_agent = re.compile("^" + method + "$")
    return re_agent.match(strn) is not None

def is_abs_path(strn:str)->bool:
    global abs_path
    re_agent = re.compile("^" + abs_path + "$")
    return re_agent.match(strn) is not None

if __name__ == "__main__":
    #valid_abs_path = '/123//;/d/;/?oi=10'
    #valid_abs_path2 = '/search/node/hello%20world'
    #r1 = HTTPRequest(valid_abs_path, 'GET')
    #r2 = HTTPRequest(valid_abs_path2, 'GET')
    #print(f"{r1.get_str_message()}")
    #print(f"{r2.get_str_message()}")
    
    #print(parse_url("http://www.ita.br/search/node/teste%20oi"))

    #request1 = "GET /\r\n"
    #print(f"Parsing for {request1 = }\n{HTTPRequest.parse(request1.encode())}")
    #request1 = "GET /test/123.txt\r\n"
    #print(f"Parsing for {request1 = }\n{HTTPRequest.parse(request1.encode())}")
    #request2 = "GET/\r\n"
    #print(f"Parsing for {request2 = }\n{HTTPRequest.parse(request2.encode())}")
    #request3 = "GET /teste/oi.pdf HTTP/1.0\r\n"\
    #           "\r\n"\
    #           """Content 
    #           Hello World!
    #           Bye Bye:!!!$%#
    #           """
    #print(f"Parsing for {request3 = }\n{HTTPRequest.parse(request3.encode())}")
    #request4 = "GET /teste/oi.pdf HTTP/1.0\r\n"\
    #           "Date: 12/02/1990\r\n"\
    #           "Content-Length: 2045\r\n"\
    #           "Pragma: hello-world\r\n"\
    #           "\r\n"\
    #           """Content 
    #           Hello World!
    #           Bye Bye:!!!$%#
    #           """
    #print(f"Parsing for {request4 = }\n{HTTPRequest.parse(request4.encode())}")

    #request5 = "GET /oi/teste HTTP/1.0\r\nPragma: teste\r\nAuthorization: auth\r\nDate: \r\n\r\n"
    #print(f"Parsing for {request5 = }\n{HTTPRequest.parse(request5.encode())}")

    entity_body = "Hello World!\n<body><h>\n"
    headers = {
            "Date":f'{datetime.today().strftime("%a, %d %b %Y %H:%M:%S %Z")}',
            "Content-Type":f"text/html; charset=utf-8",
            "Content-Length":len(entity_body)}
    response = HTTPResponse(301, entity_body=entity_body, headers=headers).get_str_message()
    print(f'{response}')
    print(f'\n{HTTPResponse.parse(response.encode())}')


    




    
