from awsapp.db.fields import *
from awsapp.db.model import Model,ObjectManager
from awsapp import db
import zlib
import nose
from random import shuffle

class TestModel(Model):
    __hash_key__ = "%(Field1)s"
    Field1 = Field()
    Field2 = Field()

class Test_ModelSuite:
    def test_checksum(self):
        k = [u'Field1',u'Field2',u'Field3']
        v = [u'Value1',u'Value2',u'Value3']
        cs = "%x" % zlib.crc32( repr(zip(k,v)) )
        k = k[::-1]
        v = v[::-1]
        assert cs == Model._checksum( dict(zip(k,v)) )
    def test_field_checksum(self):
        k = [u'Field1',u'Field2',u'Field3']
        cs = "%x" % zlib.crc32( repr(k) )
        k = k[::-1]
        assert cs == Model._field_checksum(k)
    def test_fields(self):
        assert "Field1" in TestModel.field_objs.keys()
        assert "Field2" in TestModel.field_objs.keys()
    def test_values(self):
        m = TestModel(Field1="Value1",Field2="Value2")
        assert m.Field1 == u"Value1"
        assert m.Field2 == u"Value2"

class Test_DBSuite:
    def test_comps(self):
        pass 
    def test_objects(self):
        assert isinstance(TestModel.objects,ObjectManager)
    def test_get(self):
        TestModel.objects
