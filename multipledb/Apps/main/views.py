#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from models import *
from forms import *
from django.db import connection
from django.db import connections

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from multipledb.settings import PRECIOS_EMPRESA_EXTRA
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def ingresar(request):
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/')
                else:
                    return render_to_response('noactivo.html', context_instance=RequestContext(request))
            else:
                return render_to_response('login.html',{'form':formulario, 'message':'Nombre de usaurio o password no validos',}, context_instance=RequestContext(request))
    else:
        formulario = AuthenticationForm()
    return render_to_response('login.html',{'form':formulario, 'message':'',}, context_instance=RequestContext(request))

def logoutUser(request):
    logout(request)
    return HttpResponseRedirect('/')


def c_get_next_key(BASE_DE_DATOS = "default"):
    """ return next value of sequence """
    c = connections[BASE_DE_DATOS].cursor()
    
    c.execute("SELECT GEN_ID(ID_CATALOGOS, 1 ) FROM RDB$DATABASE;")
    row = c.fetchone()
    return int(row[0])

@login_required(login_url='/login/')
def articulos_view(request, clave='', nombre ='', template_name='articulos/articulos.html'):
    if request.method =='POST':
        filtro_form = filtroarticulos_form(request.POST)
        if filtro_form.is_valid():
            articulo = filtro_form.cleaned_data['articulo']
            nombre = filtro_form.cleaned_data['nombre']
            if articulo != None:
                return HttpResponseRedirect('/articulo/%s/'% articulo.id)
            else:
                articulos_list = Articulos.objects.filter(nombre__icontains=nombre).order_by('nombre')
    else:
        filtro_form = filtroarticulos_form()
        articulos_list = Articulos.objects.all().order_by('nombre')


    paginator = Paginator(articulos_list, 20) # Muestra 10 ventas por pagina
    page = request.GET.get('page')

    #####PARA PAGINACION##############
    try:
        articulos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articulos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articulos = paginator.page(paginator.num_pages)


    c = {
        'articulos': articulos,
        'filtro_form':filtro_form,
    }
    return render_to_response(template_name, c , context_instance=RequestContext(request))

@login_required(login_url='/login/')
def alta_articulo(request, id =None, template_name='articulo.html'):
    precio_empresaextra1_id = PRECIOS_EMPRESA_EXTRA['default']
    precio_empresaextra2_id = PRECIOS_EMPRESA_EXTRA['OTRA']
    
    if id:
        articulo = get_object_or_404(Articulos, pk=id)
        
        precio_articulo = precios_articulos.objects.filter(articulo=articulo)
        if precio_articulo.count() > 0:
            precio_articulo = precio_articulo[0]
        else:
            precio_articulo = precios_articulos()
                
        impuesto_articulo = ImpuestosArticulo.objects.filter(articulo=articulo)
        if impuesto_articulo.count() > 0:
            impuesto_articulo = impuesto_articulo[0]
        else:
            impuesto_articulo = ImpuestosArticulo()

        nivel_articulo = NivelesArticulos.objects.filter(articulo=articulo)
        if nivel_articulo.count() > 0:
            nivel_articulo = nivel_articulo[0]
        else:
            nivel_articulo = NivelesArticulos()

        clave_articulo = ClavesArticulos.objects.filter(articulo=articulo)
        if clave_articulo.count() > 0:
            clave_articulo = clave_articulo[0]
        else:
            clave_articulo = ClavesArticulos()
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
            
            precios2 = precio_articulo_formulario.save(commit = False)
            if precios2.id == None:
                precios2.id = -1
                precios2.articulo = articulo2
                precios2.precio_empresa = precios_empresa.objects.get(pk=precio_empresaextra1_id)
                precios2.precio = 0
                precios2.moneda = precios1.moneda

            impuesto3 = impuesto_articulo_formulario.save(commit = False)
            if impuesto3.id == None:
                impuesto3.id = -1
                impuesto3.articulo = articulo2
            
            claves4 = clave_articulo_formulario.save(commit = False)
            if claves4.id == None:
                claves4.id = -1
                claves4.articulo = articulo2
            
            niveles4 = nivel_articulo_formulario.save(commit = False)
            if niveles4.id == None:
                niveles4.id = -1
                niveles4.articulo = articulo2
           
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
            precios1.save()
            if precios2.id == None:
                precios2.save()
            impuesto3.save()
            claves4.save()
            niveles4.save()

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