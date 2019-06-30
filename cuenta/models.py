from decimal import Decimal
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from simple_history.models import HistoricalRecords
from fuente import utils
from fuente.var import *
from documento.models import Documento





class Cuenta(models.Model, utils.Texto):
    """
    Representa una cuenta contable interna.
    """
    moneda = models.ForeignKey("moneda.Moneda", verbose_name=_("Moneda"), on_delete=models.CASCADE, help_text=_("Tipo de moneda de esta cuenta"))
    almacen = models.ForeignKey("almacen.Almacen", verbose_name=_("Almacén"), on_delete=models.CASCADE, help_text=_("Almacén al que pertenece la cuenta"))
    tags = models.CharField(blank=True, max_length=512, editable=False)

    orden = models.IntegerField("Orden", default=0, blank=True, null=True)
    # Auditoria
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Cuenta")
        verbose_name_plural = _("Cuentas")
    
    def __str__(self):
        return str(self.moneda)

    def get_absolute_url(self):
        return reverse_lazy("cuenta-cuenta-detail", kwargs={"pk": self.pk})
    
    def clean(self, *args, **kwargs):
        # No puede existir mas de una cuenta con la misma moneda en el mismo almacén.
        try:
            other = Cuenta.objects.get(moneda=self.moneda, almacen=self.almacen)
        except (ObjectDoesNotExist):
            pass 
        else:
            if other != self:
                raise ValidationError({"moneda": _("Ya existe una cuenta de {} en el almacén {}".format(self.moneda, self.almacen))})

        self.tags = self.GetEtiquetas((self.moneda.simbolo, self.moneda.nombre, str(self.almacen)))[:512]
        super().clean(*args, **kwargs)

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        return self.GetDetail(subfields=subfields)

    def GetImg(self):
        return IMG_CUENTA

    def GetDisponible(self):
        """
        Obtiene el fondo disponible en esta cuenta.
        """
        ent = self.entrada_set.all().aggregate(suma=models.Sum("monto_entrada"))["suma"]
        sal = self.salida_set.all().aggregate(suma=models.Sum("monto_salida"))["suma"]
        if (ent != None) and (sal != None):
            return ent - sal
        elif (ent != None):
            return ent 
        elif (sal != None):
            return - sal
        return Decimal(0)
        
        


