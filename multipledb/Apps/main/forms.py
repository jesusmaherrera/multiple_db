from django import forms
from models import *
import autocomplete_light

class articulos_form(forms.ModelForm):
	class Meta:
		model = Articulos

class precios_articulos_form(forms.ModelForm):
	class Meta:
		model = precios_articulos
		exclude = ('articulo')

class impuestos_articulos_form(forms.ModelForm):
	class Meta:
		model = ImpuestosArticulo
		exclude = ('articulo')

class claves_articulos_form(forms.ModelForm):
	class Meta:
		model = ClavesArticulos
		exclude = ('articulo')

class niveles_articulos_form(forms.ModelForm):
	class Meta:
		model = NivelesArticulos
		exclude = ('articulo')

class filtroarticulos_form(forms.Form):
	clave 	= forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
	nombre 	= forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Nombre...'}),required=False)
	articulo = forms.ModelChoiceField(required= False, queryset=Articulos.objects.all(),
		widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))
