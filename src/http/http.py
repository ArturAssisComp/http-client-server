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
####################

class HTTPResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

    def get_str_message(self):
        pass

    @staticmethod
    def parse(bytecode):
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

    @staticmethod
    def parse(bytecode):
        pass

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
    valid_abs_path = '/123//;/d/;/?oi=10'
    valid_abs_path2 = '/search/node/hello%20world'
    r1 = HTTPRequest(valid_abs_path, 'GET')
    r2 = HTTPRequest(valid_abs_path2, 'GET')
    print(f"{r1.get_str_message()}")
    print(f"{r2.get_str_message()}")

    
    #print(parse_url("http://www.ita.br/search/node/teste%20oi"))





    
