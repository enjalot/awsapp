import hashlib,sys,time,zlib
from math import ceil
import boto
from awsapp.db import Field

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("awsapp/aws.conf")
aws_config = dict(config.items('aws'))
crypt_config = dict(config.items('crypt'))

class ObjectManager(object):
    def __init__(self,cls,dict,*args,**kwargs):
        self.cls = cls
        self.dict = dict
    def get(self,*args,**kwargs):
        if kwargs.has_key('order_by'):
            field_name = kwargs['order_by']
            field_obj = self.dict[field_name]
            if field_obj.label != 'None':
                field_name = field_obj.label
            print "SELECT * FROM `domain` WHERE `__class__` = '%s' ORDER BY '%s'"% (self.cls,field_name)

class ModelBase(type):
    def __init__(cls,*args,**kwargs):
        if args[0] != "Model":
            cls.objects = ObjectManager(args[0],args[2])

class Model(object):
    __metaclass__ = ModelBase
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
        attrs = map(unicode,dir(self))
        if "__hash_key__" not in attrs:
            raise Exception("Required field '__hash_key__' is not set.")
        for attr_name in attrs:
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
        else:
            pass
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
        if not item:
            pass
        #print item
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
        attr_chunks = {} # {'Content':['Content.1','Content.2']}
        for attr,value in item.items():
            if attr in ("__classname__"):
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
        #domain.delete_attributes(self.ID,["Origin"])
        domain.put_attributes(self.ID, self.__dict, replace=True)
            
            
