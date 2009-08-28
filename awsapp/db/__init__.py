from functools import partial
class op:
   eq="="
   neq="!="
   lt="<"
   leq="<="
   gt=">"
   geq=">="


class Comp(object):
    def __init__(self,cmp,a,b):
        self.a = a
        self.b = b
        if cmp in ('AND','OR'):
            self.cmp = cmp
        else:
            raise ValueError("cmp can only be a valid SQL comparison operator: AND or OR")
    def __repr__(self):
        if isinstance(self.a,Comp) and isinstance(self.b,Comp):
            return "(%s) %s (%s)" % (self.a,self.cmp,self.b)
        elif isinstance(self.a,Comp):
            return "(%s) %s %s" % (self.a,self.cmp,self.b)
        elif isinstance(self.b,Comp):
            return "%s %s (%s)" % (self.a,self.cmp,self.b)
        else:
            return "%s %s %s" % (self.a,self.cmp,self.b)

class Where(object):
    def __init__(self,attr,value):
        self.attr = attr
        self.value = value
    def __repr__(self):
        return "`%s` = '%s'" % (self.attr,self.value)

and_ = partial(Comp,"AND")
or_  = partial(Comp,"OR")


