#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
from forms import *
from django.db import connection
from django.db import connections
def c_get_next_key(BASE_DE_DATOS = "default"):
    """ return next value of sequence """
    c = connections[BASE_DE_DATOS].cursor()
    
    c.execute("SELECT GEN_ID(ID_CATALOGOS, 1 ) FROM RDB$DATABASE;")
    row = c.fetchone()
    return int(row[0])

def articulos_view(request, clave='', nombre ='', template_name='articulos/articulos.html'):
    c = {'articulos': Articulos.objects.all(),}
    return render_to_response(template_name, c , context_instance=RequestContext(request))

def alta_articulo(request, id =None, template_name='articulo.html'):
    precio_empresaextra1_id = 210
    precio_empresaextra2_id = 210
    
    if id:
        articulo = get_object_or_404(Articulos, pk=id)
        precio_articulo = precios_articulos.objects.filter(articulo=articulo)[0]
        impuesto_articulo = ImpuestosArticulo.objects.filter(articulo=articulo)[0]
        nivel_articulo = NivelesArticulos.objects.filter(articulo=articulo)[0]
        clave_articulo = ClavesArticulos.objects.filter(articulo=articulo)[0]
    else:
        articulo =  Articulos()
        precio_articulo = precios_articulos()
        impuesto_articulo = ImpuestosArticulo()
        nivel_articulo = NivelesArticulos()
        clave_articulo = ClavesArticulos()

    if request.method =='POST':
        articulo_formulario = articulos_form(request.POST, instance=  articulo)
        
        impuesto_articulo_formulario = impuestos_articulos_form(request.POST, instance= impuesto_articulo)
        precio_articulo_formulario = precios_articulos_form(request.POST, instance=precio_articulo)
        clave_articulo_formulario = claves_articulos_form(request.POST, instance = clave_articulo)
        nivel_articulo_formulario = niveles_articulos_form(request.POST, instance=nivel_articulo)
        
        if articulo_formulario.is_valid() and precio_articulo_formulario.is_valid() and impuesto_articulo_formulario.is_valid() and clave_articulo_formulario.is_valid() and nivel_articulo_formulario.is_valid():

            articulo2 = articulo_formulario.save(commit = False)
            if articulo2.id == None:
                articulo2.id = c_get_next_key()
            

            precios1 = precio_articulo_formulario.save(commit = False)
            if precios1.id == None:
                precios1.id = -1
                precios1.articulo = articulo2
            precios1.save()
            precios2 = precio_articulo_formulario.save(commit = False)
            if precios2.id == None:
                precios2.id = -1
                precios2.articulo = articulo2
                precios2.precio_empresa = precios_empresa.objects.get(pk=precio_empresaextra1_id)
                precios2.precio = 0
                precios2.moneda = precios1.moneda
                precios2.save()

            impuesto3 = impuesto_articulo_formulario.save(commit = False)
            if impuesto3.id == None:
                impuesto3.id = -1
                impuesto3.articulo = articulo2
            impuesto3.save()

            claves4 = clave_articulo_formulario.save(commit = False)
            if claves4.id == None:
                claves4.id = -1
                claves4.articulo = articulo2
            claves4.save()

            niveles4 = nivel_articulo_formulario.save(commit = False)
            if niveles4.id == None:
                niveles4.id = -1
                niveles4.articulo = articulo2
            niveles4.save()

            #Articulo
            linea = LineaArticulos.objects.using('OTRA').get(nombre = articulo2.linea.nombre)
            try:
                articulo8 =  Articulos.objects.using('OTRA').get(nombre= Articulos.objects.get(pk= articulo2.id).nombre)
                articulo8.nombre = articulo2.nombre
                articulo8.linea =  linea
                articulo8.unidvta = articulo2.unidvta
                articulo8.unidcopra = articulo2.unidcopra
                articulo8.save(using='OTRA')
            except ObjectDoesNotExist:
                articulo8 = Articulos.objects.using('OTRA').create(
                    id = c_get_next_key('OTRA'), 
                    nombre = articulo2.nombre,
                    linea =  linea,
                    unidvta = articulo2.unidvta,
                    unidcopra = articulo2.unidcopra,)
            
            articulo2.save()
            #Precios
            moneda = Moneda.objects.using('OTRA').get(nombre = precio_articulo_formulario.cleaned_data['moneda'].nombre)
            precio = precios_empresa.objects.using('OTRA').get(nombre = precio_articulo_formulario.cleaned_data['precio_empresa'].nombre)
            
            p1 = precios_articulos.objects.using('OTRA').filter(articulo = articulo8)
            if p1.count() > 0:
                p1 = p1[0]
                p1 = precios_articulos.objects.using('OTRA').filter(articulo = articulo8)[0]
                p1.moneda = moneda
                p1.precio_empresa = precio
                p1.precio = precio_articulo_formulario.cleaned_data['precio']
                p1.save(using='OTRA')
            else:
                precios_articulos.objects.using('OTRA').create(id = c_get_next_key('OTRA'), articulo = articulo8, moneda = moneda, precio_empresa = precio, precio = precio_articulo_formulario.cleaned_data['precio'])
                precios_articulos.objects.using('OTRA').create(id = c_get_next_key('OTRA'), articulo = articulo8, moneda = moneda, precio_empresa = precios_empresa.objects.using('OTRA').get(pk=precio_empresaextra2_id) , precio = 0)
            
            
            #Impuestos
            impuesto = Impuesto.objects.using('OTRA').get(nombre = impuesto3.impuesto.nombre)

            impuestoArticulo = ImpuestosArticulo.objects.using('OTRA').filter(articulo = articulo8)
            if impuestoArticulo.count() > 0:
                impuestoArticulo = impuestoArticulo[0]
                impuestoArticulo = ImpuestosArticulo.objects.using('OTRA').filter(articulo = articulo8)[0]  
                impuestoArticulo.impuesto = impuesto
                impuestoArticulo.save(using='OTRA')
            else:
                ImpuestosArticulo.objects.using('OTRA').create(id = -1, articulo = articulo8, impuesto = impuesto)
            
            #clave
            rol = RolesClavesArticulos.objects.using('OTRA').get(nombre = claves4.rol.nombre)
            claveArticulo = ClavesArticulos.objects.using('OTRA').filter(articulo = articulo8)
            if claveArticulo.count() > 0:
                claveArticulo = claveArticulo[0]
                claveArticulo.rol = rol
                claveArticulo.clave = claves4.clave
                claveArticulo.save(using='OTRA')
            else:
                ClavesArticulos.objects.using('OTRA').create(id = -1, articulo = articulo8, rol = rol, clave = claves4.clave)
            
            #Puntos de reorden
            almacen = Almacenes.objects.using('OTRA').get(nombre = niveles4.almacen.nombre)
            
            nivelArticulo = NivelesArticulos.objects.using('OTRA').filter(articulo = articulo8)
            if nivelArticulo.count() > 0:
                nivelArticulo=  nivelArticulo[0]
                nivelArticulo.almacen =almacen
                nivelArticulo.localizacion = niveles4.localizacion
                nivelArticulo.inventario_maximo = niveles4.inventario_maximo
                nivelArticulo.inventario_minimo = niveles4.inventario_minimo
                nivelArticulo.punto_reorden = niveles4.punto_reorden
                nivelArticulo.save(using='OTRA')
            else:
                NivelesArticulos.objects.using('OTRA').create(id = -1, articulo = articulo8, almacen =almacen, 
                    localizacion = niveles4.localizacion, inventario_maximo = niveles4.inventario_maximo, inventario_minimo = niveles4.inventario_minimo,
                    punto_reorden = niveles4.punto_reorden )
            return HttpResponseRedirect('/articulos/')

    else:

        precio_articulo_formulario = precios_articulos_form(instance=precio_articulo)
        articulo_formulario = articulos_form(instance=  articulo)
        impuesto_articulo_formulario = impuestos_articulos_form(instance= impuesto_articulo)
        clave_articulo_formulario = claves_articulos_form(instance = clave_articulo)
        nivel_articulo_formulario = niveles_articulos_form(instance=nivel_articulo)
      

    a = {'formulario_articulo': articulo_formulario, 
    'precio_articulo_formulario': precio_articulo_formulario, 
    'impuesto_articulo_formulario': impuesto_articulo_formulario,
    'clave_articulo_formulario': clave_articulo_formulario,
    'nivel_articulo_formulario': nivel_articulo_formulario,} 
    return render_to_response(template_name, a, context_instance=RequestContext(request))