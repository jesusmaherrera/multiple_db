from django.db import models

class GrupoLineas(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='GRUPO_LINEA_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
   
    
    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'grupos_lineas'

class LineaArticulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='LINEA_ARTICULO_ID')
    nombre              = models.CharField(max_length=50, db_column='NOMBRE')
    cuenta_ventas       = models.CharField(max_length=30, db_column='CUENTA_VENTAS')
    grupo               = models.ForeignKey(GrupoLineas, db_column='GRUPO_LINEA_ID')

 

    def __unicode__(self):
        return u'%s (%s )' %(self.nombre,self.grupo)

    class Meta:
        db_table = u'lineas_articulos'

class Articulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='ARTICULO_ID')
    nombre              = models.CharField(max_length=100, db_column='NOMBRE', unique=True)
    linea               = models.ForeignKey(LineaArticulos, db_column='LINEA_ARTICULO_ID')
    unidvta             = models.CharField('Unidad de Venta',default = 'PIEZA' ,max_length=20,blank=True, null=True, db_column='UNIDAD_VENTA')
    unidcopra           = models.CharField('Unidad de Compra',default = 'PIEZA' ,max_length=20, blank=True, null=True, db_column='UNIDAD_COMPRA')



    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'articulos'

class precios_empresa(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PRECIO_EMPRESA_ID')
    nombre              = models.CharField(default='N', max_length=30, db_column='NOMBRE')
   


    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'PRECIOS_EMPRESA'

class Moneda(models.Model):
    id = models.AutoField(primary_key=True, db_column='MONEDA_ID')
    es_moneda_local = models.CharField(default='N', max_length=1, db_column='ES_MONEDA_LOCAL')
    nombre = models.CharField(max_length=30, db_column='NOMBRE')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        db_table = u'monedas'



class precios_articulos(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='PRECIO_ARTICULO_ID')
    articulo            = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    precio_empresa      = models.ForeignKey(precios_empresa, db_column='PRECIO_EMPRESA_ID')
    precio              = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=6, db_column='PRECIO')
    moneda              = models.ForeignKey(Moneda, db_column='MONEDA_ID')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'PRECIOS_ARTICULOS'


class Almacenes(models.Model):
    ALMACEN_ID  = models.AutoField(primary_key=True)
    nombre      = models.CharField(max_length=50, db_column='NOMBRE')
    
    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'almacenes'


class Impuesto(models.Model):
    id              = models.AutoField(primary_key=True, db_column='IMPUESTO_ID')
    nombre          = models.CharField(max_length=30, db_column='NOMBRE')
    porcentaje      = models.DecimalField(default=0, blank=True, null=True, max_digits=9, decimal_places=6, db_column='PCTJE_IMPUESTO')

    def __unicode__(self):
        return u'%s' % self.nombre
    
    class Meta:
        db_table = u'impuestos'

class ImpuestosArticulo(models.Model):
    id          = models.AutoField(primary_key=True, db_column='IMPUESTO_ART_ID')
    articulo    = models.ForeignKey(Articulos, on_delete= models.SET_NULL, blank=True, null=True, db_column='ARTICULO_ID')
    impuesto    = models.ForeignKey(Impuesto, on_delete= models.SET_NULL, blank=True, null=True, db_column='IMPUESTO_ID')

    class Meta:
        db_table = u'impuestos_articulos'


class RolesClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='ROL_CLAVE_ART_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    es_ppal = models.CharField(default='N', max_length=1, db_column='ES_PPAL')
    
    def __unicode__(self):
        return u'%s' % self.nombre
    class Meta:
        db_table = u'roles_claves_articulos'

class ClavesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='CLAVE_ARTICULO_ID')
    clave = models.CharField(max_length=20, db_column='CLAVE_ARTICULO', unique=True)
    articulo = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    rol = models.ForeignKey(RolesClavesArticulos, db_column='ROL_CLAVE_ART_ID')

    def __unicode__(self):
        return u'%s' % self.clave

    class Meta:
        db_table = u'claves_articulos'

class Almacenes(models.Model):
    id  = models.AutoField(primary_key=True, db_column = 'ALMANCEN_ID')
    nombre = models.CharField(max_length=50, db_column='NOMBRE')
    
    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = u'almacenes'

class NivelesArticulos(models.Model):
    id = models.AutoField(primary_key=True, db_column='NIVEL_ART_ID')
    localizacion = models.CharField(max_length=15, db_column='LOCALIZACION')
    articulo = models.ForeignKey(Articulos, db_column='ARTICULO_ID')
    inventario_maximo = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='INVENTARIO_MAXIMO')
    punto_reorden = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='PUNTO_REORDEN')
    inventario_minimo = models.DecimalField(default=0, blank=True, null=True, max_digits=18, decimal_places=5, db_column='INVENTARIO_MINIMO')
    almacen = models.ForeignKey(Almacenes, db_column='ALMACEN_ID')

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        db_table = u'niveles_articulos'