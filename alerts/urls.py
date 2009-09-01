from django.conf.urls.defaults import *

urlpatterns = patterns('motoproto.alerts.views',
    url(r'^alerts/$', 'alerts', name="alerts"),
)
