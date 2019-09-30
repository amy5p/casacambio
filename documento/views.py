import decimal
import datetime
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
# Locales
from .models import *
from cuenta.models import *
from .forms import *
from fuente import utils






# --------------------------------------------------------------
# DOCUMENTOS
# --------------------------------------------------------------


class DocumentoListView(LoginRequiredMixin, ListView, utils.Texto):
    model = Documento
    paginate_by = 200


    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        q = self.request.GET.get("q")
        fieldname = self.request.GET.get("field")
        year = self.request.GET.get("fecha__year")
        month = self.request.GET.get("fecha__month")
        day = self.request.GET.get("fecha__day")

        try:
            year = abs(int(year))
        except (ValueError, TypeError):
            year = 0
        try:
            month = abs(int(month))
        except (ValueError, TypeError):
            month = 0
        try:
            day = abs(int(day))
        except (ValueError, TypeError):
            day = 0

        if (q):
            q = self.GetEtiqueta(q, False)
        else:
            q = ""

        if (fieldname):
            fieldname = fieldname.lower().strip() + "__icontains"
            qs = self.model.objects.filter(**{fieldname: q})
        else:
            qs = self.model.objects.filter(tags__icontains=q)

        if (year) and (month) and (day):
            date = datetime.date(year, month, day)
            qs = qs.filter(fecha=date)
        elif (year) and (month):
            qs = qs.filter(fecha__year=year, fecha__month=month)
        elif (year) and (day):
            qs = qs.filter(fecha__year=year, fecha__day=day)
        elif (month) and (day):
            qs = qs.filter(fecha__month=month, fecha__day=day)
        elif (year):
            qs = qs.filter(fecha__year=year)
        elif (month):
            qs = qs.filter(fecha__month=month)
        elif (day):
            qs = qs.filter(fecha__day=day)

        self.queryset = qs
        return super().get_queryset()



class DocumentoDetailView(LoginRequiredMixin, DetailView):
    model = Documento

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DocumentoPrintDetailView(LoginRequiredMixin, DetailView):
    model = Documento
    template_name = "documento/documento_print2.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DocumentoCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para la creación de cualquier tipo de documento.
    """
    model = Documento
    form_class = DocumentoForm

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["img"] = IMG_DOCUMENTO
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.cajero = self.request.user
        obj.save()
        return super().form_valid(form)



class DocumentoFacturaCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para la creación de documentos de tipo factura.
    """
    model = Documento
    form_class = DocumentoFacturaForm
    template_name = "documento/documento_factura_form.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["img"] = IMG_DOCUMENTO
        try:
            context["lastfactura"] = Documento.objects.filter(tipo__modo=FACTURA, cajero=self.request.user).order_by("-id")[0]
        except (IndexError) as e:
            context["lastfactura"] = None

        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.cajero = self.request.user
        obj.save()
        return super().form_valid(form)



class DocumentoEntradaCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para la creación de documentos de tipo entrada.
    """
    model = Documento
    form_class = DocumentoEntradaForm
    template_name = "documento/documento_form.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = "{} DE ENTRADA".format(self.model._meta.verbose_name.upper())
        context["img"] = IMG_DOCUMENTO_ENTRADA
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.cajero = self.request.user
        obj.save()
        return super().form_valid(form)


class DocumentoSalidaCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para la creación de documentos de tipo salida.
    """
    model = Documento
    form_class = DocumentoSalidaForm
    template_name = "documento/documento_form.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = "{} DE SALIDA".format(self.model._meta.verbose_name.upper())
        context["img"] = IMG_DOCUMENTO_SALIDA
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.cajero = self.request.user
        obj.save()
        return super().form_valid(form)





# -------------------------------------------------------------------
# JSON
# -------------------------------------------------------------------

@login_required()
def documentoCalcularMontoSalida(request):
    """
    Calcula el monto de salida a partir del la cuenta de entrada,
    monto de entrada y la tasa establecida.

    :param request:
    :return: JsonResponse({})
    """

    entrada = request.GET.get("entrada")
    salida = request.GET.get("salida")
    monto = request.GET.get("monto")
    tasa1 = request.GET.get("tasa1")
    tasa2 = request.GET.get("tasa2")

    try:
        entrada = Cuenta.objects.get(id=entrada)
    except (ValueError):
        return JsonResponse({"results": None, "error": True, "message": _("Debe indicar la cuenta de entrada")})

    try:
        salida = Cuenta.objects.get(id=salida)
    except (ValueError):
        return JsonResponse({"results": None, "error": True, "message": _("Debe indicar la cuenta de salida")})
    try:
        monto = Decimal(monto)
    except (ValueError, decimal.InvalidOperation):
        monto = Decimal(0)

    try:
        tasa1 = Decimal(tasa1)
    except (ValueError, decimal.InvalidOperation):
        tasa1 = Decimal(0)

    try:
        tasa2 = Decimal(tasa2)
    except (ValueError, decimal.InvalidOperation):
        tasa2 = Decimal(0)

    monto_salida = Documento().CalcularMontoSalida(entrada, salida, monto, tasa1, tasa2)

    return JsonResponse({"results": round(monto_salida, 2), "error": False, "message": ""})



@login_required()
def documentoCalcularMontoEntrada(request):
    """
    Calcula el monto de entrada a partir del la cuenta de entrada,
    monto de salida y la tasa establecida.

    :param request:
    :return: JsonResponse({})
    """

    entrada = request.GET.get("entrada")
    salida = request.GET.get("salida")
    monto = request.GET.get("monto")
    tasa1 = request.GET.get("tasa1")
    tasa2 = request.GET.get("tasa2")

    try:
        entrada = Cuenta.objects.get(id=entrada)
    except (ValueError):
        return JsonResponse({"results": None, "error": True, "message": _("Debe indicar la cuenta de entrada")})

    try:
        salida = Cuenta.objects.get(id=salida)
    except (ValueError):
        return JsonResponse({"results": None, "error": True, "message": _("Debe indicar la cuenta de salida")})
    try:
        monto = Decimal(monto)
    except (ValueError, decimal.InvalidOperation):
        monto = Decimal(0)

    try:
        tasa1 = Decimal(tasa1)
    except (ValueError, decimal.InvalidOperation):
        tasa1 = Decimal(0)

    try:
        tasa2 = Decimal(tasa2)
    except (ValueError, decimal.InvalidOperation):
        tasa2 = Decimal(0)

    monto_entrada = Documento().CalcularMontoEntrada(entrada, salida, monto, tasa1, tasa2)

    return JsonResponse({"results": round(monto_entrada, 2), "error": False, "message": ""})


