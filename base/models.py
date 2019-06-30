from decimal import Decimal, DivisionUndefined
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from simple_history.models import HistoricalRecords
#from auditoria.mixins import AuditMixin
from fuente import utils
from fuente.var import *





class Error(models.Model):
    """
    Registro de los errores producidos en el Sistema.
    """
    user = models.ForeignKey(User, verbose_name=_("Usuario"), on_delete=models.CASCADE, null=True, default=None, blank=True)
    title = models.CharField(_("Título"), max_length=256, blank=True)
    description = models.TextField(_("Descripción"), blank=True)
    appname = models.CharField(_("Aplicación"), max_length=50)
    module = models.CharField(_("Módulo"), max_length=50)
    line = models.IntegerField(_("Linea"), default=0)
    error_type = models.CharField(_("Tipo de error"), max_length=50, blank=True)
    error_message = models.TextField(_("Mensaje"), blank=True)
    date = models.DateTimeField(_("Fecha"), auto_now_add=True)

    def __str__(self):
        return self.title



class ConfiguracionGeneral(models.Model):
    """
    Registro de las configuraciones globales del Sistema.
    """


class ConfiguracionFacturacion(models.Model):
    """
    Registro de las configuraciones en el área de facturación.
    """
    #moneda_entrada_predeterminada = models.ForeignKey("moneda.Moneda", on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name=_("Moneda de entrada predeterminada"))
    #moneda_salida_predeterminada = models.ForeignKey("moneda.Moneda", on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name="cf_moneda_salida_predeterminada", verbose_name=_("Moneda de salida predeterminada"))
    tipo_documento_predeterminado = models.ForeignKey("documento.DocumentoTipo", on_delete=models.SET_NULL, null=True, blank=True, default=None, verbose_name=_("Tipo de documento predeterminado"))
    creacion = models.DateTimeField(auto_now_add=True)


class ConfiguracionCSV(models.Model):
    """
    Configuración para la exportación de archivos
    en formato CSV
    """
    caracter_division_celdas = models.CharField(_("Carácter de división de celdas"), max_length=1, default=",")

    def clean(self):
        # Solo puede existir una sola configuración.
        if (len(ConfiguracionCSV.objects.all()) > 0):
            if (not self.id):
                raise ValidationError("Ya existe una configuración registrada.")


        




def _set(modelo):
    try:
        obj = modelo.objects.all()[0]
    except (BaseException):
        obj = modelo()
        obj.save()
    return obj


class __Configuracion():
    
    def __getattr__(self, name):
        return self


class Configuracion():

    def __init__(self):
        try:
            self.general = _set(ConfiguracionGeneral)
        except (BaseException) as e:
            print(e)
        try:
            self.facturacion = _set(ConfiguracionFacturacion)
        except (BaseException) as e:
            print(e)
        try:
            self.csv = _set(ConfiguracionCSV)
        except (BaseException) as e:
            print(e)

    



# Inicialización por primera vez.
def inicializacion():
    from empresa.models import Empresa
    from almacen.models import Almacen
    from persona.models import Persona
    from documento.models import DocumentoTipo
    from moneda.models import Moneda
    from cuenta.models import Cuenta


    try:
        empresa = Empresa.objects.all()[0]
    except (IndexError):
        empresa = Empresa()
        empresa.nombre = _("EMPRESA")
        empresa.razon_social = _("EMPRESA")
        empresa.save()
    except (BaseException):
        pass
        
    try:
        almacen = Almacen.objects.all()[0]
    except (IndexError):
        almacen = Almacen()
        almacen.nombre = _("PRINCIPAL")
        almacen.codigo = "01"
        almacen.empresa = empresa
        almacen.save()
    except (BaseException):
        pass 

    # DOCUMENTOS PREDETERMINADOS PARA INICIAR LAS OPERACIONES.
    try:
        fac = DocumentoTipo()
        fac.codigo = "FAC"
        fac.nombre = _("FACTURA A CONTADO")
        fac.modo = FACTURA
        fac.save()
    except (BaseException):
        pass

    try:
        ent = DocumentoTipo()
        ent.codigo = "ENT"
        ent.nombre = _("ENTRADA DE EFECTIVO")
        ent.modo = ENTRADA
        ent.save()
    except (BaseException):
        pass

    try:
        sal = DocumentoTipo()
        sal.codigo = "SAL"
        sal.nombre = _("SALIDA DE EFECTIVO")
        sal.modo = SALIDA
        sal.save()
    except (BaseException):
        pass

    try:
        moneda1 = Moneda()
        moneda1.simbolo = DOP
        moneda1.nombre = _("PESO")
        moneda1.is_principal = True 
        moneda1.save()
    except (BaseException):
        pass 

    try:
        moneda2 = Moneda()
        moneda2.simbolo = USD
        moneda2.nombre = _("DOLAR")
        moneda2.save()
    except (BaseException):
        pass 

    try:
        moneda3 = Moneda()
        moneda3.simbolo = EUR
        moneda3.nombre = _("EURO")
        moneda3.save()
    except (BaseException):
        pass 


    try:
        cuenta = Cuenta()
        cuenta.almacen = almacen
        cuenta.moneda = moneda1
        cuenta.save()
    except (BaseException):
        pass

    try:
        cuenta = Cuenta()
        cuenta.almacen = almacen
        cuenta.moneda = moneda2
        cuenta.save()
    except (BaseException):
        pass

    try:
        cuenta = Cuenta()
        cuenta.almacen = almacen
        cuenta.moneda = moneda3
        cuenta.save()
    except (BaseException):
        pass

    try:
        persona = Persona()
        persona.nombre = "GENERICO"
        persona.identificacion = "0"
        persona.save()
    except (BaseException):
        pass

    
    

    

inicializacion()
