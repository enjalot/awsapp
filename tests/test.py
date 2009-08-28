from awsapp.db.model import Model
from awsapp.db.fields import Field,BooleanField,NumericField,DateTimeField,MoneyField,PickleField,EncryptedField
from datetime import datetime
import random
import string
from nose.tools import *

def check(a,b):
    assert_equal(a,b)

class TestFields:
    def random_string(self,n):
        return ''.join([random.choice(string.printable) for x in xrange(n)])
    def test_boolean(self):
        f = BooleanField()
        def test(b):
            v1 = f.encode(b)
            v2 = f.decode(v1)
            assert_equal(b,v2)
        yield test,True
        yield test,False
    def test_datetime(self):
        f = DateTimeField()
        def test():
            d = datetime.today()
            v1 = f.encode(d)
            v2 = f.decode(v1)
            assert_equal(v2,d)
        for i in range(4):
            yield test,
    def test_numeric(self):
        f = NumericField()
        def test(v):
            v1 = f.encode(v)
            v2 = f.decode(v1)
            assert_equal(v2,v)
        for x in (1,1.0,-1,-1.0):
            yield test,x
    def test_numeric_padding(self):
        f1 = NumericField(padding=4)
        f2 = NumericField(padding=10)
        vs = [(1,'0001','0000000001'),(10.0,'0010','0000000010'),
                (10.1,'0010','0000000010'),(-1,'-0001','-0000000001')]
        for v1,v2,v3 in vs:
            assert f1.encode(v1) == v2
            assert f2.encode(v1) == v3
            assert f1.decode(v2) == int(v1)
            assert f2.decode(v3) == int(v1)
    def test_numeric_precision(self):
        f1 = NumericField(precision=4)
        f2 = NumericField(precision=10)
        vs = [(1.0000,'1.0000','1.0000000000'),(1.0001,'1.0001','1.0001000000'),
                (-1.0000,'-1.0000','-1.0000000000'),(10.1,'10.1000','10.1000000000')]
        for v1,v2,v3 in vs:
            assert f1.encode(v1) == v2
            assert f2.encode(v1) == v3
            assert f1.decode(v2) == v1
            assert f2.decode(v3) == v1
    def test_numeric_precision_padding(self):
        f1 = NumericField(precision=4,padding=4)
        f2 = NumericField(precision=10,padding=10)
        vs = [(1.0000,'0001.0000','0000000001.0000000000'),(1.0001,'0001.0001','0000000001.0001000000'),
                (-1.0000,'-0001.0000','-0000000001.0000000000'),(10.1,'0010.1000','0000000010.1000000000')]
        for v1,v2,v3 in vs:
            assert f1.encode(v1) == v2
            assert f2.encode(v1) == v3
            assert f1.decode(v2) == v1
            assert f2.decode(v3) == v1
    def test_numeric_money(self):
        f = MoneyField()
        vs = [(10.99,'0000000010.99'),(999.99,'0000000999.99'),
            (-10.99,'-0000000010.99'),(100000.50,'0000100000.50')]
        for v,v1 in vs:
            assert f.encode(v) == v1
            assert f.decode(v1) == v
    def test_pickle(self):
        f = PickleField()
        o = datetime.today()
        v1 = f.encode(o)
        v2 = f.decode(v1)
        assert v2 == o
    def test_encrypt(self):
        f = EncryptedField()
        sv = map(self.random_string,(15,16,17))
        for s in sv:
            v1 = f.encode(s)
            v2 = f.decode(v1)
            assert v2 == s
    def test_encrypt_long(self):
        f = EncryptedField()
        s = self.random_string(1024)
        v1 = f.encode(s)
        v2 = f.decode(v1)
        assert v2 == s
    def test_field(self):
        f = Field()
        s = "test string"
        v1 = f.encode(s)
        v2 = f.decode(v1)
        assert v1 == s

