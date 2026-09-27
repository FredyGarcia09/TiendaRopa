from django.views import generic
from .models import Ropa


class HomeView(generic.TemplateView):
    """Vista del menú inicial del sistema."""
    template_name = 'home.html'


class RopaListView(generic.ListView):
    """Vista de catálogo de ropa con DataTables y exportación a Excel."""
    model = Ropa
    template_name = 'ropa.html'
    context_object_name = 'ropas'

    def get_queryset(self):
        return (
            Ropa.objects.select_related('proveedor')
            .prefetch_related('modelo_set')
            .all()
            .order_by('id')
        )
