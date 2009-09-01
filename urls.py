from django.conf.urls.defaults import *

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^motoproto/', include('motoproto.foo.urls')),

    url(r'^$', 'motoproto.alerts.views.alerts', name="index"),        #this view could be changed
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'users/login.html'}, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'users/logout.html', 'next_page':'/%s' % settings.BASE_URL}, name="logout"),


    (r'^alerts/', include('motoproto.alerts.urls')),

    (r'^users/', include('motoproto.users.urls')),    



    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/(.*)', admin.site.root),
)


# We serve static content through Django in DEBUG mode only.
# In production mode, the proper directory aliases (Alias directive in Apache)
# should be defined.
if settings.DEBUG:
    urlpatterns += patterns('',
    #(r'^static/webcanvas/(?P<path>.*)$', 'django.views.static.serve',
    #        {'document_root': settings.WEBCANVAS_ROOT, 'show_indexes': True}),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    #(r'^dojo/(?P<path>.*)$', 'django.views.static.serve',
    #        {'document_root': settings.DOJO_ROOT, 'show_indexes': True}),
)
