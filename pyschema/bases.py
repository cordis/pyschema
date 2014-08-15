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


        bases_nodes = {}
        bases_factories = []
        for base_cls in cls_bases:
            bases_nodes.update(getattr(base_cls, SCHEMA_ATTRIBUTE_NODES, EMPTY_DICT))
            bases_factories.append(getattr(base_cls, SCHEMA_ATTRIBUTE_FACTORY, None))

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
            factory_bases = tuple(filter(bool, bases_factories))
            factory_attrs = dict(dict.fromkeys(nodes.keys()), **default_nodes)
            if not factory_bases:
                factory_bases = (object, )
                factory_attrs['__schema__registry_args__'] = None
            cls_attrs[SCHEMA_ATTRIBUTE_FACTORY] = type(factory_name, factory_bases, factory_attrs)

        cls_attrs[SCHEMA_ATTRIBUTE_NODES] = dict(bases_nodes, **nodes)

        return super(SchemaMeta, mcs).__new__(mcs, cls_name, cls_bases, cls_attrs)
