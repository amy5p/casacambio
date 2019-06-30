from django.shortcuts import render
from django.views.generic import TemplateView
from fuente import utils
from fuente.var import *
# Create your views here.




def error403(request, exception):
    return "ERROR 403 - base.views.error403 - Aun no configurado."






class IndexView(TemplateView):
    """
    Página principal.
    """
    template_name = "base/index.html"

