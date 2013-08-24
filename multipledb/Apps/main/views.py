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
from multipledb.settings import PRECIOS_EMPRESA_EXTRA, DATABASES
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
    msg =''
    if request.method =='POST':
        filtro_form = filtroarticulos_form(request.POST)
        if filtro_form.is_valid():
            articulo = filtro_form.cleaned_data['articulo']
            nombre = filtro_form.cleaned_data['nombre']
            clave = filtro_form.cleaned_data['clave']

            if articulo != None:
                return HttpResponseRedirect('/articulo/%s/'% articulo.id)
            elif clave != '':
                clave_articulo = ClavesArticulos.objects.filter(clave=clave)
                if clave_articulo.count() > 0:
                    return HttpResponseRedirect('/articulo/%s/'% clave_articulo[0].articulo.id)
                else:
                    articulos_list = Articulos.objects.filter(nombre__icontains=nombre).order_by('nombre')
                    msg='No se encontro ningun articulo con esta clave'
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
        'msg':msg,
    }
    return render_to_response(template_name, c , context_instance=RequestContext(request))

@login_required(login_url='/login/')
def ArticuloManageView(request, id =None, template_name='articulo.html'):
    #Si es un articulo que voy a modificar obtengo sus datos:
    #   articulo (datos generales)
    #   precios_articulos, impuestos_articulo, niveles_articulo, claves_articulo (solo tomamos el primer elemento si es que lo tiene)              
    msg=''
    if id:
        articulo = get_object_or_404(Articulos, pk=id)

        precios_articulo = precios_articulos.objects.filter(articulo=articulo)
        if precios_articulo.count() > 0:
            precio_articulo = precios_articulo[0]
        else:
            precio_articulo = precios_articulos()
                
        impuestos_articulo = ImpuestosArticulo.objects.filter(articulo=articulo)
        if impuestos_articulo.count() > 0:
            impuesto_articulo = impuestos_articulo[0]
        else:
            impuesto_articulo = ImpuestosArticulo()

        niveles_articulo = NivelesArticulos.objects.filter(articulo=articulo)
        if niveles_articulo.count() > 0:
            nivel_articulo = niveles_articulo[0]
        else:
            nivel_articulo = NivelesArticulos()

        claves_articulo = ClavesArticulos.objects.filter(articulo=articulo)
        if claves_articulo.count() > 0:
            clave_articulo = claves_articulo[0]
        else:
            clave_articulo = ClavesArticulos()
    #Si es un articulo nuevo creamos instacia de todos los elementos de un articulo
    else:
        articulo =  Articulos()
        precio_articulo = precios_articulos()
        impuesto_articulo = ImpuestosArticulo()
        nivel_articulo = NivelesArticulos()
        clave_articulo = ClavesArticulos()
 
    #Si estamos mandando un formulario a la vista
    if request.method =='POST':
        articulo_form = articulos_form(request.POST, instance=articulo)
        
        precio_articulo_form = precios_articulos_form(request.POST, instance=precio_articulo)
        impuesto_articulo_form = impuestos_articulos_form(request.POST, instance= impuesto_articulo)
        nivel_articulo_form = niveles_articulos_form(request.POST, instance=nivel_articulo)
        clave_articulo_form = claves_articulos_form(request.POST, instance = clave_articulo)
        
        #Si los datos de los formularios son correctos
        if articulo_form.is_valid() and precio_articulo_form.is_valid() and impuesto_articulo_form.is_valid() and nivel_articulo_form.is_valid() and clave_articulo_form.is_valid():

            articulo = articulo_form.save(commit=False)
            
            #Para sacar nombre y clave anteriores
            nombre_old = None
            clave_old = None
            if articulo.id != None:
                nombre_old = Articulos.objects.get(pk=articulo.id).nombre
                
                try:
                    clave_old = ClavesArticulos.objects.filter(articulo=articulo)[0].clave
                except IndexError:
                    clave_old = None
            
            #Si se modifica la clave y el articulo al mismo tiempo que no permita guardar                
            if clave_articulo_form.cleaned_data['clave'] != clave_old and articulo_form.cleaned_data['nombre'] !=  nombre_old and articulo.id != None:
                msg = 'No es posible modificar el nombre y la clave de un articulo al mismo tiempo. para guardar modifica uno a la vez'
            else:
                if articulo.id == None:
                    articulo.id = c_get_next_key()
                articulo.save()    



                precio_articulo_1 = precio_articulo_form.save(commit=False)
                if precio_articulo_1.id == None:
                    precio_articulo_1.id = -1
                    precio_articulo_1.articulo = articulo
                
                precio_articulo_1.save()
                
                #Para agregar un segundo precio_articulo en ceros solo al crear uno nuevo          
                precio_articulo_2 = precio_articulo_form.save(commit=False)
                if precio_articulo_2.id == -1:
                    precio_articulo_2.articulo = articulo
                    precio_articulo_2.precio_empresa = precios_empresa.objects.get(pk=PRECIOS_EMPRESA_EXTRA['default'])
                    precio_articulo_2.precio = 0
                    precio_articulo_2.moneda = precio_articulo_1.moneda
                    precio_articulo_2.save()    

                impuesto_articulo = impuesto_articulo_form.save(commit=False)
                if impuesto_articulo.id == None:
                    impuesto_articulo.id = -1
                    impuesto_articulo.articulo = articulo
                
                clave_articulo = clave_articulo_form.save(commit=False)
                if clave_articulo.id == None:
                    clave_articulo.id = -1
                    clave_articulo.articulo = articulo
                
                nivel_articulo = nivel_articulo_form.save(commit=False)
                if nivel_articulo.id == None:
                    nivel_articulo.id = -1
                    nivel_articulo.articulo = articulo
               
                #Sincronizar articulos de base de datos default con las otras bases de datos
                app_databases = DATABASES.keys()
                #para quitar la base de datos default de las bases de datos a sincronizar
                for i in range(0,len(app_databases)-1):
                    if app_databases[i] == 'default':
                        del app_databases[i]

                #########################################################
                #Guarda datos del articulo en la base de datos 'default'#
                #########################################################
                
                impuesto_articulo.save()
                nivel_articulo.save()
                clave_articulo.save()
                for database_x in app_databases:
                    linea_articulo_x = LineaArticulos.objects.using(database_x).get(nombre=articulo.linea.nombre)
                    #Si ya existe un articulo en esta base de datos lo modifica
                    try:
                        articulo_x = ClavesArticulos.objects.using(database_x).filter(clave=clave_articulo.clave)[0].articulo
                    #Si el articulo no existe se crea uno nuevo
                    except IndexError:
                        try:
                            articulo_x = Articulos.objects.using(database_x).get(nombre=articulo.nombre)
                        except ObjectDoesNotExist:
                            articulo_x = Articulos.objects.using(database_x).create(
                                id = c_get_next_key(database_x), 
                                nombre = articulo.nombre,
                                linea =  linea_articulo_x,
                                unidvta = articulo.unidvta,
                                unidcopra = articulo.unidcopra,)    
                        else:
                            articulo_x.nombre = articulo.nombre
                            articulo_x.linea =  linea_articulo_x
                            articulo_x.unidvta = articulo.unidvta
                            articulo_x.unidcopra = articulo.unidcopra
                            articulo_x.save(using=database_x)    
                    #Si el articulo si existe modifico sus datos con los nuevos datos
                    else:
                        articulo_x.nombre = articulo.nombre
                        articulo_x.linea =  linea_articulo_x
                        articulo_x.unidvta = articulo.unidvta
                        articulo_x.unidcopra = articulo.unidcopra
                        articulo_x.save(using=database_x)

                    #########################################################
                    #  Guarda datos del articulo en la otra base de datos   #
                    #########################################################

                    #Precios
                    moneda_x = Moneda.objects.using(database_x).get(nombre=precio_articulo_form.cleaned_data['moneda'].nombre)
                    
                    precio_empresa_x = precios_empresa.objects.using(database_x).get(nombre=precio_articulo_form.cleaned_data['precio_empresa'].nombre)
                
                    precios_articulo_x = precios_articulos.objects.using(database_x).filter(articulo=articulo_x)
                    #Si precios_articulo_x tiene al menos un precio
                    if precios_articulo_x.count() > 0:
                        precio_articulo_x = precios_articulo_x[0]
                        precio_articulo_x.moneda = moneda_x
                        precio_articulo_x.precio_empresa = precio_empresa_x
                        precio_articulo_x.precio = precio_articulo_form.cleaned_data['precio']
                        precio_articulo_x.save(using=database_x)
                    else:
                        precios_articulos.objects.using(database_x).create(id=c_get_next_key(database_x), articulo=articulo_x, moneda=moneda_x, precio_empresa=precio_empresa_x, precio=precio_articulo_form.cleaned_data['precio'])
                        precios_articulos.objects.using(database_x).create(id=c_get_next_key(database_x), articulo=articulo_x, moneda=moneda_x, precio_empresa=precios_empresa.objects.using(database_x).get(pk=PRECIOS_EMPRESA_EXTRA[database_x]) , precio=0)
                
                    #Impuestos
                    impuesto_x = Impuesto.objects.using(database_x).get(nombre = impuesto_articulo.impuesto.nombre)
                    impuestos_articulo_x = ImpuestosArticulo.objects.using(database_x).filter(articulo = articulo_x)

                    if impuestos_articulo_x.count() > 0:
                        impuesto_articulo_x = impuestos_articulo_x[0]
                        impuesto_articulo_x.impuesto = impuesto_x
                        impuesto_articulo_x.save(using=database_x)
                    else:
                        ImpuestosArticulo.objects.using(database_x).create(id=-1, articulo=articulo_x, impuesto=impuesto_x)
                
                    #clave
                    rol_x = RolesClavesArticulos.objects.using(database_x).get(nombre=clave_articulo.rol.nombre)
                    claves_articulo_x = ClavesArticulos.objects.using(database_x).filter(articulo=articulo_x)

                    if claves_articulo_x.count() > 0:
                        clave_articulo_x = claves_articulo_x[0]
                        clave_articulo_x.rol = rol_x
                        clave_articulo_x.clave = clave_articulo.clave
                        clave_articulo_x.save(using=database_x)
                    else:
                        ClavesArticulos.objects.using(database_x).create(id=-1, articulo=articulo_x, rol=rol_x, clave=clave_articulo.clave)
                
                    #Puntos de reorden
                    almacen_x = Almacenes.objects.using(database_x).get(nombre=nivel_articulo.almacen.nombre)
                    niveles_articulo_x = NivelesArticulos.objects.using(database_x).filter(articulo=articulo_x)
                    if niveles_articulo_x.count() <= 0:
                        NivelesArticulos.objects.using(database_x).create(id=-1, articulo=articulo_x, almacen=almacen_x, 
                            localizacion=nivel_articulo.localizacion, inventario_maximo=nivel_articulo.inventario_maximo, inventario_minimo=nivel_articulo.inventario_minimo,
                            punto_reorden=nivel_articulo.punto_reorden)
                    
                return HttpResponseRedirect('/articulos/')
    #Si estamos cargando la vista por primera ves
    else:
        articulo_form = articulos_form(instance= articulo)

        precio_articulo_form = precios_articulos_form(instance=precio_articulo)
        impuesto_articulo_form = impuestos_articulos_form(instance=impuesto_articulo)
        nivel_articulo_form = niveles_articulos_form(instance=nivel_articulo)
        clave_articulo_form = claves_articulos_form(instance=clave_articulo)
      

    c = {
        'articulo_form': articulo_form, 
        'precio_articulo_form': precio_articulo_form, 
        'impuesto_articulo_form': impuesto_articulo_form,
        'nivel_articulo_form': nivel_articulo_form,
        'clave_articulo_form': clave_articulo_form,
        'msg':msg,
    } 
    return render_to_response(template_name, c, context_instance=RequestContext(request))