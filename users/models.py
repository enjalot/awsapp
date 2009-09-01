from django.db import models

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_save


#this creates a custom User class that inherits all of the functionality of standard Django Users
#The only problem here is deleting a MotorUser doesn't delete the Django user
class MotorUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    #info    
    description = models.TextField(blank=True)
    #preferences

    def __unicode__(self):
        return self.user.username

#Creates the User profile automatically when a User is created
def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        mu = MotorUser(user=user)
        mu.save()
post_save.connect(create_profile, sender=User)

#TODO create something to auto-delete the User if profile is deleted


admin.site.register(MotorUser)

