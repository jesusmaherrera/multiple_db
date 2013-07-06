from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import autocomplete_light
autocomplete_light.autodiscover()

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',

	url(r'', include('multipledb.Apps.main.urls', namespace='main')),
	#LOGIN
    url(r'^login/$','multipledb.Apps.main.views.ingresar'),
    url(r'^logout/$', 'multipledb.Apps.main.views.logoutUser'),
	url(r'autocomplete/', include('autocomplete_light.urls')),
    # Examples:
    # url(r'^$', 'multipledb.views.home', name='home'),
    # url(r'^multipledb/', include('multipledb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()