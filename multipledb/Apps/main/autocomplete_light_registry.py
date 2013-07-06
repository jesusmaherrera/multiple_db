import autocomplete_light

from multipledb.Apps.main.models import *

autocomplete_light.register(Articulos, search_fields=('nombre',),
    autocomplete_js_attributes={'placeholder': 'Busca un articulo..'})