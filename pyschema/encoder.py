from .nodes import *


class SchemaEncoder(object):
    visitors = None
    EMPTY = ()

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

    def __call__(self, node, obj, ignore=None):
        if ignore is None:
            ignore = self.EMPTY
        return self._visit_node(node, obj, ignore)

    def _visit_node(self, node, obj, ignore):
        if obj is None or type(node) in ignore:
            return obj
        visitor = self._get_visitor(node)
        value = visitor(node, obj, ignore)
        if node.encode:
            value = node.encode(value)
        return value

    def _get_visitor(self, node):
        return self.visitors[type(node)]

    def _visit_value(self, node, obj, ignore):
        return obj

    def _visit_builder(self, node, obj, ignore):
        return self._visit_schema(node.schema, obj, ignore)

    def _visit_schema(self, schema, obj, ignore):
        value = {}
        for attr, node in schema.get_nodes():
            value[node.key] = self._visit_node(node, getattr(obj, attr), ignore)
        return value

    def _visit_registry(self, node, obj, ignore):
        args = self._try_schema_registry_args(obj)
        if args is None:
            return obj
        target_node = node.registry[args]
        return self._visit_node(target_node, obj, ignore)

    def _try_schema_registry_args(self, obj):
        try:
            return obj.__schema_registry_args__
        except AttributeError as e:
            import warnings
            warnings.warn(str(e), UserWarning)
            return None

    def _visit_list(self, node, obj, ignore):
        ret = []
        for item in obj:
            ret.append(self._visit_node(node.node, item, ignore))
        return ret

    def _visit_dict(self, node, obj, ignore):
        ret = {}
        for key, item in obj.iteritems():
            key = self._visit_node(node.key_node, key, ignore)
            ret[key] = self._visit_node(node.value_node, item, ignore)
        return ret
