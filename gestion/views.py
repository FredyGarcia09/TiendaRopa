from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import generic
from .models import Ropa, Modelo


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


class InventarioListView(generic.ListView):
    """Vista general para consultar productos con su inventario total disponible."""
    model = Ropa
    template_name = 'inventario_lista.html'
    context_object_name = 'ropas'

    def get_queryset(self):
        return (
            Ropa.objects.select_related('proveedor')
            .prefetch_related('modelo_set')
            .all()
            .order_by('id')
        )


def actualizar_inventario_view(request, ropa_id):
    """Formulario para consultar y actualizar el inventario existente de un producto por color."""
    ropa = get_object_or_404(
        Ropa.objects.select_related('proveedor').prefetch_related('modelo_set'),
        pk=ropa_id
    )
    modelos = ropa.modelo_set.all().order_by('color', 'talla')

    if request.method == 'POST':
        for modelo in modelos:
            campo = f'stock_{modelo.id}'
            if campo in request.POST:
                try:
                    nuevo_stock = int(request.POST[campo])
                    if nuevo_stock >= 0:
                        modelo.stock = nuevo_stock
                        modelo.save(update_fields=['stock'])
                except ValueError:
                    pass
        messages.success(request, f'Inventario actualizado con éxito para "{ropa.descripcion or ropa.marca}".')
        return redirect('actualizar_inventario', ropa_id=ropa.id)

    total_stock = sum(m.stock for m in modelos)
    return render(request, 'inventario_detalle.html', {
        'ropa': ropa,
        'modelos': modelos,
        'total_stock': total_stock,
    })

