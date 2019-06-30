from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _
from dal import autocomplete
from .models import *
from persona.models import *
from cuenta.models import *
from fuente import utils
from fuente.var import *
from base.models import Configuracion



conf = Configuracion()


# -------------------------------------------------
# DOCUMENTOS
# -------------------------------------------------



class DocumentoForm(forms.ModelForm, utils.Texto):

    class Meta:
        model = Documento
        fields = "__all__"

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
    persona = forms.ModelChoiceField(label=_("Cliente"), queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    tipo = forms.ModelChoiceField(label=_("Tipo"), queryset=DocumentoTipo.objects.all())


class DocumentoEntradaForm(forms.ModelForm, utils.Texto):
    """
    Utilizado para crear documento de tipo ENTRADA.
    """
    class Meta:
        model = Documento
        fields = ("almacen", "tipo", "fecha", "entrada", "monto_entrada", "nota")

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
    #persona = forms.ModelChoiceField(label=_("Cliente"), queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    tipo = forms.ModelChoiceField(label=_("Tipo"), queryset=DocumentoTipo.objects.filter(modo=ENTRADA))
    entrada = forms.ModelChoiceField(label=_("Cuenta"), queryset=Cuenta.objects.all())
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        return super().save(commit=commit)


class DocumentoSalidaForm(forms.ModelForm, utils.Texto):
    """
    Utilizado para crear documento de tipo SALIDA.
    """
    class Meta:
        model = Documento
        fields = ("almacen", "tipo", "fecha", "salida", "monto_entrada", "nota")

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
    #persona = forms.ModelChoiceField(label=_("Cliente"), queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    tipo = forms.ModelChoiceField(label=_("Tipo"), queryset=DocumentoTipo.objects.filter(modo=SALIDA))
    salida = forms.ModelChoiceField(label=_("Cuenta"), queryset=Cuenta.objects.all())
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        return super().save(commit=commit)


class DocumentoTransferenciaForm(forms.ModelForm, utils.Texto):
    """
    Utilizado para crear documento de tipo TRANSFERENCIA.
    """
    class Meta:
        model = Documento
        fields = ("almacen", "tipo", "persona", "fecha", "entrada", "salida", "monto_entrada", "tasa_entrada", "tasa_salida", "nota")

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
    persona = forms.ModelChoiceField(label=_("Cliente"), queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    tipo = forms.ModelChoiceField(label=_("Tipo"), queryset=DocumentoTipo.objects.filter(modo=FACTURA))
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        return super().save(commit=commit)



class DocumentoFacturaForm(forms.ModelForm, utils.Texto):
    """
    Utilizado para crear documento de tipo FACTURA.
    """
    class Meta:
        model = Documento
        fields = ("almacen", "tipo", "persona", "fecha", "entrada", "salida", "monto_entrada", "monto_salida", "tasa_entrada", "tasa_salida", "nota")

    __nowStr = timezone.now().strftime("%Y-%m-%d")
    fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "value": __nowStr}))
    persona = forms.ModelChoiceField(label=_("Cliente"), required=False, queryset=Persona.objects.all(), widget=autocomplete.ModelSelect2(url="persona-persona-json-list", attrs={"data-placeholder": _("Buscar cliente..."), "data-html": True, "style": "width: 20px"}))
    tipo = forms.ModelChoiceField(label=_("Tipo"), required=True, queryset=DocumentoTipo.objects.filter(modo=FACTURA))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields["tasa_salida"].widget.attrs = {"readonly": True}
        #self.fields["monto_salida"].widget.attrs = {"readonly": True}
        
        self.fields["monto_entrada"]
        self.fields["entrada"].queryset = Cuenta.objects.all()
        self.fields["salida"].queryset = Cuenta.objects.all()
        self.fields["nota"].widget.attrs = {"rows": 1, "style": "width: 100%", "placeholder": _("Escriba un comentario...")}

        try:
            self.fields["tipo"].initial = conf.facturacion.tipo_documento_predeterminado
        except (BaseException) as e:
            print(e)

        try:
            lastfactura = Documento.objects.filter(tipo__modo=FACTURA).order_by("-id")[0]
        except (BaseException):
            pass
        else:
            try:
                self.fields["almacen"].initial = lastfactura.almacen
            except (BaseException) as e:
                print(e)
            try:
                self.fields["tipo"].initial = lastfactura.tipo
            except (BaseException) as e:
                print(e)
            try:
                self.fields["persona"].initial = Persona.objects.filter(nombre__in=("GENERICO", "GENÉRICO", "generico", "genérico"))[0]
            except (BaseException) as e:
                print(e)
            


    def clean(self):
        monto_entrada = self.cleaned_data["monto_entrada"]
        monto_salida = self.cleaned_data["monto_salida"]

        if (not monto_entrada) and (not monto_salida):
            raise ValidationError({"monto_entrada": _("Indique el monto de entrada")})

        
            

    def save(self, commit=True):
        instance = super().save(commit=False)
        return super().save(commit=commit)

    