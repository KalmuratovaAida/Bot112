import pjsua2 as pj

class Endpoint(pj.Endpoint):
    instance = None
    def __init__(self):
        pj.Endpoint.__init__(self)
        Endpoint.instance = self
