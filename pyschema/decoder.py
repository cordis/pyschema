from .nodes import *


class SchemaDecoder(object):
    visitors = None

    @classmethod
    def create_instance(cls):
        instance = cls()
        instance.visitors = {
            Str: instance._visit_value,
            Unicode: instance._visit_value,
            Int: instance._visit_value,
            Float: instance._visit_value,
            Decimal: instance._visit_value,
            ObjectId: instance._visit_value,
            Builder: instance._visit_builder,
            Registry: instance._visit_registry,
            List: instance._visit_list,
            Dict: instance._visit_dict,
        }
        return instance

    def __call__(self, node, data):
        return self._visit_node(node, data)

    def _visit_node(self, node, value):
        if value is None:
            return value
        if node.decode:
            value = node.decode(value)
        visitor = self._get_visitor(node)
        return visitor(node, value)

    def _get_visitor(self, node):
        return self.visitors[type(node)]

    def _visit_value(self, node, value):
        return value

    def _visit_builder(self, node, value):
        return self._visit_schema(node.schema, value)

    def _visit_schema(self, schema, data):
        schema.__builder__.reset()
        for attr, node in schema.get_nodes():
            value = self._visit_node(node, data[node.key])
            schema.__builder__.set_attr(attr, value)
        return schema.__builder__.get()

    def _visit_registry(self, node, value):
        args = node.args_getter(value)
        target_node = node.registry[args]
        ret = self._visit_node(target_node, value)
        self._try_schema_registry_args(ret, args)
        return ret

    def _try_schema_registry_args(self, value, args):
        try:
            value.__schema_registry_args__ = args
        except AttributeError as e:
            import warnings
            warnings.warn(str(e), UserWarning)

    def _visit_list(self, node, value):
        ret = []
        for item in value:
            ret.append(self._visit_node(node.node, item))
        return ret

    def _visit_dict(self, node, value):
        ret = {}
        for key, item in value.iteritems():
            key = self._visit_node(node.key_node, key)
            ret[key] = self._visit_node(node.value_node, item)
        return ret
