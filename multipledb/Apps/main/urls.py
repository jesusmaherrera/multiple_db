from django.conf.urls import patterns, url
from django.views import generic


urlpatterns = patterns('',
    
    url(r'^$', 'multipledb.Apps.main.views.articulos_view'),
    url(r'^articulo/(?P<id>\d+)/', 'multipledb.Apps.main.views.alta_articulo'),
    url(r'^articulo/', 'multipledb.Apps.main.views.alta_articulo'),
    url(r'^articulos/', 'multipledb.Apps.main.views.articulos_view')
    

)