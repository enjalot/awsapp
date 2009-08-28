import operator
from functools import partial
from awsapp.db.model import *
from awsapp.db.fields import *
from awsapp.db import Where,and_,or_,op

class Author(Model):
    __hash_key__  = "%(Email)s"
    FirstName = Field(indexed=True,required=True)
    LastName  = Field(indexed=True)
    Email     = Field(indexed=True,required=True)
    Origin    = PickleField()
    BirthDay  = DateTimeField()
    
    @property
    def Name(self):
        return "%s %s" % (self.FirstName, self.LastName)

class Recipe(Model):
    __hash_key__  = "%(Name)s:%(Author)s"
    Name         = Field(indexed=True)
    Author       = Author()
    Content      = Field()
    Original     = BooleanField(default=True)
    LastModified = DateTimeField(default=datetime.today())

class Foo(Model):
    __hash_key__ = "%(Bar)s"
    Bar = Field()
    Enc = EncryptedField()

if __name__ == "__main__":

    # These are used by ObjectModel - Users shouldn't really use 
    # these directly, but whatever
    w1 = Where('attr1','value1')
    w2 = Where('attr2','value2')
    w3 = Where('attr3','value3')

    print and_(w1,or_(w3,w2))

    #def cmpattr(a,b,c):
    #    # Compares c.a with b
    #    return getattr(c,a) == b
    #f = partial(cmpattr,'FirstName','David')
    #authors = filter(f,Author.objects.get())
    #for a in authors:
    #    print a.Name

    authors = Author.objects.get(FirstName='David')
    authors = Author.objects.filter(Author.FirstName,'David',op.eq)
    for a in authors[::-1]:
        print a.Name


    #r = Recipe('7ebe81e6419f30b0dbd521e1872d681b')
    #print r.Name
    #print r.Content
    #print r.Author.Name
    #exit()
    #r.save()
    
    #a = Author(FirstName="David",Email="mumrah@gmail.com")
    #a.BirthDay = datetime.strptime("1985-02-04","%Y-%m-%d")
    #a.Origin = Recipe(Author=a) 
    #a.save()
    #print a
    #exit()
