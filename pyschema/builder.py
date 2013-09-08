class SchemaObjectBuilder(object):
    def __init__(self, factory):
        self.factory = factory
        self.instance = None

    def reset(self):
        self.instance = self.factory()

    def set_attr(self, name, value):
        setattr(self.instance, name, value)

    def get(self):
        return self.instance
