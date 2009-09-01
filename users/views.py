from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

#from django.contrib.auth.models import User
from motoproto.users.models import *
from motoproto.users.forms import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

#@render_to: decorator for render_to_response
from motoproto.utils import render_to#, datagrid_helper

#from dojango.util import to_dojo_data
#from dojango.decorators import json_response


@render_to('users/register.html')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password2"])
            login(request, user)
            return HttpResponseRedirect(reverse("news")) #TODO: add support for next redirection
    else:
        form = RegisterForm()
        #TODO: add support for next redirection
    
    return {'form':form}

@login_required
@render_to('users/profile.html')
def profile(request, userid):
    tu = get_object_or_404(MotorUser, pk=userid)
    if tu.user == request.user:
        return HttpResponseRedirect(reverse('user-edit-profile', args=[userid]))
    else:
        return {'motor_user':mu}
   
