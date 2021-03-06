from awsapp.db.fields import Field
from functools import partial
import logging
class operator:
    def __init__(self,name,value,isSetOp):
        self.name = name
        self.value = value
        self.isSetOp = isSetOp
    def __repr__(self):
        return "%s" % self.value

EQ  = operator('Equals','=',False)
NEQ = operator('Not Equals','!=',False)
LT  = operator('Less Than','<',False)
LEQ = operator('Less Than or Equals','<=',False)
GT  = operator('Greater Than','>',False)
GEQ = operator('Greater Than or Equals','>=',False)
IN  = operator('In','IN',True)
NIN = operator('Not In','NOT IN',True)

class CompoundWhere(object):
    def __init__(self,cmp,a,b):
        self.a = a
        self.b = b
        if cmp in ('AND','OR'):
            self.cmp = cmp
        else:
            raise ValueError("cmp can only be a valid SQL comparison operator: AND or OR")
    def __repr__(self):
        if isinstance(self.a,CompoundWhere) and isinstance(self.b,CompoundWhere):
            return "(%s) %s (%s)" % (self.a,self.cmp,self.b)
        elif isinstance(self.a,CompoundWhere):
            return "(%s) %s %s" % (self.a,self.cmp,self.b)
        elif isinstance(self.b,CompoundWhere):
            return "%s %s (%s)" % (self.a,self.cmp,self.b)
        else:
            return "%s %s %s" % (self.a,self.cmp,self.b)

class where(object):
    def __init__(self,attr,value,op=None):
        # Check for the type of attr
        if isinstance(attr,Field):
            pass
        elif isinstance(attr,basestring):
            logging.warning("It is best to use Field objects instead of strings. We are treating this attribute as a plain Field with no special encoding")
            attr = Field(label=attr)
        else:
            raise ValueError("You must provide a string or a Field object")
        self.attr = attr.label
        # See if value was actually a list of values
        if type(value) in (list,tuple):
            self.isSetCompoundWhere = True
            self.value = map(attr.encode,value)
        else:
            self.isSetCompoundWhere = False
            self.value = attr.encode(value)
        # If no operator was specified, default to EQ or IN
        if not op:
            if self.isSetCompoundWhere:
                self.op = IN
            else:
                self.op = EQ
        else:
            if self.isSetCompoundWhere and op in (IN,NIN):
                self.op = op
            elif self.isSetCompoundWhere and op not in (IN,NIN):
                raise ValueError("Set-based Where clauses can only use the db.IN or db.NIN operators")
            else:
                self.op = op
    def __repr__(self):
        if self.isSetCompoundWhere:
            return u"`%s` %s (%s)" % (self.attr,self.op,','.join(["'%s'"%v for v in self.value]))
        else:
            return u"`%s` %s '%s'" % (self.attr,self.op,self.value)
    def __str__(self):
        return repr(self) 
    def __cmp__(self,x):
        return repr(self) == x

class where_every(where):
    def __init__(self,attr,value,op=None):
        where.__init__(self,attr,value,op)
        self.attr = "every(`%s`)" % self.attr
    def __repr__(self):
        if self.isSetCompoundWhere:
            return "%s %s (%s)" % (self.attr,self.op,','.join(["'%s'"%v for v in self.value]))
        else:
            return "%s %s '%s'" % (self.attr,self.op,self.value)

and_ = partial(CompoundWhere,"AND")
or_  = partial(CompoundWhere,"OR")


