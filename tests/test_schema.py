from bson import ObjectId as object_id_factory
from decimal import Decimal as decimal_factory
from pyschema import *


def test_plain_schema():
    default_node_value = 10
    unicode_node_value = u'Blablabla'
    str_node_value = 'adfsdf sadf sdaf'
    int_node_value = 10
    float_node_value = 4.45
    decimal_node_value = decimal_factory('32.233')
    object_id_node_value = object_id_factory()

    class TestSchema(Schema):
        default_node = Default(default_node_value)
        unicode_node = Unicode()
        str_node = Str()
        int_node = Int()
        float_node = Float()
        decimal_node = Decimal()
        object_id_node = ObjectId('_object_id_node_key')

    data = {
        'default_node': 'something unexpected',
        'unicode_node': unicode_node_value,
        'str_node': str_node_value,
        'int_node': int_node_value,
        'float_node': float_node_value,
        'decimal_node': str(decimal_node_value),
        '_object_id_node_key': object_id_node_value,
    }
    schema = TestSchema()
    object = schema.decode(dict(data))
    assert isinstance(object, TestSchema.Bean)
    assert object.default_node == default_node_value
    assert object.unicode_node == unicode_node_value
    assert object.str_node == str_node_value
    assert object.int_node == int_node_value
    assert object.float_node == float_node_value
    assert object.decimal_node == decimal_node_value
    assert object.object_id_node == str(object_id_node_value)

    data.pop('default_node')
    assert data == schema.encode(object)


def test_deep_schema():
    class TestSubSchema(Schema):
        int_node = Int()


    class TestSchema(Schema):
        list_node = List(Builder(TestSubSchema()))
        dict_node = Dict(Int())

    data = {
        'list_node': [ { 'int_node': 1 }, { 'int_node': 2 }, { 'int_node': 3 }, ],
        'dict_node': { 'apple': 1, 'orange':2 },
    }
    schema = TestSchema()
    object = schema.decode(data)

    assert isinstance(object, TestSchema.Bean)
    for i in range(3):
        assert isinstance(object.list_node[i], TestSubSchema.Bean)
        assert object.list_node[i].int_node == i + 1
    assert object.dict_node['apple'] == 1
    assert object.dict_node['orange'] == 2

    assert data == schema.encode(object)


def test_registry_schema():
    one_id = 10
    two_id = 'dsafdsf'

    class TestSubOneSchema(Schema):
        id = Int()
        type = Str()

    class TestSubTwoSchema(Schema):
        id = Str()
        type = Str()


    class MyInt(int):
        __schema_registry_args = None

    class MyStr(str):
        __schema_registry_args = None


    class TestSchema(Schema):
        sub_one = Registry(lambda value: value['type'], {
            'one': Builder(TestSubOneSchema()),
            'two': Builder(TestSubTwoSchema()),
        })
        sub_two = Registry(type, {
            int: Int(decode=MyInt),
            str: Str(decode=MyStr),
        })

    data = {
        'sub_one': {
            'type': 'two',
            'id': two_id,
            },
        'sub_two': 4,
    }
    schema = TestSchema()
    object = schema.decode(data)
    assert isinstance(object, TestSchema.Bean)
    assert isinstance(object.sub_one, TestSubTwoSchema.Bean)
    assert object.sub_one.id == two_id
    assert object.sub_two == 4

    assert data == schema.encode(object)

    data = {
        'sub_one': {
            'type': 'one',
            'id': one_id,
            },
        'sub_two': None,
    }
    schema = TestSchema()
    object = schema.decode(data)
    assert isinstance(object, TestSchema.Bean)
    assert isinstance(object.sub_one, TestSubOneSchema.Bean)
    assert object.sub_one.id == one_id
    assert object.sub_two is None

    assert data == schema.encode(object)


def test_custom_factory():
    class TestSchema(Schema):
        name = Str()

    class TestCustom(object):
        def __init__(self, custom_id, status=None):
            self.id = custom_id
            self.status = status
            self.name = None

        def get_id(self):
            return self.id

        def get_name(self):
            return self.name

        def is_deleted(self):
            return self.status == 0

    class TestCustomFactory(object):
        def __init__(self, custom_id, status=None):
            self.custom_id = custom_id
            self.status = status

        def __call__(self):
            return TestCustom(self.custom_id, status=self.status)


    data = { 'name': 'CordiS' }
    regular_object = TestSchema().decode(data)
    custom_object = TestSchema(TestCustomFactory(5, status=0)).decode(data)

    assert isinstance(regular_object, TestSchema.Bean)
    assert not isinstance(regular_object, TestCustom)
    assert isinstance(custom_object, TestCustom)
    assert not isinstance(custom_object, TestSchema.Bean)
    assert custom_object.get_id() == 5
    assert custom_object.get_name() == 'CordiS'
    assert custom_object.is_deleted() is True

    assert data == TestSchema().encode(regular_object)
    assert data == TestSchema().encode(custom_object)


def test_encoding_ignore():
    class TestSchema(Schema):
        id = ObjectId('_id')

    data = { '_id': object_id_factory() }
    object = TestSchema().decode(data)
    assert isinstance(TestSchema().encode(object)['_id'], object_id_factory)
    assert isinstance(TestSchema().encode(object, ignore=[ObjectId])['_id'], str)
