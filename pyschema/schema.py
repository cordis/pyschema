from pyschema.const import *
from pyschema.bases import SchemaMeta
from pyschema.nodes import Builder, Registry
from pyschema.decoder import SchemaDecoder
from pyschema.encoder import SchemaEncoder


class Schema(object):
    __metaclass__ = SchemaMeta
    __encoder__ = SchemaEncoder.create_instance()
    __decoder__ = SchemaDecoder.create_instance()

    @classmethod
    def decode_registry(cls, data, args_getter, registry):
        return cls.__decoder__(Registry(args_getter, registry), data)

    @classmethod
    def encode_registry(cls, obj, registry):
        return cls.__encoder__(Registry(None, registry), obj)

    @classmethod
    def decode(cls, data):
        return cls.__decoder__(Builder(cls), data)

    @classmethod
    def get_nodes(cls):
        return getattr(cls, SCHEMA_ATTRIBUTE_NODES).items()

    def __init__(self):
        if type(self) is Schema:
            raise TypeError('Unable to instantiate base Schema class')
        print type(self)

    def encode(self, ignore=None):
        return self.__encoder__(Builder(type(self)), self, ignore)
