from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.conf import settings

#from motoproto.alerts.models import *
from motoproto.alerts.awsmodels import *

from motoproto.utils import render_to

@render_to('base/base.html')
def index(request):
    return {'hello': "Hello B&N"}


@render_to('alerts/index.html')
def alerts(request):
    #alerts = Alert.objects.all().order_by('-date')
    #a = Alert(title="Numerical Recipes", author="I. Dunnough", media="TV", date=datetime.now(), level=8)
    #a.save()
    alerts = Alert.objects.get()[::]
    return {'alerts': alerts} 


@render_to('alerts/create.html')
def create(request):
    a = Alert(title="Numerical Recipes", author="I. Dunnough", media="TV", date=datetime.now(), level=8)
    a.save()
    #b = Alert(title="Goosebumps", author="RL Stien", media="Magazine", date=datetime.now(), level=3)
    #b.save()
    #c = Alert(title="Boondocks", author="A. McGregor", media="TV", date=datetime.now(), level=5)
    #c.save()
    #d = Alert(title="Mining for Gold", author="I.P. Freely", media="Web", date=datetime.now(), level=10)
    #d.save()
    alerts = Alert.objects.get()[::]
    print "alerts", alerts
    return {'alerts': alerts}



