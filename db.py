import hashlib,time,zlib
from math import ceil
from datetime import datetime
from cPickle import loads,dumps
from Crypto.Cipher import AES
import base64

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("aws.conf")
aws_config = dict(config.items('aws'))
crypt_config = dict(config.items('crypt'))

import boto
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
        v = self.__c.encrypt(value.ljust(padding,'\x00'))
        v = base64.encodestring(v)
        return unicode(v)
    def decode(self,value):
        v = base64.decodestring(value)
        v = self.__c.decrypt(v)
        return v.strip('\x00')
        
 
class Model(object):
    def __repr__(self):
        return "<%s, %s>" % (self.__class__.__name__,self.ID)
    @property
    def ID(self):
        self.checkFields()
        #return '%s:%s' % (self.__class__.__name__,self.__hash_key__ % self )
        return hashlib.md5(
            '%s:%s' % (self.__class__.__name__,self.__hash_key__ % self)).hexdigest()
    def __getitem__(self,k):
        v = getattr(self,k,"")
        #if isinstance(v,Model):
        #    v = v.ID
        return v
    def __init__(self,*args,**kwargs):
        # Build a list of fields for this model
        self.fields = []
        self.req_fields = []
        self.field_objs = {}
        self.refs = {}
        for attr_name in map(unicode,dir(self)):
            if attr_name == u"ID":
                continue
            attr = getattr(self,attr_name)
            # Handle Field attributes
            if isinstance(attr,Field):
                if not attr.label:
                    attr.label = attr_name
                if attr.required == True:
                    self.req_fields += [attr_name]
                self.fields += [attr_name]
                self.field_objs[attr_name] = attr
                # Set default value
                setattr(self,attr_name,attr.default)
            # Handle Model (reference) attributes
            elif isinstance(attr,Model):
                self.refs[attr_name] = attr
                setattr(self,attr_name,"")
        # Handle arguments
        if len(args) == 1 and len(kwargs) == 0:
            # Got and ID, load the object
            self.load(args[0])
        elif len(args) == 0 and len(kwargs) > 0:
            # Got some kwargs to load data into the object
            for k,v in kwargs.items():
                if hasattr(self,k):
                    self.setField(k,v)
                else:
                    raise Exception("Undefined field '%s' for class '%s'" % (k,self.__class__.__name__))
    def checkFields(self):
        for field in self.req_fields:
            if not getattr(self,field):
                raise Exception("Required field '%s' is not set" % field)
    def __field_checksum(self,fields):
        fields.sort()
        return u"%x" % zlib.crc32( repr(fields) )
    def __checksum(self,d):
        keys = d.keys()
        keys.sort()
        out = zip( map(unicode,keys), map(unicode,map(d.get,keys)) )
        return u"%x" % zlib.crc32( repr(out) )
            
    def setField(self,field,value):
        if hasattr(self,field):
            setattr(self,field,value)
        else:
            raise Exception("Undefined field '%s' for class '%s'" % (field,self.__class__.__name__))
    def __to_dict(self):
        self.__dict = {}
        # Go through each field and encode the values
        for field in self.fields:
            value = self[field]
            field_obj = self.field_objs[field]
            encoded_value = field_obj.encode(value)
            if encoded_value == u"": # Don't try to split empty strings
                self.__dict[field] = encoded_value
                continue
            chunk = lambda v, l: [v[i*l:(i+1)*l] for i in range(int(ceil(len(v)/float(l))))]
            values = chunk(encoded_value,1000) # Make 1000 byte chunks
            if len(values) == 1:
                self.__dict[field] = values[0]
            else:
                for value,i in zip(values,range(len(values))):
                    self.__dict['%s.%s' % (field,i+1)] = value
                self.__dict['%s.len' % (field)] = len(values)
        # Set the 'foreign keys'
        for ref in self.refs.keys(): 
            self[ref].save() # Save any members which are Model subtypes
            self.__dict[ref] = self[ref].ID # We only store the item ID
        # Set the __classname__ field so we know what kind of object we're storing
        self.__dict['__classname__'] = self.__class__.__name__
        self.__dict['__checksum__'] = self.__checksum(self.__dict)
        self.__dict['__field_checksum__'] = self.__field_checksum(self.fields + self.refs.keys())
    def load(self,id):
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        item = domain.get_item(id)
        
        old_checksum = item['__checksum__']
        field_checksum = item['__field_checksum__']
        del item['__checksum__']
        del item['__field_checksum__']
        
        # See that the checksum is correct
        if old_checksum == self.__checksum(item):
            print "Checksum is OK (%s)" % old_checksum
        else:
            print "Checksums do not match. Data integrity cannot be guaranteed"
        
        # See if the fields have changed
        if field_checksum == self.__field_checksum(self.fields + self.refs.keys()):
            print "Object schema has not changed"
        else:
            print "Schema has changed"
        # Check that this is the right class
        if item['__classname__'] != self.__class__.__name__:
            raise Exception("Classname mismatch: Expected '%s', got '%s'" % (
                self.__class__.__name__,item['__classname__']))
        # First grab all required attributes
        for field in self.req_fields:
            if item.has_key(field):
                continue
            else:
                raise Exception("Required field '%s' is not set" % field)
        # Load all the fields from the sdb item into the object
        attr_chunks = {}
        for attr,value in item.items():
            if attr == "__classname__":
                continue
            if attr[-4:] == ".len":
                base = attr.split(".len")[0]
                if base in self.fields:
                    attr_chunks[base] = []
                continue
            if attr in self.refs:
                attr_obj = self.refs[attr]
                attr_obj.load(value)
                setattr(self,attr,attr_obj)
            if attr in self.fields:
                field_obj = self.field_objs[attr]
                decoded_value = field_obj.decode(value)
                setattr(self,attr,decoded_value)
        # Gather all pieces to striped attributes
        for attr,value in item.items():
            for base in attr_chunks.keys():
                if base in attr and attr[-4:] != ".len":
                    attr_chunks[base] += [attr]
        # Reconstruct striped attributes
        for attr,chunks in attr_chunks.items():
            field_obj = self.field_objs[attr]
            value = field_obj.decode("".join([item[chunk] for chunk in chunks]))
            setattr(self,attr,value)
    def save(self):
        self.checkFields()
        self.__to_dict()
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        domain.delete_attributes(self.ID,["Origin"])
        domain.put_attributes(self.ID, self.__dict, replace=True)
            
            
