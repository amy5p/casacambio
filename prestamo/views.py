
# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, ListView, DeleteView, UpdateView, TemplateView, FormView



# Módulos locales
from base.models import Configuracion
from .models import *
from .forms import *
from fuente import utils
from fuente.var import *



conf = Configuracion()




add = {"id": "add", "name": _("Nuevo préstamo"), "url": reverse_lazy("prestamo-prestamo-create"), "img": IMG_ADD}
edit = {"id": "edit", "name": _("Modificar préstamo"), "url": "", "img": IMG_EDIT}
#delete = {"id": "delete", "name": _("Eliminar préstamo"), "url": reverse_lazy("prestamos_delete"), "img": IMG_DELETE}
#menuitem1 = {"id": "transacciones", "name": _("Transacciones"), "url": reverse_lazy("transacciones_list"), "img": IMG_TRANSACCION}






class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "prestamos/index.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SolicitudView(LoginRequiredMixin, CreateView):
    model = Solicitud
    template_name = "prestamos/solicitud.html"
    fields = "__all__"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SolicitudEnviadaView(LoginRequiredMixin, TemplateView):
    template_name = "prestamos/solicitud_enviada.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CalculadoraView(LoginRequiredMixin, TemplateView):
    template_name = "prestamos/calculadora.html"
    
    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PrestamoStatView(LoginRequiredMixin, TemplateView):
    template_name = "prestamos/estadisticas.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PrestamoCreateView(LoginRequiredMixin, CreateView):
    """
    Crea un nuevo préstamo.
    """
    template_name = "prestamos/prestamo_create.html"
    model = Prestamo
    form_class = PrestamoForm

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PrestamoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Modifica un préstamo.
    """
    template_name = "prestamos/prestamo_update.html"
    model = Prestamo
    form_class = PrestamoForm

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class PrestamoDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra la información de un préstamo.
    """
    model = Prestamo
    template_name = "prestamos/prestamo_detail.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PrestamoListView(LoginRequiredMixin, ListView):
    """
    Listado de préstamos.
    """
    model = Prestamo
    template_name = "prestamos/prestamo_list.html"

    @utils.context_decorator()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required()
def desembolsar_view(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    # Si ya el préstamo ha sido desembolsado, no mostramos el formulario, solo información.
    # Esto es porque solo debe haber un desembolso por cada préstamo.
    if prestamo.IsDesembolsado():
        return render(request, 'prestamos/prestamo_desembolso_create.html', {"prestamo": prestamo})

    elif request.method == "POST":
        form = PrestamoDesembolsarForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.author = request.user 
            t.desde = prestamo.cuenta 
            t.monto = prestamo.monto 
            t.tipo = DESEMBOLSO
            t.save()
            return redirect('prestamo-prestamo-detail', pk=prestamo.pk)
    else:
        form = PrestamoDesembolsarForm()
    return render(request, 'prestamos/prestamo_desembolso_create.html', {'form': form, 'prestamo': prestamo})


@login_required()
def pagar_view(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    # Si el préstamo no se ha desembolsado no se pueden realizar pagos aún.
    if not prestamo.IsDesembolsado():
        return render(request, 'prestamos/prestamo_pago_create.html', 
            {"prestamo": prestamo, "error": True, 
            "mensaje": _("Este préstamo aún no ha sido desembolsado. Debe realizar el desembolso del mismo antes de proceder con los pagos. ")})

    elif request.method == "POST":
        form = PrestamoPagarForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.author = request.user 
            t.hacia = prestamo.cuenta 
            t.tipo = PAGO
            t.fecha_efectiva = prestamo.GetSiguientePago()["corte"]
            t.save()
            return redirect('prestamo-prestamo-detail', pk=prestamo.pk)
    else:
        form = PrestamoPagarForm()
    return render(request, 'prestamos/prestamo_pago_create.html', {'form': form, "prestamo": prestamo})



@login_required()
def print_view(request, pk):
    object = get_object_or_404(Prestamo, pk=pk)
    # Lo que se va a imprimir se determina de acuerdo al parametro 
    # pasado por la url denominado 'part', en el diccionario request.GET.
    return render(request, "prestamos/prestamo_print.html", {"object": object})








# ----------------------------------------------------------
# CUENTA Y TRANSACCIONES 
# ----------------------------------------------------------


class CuentaAutocomplete(autocomplete.Select2QuerySetView):
    """
    Clase utilizada por 'django-autocomplete-ligth', el cual muestra un control de 
    busqueda para los ForeignKey en los formularios.
    """
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Cliente.objects.none()

        qs = Cuenta.objects.all()
        if self.q:
            qs = qs.filter(tags__istartswith=self.q)
        return qs


class CuentaDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra el detalle de una cuenta.
    """
    model = Cuenta
    template_name = "contabilidad/cuenta_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = str(self.object)
        context["subtitleimg"] = self.object.GetImg()
        context["IMAGE"] = context["subtitleimg"]
        context["KEYWORDS"] = "cuenta"
        return context

    def dispatch(self, request, *args, **kwargs):
        # Detecta si es un dispositivo movil y obtiene la ruta de la plantilla 
        self.template_name = mobile.getTemplate(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)


class TransaccionCreateView(LoginRequiredMixin, CreateView):
    """
    Crea una transacción.
    """
    model = Transaccion
    template_name = "contabilidad/transaccion_create.html"
    form_class = TransaccionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = _("Nueva transacción")
        context["subtitleimg"] = IMG_TRANSACCION
        context["IMAGE"] = context["subtitleimg"]
        context["KEYWORDS"] = "transacción"
        return context

    def dispatch(self, request):
        # Detecta si es un dispositivo movil y obtiene la ruta de la plantilla 
        self.template_name = mobile.getTemplate(request, self.template_name)
        return super().dispatch(request)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TransaccionDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra el detalle de una transacción.
    """
    model = Transaccion
    template_name = "contabilidad/transaccion_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = str(self.object)
        context["subtitleimg"] = self.object.GetImg()
        context["IMAGE"] = context["subtitleimg"]
        context["KEYWORDS"] = "transacción"
        return context

    def dispatch(self, request, *args, **kwargs):
        # Detecta si es un dispositivo movil y obtiene la ruta de la plantilla 
        self.template_name = mobile.getTemplate(request, self.template_name)
        return super().dispatch(request, *args, **kwargs)











