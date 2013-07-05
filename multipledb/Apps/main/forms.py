from django import forms
from models import *

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