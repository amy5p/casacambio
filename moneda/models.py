from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords
from fuente import utils
from fuente.var import *





class Moneda(models.Model, utils.Texto):
    """
    Representa un tipo de divisa.
    """
    simbolo = models.CharField(_("Símbolo"), max_length=3, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=50, unique=True)
    tasa_compra = models.DecimalField(_("Tasa de compra"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], help_text=_("Tasa en la que la Empresa le compra al cliente."))
    tasa_venta = models.DecimalField(_("Tasa de venta"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)], help_text=_("Tasa en la que la Empresa le vende al cliente."))
    is_principal = models.BooleanField(_("¿Es principal?"), default=False, help_text=_("Indica que esta moneda es la principal (solo puede existir una sola moneda como principal)"))
    tags = models.CharField(blank=True, max_length=512, editable=False)

    # Auditoria
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

    
    def __str__(self):
        return "{}: {}".format(self.simbolo, self.nombre)

    def get_absolute_url(self):
        return reverse_lazy("moneda-moneda-detail", kwargs={"pk": self.pk})
    
    def clean(self, *args, **kwargs):
        self.simbolo = self.simbolo.upper()
        self.nombre = self.nombre.upper()

        # La tasa para la moneda principal será siempre 1
        if (self.is_principal == True):
            self.tasa_compra = 1    
            self.tasa_venta = 1
        else:
            try:
                self.tasa_compra = round(self.tasa_compra, 4)
            except (ValueError, TypeError):
                raise ValidationError({"tasa_compra": _("Debe indicar un valor númerico en la tasa de compra")})

            try:
                self.tasa_venta = round(self.tasa_venta, 4)
            except (ValueError, TypeError):
                raise ValidationError({"tasa_venta": _("Debe indicar un valor númerico en la tasa de venta")})

            if (self.tasa_compra <= 0):
                raise ValidationError({"tasa_compra": _("La tasa de compra debe ser mayor que 0")})
            if (self.tasa_venta <= 0):
                raise ValidationError({"tasa_venta": _("La tasa de venta debe ser mayor que 0")})
            if (self.tasa_compra > 999):
                raise ValidationError({"tasa_compra": _("La tasa de compra debe ser menor que 1,000")})
            if (self.tasa_venta > 999):
                raise ValidationError({"tasa_venta": _("La tasa de venta debe ser menor que 1,000")})

        self.tags = self.GetEtiquetas((self.simbolo, self.nombre))[:512]
        super().clean(*args, **kwargs)

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        return self.GetDetail(subfields=subfields)

    def GetImg(self):
        return IMG_MONEDA




class MonedaTasasUpdate(models.Model):
    """
    Modelo para registrar los cambios de tasas en las monedas.
    """
    fecha = models.DateTimeField(_("Fecha"), auto_now_add=True)
    items = models.TextField(blank=True) # diccionario en str object. moneda_id: {'moneda_id': int, 'tasa_compra': Decimal, 'tasa_venta': Decimal}

    class Meta:
        verbose_name = _("Actualización de tasas")
        verbose_name_plural = _("Actualizaciones de tasas")
