from abc import abstractproperty


class SchemaAbstractProperty(abstractproperty):
    __schema_node__ = None


def schema_property(node_factory, *args, **kwargs):
    """
    @rtype: C{type}
    """
    class SchemaConcreteProperty(SchemaAbstractProperty):
        __schema_node__ = node_factory(*args, **kwargs)
    return SchemaConcreteProperty
