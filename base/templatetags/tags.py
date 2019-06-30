import types
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from django import template
register = template.Library()

from fuente.var import IMG_DEFAULT
from empresa.models import Empresa
from fuente import utils

"""
Tags predefinidos que se usarán en las plantillas.

{% load tags %} # Plantilla base.

Ej.: {{ object|verbose_name }}

Util, porque en las plantillas no se puede llamar
una variable que empiece con guión bajo como object._meta.verbose_name
"""


@register.simple_tag
def empresa(fieldname=None, *args, **kwargs):
    """Obtiene el objeto con los datos de la empresa.
    si se indica el fieldname, retorna el valor del campo indicado."""
    try:
        obj = Empresa.objects.all()[0] # Solo existirá una sola empresa.
    except (IndexError):
        obj = Empresa()
        obj.nombre = "Mi Empresa"
        obj.razon_social = "Mi Empresa SRL"
        obj.save()

    if (fieldname):
        attr = getattr(obj, fieldname, None)
        try:
            return attr(*args, **kwargs)# Verificamos si se intenta llamar a una función.
        except (TypeError):
            return attr 
    return obj


@register.simple_tag
def trans(value):
    """Traduce el texto indicado con gettext."""
    return _(value)


@register.filter
def traducir(value):
    """Traduce el texto utilizando gettext."""
    return _(value)


@register.filter
def complete0(value, cant=1):
    """Completa con 0 a la izquieda"""
    t = "{:0>" + str(cant) + "}"
    return t.format(value)

@register.filter
def getimg(obj):
    """Obtiene la imagen asignada al modelo.
    En caso de no existir retorna la imagen por defecto."""
    try:
        if (isinstance(obj, QuerySet)):
            return obj.model.GetImg(None)
        return obj.GetImg()
    except (AttributeError):
        return IMG_DEFAULT


@register.filter
def moneda(number, simbol="$"):
    if (number == ""):
        number = 0
    if isinstance(number, str):
        utils.Texto().Float()
    try:
        return "{} {:,.2f}".format(simbol, float(number))
    except (ValueError):
        return ""

@register.filter 
def intcomma(number, simbol="$"):
    return moneda(number, simbol)

@register.filter
def verbose_name(obj):
    if (isinstance(obj, QuerySet)):
        return obj.model._meta.verbose_name
    if (isinstance(obj, str)):
        return obj
    return obj._meta.verbose_name


@register.filter
def verbose_name_plural(obj):
    if (isinstance(obj, QuerySet)):
        return obj.model._meta.verbose_name_plural
    if (isinstance(obj, str)):
        return obj
    return obj._meta.verbose_name_plural


@register.filter
def sino(value):
    """De un valor booleano True o False, 
    retorna los string 'Si' o 'No'"""
    if (value):
        return _("Si")
    return _("No")

