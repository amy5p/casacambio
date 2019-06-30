from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords
from fuente import utils
from fuente.var import *



class Almacen(models.Model, utils.Texto):
    """
    Un almacén es una oficina, sucursal, entidad que 
    pertenece a la misma empresa.
    """
    codigo = models.CharField(_("Código"), max_length=10, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=50, unique=True)
    ubicacion = models.CharField(_("Ubicación"), max_length=100, blank=True)
    telefonos = models.CharField(_("Teléfonos"), max_length=50, blank=True)
    empresa = models.ForeignKey("empresa.Empresa", verbose_name=_("Empresa"), on_delete=models.CASCADE)
    activo = models.BooleanField(_("Activo"), default=True)

    # Configuración
    #entrada_predeterminada = models.ForeignKey("cuenta.Cuenta", on_delete=models.SET_NULL, related_name="cuenta_entrada_predeterminada", verbose_name=_("Cuenta de entrada predeterminada"), null=True, default=None, blank=True)
    #salida_predeterminada = models.ForeignKey("cuenta.Cuenta", on_delete=models.SET_NULL, related_name="cuenta_salida_predeterminada", verbose_name=_("Cuenta de salida predeterminada"), null=True, default=None, blank=True)

    tags = models.CharField(blank=True, max_length=512, editable=False)

    # Audiroría
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Almacén")
        verbose_name_plural = _("Almacenes")

    def __str__(self):
        return "{}: {}".format(self.codigo, self.nombre)

    def get_absolute_url(self):
        return reverse_lazy("almacen-almacen-update", kwargs={"pk": self.pk})

    def GetImg(self):
        return IMG_ALMACEN
    
    def clean(self, *args, **kwargs):
        self.codigo = self.codigo.upper()
        self.nombre = self.nombre.upper()
        self.tags = self.GetEtiquetas((self.codigo, self.nombre, self.ubicacion, self.empresa.tags))[:512]
        super().clean(*args, **kwargs)

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        return self.GetDetail(subfields=subfields)
