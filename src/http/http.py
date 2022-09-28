import re


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
port = '[0-9]*'
ipv4 = r"([0-9]{1,3}\.){3}([0-9]{1,3})"
hostname = r'((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}' #From: https://www.geeksforgeeks.org/how-to-validate-a-domain-name-using-regular-expression/
host = f"({ipv4})|({hostname})"
http_URL = f"http://(?P<host>({host}))(:(?P<port>{port}))?(?P<abs_path>{abs_path})?"

#Pattern for headings:
date = r'(?P<date>Date: )(?P<date_value>.*?)\r\n'
pragma = r'(?P<pragma>Pragma: )(?P<pragma_value>.*?)\r\n'
general_header = f"({date})|({pragma})"

authorization = r'(?P<authorization>Authorization: )(?P<authorization_value>.*?)\r\n'
from_ = r'(?P<from>From: )(?P<from_value>.*?)\r\n'
if_modified_since = r'(?P<if_modified_since>If-Modified-Since: )(?P<if_modified_since_value>.*?)\r\n'
referer = r'(?P<referer>Referer: )(?P<referer_value>.*?)\r\n'
user_agent = r'(?P<user_agent>User-Agent: )(?P<user_agent_value>.*?)\r\n'
request_header = f"({authorization})|({from_})|({if_modified_since})|({referer})|({user_agent})"


allow = r'(?P<allow>Allow: )(?P<allow_value>.*?)\r\n'
content_encoding = r'(?P<content_encoding>Content-Encoding: )(?P<content_encoding_value>.*?)\r\n'
content_length = r'(?P<content_length>Content-Length: )(?P<content_length_value>[0-9]+)\r\n'
content_type = r'(?P<content_type>Content-Type: )(?P<content_type_value>.*?)\r\n'
expires = r'(?P<expires>Expires: )(?P<expires_value>.*?)\r\n'
last_modified = r'(?P<last_modified>Last-Modified: )(?P<last_modified_value>.*?)\r\n'
entity_header  = f"({allow})|({content_encoding})|({content_length})|({content_type})|({expires})|({last_modified})"

#Entity body
entity_body = r'(?P<entity_body>(.|\n)*)'

#Pattern for requests:
request_line = f"(?P<method>(GET)|(HEAD)|(POST)) (?P<abs_path>{abs_path}) HTTP/(?P<major>[0-9]+)\\.(?P<minor>[0-9]+)\\r\\n"
full_request = f"({request_line})(({general_header})|({request_header})|({entity_header}))*\\r\\n({entity_body})?"
simple_request = f"(?P<method>GET) (?P<abs_path>{abs_path})\\r\\n"

####################

class HTTPResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

    def get_str_message(self):
        pass

    @staticmethod
    def parse(bytecode, encoding='utf-8'):
        pass



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
    #todo
    pass




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

    request1 = "GET /\r\n"
    print(f"Parsing for {request1 = }\n{HTTPRequest.parse(request1.encode())}")
    request1 = "GET /test/123.txt\r\n"
    print(f"Parsing for {request1 = }\n{HTTPRequest.parse(request1.encode())}")
    request2 = "GET/\r\n"
    print(f"Parsing for {request2 = }\n{HTTPRequest.parse(request2.encode())}")
    request3 = "GET /teste/oi.pdf HTTP/1.0\r\n"\
               "\r\n"\
               """Content 
               Hello World!
               Bye Bye:!!!$%#
               """
    print(f"Parsing for {request3 = }\n{HTTPRequest.parse(request3.encode())}")
    request4 = "GET /teste/oi.pdf HTTP/1.0\r\n"\
               "Date: 12/02/1990\r\n"\
               "Content-Length: 2045\r\n"\
               "Pragma: hello-world\r\n"\
               "\r\n"\
               """Content 
               Hello World!
               Bye Bye:!!!$%#
               """
    print(f"Parsing for {request4 = }\n{HTTPRequest.parse(request4.encode())}")

    request5 = "GET /oi/teste HTTP/1.0\r\nPragma: teste\r\nAuthorization: auth\r\nDate: \r\n\r\n"
    print(f"Parsing for {request5 = }\n{HTTPRequest.parse(request5.encode())}")

    




    
