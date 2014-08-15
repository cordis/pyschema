from .const import *
from .bases import SchemaMeta
from .nodes import Builder, Registry
from .builder import SchemaBeanBuilder
from .decoder import SchemaDecoder
from .encoder import SchemaEncoder


class Schema(object):
    __metaclass__ = SchemaMeta
    __decoder__ = SchemaDecoder.create_instance()
    __encoder__ = SchemaEncoder.create_instance()

    class Interface(object):
        pass

    @classmethod
    def decode_registry(cls, data, args_getter, registry):
        return cls.__decoder__(Registry(args_getter, registry), data)

    @classmethod
    def encode_registry(cls, obj, registry):
        return cls.__encoder__(Registry(None, registry), obj)

    def __init__(self, factory=None):
        if type(self) is Schema:
            raise TypeError('Unable to instantiate base Schema class')
        if factory is not None:
            setattr(self, SCHEMA_ATTRIBUTE_FACTORY, factory)
        else:
            factory = getattr(self, SCHEMA_ATTRIBUTE_FACTORY)
        self.__builder__ = SchemaBeanBuilder(factory)

    def decode(self, data):
        return self.__decoder__(Builder(self), data)

    def encode(self, obj, ignore=None):
        return self.__encoder__(Builder(self), obj, ignore)

    def get_nodes(self):
        return getattr(self, SCHEMA_ATTRIBUTE_NODES).items()
