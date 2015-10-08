import inspect

def method(*types):
    def decorator(jrpcMethod):
        jrpcMethod.params = zip(types, inspect.getargspec(jrpcMethod.remote_func)[0][1:])
        return jrpcMethod
    return decorator

class interface(object):
    def __init__(self):
        self.methods = {}
        boring = dir(type('dummy', (object,), {}))
        return [item
                for item in inspect.getmembers(cls)
                if item[0] not in boring]
        self.attributes = {}

class attributeType(object):
    def __init__(self, atype = "object"):
        self.type = atype
        self.name = None

class NUMBER(attributeType):
    def __init__(self, vmin = None, vmax = None):
        attributeType.__init__(self, "number")
        self.min = vmin
        self.max = vmax

class STRING(attributeType):
    def __init__(self, vmin = None, vmax = None):
        attributeType.__init__(self, "number")
        self.min = vmin
        self.max = vmax