from functools import partial

from pyschema.bases import SchemaAbstractProperty
from pyschema.nodes import Builder
from pyschema.schema import Schema


def schema_property(node_factory, *args, **kwargs):
    """
    @rtype: C{type}
    """
    if isinstance(node_factory, Schema):
        node_factory = partial(Builder, node_factory)

    class SchemaConcreteProperty(SchemaAbstractProperty):
        __schema_node__ = node_factory(*args, **kwargs)

    return SchemaConcreteProperty
