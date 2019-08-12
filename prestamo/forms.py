
import datetime
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext as _
from dal import autocomplete
#from searchableselect.widgets import SearchableSelect

from fuente import utils
from .models import Solicitud, Prestamo, Cuenta, Transaccion
from persona.models import Persona
from fuente.var import *



class DateInput(forms.DateInput):
    input_type = 'date'


class PrestamoForm(forms.ModelForm):
    """
    Formulario para la creación y modificación de préstamos.
    """

    class Meta:
        model = Prestamo
        fields = ("cliente", "monto", "tasa", "periodo", "cuotas", "cuotas_tipo", "mora", "fecha_inicio", "note", "isactive")

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    cliente = forms.ModelChoiceField(label=_("Cliente"), queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    fecha_inicio = forms.DateField(label=_("Fecha de inicio"), widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
        

class PrestamoDesembolsarForm(forms.ModelForm):
    """
    Formulario para la creación de la transacción que servirá
    como desembolso de un préstamo.
    """

    class Meta:
        model = Transaccion
        fields = ["desde", "modo", "fecha_efectiva"]
        widgets = {
            "desde": forms.HiddenInput(),
            #"hacia": autocomplete.ModelSelect2(url="contabilidad_cuenta_autocomplete"),
            "fecha_efectiva": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        # El monto debe ser igual al monto indicado en el préstamo.
        # La fecha efectiva debe ser mayor o igual que hoy (ya se trabaja en el modelo.)
        # La cuenta 'desde' (salida) debe ser la cuenta del préstamo a desembolsar, esto lo 
        # trabajamos en la View.
        pass


class PrestamoPagarForm(forms.ModelForm):
    """
    Formulario para la creación de las transacciones que servirán
    como pagos a un préstamo.
    """
    class Meta:
        model = Transaccion
        fields = ["desde", "hacia", "modo", "monto"]
        widgets = {
            "desde": forms.HiddenInput(),
            "hacia": forms.HiddenInput(),
        }

    def clean(self):
        # La fecha efectiva debe ser mayor o igual que hoy (ya se trabaja en el modelo.)
        # La cuenta 'desde' (salida) debe ser la cuenta del préstamo a desembolsar, esto lo 
        # trabajamos en la View.
        pass


class SolicitudForm(forms.Form, utils.Texto):
    nombre = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": _("Nombre"), "title": _("Ingrese su nombre.")}))
    cedula = forms.CharField(label="", max_length=13, widget=forms.TextInput(attrs={"placeholder": _("Cédula"), "title": _("Ingrese su número de cédula")}))
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={"placeholder": _("Correo electrónico"), "title": _("Ingrese su correo electrónico")}))
    telefono = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder": _("Teléfono"), "title": _("Ingrese su número de teléfono")}))
    nota = forms.CharField(label="", required=False, max_length=2048, widget=forms.Textarea(attrs={"placeholder": _("Escriba un breve comentario...")}))
    consentimiento = forms.BooleanField(label=_("Estoy de acuerdo con la política de privacidad"), widget=forms.CheckboxInput(attrs={"title": _("Indica que estás de acuerdo en enviarnos tus datos para ser evaluado.")}))

    def clean(self):
        """
        Operación de limpieza para validar los datos antes de guardar.
        """
        # Validamos la cédula ingresada.
        try:
            self.cleaned_data["cedula"] = self.ValidarCedula(self.cleaned_data["cedula"])
        except BaseException as e:
            raise ValidationError({"cedula": _("¡Ups! Al parecer la cédula no es válida. {}".format(e))})
        # Limpiamos el nombre para que sea en mayuscula.
        self.cleaned_data["nombre"] = self.cleaned_data["nombre"].upper()



class TransaccionForm(forms.ModelForm):

    class Meta:
        model = Transaccion
        exclude = ("id", "tags", "author", "fecha_creacion")
        widgets = {
            "desde": autocomplete.ModelSelect2(url="prestamo-cuenta-json-list"),
            "hacia": autocomplete.ModelSelect2(url="prestamo-cuenta-json-list"),
            "fecha_efectiva": forms.DateInput(attrs={"type": "date"}),
        }





