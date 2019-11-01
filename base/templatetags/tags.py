import types
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from django import template
from django.utils import timezone
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, Permission
register = template.Library()

from fuente.var import IMG_DEFAULT
from empresa.models import Empresa
from django.contrib.auth.models import User
from base.models import Nota
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


@register.filter
def make_list(number):
    return list(range(int(number)))

@register.simple_tag
def fecha_actual(formato=None):
    """Traduce el texto indicado con gettext."""
    if formato:
        return timezone.now().strftime(formato)
    return timezone.now()

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
    except (ValueError, TypeError):
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


@register.filter(name='has_group')
def has_group(user, group_name):
    if user.is_superuser:
        return True
    try:
        group = Group.objects.get(name=group_name)
    except (ObjectDoesNotExist) as e:
        print(e)
        return False
    return True if group in user.groups.all() else False


@register.filter(name='has_permission')
def has_permission(user, permission_name):
    if user.is_superuser:
        return True
    return user.has_perm(permission_name)


@register.filter
def get_permissions(username):
    try:
        user = User.objects.get(username=username)
    except (ObjectDoesNotExist):
        return []
    return user.get_all_permissions()

@register.filter
def seguimiento(request, object1=None):

    if (request.path in ("/favicon.ico",)):
        return
    try:
        obj = Seguimiento()
    except (NameError):
        return
    try:
        obj.user = request.user
    except (BaseException):
        obj.user = None
    try:
        obj.url = request.get_full_path()
    except (BaseException) as e:
        obj.url = str(e)
    try:
        obj.referer = request.META["HTTP_REFERER"]
    except (BaseException) as e:
        obj.referer = str(e)
    try:
        obj.useragent = request.META["HTTP_USER_AGENT"]
    except (BaseException) as e:
        obj.useragent = str(e)
    try:
        obj.ip = request.META["REMOTE_ADDR"]
    except (BaseException) as e:
        obj.ip = str(e)
    try:
        obj.host = request.META["REMOTE_HOST"]
    except (BaseException) as e:
        obj.host = str(e)

    obj.description = str(object1)

    try:
        obj.save()
    except (BaseException) as e:
        print(e)


@register.filter
def urlname(request):
    """Obtiene el nombre de la url"""
    return resolve(request.path_info).url_name


@register.filter
def getnotas(request):
    """Obtiene laz notas especificada, según
    la url donde se haya establecido."""
    return Nota.objects.filter(urlname=urlname(request))


