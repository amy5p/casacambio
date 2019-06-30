import os
from django.utils.translation import gettext_lazy as _
# Locales
from .paises import *




STATIC_URL = "/static/"
STATIC_ROOT = ""
MEDIA_ROOT = ""
MEDIA_URL = "/media/"
BASE_DIR = ""

try:
    from django.conf import settings
except (BaseException) as e:
    print(e)
try:
    STATIC_URL = str(settings.STATIC_URL)
except (BaseException) as e:
    print(e)
try:
    STATIC_ROOT = str(settings.STATIC_ROOT)
except (BaseException) as e:
    print(e)
try:
    MEDIA_ROOT = str(settings.MEDIA_ROOT)
except (BaseException) as e:
    print(e)
try:
    MEDIA_URL = str(settings.MEDIA_URL)
except (BaseException) as e:
    print(e)
try:
    BASE_DIR = str(settings.BASE_DIR)
except (BaseException) as e:
    print(e)




APP_NAME = "QUIMERA"


PRIMER_NUMERO_DE_CUENTA = "10221110"
PRIMER_NUMERO_DE_CLIENTE = "10102020"


FILE_EXPORT = os.path.join(MEDIA_ROOT, "file_export.csv")
FILE_EXPORT_URL = MEDIA_URL + "file_export.csv"



# PERSONAS -----------------------------------------------------------

MASCULINO = "M"
FEMENINO = "F"
NO_DEFINIDO = "ND"
SEXO_CHOICES = (
    (MASCULINO, _("Masculino")),
    (FEMENINO, _("Femenino")),
    (NO_DEFINIDO, _("No definido")),
)


SOLTERO = "SOLTERO"
CASADO = "CASADO"
UNION_LIBRE = "UNION_LIBRE"
OTRO = "OTRO"
ESTADO_CIVIL_CHOICES = (
    (SOLTERO, _("Soltero")),
    (CASADO, _("Casado")),
    (UNION_LIBRE, _("Unión libre")),
    (OTRO, _("Otro")),
)



# IDENTIFICACIÓN -----------------------------------------------------

CEDULA = "CÉDULA"
PASAPORTE = "PASAPORTE"
RNC = "RNC"
OTRO = "OTRO"
IDENTIFICACION_CHOICES = (
    (CEDULA, _("Cédula")),
    (PASAPORTE, _("Pasaporte")),
    (RNC, _("RNC")),
    (OTRO, _("")),
)


# CONTABILIDAD -------------------------------------------------------

DOP = "DOP"
USD = "USD"
EUR = "EUR"
CAD = "CAD"
GSB = "GSB"
MONEDA_CHOICES = (
    (DOP, _("DOP: Peso dominicano")),
    (USD, _("USD: Dólar estadounidense")),
    (EUR, _("EUR: Euro")),
    (CAD, _("CAD: Dólar canadiense")),
    (GSB, _("GSB: Libra esterlina")),
)

EFECTIVO = "EF"
CUENTA_CORRIENTE = "CC"
CUENTA_AHORROS = "CA"
PRESTAMO = "PR"
TARJETA_CREDITO = "TC"
TARJETA_DEBITO = "TD"
CUENTA_CHOICES = (
    (EFECTIVO, _("Efectivo")),
    (CUENTA_CORRIENTE, _("Cuenta corriente")),
    (CUENTA_AHORROS, _("Cuenta de ahorros")),
    (PRESTAMO, _("Préstamo")),
    (TARJETA_CREDITO, _("Tarjeta de crédito")),
    (TARJETA_DEBITO, _("Tarjeta de débito")),
)

CUOTA_FIJA = "FIJA"
CUOTA_VARIABLE = "VARIABLE"
CUOTA_TIPOS = (
    (CUOTA_FIJA, _("Cuota fija")),
    (CUOTA_VARIABLE, _("Cuota variable")),
)

EFECTIVO = "EFECTIVO"
CUENTA = "CUENTA"
TARJETA = "TARJETA"
PAYPAL = "PAYPAL"
BITCOIN = "BITCOIN"
CHEQUE = "CHEQUE"
MODOS_DE_PAGO = (
    (EFECTIVO, _("Efectivo")),
    (CUENTA, _("Cuenta")),
    (TARJETA, _("Tarjeta de crédito")),
    (PAYPAL, _("Paypal")),
    (BITCOIN, _("Bitcoin")),
    (CHEQUE, _("Cheque")),
)

DESEMBOLSO = "DESEMBOLSO"
PAGO = "PAGO"
TRANSFERENCIA = "TRANSFERENCIA"
TRANSACCION_TIPO = (
    (PAGO, _("Pago")),
    (DESEMBOLSO, _("Desembolso")),
    (TRANSFERENCIA, _("Transferencia")),

)

ENTRADA = "ENTRADA"
SALIDA = "SALIDA"
TRANSFERENCIA = "TRANSFERENCIA"
FACTURA = "FACTURA"
COTIZACION = "COTIZACION"
ORDEN = "ORDEN"
ENTRADA_SALIDA_CHOICES = (
    (ENTRADA, _("Entrada")),
    (SALIDA, _("Salida")),
    (TRANSFERENCIA, _("Transferencia")),
    (FACTURA, _("Factura")),
    (COTIZACION, _("Cotización")),
    (ORDEN, _("Orden")),
)

PORCENTAJE = "PORCENTAJE"
FIJO = "FIJO"
VALOR_TIPO = (
    (PORCENTAJE, _("Porcentaje")),
    (FIJO, _("Fijo")),
)


# FECHAS ------------------------------------------------------------

DIARIO = "DIARIO"
SEMANAL = "SEMANAL"
QUINCENAL = "QUINCENAL"
MENSUAL = "MENSUAL"
ANUAL = "ANUAL"
PERIODO_CHOICES = (
    (DIARIO, _("Diario")),
    (SEMANAL, _("Semanal")),
    (QUINCENAL, _("Quincenal")),
    (MENSUAL, _("Mensual")),
    (ANUAL, _("Anual")),
)


# INFORMÁTICA ------------------------------------------------------

TUPLE = "TUPLE"
LIST = "LIST"
DICT = "DICT"
INT = "INT"
FLOAT = "FLOAT"
DECIMAL = "DECIMAL"
STR = "STR"
BOOL = "BOOL"
DATE = "DATE"
DATETIME = "DATETIME"
TIPO_DE_DATOS_CHOICES = (
    (STR, _("Texto")),
    (INT, _("Número entero.")),
    (FLOAT, _("Número de coma flotante.")),
    (DECIMAL, _("Número decimal")),
    (TUPLE, _("Tupla")),
    (LIST, _("Lista")),
    (DICT, _("Diccionario")),
    (BOOL, _("Falso o Verdadero")),
    (DATE, _("Fecha")),
    (DATETIME, _("Fecha y hora")),
)





# IMAGENES.

IMG_ALMACEN = '/static/img/almacen.svg'
IMG_ARTICULO = '/static/img/articulo.svg'
IMG_ADD = '/static/img/base/add.svg'
IMG_BACK = '/static/img/base/back.svg'
IMG_CALC = '/static/img/base/calc.svg'
IMG_CANCEL = '/static/img/base/cancel.svg'
IMG_CLOSE = '/static/img/base/close.svg'
IMG_DEFAULT = '/static/img/base/default.svg'
IMG_DELETE = '/static/img/base/delete.svg'
IMG_EDIT = '/static/img/base/edit.svg'
IMG_EFECTIVO = '/static/img/base/efectivo.svg'
IMG_FLECHA_DERECHA = "/static/img/base/flecha_derecha.svg"
IMG_IDENTIFICATION = '/static/img/base/identification.svg'
IMG_INFO = '/static/img/base/info.svg'
IMG_LIST = '/static/img/base/list.svg'
IMG_LOGO = '/static/img/base/logo.svg'
IMG_MENU = '/static/img/base/menu.svg'
IMG_NEXT = '/static/img/base/next.svg'
IMG_PRINT = '/static/img/base/print.svg'
IMG_QUESTION = '/static/img/base/question.svg'
IMG_SAVE = '/static/img/base/save.svg'
IMG_SEARCH = '/static/img/base/search.svg'
IMG_FACEBOOK = '/static/img/base/social/facebook.svg'
IMG_GPLUS = '/static/img/base/social/gplus.svg'
IMG_INSTAGRAM = '/static/img/base/social/instagram.svg'
IMG_LINKEDIN = '/static/img/base/social/linkedin.svg'
IMG_PINTERES = '/static/img/base/social/pinteres.svg'
IMG_TWITTER = '/static/img/base/social/twitter.svg'
IMG_VK = '/static/img/base/social/vk.svg'
IMG_SORRY = '/static/img/base/sorry.svg'
IMG_STAT = '/static/img/base/stat.svg'
IMG_STOP = '/static/img/base/stop.svg'
IMG_CUENTA = '/static/img/cuenta.svg'
IMG_DOCUMENTO = '/static/img/documento.svg'
IMG_DOCUMENTO_ENTRADA = '/static/img/documento_entrada.svg'
IMG_DOCUMENTO_SALIDA = '/static/img/documento_salida.svg'
IMG_DOCUMENTO_TRANSFERENCIA = '/static/img/documento_transferencia.svg'
IMG_ESTADISTICA = '/static/img/estadistica.svg'
IMG_MONEDA = '/static/img/moneda.svg'
IMG_PERSONA = '/static/img/persona.svg'
IMG_PRESTAMO = '/static/img/prestamo.svg'
IMG_QUESTION = '/static/img/question.svg'
IMG_REPORTE = '/static/img/reporte.svg'
IMG_TRANSACCION = '/static/img/transaccion.svg'
IMG_USUARIO = '/static/img/usuario.svg'








# Todas las variables (esto debe ir siempre al final del archivo, 
# para que tome todas las variables)
VAR = vars().copy()
