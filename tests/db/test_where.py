from awsapp.db.model import Model
from awsapp.db.fields import *
from awsapp import db
from datetime import datetime
import nose

import logging
logging.basicConfig(level=logging.ERROR)

def assert_equals(a,b,*args):
    assert str(a)==str(b)

# The test Model
class TestModel(Model):
    __hash_key__ = "%(Field1)s"
    Field1 = Field()
    Field2 = DateTimeField()
    Field3 = NumericField()

# Test operators
def test_ops():
    yield assert_equals,db.EQ.value,"="
    yield assert_equals,db.NEQ.value,"!="
    yield assert_equals,db.LT.value,"<"
    yield assert_equals,db.GT.value,">"
    yield assert_equals,db.LEQ.value,"<="
    yield assert_equals,db.GEQ.value,">="
    yield assert_equals,db.IN.value,"IN"
    yield assert_equals,db.NIN.value,"NOT IN"

# Test singlton where clauses
def test_where_s1():
    yield assert_equals,db.where('attr1','value1'),"`attr1` = 'value1'"
def test_where_s2():
    yield assert_equals,db.where('attr1','value1',db.NEQ),"`attr1` != 'value1'"
def test_where_s3():
    yield assert_equals,db.where('attr1','value1',db.LT),"`attr1` < 'value1'"
def test_where_s4():
    yield assert_equals,db.where('attr1','value1',db.LEQ),"`attr1` <= 'value1'"
def test_where_s5():
    yield assert_equals,db.where('attr1','value1',db.GT),"`attr1` > 'value1'"
def test_where_s6():
    yield assert_equals,db.where('attr1','value1',db.GEQ),"`attr1` >= 'value1'"
def test_where_s7():
    yield assert_equals,db.where('attr1','value1',db.EQ),"`attr1` = 'value1'"

# Test singlton where clauses using Field objects
def test_where_f1():
    yield assert_equals,db.where(TestModel.Field1,'value1'),"`Field1` = 'value1'"
    yield assert_equals,db.where(TestModel.Field1,'value1',db.EQ),"`Field1` = 'value1'"
    yield assert_equals,db.where(TestModel.Field1,'value1',db.NEQ),"`Field1` != 'value1'"
def test_where_f2():
    d = datetime.now()
    yield assert_equals,db.where(TestModel.Field2,d),"`Field2` = '%s'" % TestModel.Field2.encode(d)
    yield assert_equals,db.where(TestModel.Field2,d,db.LT),"`Field2` < '%s'" % TestModel.Field2.encode(d)
    yield assert_equals,db.where(TestModel.Field2,d,db.LEQ),"`Field2` <= '%s'" % TestModel.Field2.encode(d)
def test_where_f3():
    v = 42.3
    yield assert_equals,db.where(TestModel.Field3,v),"`Field3` = '%s'" % TestModel.Field3.encode(v)
    yield assert_equals,db.where(TestModel.Field3,v,db.GT),"`Field3` > '%s'" % TestModel.Field3.encode(v)
    yield assert_equals,db.where(TestModel.Field3,v,db.GEQ),"`Field3` >= '%s'" % TestModel.Field3.encode(v)

# Test set where clauses
def test_where_m1():
    yield assert_equals,db.where('attr1',['value1a','value1b']),"`attr1` IN ('value1a','value1b')"
def test_where_m2():
    yield assert_equals,db.where('attr1',['value1a','value1b'],db.IN),"`attr1` IN ('value1a','value1b')"
def test_where_m3():
    yield assert_equals,db.where('attr1',['value1a','value1b'],db.NIN),"`attr1` NOT IN ('value1a','value1b')"
def test_where_m4():
    yield assert_equals,db.where(TestModel.Field1,['value1','value2']),"`Field1` IN ('value1','value2')"
def test_where_m5():
    d = datetime.now()
    yield assert_equals,db.where(TestModel.Field2,(d,d)),"`Field2` IN ('%(d)s','%(d)s')" % \
                    dict(d=TestModel.Field2.encode(d))
    yield assert_equals,db.where(TestModel.Field2,(d,d),db.IN),"`Field2` IN ('%(d)s','%(d)s')" % \
                    dict(d=TestModel.Field2.encode(d))
    yield assert_equals,db.where(TestModel.Field2,(d,d),db.NIN),"`Field2` NOT IN ('%(d)s','%(d)s')" % \
                    dict(d=TestModel.Field2.encode(d))

# Test 'every()' where clauses
def test_where_e1():
    yield assert_equals,db.where_every('attr1','value1'),"every(`attr1`) = 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.EQ),"every(`attr1`) = 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.NEQ),"every(`attr1`) != 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.GT),"every(`attr1`) > 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.GEQ),"every(`attr1`) >= 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.LT),"every(`attr1`) < 'value1'"
    yield assert_equals,db.where_every('attr1','value1',db.LEQ),"every(`attr1`) <= 'value1'"
def test_where_e2():
    yield assert_equals,db.where_every('attr1',('value1','value2')),"every(`attr1`) IN ('value1','value2')"
    yield assert_equals,db.where_every('attr1',('value1','value2'),db.IN),"every(`attr1`) IN ('value1','value2')"
    yield assert_equals,db.where_every('attr1',('value1','value2'),db.NIN),"every(`attr1`) NOT IN ('value1','value2')"
def test_where_e3():
    yield assert_equals,db.where_every(TestModel.Field1,'value1'),"every(`Field1`) = 'value1'"
    yield assert_equals,db.where_every(TestModel.Field1,'value1',db.EQ),"every(`Field1`) = 'value1'"
    yield assert_equals,db.where_every(TestModel.Field1,'value1',db.NEQ),"every(`Field1`) != 'value1'"
def test_where_e4():
    d = datetime.now()
    yield assert_equals,db.where_every(TestModel.Field2,d),"every(`Field2`) = '%s'" % TestModel.Field2.encode(d) 
    yield assert_equals,db.where_every(TestModel.Field2,d,db.EQ),"every(`Field2`) = '%s'" % TestModel.Field2.encode(d) 
    yield assert_equals,db.where_every(TestModel.Field2,d,db.NEQ),"every(`Field2`) != '%s'" % TestModel.Field2.encode(d)
def test_where_e5():
    yield assert_equals,db.where_every(TestModel.Field1,('value1','value2')),"every(`Field1`) IN ('value1','value2')"
    yield assert_equals,db.where_every(TestModel.Field1,('value1','value2'),db.IN),"every(`Field1`) IN ('value1','value2')"
    yield assert_equals,db.where_every(TestModel.Field1,('value1','value2'),db.NIN),"every(`Field1`) NOT IN ('value1','value2')"
def test_where_e6():
    v = 42.7
    yield assert_equals,db.where_every(TestModel.Field3,(v,v)),"every(`Field3`) IN ('%(v)s','%(v)s')" % dict(v=TestModel.Field3.encode(v))

# Test simple combined clauses
def test_where_and1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    yield assert_equals,db.and_(c1,c2),"`attr1` = 'value1' AND `attr2` = 'value2'"

def test_where_and2():
    c1 = db.where(TestModel.Field1,'value1')
    c2 = db.where(TestModel.Field1,'value2')
    yield assert_equals,db.and_(c1,c2),"`Field1` = 'value1' AND `Field1` = 'value2'"

def test_where_or1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    yield assert_equals,db.or_(c1,c2),"`attr1` = 'value1' OR `attr2` = 'value2'"

def test_where_or2():
    v1 = 'value1'
    v2 = datetime.now()
    c1 = db.where(TestModel.Field1,v1)
    c2 = db.where(TestModel.Field2,v2)
    yield assert_equals,db.or_(c1,c2),"`Field1` = '%s' OR `Field2` = '%s'" % (v1, TestModel.Field2.encode(v2))



#2 combinations
def test_where_and_and1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    c3 = db.where('attr3','value3')
    yield assert_equals,db.and_(db.and_(c2,c3),c1),"(`attr2` = 'value2' AND `attr3` = 'value3') AND `attr1` = 'value1'"

def test_where_and_and2():
    t = {}
    t['v1'] = 'value1'
    t['v2'] = datetime.now()
    t['v3'] = 42
    c1 = db.where(TestModel.Field1,t['v1'])
    c2 = db.where(TestModel.Field2,t['v2'])
    c3 = db.where(TestModel.Field3,t['v3'])
    t['v1'] = TestModel.Field1.encode(t['v1'])
    t['v2'] = TestModel.Field2.encode(t['v2'])
    t['v3'] = TestModel.Field3.encode(t['v3'])
    yield assert_equals,db.and_(db.and_(c2,c3),c1),"(`Field2` = '%(v2)s' AND `Field3` = '%(v3)s') AND `Field1` = '%(v1)s'" % t


def test_where_or_or1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    c3 = db.where('attr3','value3')
    yield assert_equals,db.or_(db.or_(c2,c3),c1),"(`attr2` = 'value2' OR `attr3` = 'value3') OR `attr1` = 'value1'"

def test_where_or_or2():
    t = {}
    t['v1'] = 'value1'
    t['v2'] = datetime.now()
    t['v3'] = 42
    c1 = db.where(TestModel.Field1,t['v1'])
    c2 = db.where(TestModel.Field2,t['v2'])
    c3 = db.where(TestModel.Field3,t['v3'])
    t['v1'] = TestModel.Field1.encode(t['v1'])
    t['v2'] = TestModel.Field2.encode(t['v2'])
    t['v3'] = TestModel.Field3.encode(t['v3'])

    yield assert_equals,db.or_(db.or_(c2,c3),c1),"(`Field2` = '%(v2)s' OR `Field3` = '%(v3)s') OR `Field1` = '%(v1)s'" % t


def test_where_and_or1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    c3 = db.where('attr3','value3')
    yield assert_equals,db.and_(db.or_(c2,c3),c1),"(`attr2` = 'value2' OR `attr3` = 'value3') AND `attr1` = 'value1'"

def test_where_and_or2():
    t = {}
    t['v1'] = 'value1'
    t['v2'] = datetime.now()
    t['v3'] = 42
    c1 = db.where(TestModel.Field1,t['v1'])
    c2 = db.where(TestModel.Field2,t['v2'])
    c3 = db.where(TestModel.Field3,t['v3'])
    t['v1'] = TestModel.Field1.encode(t['v1'])
    t['v2'] = TestModel.Field2.encode(t['v2'])
    t['v3'] = TestModel.Field3.encode(t['v3'])

    yield assert_equals,db.and_(db.or_(c2,c3),c1),"(`Field2` = '%(v2)s' OR `Field3` = '%(v3)s') AND `Field1` = '%(v1)s'" % t


def test_where_or_and1():
    c1 = db.where('attr1','value1')
    c2 = db.where('attr2','value2')
    c3 = db.where('attr3','value3')
    yield assert_equals,db.or_(db.and_(c2,c3),c1),"(`attr2` = 'value2' AND `attr3` = 'value3') OR `attr1` = 'value1'"

def test_where_or_and2():
    t = {}
    t['v1'] = 'value1'
    t['v2'] = datetime.now()
    t['v3'] = 42
    c1 = db.where(TestModel.Field1,t['v1'])
    c2 = db.where(TestModel.Field2,t['v2'])
    c3 = db.where(TestModel.Field3,t['v3'])
    t['v1'] = TestModel.Field1.encode(t['v1'])
    t['v2'] = TestModel.Field2.encode(t['v2'])
    t['v3'] = TestModel.Field3.encode(t['v3'])

    yield assert_equals,db.or_(db.and_(c2,c3),c1),"(`Field2` = '%(v2)s' AND `Field3` = '%(v3)s') OR `Field1` = '%(v1)s'" % t


# Test complex combined clauses


