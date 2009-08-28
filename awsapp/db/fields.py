from datetime import datetime
from cPickle import loads,dumps
from Crypto.Cipher import AES
import base64

class Field(object):
    def __init__(self,required=False,indexed=False,label=None,default=None,**kwargs):
        self.required = required
        self.indexed = indexed
        self.label = unicode(label)
        self.default = default
    def encode(self,v):
        if v == None:
            v = ""
        return unicode(v)
    def decode(self,v):
        return v
  
class BooleanField(Field):
    def encode(self,value):
        if value not in (0,1):
            raise ValueError("BooleanField must be one of: True or False")
        return (u'0',u'1')[value]
    def decode(self,value):
        if value not in (u'0',u'1'):
            raise ValueError("Encoded BooleanField must be one of: '0' or '1'")         
        return {u'0':False,u'1':True}[value]
        
class NumericField(Field):
    def __init__(self,padding=0,precision=0,**kwargs):
        self.padding = padding
        self.precision = precision
        super(NumericField,self).__init__(**kwargs)
    def encode(self,value):      
        padding = self.padding
        if value < 0:
            padding += 1
        if self.precision > 0 and self.padding > 0:
            # Padding shouldn't include decimal digits or the decimal point.
            padding += self.precision + 1
        return (u'%%0%d.%df' % (padding, self.precision)) % (value)
    def decode(self,value):
        return float(value)

class MoneyField(NumericField):
    def __init__(self,padding=10,precision=2,**kwargs):
        super(MoneyField,self).__init__(padding=padding,precision=precision,**kwargs)

class DateTimeField(Field):
    def encode(self,value):
        if isinstance(value,datetime):
            return unicode(value.isoformat())
        else:
            raise TypeError("DateTimeField only accepts datetime objects")
    def decode(self,value):
        parts = value.split(".")
        dt = datetime.strptime(parts[0],'%Y-%m-%dT%H:%M:%S')
        if len(parts) == 2:
            return dt.replace(microsecond=int(parts[1]))
        else:
            return dt

class PickleField(Field):
    def encode(self,value):
        return unicode( dumps(value) )
    def decode(self,value):
        return loads(str(value))
        
class EncryptedField(Field):
    def __init__(self,**kwargs):
        key = crypt_config['key']
        padding = max(16,8*(len(key)/8)+8)
        self.__c = AES.new(key.rjust(padding,'X'), AES.MODE_ECB)
        super(EncryptedField,self).__init__(**kwargs)
    def encode(self,value):  
        padding = 16*(len(value)/16)+16
        npad = '%x' % (padding - len(value)-1)
        pad = '\x00'*int(npad,16)   
        v = self.__c.encrypt(value+pad+npad)
        v = base64.encodestring(v)
        return unicode(v)
    def decode(self,value):
        v = base64.decodestring(value)
        v = self.__c.decrypt(v)
        npad = int(v[-1:],16)+1
        return v[:-npad]
