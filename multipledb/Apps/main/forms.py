from django.core.exceptions import ObjectDoesNotExist

from django import forms
from models import *
import autocomplete_light
from multipledb.settings import DATABASES

def get_databases_values():
    app_databases = DATABASES.keys()
    #para quitar la base de datos default de las bases de datos a sincronizar
    for i in range(0,len(app_databases)-1):
        if app_databases[i] == 'default':
            del app_databases[i]
    return app_databases

class articulos_form(forms.ModelForm):
    class Meta:
        model = Articulos

    def clean_nombre(self):
        cleaned_data = self.cleaned_data
        nombre = cleaned_data.get("nombre")

        articulo_id  = self.instance.pk
        if articulo_id != None:
            old_nombre = Articulos.objects.get(pk=articulo_id).nombre
        else:
            old_nombre = None
        
        try:
            old_clave = ClavesArticulos.objects.filter(articulo__id=articulo_id)[0].clave
        except IndexError:
            old_clave= None
            
        for DATABASE in get_databases_values():
            try:
                articulo_x = ClavesArticulos.objects.using(DATABASE).exclude(clave = old_clave).filter(articulo__nombre = nombre)[0].articulo
            except IndexError:
                articulo_x = None       

            if articulo_x != None:
                raise forms.ValidationError(u'Ya existe un articulo con el nombre [%s] en la empresa [%s]'% (nombre ,DATABASE))   

        return nombre

    def clean_linea(self):
        cleaned_data = self.cleaned_data
        linea = cleaned_data.get("linea")
        for DATABASE in get_databases_values():
            try:
                linea_x = LineaArticulos.objects.using(DATABASE).get(nombre = linea.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una linea con el nombre [%s] en la empresa [%s]'% (linea.nombre ,DATABASE))   

        return linea

class precios_articulos_form(forms.ModelForm):
    class Meta:
        model = precios_articulos
        exclude = ('articulo')
    
    def clean_moneda(self):
        cleaned_data = self.cleaned_data
        moneda = cleaned_data.get("moneda")
        for DATABASE in get_databases_values():
            try:
                moneda_x = Moneda.objects.using(DATABASE).get(nombre = moneda.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una moneda con el nombre [%s] en la empresa [%s]'% (moneda.nombre ,DATABASE))   

        return moneda

    def clean_precio_empresa(self):
        cleaned_data = self.cleaned_data
        precio_empresa_form = cleaned_data.get("precio_empresa")
        for DATABASE in get_databases_values():
            try:
                precio_empresa_x = precios_empresa.objects.using(DATABASE).get(nombre = precio_empresa_form.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una precio_empresa con el nombre [%s] en la empresa [%s]'% (precio_empresa_form.nombre ,DATABASE))   

        return precio_empresa_form

class impuestos_articulos_form(forms.ModelForm):
    class Meta:
        model = ImpuestosArticulo
        exclude = ('articulo')

    def clean_impuesto(self):
        cleaned_data = self.cleaned_data
        impuesto = cleaned_data.get("impuesto")
        for DATABASE in get_databases_values():
            try:
                impuesto_x = Impuesto.objects.using(DATABASE).get(nombre = impuesto.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una impuesto con el nombre [%s] en la empresa [%s]'% (impuesto.nombre ,DATABASE))   

        return impuesto

class claves_articulos_form(forms.ModelForm):
    class Meta:
        model = ClavesArticulos
        exclude = ('articulo')

    def clean_rol(self):
        cleaned_data = self.cleaned_data
        rol = cleaned_data.get("rol")
        for DATABASE in get_databases_values():
            try:
                rol_x = RolesClavesArticulos.objects.using(DATABASE).get(nombre = rol.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una rol con el nombre [%s] en la empresa [%s]'% (rol.nombre ,DATABASE))   

        return rol

    def clean_clave(self):
        cleaned_data = self.cleaned_data
        clave = cleaned_data.get("clave")

        clave_id  = self.instance.pk
        
        if clave_id != None:
            old_clave = ClavesArticulos.objects.get(pk=clave_id).clave
        else:
            old_clave = None
            
        for DATABASE in get_databases_values():
            try:
                clave_x = ClavesArticulos.objects.using(DATABASE).exclude(clave = old_clave).filter(clave = clave)[0].clave
            except IndexError:
                clave_x = None       

            if clave_x != None:
                raise forms.ValidationError(u'La clave [%s] ya esta registrada en la empresa [%s]'% (clave ,DATABASE))   

        return clave
        
class niveles_articulos_form(forms.ModelForm):
    class Meta:
        model = NivelesArticulos
        exclude = ('articulo')

    def clean_almacen(self):
        cleaned_data = self.cleaned_data
        almacen = cleaned_data.get("almacen")
        for DATABASE in get_databases_values():
            try:
                almacen_x = Almacenes.objects.using(DATABASE).get(nombre = almacen.nombre) 
            except ObjectDoesNotExist:
                raise forms.ValidationError(u'No existe una almacen con el nombre [%s] en la empresa [%s]'% (almacen.nombre ,DATABASE))   

        return almacen

class filtroarticulos_form(forms.Form):
    clave   = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-small', 'placeholder':'Clave...'}),required=False)
    nombre  = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class':'input-medium', 'placeholder':'Nombre...'}),required=False)
    articulo = forms.ModelChoiceField(required= False, queryset=Articulos.objects.all(),
        widget=autocomplete_light.ChoiceWidget('ArticulosAutocomplete'))
