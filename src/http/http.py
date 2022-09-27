
class HTTPResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

    def encode(self):
        pass

    @staticmethod
    def parse(bytecode):
        pass



class HTTPRequest(object):
    def __init__(self, URL, method):
        self.URL = URL
        self.method = method

    def encode(self):
        pass

    @staticmethod
    def parse(bytecode):
        pass

if __name__ == "__main__":
    
