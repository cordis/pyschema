from decimal import Decimal as DecimalDecoder
try:
    from bson import ObjectId as ObjectIdEncoder
except ImportError:
    def ObjectIdEncoder(*args):
        raise ImportWarning('`bson` module not found')

from pyschema.bases import BaseNode


__all__ = [
    'Node',
    'Str',
    'Unicode',
    'Int',
    'Bool',
    'Float',
    'Decimal',
    'ObjectId',
    'Builder',
    'Registry',
    'List',
    'Dict',
]


class Node(BaseNode):
    default_encode = None
    default_decode = None

    def __init__(self, key=None, decode=None, encode=None):
        super(Node, self).__init__(key)
        if decode is None:
            decode = self.default_decode
        if encode is None:
            encode = self.default_encode
        self.decode = decode
        self.encode = encode


class Str(Node):
    default_decode = str


class Unicode(Node):
    default_decode = unicode


class Int(Node):
    default_decode = int


class Bool(Node):
    default_decode = bool


class Float(Node):
    default_decode = float


class Decimal(Node):
    default_decode = DecimalDecoder
    default_encode = str


class ObjectId(Node):
    default_decode = str
    default_encode = ObjectIdEncoder


class Builder(Node):
    default_decode = dict

    def __init__(self, schema_cls, key=None):
        super(Builder, self).__init__(key=key)
        self.schema_cls = schema_cls


class Registry(Node):
    def __init__(self, args_getter, registry, key=None):
        super(Registry, self).__init__(key=key)
        self.args_getter = args_getter
        self.registry = registry


class List(Node):
    default_decode = list
    default_encode = list

    def __init__(self, node, **kwargs):
        super(List, self).__init__(**kwargs)
        self.node = node


class Dict(Node):
    default_decode = dict
    default_encode = dict

    def __init__(self, value_node, key_node=None, **kwargs):
        super(Dict, self).__init__(**kwargs)
        self.value_node = value_node
        self.key_node = key_node or Str()
