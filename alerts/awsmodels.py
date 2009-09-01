import operator
from functools import partial
from awsapp.db.model import *
from awsapp.db.fields import *
from awsapp.db import Where,and_,or_,op

class Alert(Model):
    __hash_key__="%(Title)s%(Date)s"
    title = Field(indexed=True, required=True)
    author = Field(indexed=True, required=True)
    media = Field(indexed=True, required=True)
    level = Field(indexed=True, required=True)
    date = DateTimeField()
    
    @property
    def get_media_display(self):
        return "%s - %s" % (self.title, self.author)
