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




class DocumentoTipo(models.Model, utils.Texto):
    """
    Representa un tipo de documento.
    """
    codigo = models.CharField(_("Código"), max_length=10, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=50, unique=True)
    modo = models.CharField(_("Modo"), max_length=20, choices=ENTRADA_SALIDA_CHOICES)
    tags = models.CharField(blank=True, max_length=512, editable=False)

    # Audiroría
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documentos"
    
    
    def __str__(self):
        return "{}: {}".format(self.codigo, self.nombre)

    def clean(self, *args, **kwargs):
        self.codigo = self.codigo.upper()
        self.nombre = self.nombre.upper()
        self.tags = self.GetEtiquetas((self.codigo, self.nombre))[:512]
        super().clean(*args, **kwargs)


class Documento(models.Model, utils.Texto):
    """
    Representa un documento (facturas, ordenes, entradas, etc.)
    """
    numero = models.IntegerField(_("Número"), editable=False, unique=True, default=-1)
    tipo = models.ForeignKey(DocumentoTipo, on_delete=models.CASCADE, help_text=_("Tipo de documento"))
    almacen = models.ForeignKey("almacen.Almacen", verbose_name=_("Almacén"), on_delete=models.PROTECT)
    persona = models.ForeignKey("persona.Persona", verbose_name=_("Persona"), on_delete=models.PROTECT, null=True, blank=True, default=None)
    fecha = models.DateField(_("Fecha"), default=timezone.now)
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    cajero = models.ForeignKey(User, verbose_name=_("Cajero"), editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    # Movimientos
    entrada = models.ForeignKey("cuenta.Cuenta", related_name="entrada_set", verbose_name=_("Entrada"), null=True, blank=True, default=None, on_delete=models.CASCADE)
    salida = models.ForeignKey("cuenta.Cuenta", related_name="salida_set", verbose_name=_("Salida"), null=True, blank=True, default=None, on_delete=models.CASCADE)
    monto_entrada = models.DecimalField(_("Monto de entrada"), max_digits=17, decimal_places=2, validators=[MinValueValidator(0)], blank=True, help_text=_("Monto que trae el cliente"))
    monto_salida = models.DecimalField(_("Monto de salida"), max_digits=17, decimal_places=2, validators=[MinValueValidator(0)], blank=True, help_text=_("Monto que se le entregará al cliente"))
    tasa_entrada = models.DecimalField(_("Tasa de entrada"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=None, null=True, blank=True, help_text=_("Tasa de entrada (compra)"))
    tasa_salida = models.DecimalField(_("Tasa de salida"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], default=None, null=True, blank=True, help_text=_("Tasa de salida (venta)"))
    # La ganancia generada en esta transacción. La ganancia estará en la moneda de entrada.
    tasa_entrada_para_venta_del_dia = models.DecimalField("Tasa de venta del día", max_digits=5, decimal_places=2, default=0, blank=True)
    ganancia = models.DecimalField(_("Ganancia"), max_digits=17, decimal_places=2, default=0, blank=True)

    is_print = models.BooleanField(_("¿Se imprimió?"), default=False)

    nota = models.TextField(_("Nota"), blank=True)
    tags = models.TextField(blank=True, editable=False)

    # Audiroría
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return "{}-{}".format(self.tipo.codigo, self.numero)

    def get_absolute_url(self):
        if (self.tipo.modo == FACTURA) and (self.is_print == False):
            self.is_print = True
            self.save()
            return reverse_lazy("documento-documento-print", kwargs={"pk": self.pk})
        return reverse_lazy("documento-documento-detail", kwargs={"pk": self.pk})

    def clean(self, *args, **kwargs):
        # El número del documento estará compuesto por el id del almacén y una secuencia automática única 
        # para cada documento en dicho almacén.
        if (self.numero == -1):
            self.numero = self.GetSiguienteNumero(self.almacen)

        if (not self.monto_entrada):
            self.monto_entrada = 0
        if (not self.monto_salida):
            self.monto_salida = 0

        # El monto de entrada tiene que ser igual o mayor a 0
        if (self.monto_entrada < 0):
            raise ValidationError({"monto_entrada": _("El monto de entrada debe ser igual o mayor a 0")})

        # No es posible realizar cambios de divisa entre la misma divisa.
        if (self.entrada == self.salida):
            raise ValidationError({"salida": _("La moneda de salida debe ser distinta a la moneda de entrada"), "entrada": _("La moneda de entrada debe ser distinta a la moneda de salida")})

        # Establecemos el monto de salida.
        self.monto_salida = self.__GetMontoSalida()

        # Validamos la disponibilidad de la cuenta de salida.
        if (self.salida):
            if (self.salida.GetDisponible() < self.monto_salida):
                raise ValidationError({"salida": _("La cuenta en {} no tiene fondos suficientes para realizar esta transacción".format(self.salida.moneda.simbolo))})
        else:
            # Si no hay una salida, no tiene porque 
            # existir un monto de salida y una tasa.
            self.monto_salida = 0
            self.tasa_entrada = 0
            self.tasa_salida = 0

        # Calculamos la ganancia.
        if (self.entrada):
            if self.entrada.moneda.is_principal:
                if (not self.tasa_entrada_para_venta_del_dia):
                    if (self.salida):
                        self.tasa_entrada_para_venta_del_dia = self.salida.moneda.tasa_compra
                        # Calcular la ganancía generada.
                        # La ganancia estará generada en la moneda que recibimos del cliente. 
                        self.ganancia = self.monto_entrada / self.tasa_entrada_para_venta_del_dia
            else:
                if (not self.tasa_entrada_para_venta_del_dia):
                    if (self.entrada):
                        self.tasa_entrada_para_venta_del_dia = self.entrada.moneda.tasa_venta
                        # Calcular la ganancía generada.
                        # La ganancia estará generada en la moneda que recibimos del cliente. 
                        self.ganancia = self.tasa_entrada_para_venta_del_dia - self.tasa_entrada
        else:
            self.ganancia = 0
                
        if (not self.ganancia):
            self.ganancia = 0

        # Etiquetas
        tags = self.GetEtiquetas((self.numero, str(self.almacen), str(self.persona), str(self.fecha), str(self.entrada), str(self.salida), self.monto_entrada, self.monto_salida, str(self.cajero)))
        self.tags += self.GetEtiqueta(self.nota, False)
        super().clean(*args, **kwargs)

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        """
        Obtiene el detalle incluyendo tambien los campos de sus relaciones.
        """
        return self.GetDetail(subfields=True)

    def GetDetailSubfieldsAll(self):
        """
        Obtiene el detalle incluyendo también los campos de sus relaciones y 
        los los campos de las relaciones de estas, etc.
        """
        return self.GetDetail(subfields="__all__")

    def GetImg(self):
        if (self.entrada) and (self.salida):
            return IMG_DOCUMENTO
        if (self.entrada):
            return IMG_DOCUMENTO_ENTRADA
        if (self.salida):
            return IMG_DOCUMENTO_SALIDA

    def GetTitulo(self):
        """
        Obtiene un texto que servirá como encabezado del documento.
        """
        if (self.entrada) and (self.salida):
            return "CAMBIO DE DIVISA"
        if (self.entrada):
            return "ENTRADA DE EFECTIVO"
        if (self.salida):
            return "SALIDA DE EFECTIVO"
        else:
            return "DOCUMENTO"

    def GetTasa(self):
        """
        Retorna la tasa real entre las dos monedas a la que se estuvo cambiando, 
        dividiendo el monto de salida entre el monto de entrada.
        Nota: Cuando una de las monedas es 'principal', la tasa será la tasa 
        de la otra moneda.
        """
        try:
            if (self.entrada.moneda.is_principal):
                return self.tasa_salida
        except (BaseException) as e:
            print(e)
        try:
            if (self.salida.moneda.is_principal):
                return self.tasa_entrada
        except (BaseException) as e:
            print(e)
        try:
            return self.monto_salida / self.monto_entrada
        except (ZeroDivisionError):
            return 0
        except (BaseException):
            return 0

    def __GetMontoSalida(self):
        """
        Retorna el monto de salida.
        """
        # La moneda principal es la que tomamos como referencia cambiaria
        # La tasa de la moneda principal será siempre = 1.
        out = Decimal(0)
        
        # Si no se especifica una cuenta de salida, 
        # no tiene por que existir un monto de salida.
        if (not self.salida):
            return Decimal(0)

        # Si no se especifica una cuenta de entrada,
        # quiere decir que este es un documento solo de salida,
        if (not self.entrada):
            return self.monto_entrada

        if (not self.tasa_entrada):
            self.tasa_entrada = self.entrada.moneda.tasa_compra 
        
        if (not self.tasa_salida):
            self.tasa_salida = self.salida.moneda.tasa_venta

        # CASO 1: Cambio de moneda principal a cualquier otra moneda:
        # en vez de multiplicar el monto por la tasa, dividimos.
        if (self.entrada.moneda.is_principal == True):
            out = self.monto_entrada / self.tasa_salida
        # CASO 2: Cambio de cualquier otra moneda a la moneda principal:
        elif (self.salida.moneda.is_principal == True):
            out = self.monto_entrada * self.tasa_entrada
        # CASO 3: Cambio entre monedas que no son la principal:
        # Lo que hacemos es usar la moneda principal como intermediario,
        # convirtiendo el monto de entrada a la moneda principal y 
        # posteriormente convirtiendolo de la moneda principal a la moneda de salida.
        else:
            # Convertimos a principal.
            out = self.monto_entrada * self.tasa_entrada
            # Convertimos a la moneda de salida.
            out = out / self.tasa_salida

        return out

    def __GetMontoEntrada(self):
        """
        Retorna el monto de entrada.
        """
        # La moneda principal es la que tomamos como referencia cambiaria
        # La tasa de la moneda principal será siempre = 1.
        out = Decimal(0)
        
        # Si no se especifica una cuenta de entrada, 
        # no tiene por que existir un monto de entrada.
        if (not self.entrada):
            return Decimal(0)

        # Si no se especifica una cuenta de salida,
        # quiere decir que este es un documento solo de entrada,
        if (not self.salida):
            return self.monto_salida

        if (not self.tasa_salida):
            self.tasa_salida = self.salida.moneda.tasa_venta 
        
        if (not self.tasa_entrada):
            self.tasa_entrada = self.entrada.moneda.tasa_compra

        if (self.salida.moneda.is_principal == True):
            out = self.monto_salida / self.tasa_entrada

        elif (self.entrada.moneda.is_principal == True):
            out = self.monto_salida * self.tasa_salida

        else:
            # Convertimos a principal.
            out = self.monto_salida * self.tasa_salida
            # Convertimos a la moneda de salida.
            out = out / self.tasa_entrada

        return out

    def CalcularMontoSalida(self, entrada=None, salida=None, monto_entrada=0, tasa1=None, tasa2=None):
        """
        Calcula y retorna el monto de salida.
        :param cuenta:
        :param monto:
        :param tasa:
        :return Decimal():
        """
        obj = Documento()
        obj.entrada = entrada
        obj.salida = salida 
        obj.monto_entrada = monto_entrada
        obj.tasa_entrada = tasa1
        obj.tasa_salida = tasa2
        return obj.__GetMontoSalida()

    def CalcularMontoEntrada(self, entrada=None, salida=None, monto_salida=0, tasa1=None, tasa2=None):
        """
        Calcula y retorna el monto de entrada.
        :param cuenta:
        :param monto:
        :param tasa:
        :return Decimal():
        """
        obj = Documento()
        obj.entrada = entrada
        obj.salida = salida 
        obj.monto_salida = monto_salida
        obj.tasa_entrada = tasa1
        obj.tasa_salida = tasa2
        return obj.__GetMontoEntrada()

    def GetGanancia(self):
        factor = Decimal(0.010)
        if (self.tipo.modo != FACTURA):
            return Decimal(0)
        if (self.entrada.moneda.is_principal):
            ganancia = self.monto_entrada * factor
        elif (self.salida.moneda.is_principal):
            ganancia = self.monto_salida * factor
        else:
            ganancia = (self.monto_entrada * self.entrada.moneda.tasa_compra) * factor
        return round(ganancia, 2)


    def GetSiguienteNumero(self, almacen):
        """
        Obtiene la siguiente secuencia numérica para 
        los documentos en el almacén indicado.
        """
        try:
            return Documento.objects.filter(almacen=almacen).aggregate(models.Max("numero"))["numero__max"] + 1
        except (TypeError):
            return int("{}{:0>7}".format(almacen.id, 1))

    def GetEntradaString(self):
        if (self.entrada):
            if (not self.monto_entrada):
                return "{} {:,.2f}".format(self.entrada.moneda.simbolo, 0)
            return "{} {:,.2f}".format(self.entrada.moneda.simbolo, self.monto_entrada)
        return ""

    def GetSalidaString(self):
        if (self.salida):
            if (not self.monto_salida):
                return "{} {:,.2f}".format(self.salida.moneda.simbolo, 0)
            return "{} {:,.2f}".format(self.salida.moneda.simbolo, self.monto_salida)
        return ""


            

            
        


