#from bson import ObjectId as object_id_factory
from decimal import Decimal as decimal_factory
from pyschema import *


def test_plain_schema():
    default_node_value = 10
    unicode_node_value = u'Blablabla'
    str_node_value = 'adfsdf sadf sdaf'
    int_node_value = 10
    float_node_value = 4.45
    decimal_node_value = decimal_factory('32.233')
    #object_id_node_value = object_id_factory()

    class TestSchema(Schema):
        default_node = Default(default_node_value)
        unicode_node = Unicode()
        str_node = Str()
        int_node = Int()
        float_node = Float()
        decimal_node = Decimal('_decimal_node_key')
        #object_id_node = ObjectId('_object_id_node_key')

    data = {
        'default_node': 'something unexpected',
        'unicode_node': unicode_node_value,
        'str_node': str_node_value,
        'int_node': int_node_value,
        'float_node': float_node_value,
        '_decimal_node_key': str(decimal_node_value),
        #'_object_id_node_key': object_id_node_value,
    }
    bean = TestSchema.decode(dict(data))
    assert isinstance(bean, TestSchema)
    assert bean.default_node == default_node_value
    assert bean.unicode_node == unicode_node_value
    assert bean.str_node == str_node_value
    assert bean.int_node == int_node_value
    assert bean.float_node == float_node_value
    assert bean.decimal_node == decimal_node_value
    #assert object.object_id_node == str(object_id_node_value)

    data.pop('default_node')
    assert data == bean.encode()


def test_deep_schema():
    class TestSubSchema(Schema):
        @schema_property(Int)
        def int_node(self):
            pass

    class TestSchema(Schema):
        @schema_property(List, Builder(TestSubSchema))
        def list_node(self):
            pass

        @schema_property(Dict, Int())
        def dict_node(self):
            pass

    data = {
        'list_node': [
            {
                'int_node': 1
            },
            {
                'int_node': 2
            },
            {
                'int_node': 3
            },
        ],
        'dict_node': {
            'apple': 1,
            'orange':2
        },
    }
    bean = TestSchema.decode(data)

    assert isinstance(bean, TestSchema)
    for i in range(3):
        assert isinstance(bean.list_node[i], TestSubSchema)
        assert bean.list_node[i].int_node == i + 1
    assert bean.dict_node['apple'] == 1
    assert bean.dict_node['orange'] == 2

    assert data == bean.encode()


def test_registry_schema():
    one_id = 10
    two_id = 'dsafdsf'

    class TestSubOneSchema(Schema):
        @schema_property(Int)
        def id(self):
            pass

        @schema_property(Str)
        def type(self):
            pass

    class TestSubTwoSchema(Schema):
        @schema_property(Str)
        def id(self):
            pass

        @schema_property(Str)
        def type(self):
            pass

    class MyInt(int):
        __schema_registry_args = None

    class MyStr(str):
        __schema_registry_args = None

    class TestSchema(Schema):
        @schema_property(Registry, lambda value: value['type'], {
            'one': Builder(TestSubOneSchema),
            'two': Builder(TestSubTwoSchema),
        })
        def sub_one(self):
            pass

        @schema_property(Registry, type, {
            int: Int(decode=MyInt),
            str: Str(decode=MyStr),
        })
        def sub_two(self):
            pass

    data = {
        'sub_one': {
            'type': 'two',
            'id': two_id,
        },
        'sub_two': 4,
    }
    bean = TestSchema.decode(data)
    assert isinstance(bean, TestSchema)
    assert isinstance(bean.sub_one, TestSubTwoSchema)
    assert bean.sub_one.id == two_id
    assert bean.sub_two == 4

    assert data == bean.encode()

    data = {
        'sub_one': {
            'type': 'one',
            'id': one_id,
            },
        'sub_two': None,
    }
    bean = TestSchema.decode(data)
    assert isinstance(bean, TestSchema)
    assert isinstance(bean.sub_one, TestSubOneSchema)
    assert bean.sub_one.id == one_id
    assert bean.sub_two is None

    assert data == bean.encode()


def test_encoding_ignore():
    class TestSchema(Schema):
        @schema_property(Int, '_id')
        def test_id(self):
            pass

    data = {
        '_id': '123'
    }
    bean = TestSchema.decode(data)
    assert isinstance(bean.encode()['_id'], int)
    assert isinstance(bean.encode(ignore=[Int])['_id'], str)


if __name__ == '__main__':
    test_plain_schema()
    test_deep_schema()
    test_registry_schema()
    #test_encoding_ignore()
