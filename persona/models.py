from django.db import models
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from simple_history.models import HistoricalRecords
from fuente import utils
from fuente.var import *








class Persona(models.Model, utils.Texto):
    """
    Representa una persona, cliente, suplidor, empresa, ...
    """
    identificacion = models.CharField(_("Identificación"), max_length=20, unique=True)
    identificacion_tipo = models.CharField(_("Tipo de identificación"), max_length=20, choices=IDENTIFICACION_CHOICES)
    nombre = models.CharField(_("Nombre"), max_length=100)
    razon_social = models.CharField(_("Razón social"), max_length=100, blank=True)
    telefono1 = models.CharField(_("Teléfono"), max_length=20, blank=True)
    telefono2 = models.CharField(_("Celular"), max_length=20, blank=True)
    email = models.EmailField(_("Correo electrónico"), blank=True)
    direccion = models.CharField(_("Dirección"), max_length=256, blank=True)
    # Persona de contacto.
    persona_de_contacto_nombre = models.CharField(_("Nombre de la persona de contacto"), max_length=100, blank=True)
    persona_de_contacto_identificacion = models.CharField(_("Identificación de la persona de contacto"), max_length=20, blank=True)
    persona_de_contacto_telefono = models.CharField(_("Teléfono de la persona de contacto"), max_length=20, blank=True)

    tags = models.CharField(blank=True, max_length=512, editable=False)

    # Auditoria
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"

    
    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse_lazy("persona-persona-detail", kwargs={"pk": self.pk})

    def clean(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        self.razon_social = self.razon_social.upper()
        self.tags = self.GetEtiquetas((self.identificacion, self.nombre, self.razon_social, self.telefono1, 
            self.telefono2, self.email, self.direccion, self.persona_de_contacto_nombre, 
            self.persona_de_contacto_identificacion, self.persona_de_contacto_telefono)
        )[:512]
        super().clean(*args, **kwargs)

    def GetDetail(self, subfields=False):
        d = utils.Detail(self, subfields=subfields)
        return d
    
    def GetDetailSubfields(self):
        return self.GetDetail(subfields=subfields)

    def GetImg(self):
        return IMG_PERSONA
