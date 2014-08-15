from .const import *


class BaseNode(object):
    def __init__(self, key=None):
        self.key = key


class Default(object):
    def __init__(self, value):
        self.value = value


class SchemaMeta(type):
    def __new__(mcs, cls_name, cls_bases, cls_attrs):
        if '__metaclass__' in cls_attrs:
            return super(SchemaMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)

        bases_node_dict = {}
        bases_factory_list = []
        for base_cls in cls_bases:
            bases_node_dict.update(getattr(base_cls, SCHEMA_ATTRIBUTE_NODES, EMPTY_DICT))
            bases_factory_list.append(getattr(base_cls, SCHEMA_ATTRIBUTE_FACTORY, None))

        nodes = {}
        default_nodes = {}
        for name, node in cls_attrs.items():
            if isinstance(node, Default):
                default_nodes[name] = node.value
            if not isinstance(node, BaseNode):
                continue
            if node.key is None:
                node.key = name
            nodes[name] = node

        if SCHEMA_ATTRIBUTE_FACTORY not in cls_attrs:
            factory_name = cls_name + SCHEMA_ATTRIBUTE_FACTORY
            factory_attrs = dict(dict.fromkeys(nodes.keys()), **default_nodes)
            factory_bases = list(filter(bool, bases_factory_list))
            if SCHEMA_ATTRIBUTE_INTERFACE in cls_attrs:
                factory_bases.insert(0, cls_attrs[SCHEMA_ATTRIBUTE_INTERFACE])
            if not factory_bases:
                factory_bases = (object, )
                factory_attrs['__schema__registry_args__'] = None
            cls_attrs[SCHEMA_ATTRIBUTE_FACTORY] = type(factory_name, tuple(factory_bases), factory_attrs)

        cls_attrs[SCHEMA_ATTRIBUTE_NODES] = dict(bases_node_dict, **nodes)

        return super(SchemaMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)
