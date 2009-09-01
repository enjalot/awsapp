from awsapp.db.model import Model
from awsapp.db.fields import *
from awsapp import db
from datetime import datetime
import nose

import logging
logging.basicConfig(level=logging.ERROR)

# The test Model
class TestModel(Model):
    __hash_key__ = "%(Field1)s"
    Field1 = Field()
    Field2 = DateTimeField()
    Field3 = NumericField()

# Test operators
def test_ops():
    assert db.EQ.value == "="
    assert db.NEQ.value == "!="
    assert db.LT.value == "<"
    assert db.GT.value == ">"
    assert db.LEQ.value == "<="
    assert db.GEQ.value == ">="
    assert db.IN.value == "IN"
    assert db.NIN.value == "NOT IN"

# Test singlton where clauses
def test_where_s1():
    assert db.where('attr1','value1') == "`attr1` = 'value1'"
def test_where_s2():
    assert db.where('attr1','value1',db.NEQ) == "`attr1` != 'value1'"
def test_where_s3():
    assert db.where('attr1','value1',db.LT) == "`attr1` < 'value1'"
def test_where_s4():
    assert db.where('attr1','value1',db.LEQ) == "`attr1` <= 'value1'"
def test_where_s5():
    assert db.where('attr1','value1',db.GT) == "`attr1` > 'value1'"
def test_where_s6():
    assert db.where('attr1','value1',db.GEQ) == "`attr1` >= 'value1'"

# Test singlton where clauses using Field objects
def test_where_f1():
    assert db.where(TestModel.Field1,'value1') == "`Field1` = 'value1'"
def test_where_f2():
    d = datetime.now()
    assert db.where(TestModel.Field2,d) == "`Field2` = '%s'" % TestModel.Field2.encode(d)
def test_where_f3():
    v = 42.3
    assert db.where(TestModel.Field3,v) == "`Field3` = '%s'" % TestModel.Field3.encode(v)

# Test set where clauses

# Test simple combined clauses

# Test complex combined clauses
