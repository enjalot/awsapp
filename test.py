from db import Model,Field,BooleanField,NumericField,DateTimeField,MoneyField,PickleField,EncryptedField
from datetime import datetime
import random
import string

class TestFields:
    def random_string(self,n):
        return ''.join([random.choice(string.printable) for x in xrange(n)])
    def test_boolean(self):
        f = BooleanField()
        def test(b):
            v1 = f.encode(b)
            v2 = f.decode(v1)
            assert b == v2
        yield test,True
        yield test,False
    def test_datetime(self):
        f = DateTimeField()
        def test():
            d = datetime.today()
            v1 = f.encode(d)
            v2 = f.decode(v1)
            assert v2 == d
        for i in range(4):
            yield test
    def test_numeric(self):
        f = NumericField()
        def test(v):
            v1 = f.encode(v)
            v2 = f.decode(v1)
            assert v2 == v
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
        s = self.random_string(24)
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

if __name__ == "__main__":
    a = Author('2a7f6bdd7b88945c68726322811f47a3')
    print a
    print a.Origin
    a.save()
    exit()
    #print a
    
    #r = Recipe('cd8ee30995a3f4afc046c226217d80a1')
    #r.save()
    
    a = Author(FirstName="David",Email="mumrah@gmail.com")
    a.BirthDay = datetime.strptime("1985-02-04","%Y-%m-%d")
    a.Origin = Recipe(Author=a) 
    a.save()
    print a
    exit()
    
    
    r = Recipe(Name="My Test Recipe",Author=a)
    r.Content = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In lectus massa,
fermentum sit amet iaculis ac, luctus et purus. Nunc arcu velit, dictum nec
congue cursus, luctus vitae risus. Pellentesque vel risus lacus. Sed adipiscing
urna a leo pharetra sed tincidunt augue dignissim. Duis fringilla enim in nibh
sagittis in tempor ante rhoncus. Class aptent taciti sociosqu ad litora torquent
per conubia nostra, per inceptos himenaeos. Lorem ipsum dolor sit amet,
consectetur adipiscing elit. Donec aliquet consequat lacus, et vulputate turpis
interdum nec. Donec consectetur volutpat ipsum ut porta. Integer ornare mattis
diam, vel volutpat magna pretium non. Praesent consequat rhoncus tincidunt.

Nunc in ipsum vel magna laoreet dignissim. Etiam eu magna libero, at tempor
lacus. Suspendisse sollicitudin odio ut augue convallis mattis. Duis erat nibh,
gravida quis tempor non, faucibus eget nisi. Nulla facilisi. Nullam tristique,
mi convallis congue varius, libero dui feugiat felis, sollicitudin eleifend
lectus metus ac nibh. Mauris mauris nisl, ultricies eu blandit eget, dapibus id
odio. Sed ac mattis ipsum. Aliquam blandit faucibus ante nec sodales. Nunc dolor
sapien, bibendum vel congue ac, pharetra nec sem. Aenean eu ornare libero. Nam
luctus mauris non mi pretium eget lacinia nisl sodales. Maecenas luctus risus
sed turpis posuere consectetur. Aliquam varius, velit vel egestas accumsan, nibh
magna vulputate enim, non iaculis lorem diam non nulla. Integer et odio enimrat, eu
orci aliquam""".replace("\n","")
    #print r
    r.save()
