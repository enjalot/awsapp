import operator
from functools import partial
from awsapp.db.model import *
from awsapp.db.fields import *
from awsapp import db

class Alert(Model):
    __hash_key__="%(title)s:%(date)s"
    title = Field(indexed=True, required=True)
    author = Field(indexed=True, required=True)
    media = Field(indexed=True, required=True)
    level = Field(indexed=True, required=True)
    date = DateTimeField()
   
    def __unicode__(self): 
        return "%s - %s" % (self.title, self.author)

    @property
    def get_media_display(self):
        return self.media
