from django.conf.urls.defaults import *

urlpatterns = patterns('motoproto.alerts.views',
    url(r'^$', 'alerts', name="alerts"),
    url(r'^create$', 'create', name="create"),
)
