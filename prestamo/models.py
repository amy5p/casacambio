# Python
import os
import datetime
from decimal import Decimal
# Django.
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.formats import date_format
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.conf import settings

# Módulos locales
from persona.models import *
from base.models import Configuracion
from fuente import utils
from fuente.var import *






conf = Configuracion()







class Solicitud(models.Model, utils.Texto):
    """
    Crea solicitudes para préstatmos nuevos.
    """
    nombre = models.CharField(_("Nombres y apellidos"), max_length=50, help_text=_("Indíquenos su nombre completo."))
    cedula = models.CharField(_("Cédula"), max_length=20, help_text=_("Indíquenos su número de cédula."))
    telefono = models.CharField(_("Teléfono celular"), max_length=20, help_text=_("Indíquenos su número de teléfono movil."))
    email = models.EmailField(_("Correo electrónico"), max_length=254, blank=True, help_text=_("Indíquenos su correo electrónico."))
    nota = models.TextField(_("Comentario adicional"), blank=True)
    consentimiento = models.BooleanField(_("Estoy de acuerdo"), help_text=_("Declaro haber leído la política de privacidad, y estar de acuerdo con ella."))
    fecha = models.DateTimeField(_("Fecha"), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, editable=False, help_text=_("Usuario que registró la solicitud (opcional)"))

    # Datos extra según pedido de la Empresa.
    direccion = models.CharField(_("Dirección"), max_length=200, help_text=_("Dirección de su residencia o domicilio."))
    estado_civil = models.CharField(_("Estado civil"), max_length=10, choices=ESTADO_CIVIL_CHOICES)
    trabajo_nombre = models.CharField(_("Lugar de trabajo"), max_length=50, blank=True)
    trabajo_direccion = models.CharField(_("Dirección del trabajo"), max_length=200, blank=True)
    trabajo_telefono = models.CharField(_("Teléfono del trabajo"), max_length=20, blank=True)
    trabajo_posicion = models.CharField(_("Puesto que ocupa"), max_length=50, help_text=_("Puesto que ocupa dentro de la empresa."), blank=True)
    trabajo_ingresos = models.DecimalField(_("Ingresos mensuales"), max_digits=11, decimal_places=2, blank=True, default=0, help_text=_("Sus ingresos mensuales dentro de la empresa."))
    trabajo_inicio = models.DateField(_("Fecha en que ingresó"), blank=True, null=True, help_text=_("Fecha en que empezó a formar parte de la empresa como empleado."))
    conyugue_nombre = models.CharField(_("Nombre del conyugue"), max_length=50, blank=True)
    conyugue_trabajo_nombre = models.CharField(_("Lugar de trabajo del conyugue"), max_length=50, blank=True)
    conyugue_trabajo_posicion = models.CharField(_("Puesto que ocupa"), max_length=50, blank=True, help_text=_("Puesto que ocupa el conyugue dentro de la empresa."))
    conyugue_trabajo_direccion = models.CharField(_("Dirección del trabajo dle conyugue"), max_length=200, blank=True)
    conyugue_trabajo_telefono = models.CharField(_("Teléfono del trabajo del conyugue"), max_length=20, blank=True)
    conyugue_trabajo_ingresos = models.DecimalField(_("Ingresos mensuales del conyugue"), max_digits=11, decimal_places=2, blank=True, default=0, help_text=_("Sus ingresos mensuales dentro de la empresa."))
    ref1_nombre = models.CharField(_("Nombre"), max_length=50, blank=True)
    ref1_parentesco = models.CharField(_("Parentesco"), max_length=20, blank=True)
    ref1_telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    ref1_celular = models.CharField(_("Celular"), max_length=20, blank=True)
    ref1_direccion = models.CharField(_("Dirección"), max_length=200, blank=True)
    ref2_nombre = models.CharField(_("Nombre"), max_length=50, blank=True)
    ref2_parentesco = models.CharField(_("Parentesco"), max_length=20, blank=True)
    ref2_telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    ref2_celular = models.CharField(_("Celular"), max_length=20, blank=True)
    ref2_direccion = models.CharField(_("Dirección"), max_length=200, blank=True)
    ref3_nombre = models.CharField(_("Nombre de la empresa"), max_length=50, blank=True)
    ref3_telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    ref4_nombre = models.CharField(_("Nombre de la empresa"), max_length=50, blank=True)
    ref4_telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    cedula_file = models.FileField(_("Cédula"), upload_to="prestamos/solicitud/%Y/%m/", blank=True, help_text=_("Suba la copia de su cédula."))
    carta_de_trabajo_file = models.FileField(_("Carta de trabajo"), upload_to="prestamos/solicitud/%Y/%m/", blank=True, help_text=_("Suba la carta de trabajo escaneada."))

    class Meta:
        verbose_name = _("Solicitud")
        verbose_name_plural = _("Solicitudes")

    def __str__(self):
        return "{} {}: {}".format(_("Solicitud"), self.id, self.GetNombreCorto())

    def get_absolute_url(self):
        return reverse("prestamos_solicitud_enviada")

    def clean(self):
        """Operación de limpieza para validar los datos antes de guardar.
        """
        # Validamos la cédula ingresada.
        try:
            self.cedula = self.ValidarCedula(self.cedula)
        except BaseException as e:
            raise ValidationError({"cedula": _("¡Ups! Al parecer la cédula no es válida. {}".format(e))})
        # Limpiamos el nombre para que sea en mayuscula.
        self.nombre = self.nombre.upper()
        # El consentimiento es obligatorio.
        if self.consentimiento == False:
            raise ValidationError({"consentimiento": _("Indique que está de acuerdo con la política de privacidad.")})

    def GetNombreCorto(self):
        return self.nombre.split(" ")[0]




class Stat(utils.PrestamoBase):
    """
    Clase para el manejo de las estadisticas en el modelo.
    """
    model = None
    queryset = list()
    pagos, reembolsos, desembolsos = list(), list(), list()

    def __init__(self, model=None, queryset=[]):
        self.model = model
        self.queryset = queryset
        self.pagos = list()
        self.reembolsos = list()
        self.desembolsos = list()

        ids = [obj.id for obj in self.queryset]
        self.pagos = Transaccion.objects.filter(hacia_id__in=ids)
        self.reembolsos = Transaccion.objects.filter(desde_id__in=ids).exclude(tipo=DESEMBOLSO)
        self.desembolsos = Transaccion.objects.filter(desde_id__in=ids, tipo=DESEMBOLSO)

    def __str__(self):
        cant = len(self)
        if cant == 1:
            name = self.model._meta.verbose_name
        else:
            name = self.model._meta.verbose_name_plural
        return "{} {}".format(cant, name)

    def __repr__(self):
        return "{}({})".format(self.model._meta.verbose_name_plural, len(self))

    def __len__(self):
        return len(self.queryset)

    def __iter__(self):
        for obj in self.queryset:
            yield obj

    def Count(self):
        """
        Obtiene la cantidad de registros.
        """
        return len(self)

    def GetFirst(self):
        """
        Obtiene el primer registro registrado.
        """
        return self.queryset.order_by("fecha_creacion")[0]

    def GetLast(self):
        """
        Obtiene el último registro registado.
        """
        return self.queryset.order_by("-fecha_creacion")[0]

    def GetSaldo(self):
        """
        Obtiene la sumatoria de los saldos (balances).
        """
        return sum([obj.GetSaldo() for obj in self])

    def SumMonto(self):
        """
        Obtiene la sumatoria de los montos de los préstamos.
        """
        return sum([obj.monto for obj in self])

    def SumPagos(self):
        """
        Obtiene la sumatoria de los pagos realizados.
        """
        return sum([obj.monto for obj in self.pagos])

    def SumReembolsos(self):
        """
        Obtiene la sumatoria de los reembolsos realizados.
        """
        return sum([obj.monto for obj in self.reembolsos])

    def SumDesembolsos(self):
        """
        Obtiene la sumatoria de los desembolsos realizados.
        """
        return sum([obj.monto for obj in self.desembolsos])

    def PromTasa(self):
        """
        Obtiene el promedio de la tasa de interés.
        """
        return sum([obj.tasa for obj in self]) / len(self)

    def CountPagos(self):
        """
        Obtiene la cantidad de pagos realizados.
        """
        return len(self.pagos)

    def CountReembolsos(self):
        """
        Obtiene al cantidad de reembolsos realizados.
        """
        return len(self.reembolsos)

    def CountDesembolsos(self):
        """
        Obtiene la cantidad de desembolsos realizados.
        """
        return len(self.desembolsos)

    def CountPeriodosDiario(self):
        """
        Cantidad de registros con el periodo de pago en 'DIARIO'.
        """
        return len(self.queryset.filter(periodo = DIARIO))

    def CountPeriodosSemanal(self):
        """
        Cantidad de registros con el periodo de pago en 'SEMANAL'.
        """
        return len(self.queryset.filter(periodo = SEMANAL))

    def CountPeriodosQuincenal(self):
        """
        Cantidad de registros con el periodo de pago en 'QUINCENAL'.
        """
        return len(self.queryset.filter(periodo = QUINCENAL))

    def CountPeriodosMensual(self):
        """
        Cantidad de registros con el periodo de pago en 'MENSUAL'.
        """
        return len(self.queryset.filter(periodo = MENSUAL))

    def CountCuotaFija(self):
        """
        Cantidad de registro con el tipo de cuota 'FIJA'.
        """
        return len(self.queryset.filter(cuotas_tipo = CUOTA_FIJA))

    def CountCuotaVariable(self):
        """
        Cantidad de registros con el tipo de cuota 'VARIABLE'.
        """
        return len(self.queryset.filter(cuotas_tipo = CUOTA_VARIABLE))

    def Detail(self):
        """
        Detalle general para mostrar en las plantillas.
        """
        d = utils.Detail()
        d.Add("count", "Cantidad de préstamos", self.Count())
        d.Add("firstdate", "Fecha del primer registro", self.GetFirst().FechaInicio())
        d.Add("lastdate", "Fecha del último registro", self.GetLast().FechaInicio())
        d.Add("montos", "Total de montos", self.SumMonto())
        d.Add("desembolsos", "Total desembolsado", self.SumDesembolsos())
        d.Add("pagos", "Total de pagos", self.SumPagos())
        d.Add("reembolsos", "Total de reembolsos", self.SumReembolsos())

        tasa = self.PromTasa()
        d.Add("tasa", "Tasa de interés promedio", tasa, "{:,.2f}%".format(tasa))

        d.Add("cuotafija", "Préstamos con cuota fija", self.CountCuotaFija())
        d.Add("cuotavariable", "Préstamos con cuota variable", self.CountCuotaVariable())

        d.Add("saldo", "Total adeudado", float(self.GetSaldo()*-1))
        return d

    def GetStatForMonths(self):
        """
        Obtiene estadísticas correspondiente a los últimos 12 meses.
        """
        fin = datetime.date.today()
        inicio = datetime.date(fin.year -1, fin.month, 1)
        fechas = self.GetListadoDeFechas(inicio, MENSUAL, fin=fin)[1:]

        stats = []
        for fecha in fechas:
            trans = Transaccion.objects.filter(fecha_creacion__year=fecha.year, fecha_creacion__month=fecha.month)

            stat = {
                "movimientos": sum([obj.monto for obj in trans]),
                "pagos": sum([obj.monto for obj in trans if obj.tipo == PAGO]),
                "desembolsos": sum([obj.monto for obj in trans if obj.tipo == DESEMBOLSO]),
            }
            stats.append({"fecha": fecha, "stat": stat})
        return stats

    def GetStat(self):
        """
        Obtiene las estadísticas totales.
        """
        stat = {}
        trans = Transaccion.objects.all()
        stat["pagos"] = sum([obj.monto for obj in trans if obj.tipo == PAGO])
        stat["desembolsos"] = sum([obj.monto for obj in trans if obj.tipo == DESEMBOLSO])
        return stat



class Cuenta(models.Model, utils.Texto):
    """
    Gestión de cuentas. Es una cuenta contable, capaz de
    que se realicen transacciones con ella.
    """
    cliente = models.ForeignKey(Persona, verbose_name=_("Cliente"), on_delete=models.PROTECT, blank=True, null=True, default=None, help_text=_("Cliente del préstamo."))
    # Fields automáticas.
    numero = models.CharField(_("Número"), unique=True, max_length=8)
    user = models.ForeignKey(User, verbose_name=_("Usuario"), on_delete=models.SET_DEFAULT, default=None, blank=True, null=True, help_text=_("Usuario que creó esto."))
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    tags = models.TextField(blank=True, editable=False)

    class Meta:
        verbose_name = _("Cuenta")
        verbose_name_plural = _("Cuentas")


    def __str__(self):
        return "{} {}".format(_("Cuenta"), self.numero)

    def get_absolute_url(self):
        return reverse_lazy("prestamo-cuenta-detail", kwargs={"pk": self.pk})

    def clean(self):
        self.tags = self.GetEtiquetas((self.numero, self.user, self.fecha_creacion))
        self.tags += self.cliente.tags

    def Detail(self):
        return utils.Detail(self)

    def GetDetail(self):
        return self.Detail()

    def GetImg(self):
        return IMG_CUENTA

    def GetLasNumber(self):
        """
        Obtiene el último número de cuenta registrado.
        """
        try:
            return Cuenta.objects.all().order_by("-numero")[0].numero
        except IndexError:
            return str(int(PRIMER_NUMERO_DE_CUENTA) - 1)

    def GetNextNumber(self):
        """
        Obtiene el número de cuenta que continua para
        nuevos registros.
        """
        return str(int(self.GetLasNumber()) + 1)


class Transaccion(models.Model, utils.Fecha):
    """
    Una transacción es un modelo de base de datos que registra las
    entrada y salida de dinero desde y hacia una cuenta.
    Cuando una de las cuentas de entrada o salida (desde o hacia) no
    se especifica, la field quedará NULL y en dicho caso se presumirá
    que la transacción se realizó desde o hacia (según sea el caso) una
    cuenta externa o en efectivo.
    """
    desde = models.ForeignKey(Cuenta, verbose_name=_("Desde"), on_delete=models.CASCADE, default=None, null=True, blank=True, help_text=_("Cuenta desde donde procede el dinero."))
    hacia = models.ForeignKey(Cuenta, verbose_name=_("Hacia"), on_delete=models.CASCADE, default=None, null=True, blank=True, related_name="hacia_set2", help_text=_("Cuenta hacia donde va el dinero (opcional). Deje en blanco si es en efectivo."))
    monto = models.DecimalField(_("Monto"), max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], help_text=_("Importe de la transacción."))
    modo = models.CharField(_("Modo"), max_length=20, choices=MODOS_DE_PAGO, default=EFECTIVO, help_text=_("Modo de pago utilizado en esta transacción."))
    tipo = models.CharField(_("Tipo"), max_length=20, choices=TRANSACCION_TIPO, default=TRANSFERENCIA)
    fecha_efectiva = models.DateField(_("Fecha efectiva"), default=timezone.now, help_text=_("Fecha en que se hace efectiva esta transacción."))
    fecha_creacion = models.DateTimeField(_("Fecha de entrada"), auto_now_add=True)
    note = models.TextField(_("Nota"), blank=True)
    author = models.ForeignKey(User, verbose_name=_("Creado por"), on_delete=models.SET_NULL, null=True, blank=True, default=None)
    tags = models.TextField(blank=True, editable=False)

    class Meta:
        verbose_name = _("Transacción")
        verbose_name_plural = _("Transacciones")


    def __str__(self):
        desde, hacia = self.desde, self.hacia
        if not desde:
            desde = "Efectivo"
        if not hacia:
            hacia = "Efectivo"

        return "{} | {} | ${:,.2f}".format(self.tipo, self.fecha_efectiva, self.monto)

    def get_absolute_url(self):
        # return reverse_lazy("contabilidad_transaccion_detail", kwargs={"pk": self.id})
        return reverse_lazy("prestamo-transaccion-detail", kwargs={"pk": self.pk})

    def clean(self):
        """
        Operaciones de limpieza antes de guardar.
        """
        # No se puede transferir entre la misma cuenta.
        if (self.desde == self.hacia):
            if self.desde:
                raise ValidationError({"hacia": _("La cuenta de destino no puede ser la misma que la cuenta de origen.")})
        # Debe especificar al menos una entrada o salida.
        elif (not self.desde) and (not self.hacia):
            raise ValidationError({"desde": _("Debe especificar al menos una cuenta desde o hacia donde se realizará la transacción.")})
        # La fecha efectiva debe ser siempre igual o mayor que hoy.
        if self.CompararFechas(self.fecha_efectiva, timezone.now(), "<"):
        #if self.fecha_efectiva.date() < timezone.now().date():
            raise ValidationError({"fecha_efectiva": _("La fecha efectiva debe ser igual o posterior a hoy.")})
        # Incluimos los tags de busquedas.
        self.tags = ""
        if self.desde:
            self.tags += self.desde.tags
        if self.hacia:
            self.tags += self.hacia.tags
        return super().clean()

    def Detail(self, notnull=True):
        d = utils.Detail()
        d.Add("desde", "Origen", self.desde, html=self.Desde())
        d.Add("hacia", "Destino", self.hacia, html=self.Hacia())
        d.Add("monto", "Monto", self.monto)
        d.Add("modo", "Modo", self.modo, self.Modo())
        d.Add("tipo", "Tipo", self.tipo, self.Tipo())
        d.Add("fecha_efectiva", "Fecha efectiva", self.fecha_efectiva, self.FechaEfectiva())
        d.Add("fecha_creacion", "Fecha de creación", self.fecha_creacion, self.FechaCreacion())
        d.Add("author", "Creado por", self.author, html=self.Author())
        d.Add("note", "Nota", self.note)
        return d

    def GetDetail(self):
        return self.Detail()

    # Fields -------------------------------------------------------

    def Desde(self, html=True):
        if not self.desde:
            return _("Desde el exterior")
        if (html == True) and (self.desde):
            return '<a class="object" href="{href}">{name}</a>'.format(href=self.desde.get_absolute_url(), name=str(self.desde))
        return str(self.desde)

    def Hacia(self, html=True):
        if not self.hacia:
            return _("Hacia el exterior")
        if (html == True) and (self.hacia):
            return '<a class="object" href="{href}">{name}</a>'.format(href=self.hacia.get_absolute_url(), name=str(self.hacia))
        return str(self.hacia)

    def Monto(self):
        return self.monto

    def Modo(self):
        return dict(MODOS_DE_PAGO)[self.modo]

    def Tipo(self):
        return dict(TRANSACCION_TIPO)[self.tipo]

    def FechaEfectiva(self):
        return date_format(self.fecha_efectiva, settings.DATE_FORMAT)

    def FechaCreacion(self):
        return date_format(self.fecha_creacion, settings.DATE_FORMAT)

    def Note(self):
        return self.note

    def Author(self, html=True):
        if (html == True) and (self.desde):
            return '<a class="object" href="{href}">{name}</a>'.format(href="", name=str(self.author))
        return str(self.author)

    # End fields ---------------------------------------------------

    def GetImg(self):
        return IMG_TRANSACCION


class Prestamo(models.Model, utils.PrestamoBase, utils.Texto):
    """
    Gestión de préstamos. Aqui se almacenan los préstamos de
    los diferentes clientes.
    """
    almacen = models.ForeignKey("almacen.Almacen", verbose_name=_("Almacén"), on_delete=models.PROTECT)
    cuenta = models.ForeignKey(Cuenta, verbose_name=_("Cuenta"), blank=True, null=True, default=None, on_delete=models.CASCADE)
    cliente = models.ForeignKey("persona.Persona", verbose_name=_("Cliente"), on_delete=models.PROTECT)
    monto = models.DecimalField(_("Monto"), max_digits=12, decimal_places=2, validators=[MinValueValidator(0, _("El monto debe ser mayor o igual a 0.")), MaxValueValidator(9999999999.99)], help_text=_("Monto del préstamo."))
    tasa = models.DecimalField(_("Tasa de interés"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cuotas = models.IntegerField(_("Cantidad de cuotas"), validators=[MinValueValidator(1, _("La cantidad de cuotas debe ser mayor que 0."))])
    periodo = models.CharField(_("Periodo de pagos"), max_length=10, choices=PERIODO_CHOICES)
    cuotas_tipo = models.CharField(_("Tipo de cuotas"), max_length=10, choices=CUOTA_TIPOS)
    mora = models.DecimalField(_("Interés por mora"), max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text=_("Este es el porcentaje del valor de la cuota que se le cargará en caso de atrasos."))
    note = models.TextField(_("Nota"), blank=True)
    fecha_inicio = models.DateField(_("Fecha de inicio"), default=timezone.now)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    isactive = models.BooleanField(_("¿Está activo?"), default=True, help_text=_("Indica si el préstamos estará o no disponible, si no está activo entonces no se tomará en cuenta para los cálculos."))
    author = models.ForeignKey(User, verbose_name=_("Creado por"), on_delete=models.SET_NULL, blank=True, null=True, default=None)
    tags = models.TextField(blank=True, editable=False)

    class Meta:
        verbose_name = _("Préstamo")
        verbose_name_plural = _("Préstamos")


    def __str__(self):
        try:
            return "{} {}".format(_("Préstamo"), self.cuenta.numero)
        except BaseException:
            return "{} {} {}".format("Préstamo", self.cuenta, self.cliente)

    def html(self):
        return '<a class="object" href="{href}">{name}</a>'.format(href=self.cliente.get_absolute_url(), name=str(self))

    def get_absolute_url(self):
        return reverse_lazy("prestamo-prestamo-detail", kwargs={"pk": self.pk})

    def clean(self):
        self.tags = self.GetEtiquetas((self.almacen, self.cuenta, self.monto, self.tasa))
        self.tags += self.cliente.tags

    def save(self, *args, **kwargs):
        """
        Método llamado cuando se crea o modifica.
        """
        # Creamos la cuenta. La cuenta debe crearse automáticamente, ya que
        # es tratada como una cuenta interna para poder llevar a cabo las
        # operaciones de transacciones. El usuario no tiene que saber esto.
        if not self.id:
            cuenta = Cuenta()
            cuenta.numero = cuenta.GetNextNumber()
            cuenta.save()
            self.cuenta = cuenta
        self.tags = self.Normalize("{} {}".format(self.cliente.tags, self.cuenta.numero))
        self.cuenta.tags = self.tags
        self.cuenta.cliente = self.cliente
        return super().save(*args, **kwargs)

    def GetImg(self):
        return IMG_PRESTAMO

    def GetDetail(self, notnull=True):
        d = utils.Detail(self)
        d.Add("saldo", "Saldo", self.GetSaldo())
        return d

    def Detail(self, notnull=True):
        return self.GetDetail(notnull)

    # Fields. ---------------------------------------

    def Cliente(self, html=True):
        if html == True:
            return '<a class="object" href="{href}">{name}</a>'.format(href=self.cliente.get_absolute_url(), name=str(self.cliente))
        return str(self.cliente)

    def Cuotas(self):
        return self.cuotas

    def CuotasTipo(self):
        return dict(CUOTA_TIPOS)[self.cuotas_tipo]

    def Monto(self):
        return "${:,.2f}".format(self.monto)

    def Periodo(self):
        return dict(PERIODO_CHOICES)[self.periodo]

    def Tasa(self):
        return "{:,.2f}%".format(self.tasa)

    def FechaInicio(self):
        return date_format(self.GetFechaInicio(), settings.DATE_FORMAT)

    def FechaCreacion(self):
        return date_format(self.fecha_creacion, settings.DATETIME_FORMAT)

    def Author(self, html=False):
        if html == True:
            return '<a class="object" href="{href}">{name}</a>'.format(href=self.author.get_absolute_url(), name=str(self.author))
        return str(self.author)

    # End Fields --------------------------

    def ExportAmortizacion(self):
        """
        Exporta en un archivo CSV la tabla de amortización.
        """
        return "no disponible aun Prestamo.ExportAmortizacion"

        out = ["{},{},{},{},{},{}\n".format(_("Cuota"), _("Fecha"), _("Valor"), _("Interés"), _("Capital"), _("Capital restante"))]
        data = self.GetAmortizacion()
        for dic in data:
            cuota, fecha, valor, interes, capital, capital_restante = dic["cuota"], dic["fecha"], dic["valor"], dic["interes"], dic["capital"], dic["capital_restante"]
            l = [cuota, fecha, valor, interes, capital, capital_restante]
            l = [str(value) for value in l]
            line = ",".join(l) + "\n"
            out.append(line)
        csv = str("").join(out)
        file = open(FILE_EXPORT, "w")
        file.write(csv)
        file.close()
        return FILE_EXPORT_URL

    def ExportComportamiento(self):
        """
        Exporta en un archivo CSV la tabla del comportamiento de pagos.
        """
        return "no disponible aun Prestamo.ExportComportamiento"

        out = ["{},{},{},{},{},{},{},{},{}\n".format(_("Cuota"), _("Fecha"), _("Interés"), _("Capital"), _("Monto a pagar"), _("Monto por pagar"), _("Monto pagado"), _("Mora"), _("Saldo anterior"))]
        comp = self.GetComportamiento()
        if (not comp):
            return ""
        data = comp["comportamiento"]
        for dic in data:
            l = [dic["cuota"], dic["corte"], dic["interes"], dic["capital"], dic["apagar"], dic["porpagar"], dic["pagado"], dic["mora"], dic["saldo_anterior"]]
            l = [str(value) for value in l]
            line = ",".join(l) + "\n"
            out.append(line)
        csv = str("").join(out)
        file = open(FILE_EXPORT, "w")
        file.write(csv)
        file.close()
        return FILE_EXPORT_URL


    def GetNumero(self):
        """
        Obtiene el número de la cuenta de este préstamo.
        Nota: El número del préstamo será el número de su cuenta.
        """
        if self.cuenta:
            return self.cuenta.numero
        return ""

    def GetStat(self):
        """
        Obtiene las estadisticas.
        """
        return Stat(Prestamo, Prestamo.objects.all())

    def GetAmortizacion(self):
        """
        Obtiene la tabla de amortización de este préstamo.
        """
        inicio = self.GetFechaInicio()
        if (self.cuotas_tipo == CUOTA_FIJA):
            return self.GetAmortizacionCuotaFija(self.monto, self.tasa, self.cuotas, self.periodo, inicio)
        elif (self.cuotas_tipo == CUOTA_VARIABLE):
            return self.GetAmortizacionCuotaVariable(self.monto, self.tasa, self.cuotas, self.periodo, inicio)

    def GetComportamiento(self):
        """
        Obtiene el comportamiento de pagos de este préstamo.
        """
        if not self.IsDesembolsado():
            return None
        pagos = self.GetPagosYReembolsos()
        pagos = [(pago.fecha_efectiva, pago.monto) for pago in pagos]
        inicio = self.GetFechaInicio()
        return self.GetComportamientoDePagosCuotaFija(self.monto, self.tasa, self.cuotas, self.mora, self.periodo, inicio, pagos=pagos)

    def GetSaldo(self):
        """
        Obtiene el balance (saldo) del préstamo.
        """
        # Se tiene por entendido que no se pueden realizar pagos ni reembolsos
        # antes de hacer el desembolso del préstamo (el Sistema lo prohibe excplicitamente).
        prox = self.GetSiguientePago()
        if not prox:
            return Decimal(0)
        return prox["capital_restante"] + prox["interes"]

    def GetSiguientePago(self):
        """
        Obtiene la información de la próxima cuota a cargarse.
        """
        if not self.GetDesembolso():
            return None
        pagos = self.GetPagosYReembolsos()
        pagos = [(pago.fecha_efectiva, pago.monto) for pago in pagos]
        return self.GetProximoPago(self.monto, self.tasa, self.cuotas, self.mora, self.periodo, self.GetFechaInicio(), pagos=pagos)

    def GetFechaInicio(self):
        """
        Obtiene la fecha de inicio de las operaciones de este préstamo.
        La fecha de inicio es la fecha en que se desembolsó el préstamo.
        """
        try:
            return self.GetDesembolso().fecha_efectiva
        except (AttributeError):
            return self.fecha_inicio

    def GetDesembolsarUrl(self):
        """
        Obtiene la url para el desembolso de este préstamo.
        --> str
        """
        return reverse_lazy("prestamo-prestamo-desembolsar", kwargs={"pk": self.id})

    def GetPagarUrl(self):
        """
        Obtiene la url para el pago de la cuota.
        ---> str
        """
        return reverse_lazy("prestamo-prestamo-pagar", kwargs={"pk": self.id})

    def GetDesembolso(self):
        """
        Obtiene la transacción correspondiente al desembolso
        de este préstamo.
        """
        try:
            return Transaccion.objects.get(desde=self.cuenta, tipo=DESEMBOLSO)
        except (ObjectDoesNotExist):
            return None

    def GetPagos(self):
        """
        Obtiene un QuerySet con los pagos (transacciones entrantes)
        realizados a la cuenta de este préstamo.
        --> QuerySet
        """
        return Transaccion.objects.filter(hacia=self.cuenta).exclude(tipo=DESEMBOLSO)

    def GetPagosSum(self):
        """
        Obtiene la sumatoria de los pagos realizados a este préstamo.
        """
        return sum([obj.monto for obj in self.GetPagos()])

    def GetReembolsos(self):
        """
        Obtiene un QuerySet con los reembolsos (transacciones salientes)
        realizados a la cuenta de este préstamos.
        --> QuerySet
        """
        return Transaccion.objects.filter(desde=self.cuenta).exclude(tipo=DESEMBOLSO)

    def GetReembolsosSum(self):
        """
        Obtiene la sumatoria de los reembolsos realizados a este préstamo.
        """
        return sum([obj.monto for obj in self.GetReembolsos()])

    def GetPagosYReembolsos(self):
        """
        Obtiene todas las transacciones realizadas a la cuenta
        de este préstamo (entrantes y salientes), excluyendo el
        desembolso.
        --> QuerySet
        """
        return Transaccion.objects.filter(
            models.Q(desde=self.cuenta) | models.Q(hacia=self.cuenta)).exclude(tipo=DESEMBOLSO)

    def GetTransacciones(self):
        """
        Obtiene todas las transacciones que se han
        realizado a este préstamo, en un diccionario con
        tres claves:
            desembolso: contiene el desembolso.
            entrada: contiene un QuerySet con los pagos realizados.
            salida: contiene un QuerySet con los reembolsos realizados.
        --> dict
        """
        out = dict()
        out["desembolso"] = Transaccion.objects.get(desde=self.cuenta, tipo=DESEMBOLSO) # El desembolso es único para cada préstamo.
        out["entrada"] = Transaccion.objects.filter(hacia=self.cuenta).exclude(tipo=DESEMBOLSO)
        out["salida"] = Transaccion.objects.filter(desde=self.cuenta).exclude(tipo=DESEMBOLSO)
        return out

    def IsDesembolsado(self):
        """
        Verifica si el préstamo ha sido desembolsado.
        --> bool
        """
        if self.GetDesembolso():
            return True
        return False
