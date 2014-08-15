from abc import ABCMeta

from pyschema.const import *
from pyschema.decorators import SchemaAbstractProperty


class BaseNode(object):
    def __init__(self, key=None):
        self.key = key


class Default(object):
    def __init__(self, value):
        self.value = value


class SchemaMeta(ABCMeta):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        if '__metaclass__' in cls_attrs:
            return super(SchemaMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

        bases_node_dict = {}
        for base_cls in cls_bases:
            bases_node_dict.update(getattr(base_cls, SCHEMA_ATTRIBUTE_NODES, EMPTY_DICT))

        nodes = {}
        default_nodes = {}
        for name, node in cls_attrs.items():
            if isinstance(node, SchemaAbstractProperty):
                node = node.__schema_node__
            if isinstance(node, Default):
                default_nodes[name] = node.value
            if not isinstance(node, BaseNode):
                continue
            if node.key is None:
                node.key = name
            nodes[name] = node

        cls_attrs.update(dict(dict.fromkeys(nodes.keys()), **default_nodes))
        cls_attrs[SCHEMA_ATTRIBUTE_NODES] = dict(bases_node_dict, **nodes)

        return super(SchemaMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)
