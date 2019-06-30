from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _
from dal import autocomplete
from .models import *
from fuente import utils
from fuente.var import *





class MonedaTasasForm(forms.ModelForm):
    """
    Formulario para establecer las tasas de compra y venta
    para todas las monedas configuradas.
    """
    class Meta:
        model = MonedaTasasUpdate
        fields = ["id"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.qs = Moneda.objects.all()
        self.objects = {}
        for obj in self.qs:
            self.objects[obj.id] = obj

        label1 = "Compra"
        label2 = "Venta"
        self.fieldsets = []

        for id in self.objects:
            obj = self.objects[id]
            fieldname1 = "tasa_compra_{}".format(obj.id)
            fieldname2 = "tasa_venta_{}".format(obj.id)
            self.fields[fieldname1] = forms.DecimalField(label=label1, required=False, initial=obj.tasa_compra)
            self.fields[fieldname2] = forms.DecimalField(label=label2, required=False, initial=obj.tasa_venta)

            if obj.is_principal:
                self.fields[fieldname1].widget.attrs = {"readonly": True}
                self.fields[fieldname2].widget.attrs = {"readonly": True}

            self.fieldsets.append(
                {
                    "title": str(obj),
                    "fields": [
                        {"name": fieldname1, "id": "id_{}".format(fieldname1), "field": self.fields[fieldname1], "readonly": self.fields[fieldname1].widget.attrs.get("readonly")},
                        {"name": fieldname2, "id": "id_{}".format(fieldname2), "field": self.fields[fieldname2], "readonly": self.fields[fieldname1].widget.attrs.get("readonly")}
                    ],
                }
            )


    def clean(self):
        cleaned_data = super().clean()

        # actualizados las fields.
        for id in self.objects:
            obj = self.objects[id]
            fieldname1 = "tasa_compra_{}".format(obj.id)
            fieldname2 = "tasa_venta_{}".format(obj.id)
            tasa_compra = cleaned_data[fieldname1]
            tasa_venta = cleaned_data[fieldname2]
            self.fields[fieldname1].initial = tasa_compra
            self.fields[fieldname2].initial = tasa_venta

        
        for id in self.objects:
            obj = self.objects[id]
            fieldname1 = "tasa_compra_{}".format(obj.id)
            fieldname2 = "tasa_venta_{}".format(obj.id)
            tasa_compra = cleaned_data[fieldname1]
            tasa_venta = cleaned_data[fieldname2]

            obj.tasa_compra = tasa_compra
            obj.tasa_venta = tasa_venta 

            try:
                obj.clean()
            except (BaseException) as e:
                try:
                    raise ValidationError(e.messages)
                except (AttributeError):
                    raise ValidationError(str(e))

            self.objects[id] = obj

        return self.cleaned_data


    



