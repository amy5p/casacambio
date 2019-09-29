from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from simple_history.models import HistoricalRecords
from fuente import utils







class Empresa(models.Model, utils.Texto):
    """
    Perfil de la Empresa.
    """
    nombre = models.CharField(_("Nombre"), max_length=255, unique=True)
    razon_social = models.CharField(_("Razón social"), max_length=255, unique=True)
    identificacion = models.CharField(_("Identificación"), max_length=255, unique=True)
    identificacion_tipo = models.CharField(_("Tipo de identificación"), max_length=20, blank=True)
    logo = models.ImageField(_("Logo"), upload_to="empresa/logo/", blank=True, height_field="logo_height", width_field="logo_width", max_length=None)
    logo_height = models.IntegerField(blank=True, null=True, default=None, editable=False)
    logo_width = models.IntegerField(blank=True, null=True, default=None, editable=False)
    # Busqueda
    tags = models.TextField(blank=True, editable=False)
    # Auditoria
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Empresa")
        verbose_name_plural = _("Empresas")

    def __str__(self):
        return self.nombre
    
    def clean(self):
        self.tags = self.GetEtiquetas((self.nombre, self.razon_social, self.identificacion))[:512]
        super().clean()

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        return self.GetDetail(subfields=subfields)
        
    def GetImg(self):
        if self.logo:
            return self.logo.url
        return ""


