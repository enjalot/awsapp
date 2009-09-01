from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.conf import settings

from motoproto.alerts.models import *

from motoproto.utils import render_to

@render_to('base/base.html')
def index(request):
    return {'hello': "Hello B&N"}


@render_to('alerts/index.html')
def alerts(request):
    alerts = Alert.objects.all().order_by('-date')
    return {'alerts': alerts} 

