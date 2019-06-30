from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy 
from django.utils.translation import gettext as _
from fuente.utils import Detail, Menu
from fuente.var import *
from .models import *
from empresa.models import Empresa

"""
Esto hace que todas las views de todas las aplicaciones, hereden estas 
variables en su contexto para que todas las plantillas dispongan de esto
sin tener que desclararlas en las views.

Es necesario agregar 'base.context_processors.context' en el setting.py en la
parte de TEMPLATES -- OPTIONS -- context_procesors
"""


CONTEXT = {}
CONTEXT.update(VAR)

CONTEXT["empresa"] = Empresa # Solo habrá una empresa registrada.
CONTEXT["title"] = APP_NAME
CONTEXT["img"] = IMG_DEFAULT

# Menus.
r = reverse_lazy
m = (
    ("index", (
        Menu("index", "Página principal", r("index"), IMG_DEFAULT, False, "Ir a la página de inicio"), (

        )
    )),
    ("documentos", (
        Menu("documento-documento-list", "Documentos", r("documento-documento-list"), IMG_DOCUMENTO, False, "Listado de documentos"), (
            Menu("documento-documento-factura-create", "Facturar", r("documento-documento-factura-create"), IMG_DOCUMENTO, True, "Crea una factura"),
            Menu("documento-documento-entrada-create", "Entrada de efectivo", r("documento-documento-entrada-create"), IMG_DOCUMENTO_ENTRADA, False, "Crea un documento de entrada de efectivo"),
            Menu("documento-documento-salida-create", "Salida de efectivo", r("documento-documento-salida-create"), IMG_DOCUMENTO_SALIDA, False, "Crea un documento de salida de efectivo"),
        )
    )),
    ("personas", (
        Menu("persona-persona-list", "Personas", r("persona-persona-list"), IMG_PERSONA, False, "Listado de personas"), (
            #Menu("persona-persona-create", "Nuevo", r("persona-persona-create"), IMG_ADD, False, "Registra una nueva persona"),
        )
    )),
    ("cuentas", (
        Menu("cuenta-cuenta-list", "Cuentas", r("cuenta-cuenta-list"), IMG_CUENTA, False, "Listado de cuentas"), (
        )
    )),
    ("monedas", (
        Menu("moneda-moneda-list", "Monedas", r("moneda-moneda-list"), IMG_MONEDA, False, "Listado de monedas"), (
            Menu("moneda-moneda-tasas-update", "Actualizar tasas", r("moneda-moneda-tasas-update"), IMG_EDIT, False, "Actualizar las tasas de compra y venta en todas las monedas"),
        )
    )),
    ("almacenes", (
        Menu("almacen-almacen-list", "Almacenes", r("almacen-almacen-list"), IMG_ALMACEN, False, "Listado de almacenes"), (

        )
    )),
    ("reportes", (
        Menu("reporte-reporte", "Reportes", r("reporte-reporte"), IMG_REPORTE, False, "Reportes y estadisticas"), (
            Menu("reporte-reporte-dia", "Reporte por día", r("reporte-reporte-dia"), IMG_REPORTE, False, "Reporte por día"),
            Menu("reporte-reporte-mes", "Reporte por mes", r("reporte-reporte-mes"), IMG_REPORTE, False, "Reporte por mes"),
            Menu("reporte-reporte-ano", "Reporte por año", r("reporte-reporte-ano"), IMG_REPORTE, False, "Reporte por año"),
        )
    )),
    ("prestamos", (
        Menu("prestamo-prestamo-list", "Préstamos", r("prestamo-prestamo-list"), IMG_PRESTAMO, False, "Préstamos"), (
            Menu("prestamo-prestamo-create", "Nuevo", r("prestamo-prestamo-create"), IMG_ADD, False, "Nuevo préstamo"),
        )
    )),
)








CONTEXT["menu"] = m
CONTEXT["menu_documentos"] = dict(m)["documentos"][1]
CONTEXT["menu_cuentas"] = dict(m)["cuentas"][1]
CONTEXT["menu_monedas"] = dict(m)["monedas"][1]
CONTEXT["menu_personas"] = dict(m)["personas"][1]
CONTEXT["menu_almacenes"] = dict(m)["almacenes"][1]
CONTEXT["menu_reportes"] = dict(m)["reportes"][1]


def context(request):
    permisos = request.user.get_all_permissions()
    CONTEXT["permisos_del_usuario"] = permisos
    return CONTEXT