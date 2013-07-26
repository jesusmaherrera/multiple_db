from django.conf.urls import patterns, url
from django.views import generic


urlpatterns = patterns('',
    
    url(r'^$', 'multipledb.Apps.main.views.articulos_view'),
    url(r'^articulo/(?P<id>\d+)/', 'multipledb.Apps.main.views.ArticuloManageView'),
    url(r'^articulo/', 'multipledb.Apps.main.views.ArticuloManageView'),
    url(r'^articulos/', 'multipledb.Apps.main.views.articulos_view')
)