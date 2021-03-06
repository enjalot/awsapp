import hashlib
from itertools import izip,count
import logging
from math import ceil
import sys
import time
import zlib

import boto

from awsapp.db import *
from awsapp.db.fields import Field
from awsapp.config import *

class ObjectManager(object):
    def __init__(self,cls,name,attrs,parts=None,*args,**kwargs):
        self.cls = cls
        self.name = name 
        self.dict = attrs
        if parts:
            self.parts = parts
        else:
            self.parts = dict(order_by=None,
                where=["`__classname__` = '%s'" % self.name],
                where_in=[],select=[])
    def create(self,*args,**kwargs):
        return self.cls(*args,**kwargs)
    def order_by(self,field):
        # Set the order_by field
        if self.parts.has_key('order_by'):
            logging.warning("order by is already set, you are overriding it")
        # If the user requests a non-existant field
        if not self.dict.has_key(field):
            logging.error("Invalid key for %s Model" % self.name)
            return self
        # See if the Field has a label
        field_obj = self.dict[field]
        if field_obj.label != 'None':
            field = field_obj.label
        # Set the order_by key in query parts dict 
        self.parts['order_by'] = field
        return self
    def delete(self):
        # This needs expanding
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        items = domain.select("SELECT * FROM `awsapp` WHERE `__classname__` = '%s'" % self.name)
        for item in items:
            domain.delete_item(item)
    def filter(self,field,value,op):
        self.parts['where'] += [where(field,value,op)]
        return self
    def compound_filter(self,where):
        if type(where) != CompoundWhere:
            raise TypeError("First argument must be a CompoundWhere object")
        self.parts['where'] += [where]
        return self
    def all(self):
        return self[:]
    def get(self,*args,**kwargs):
        for field,value in kwargs.items():
            if field in self.cls.field_objs.keys():
                print "`%s`='%s'" %(self.cls.field_objs[field].label,value)
                pass
        # Will this actually do anything?
        return self
    def __compile(self):
        query_parts = ["SELECT * FROM `awsapp` WHERE"]
        query_parts += [" AND ".join(map(unicode,self.parts['where']))]
        self.__query = " ".join(query_parts)
        print self.__query
    def __execute(self):
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        self.__results = domain.select( self.__query )
    def __getitem__(self,x):
        self.__compile()
        self.__execute()
        items = [item for item in self.__results].__getitem__(x)
        results = []
        for item in items:
            o = self.cls()
            o._load_from_dict(item)
            o._to_dict()
            results += [o]
        return results
    def __iter__(self):
        # Execute the query, and yield the results
        self.__compile()
        self.__execute()
        for item in self.__results:
            o = self.cls()
            o._load_from_dict(item)
            yield o 

class ModelBase(type):
    def __init__(cls,*args,**kwargs):
        if args[0] != "Model":
            cls.objects = ObjectManager(cls,args[0],args[2])
            cls.req_fields = []
            cls.field_objs = {}
            cls.refs = {}
            if "__hash_key__" not in args[2].keys():
                raise Exception("Required field '__hash_key__' is not set.")
            for attr_name,attr in args[2].items():
                if attr_name == u"ID":
                    continue
                # Handle Field attributes
                if isinstance(attr,Field):
                    if not attr.label:
                        attr.label = attr_name
                    if attr.required == True:
                        cls.req_fields += [attr_name]
                    cls.field_objs[attr_name] = attr
                # Handle Model (reference) attributes
                elif isinstance(attr,Model):
                    cls.refs[attr_name] = attr
                else:
                    continue

class Model(object):
    __metaclass__ = ModelBase
    def __init__(self,*args,**kwargs):
        # Set default values for fields
        for field_name,field_obj in self.field_objs.items():
            setattr(self,field_name,field_obj.default) 
        # Create a placeholder for references
        for ref_name,ref in self.refs.items():
            setattr(self,ref_name,"")
        # Process arguments
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
    def __repr__(self):
        return "<%s, %s>" % (self.__class__.__name__,self.__dict__)
    @property
    def ID(self):
        self.checkFields()
        return hashlib.md5(
            '%s:%s' % (self.__class__.__name__,self.__hash_key__ % self)).hexdigest()
    def __getitem__(self,k):
        v = getattr(self,k,"")
        #if isinstance(v,Model):
        #    v = v.ID
        return v
    def checkFields(self):
        for field in self.req_fields:
            if not getattr(self,field):
                raise Exception("Required field '%s' is not set" % field)
    @classmethod
    def _field_checksum(self,fields):
        fields.sort()
        return u"%x" % zlib.crc32( repr(fields) )
    @classmethod
    def _checksum(self,d):
        keys = d.keys()
        keys.sort()
        out = zip( map(unicode,keys), map(unicode,map(d.get,keys)) )
        return u"%x" % zlib.crc32( repr(out) )
    def setField(self,field,value):
        if hasattr(self,field):
            setattr(self,field,value)
        else:
            raise Exception("Undefined field '%s' for class '%s'" % (field,self.__class__.__name__))
    def _to_dict(self):
        self.__dict = {}
        # Go through each field and encode the values
        for field_name,field_obj in self.field_objs.items():
            value = self[field_name] 
            encoded_value = field_obj.encode(value)
            if encoded_value == u"": # Don't try to split empty strings
                self.__dict[field_name] = encoded_value
                continue
            # TODO: Move this to awsapp.util
            chunk = lambda v, l: [v[i*l:(i+1)*l] for i in range(int(ceil(len(v)/float(l))))]
            values = chunk(encoded_value,1000) # Make 1000 byte chunks
            if len(values) == 1:
                self.__dict[field_name] = values[0]
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
        self.__dict['__checksum__'] = self._checksum(self.__dict)
        self.__dict['__field_checksum__'] = self._field_checksum(self.field_objs.keys() + self.refs.keys())
    def load(self,id):
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        item = domain.get_item(id)
        if not item:
            pass
        self._load_from_dict(item)
    def _load_from_dict(self,item):
        # Given an Item from SimpleDB, load it into an object
        old_checksum = item['__checksum__']
        field_checksum = item['__field_checksum__']
        del item['__checksum__']
        del item['__field_checksum__']
        # Check data integrity first - see that the checksum is correct
        if old_checksum == self._checksum(item):
            logging.debug("Checksum is OK (%s)" % old_checksum)
        else:
            logging.warning("Checksums do not match. Data integrity cannot be guaranteed")
        # See if the fields have changed
        new_field_checksum = self._field_checksum(
                self.field_objs.keys() + self.refs.keys())
        if field_checksum == new_field_checksum:
            logging.debug("Object schema has not changed")
        else:
            logging.warning("Schema has changed")
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
            # Attributes to ignore
            if attr in ("__classname__","__next__","__prev__"):
                continue
            if attr[-4:] == ".len":
                base = attr.split(".len")[0]
                if base in self.field_objs.keys():
                    attr_chunks[base] = []
                continue
            if attr in self.refs:
                attr_obj = self.refs[attr]
                attr_obj.load(value)
                setattr(self,attr,attr_obj)
            if attr in self.field_objs.keys():
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
        self._to_dict()
        sdb = boto.connect_sdb(**aws_config)
        domain = sdb.get_domain('awsapp')
        domain.put_attributes(self.ID, self.__dict, replace=True)
            


