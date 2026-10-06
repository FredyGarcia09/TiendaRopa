from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from .models import Ropa, Modelo, Cliente, Empleado, Proveedor, Venta, DetalleVenta
from .forms import RopaForm, ClienteForm, ProveedorForm, ModeloForm, EmpleadoForm


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Control de acceso por grupos de usuario."""
    roles_permitidos = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=self.roles_permitidos).exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(self.request, "No tienes permisos para acceder a esta sección.")
        return redirect('home')


class MiLoginView(LoginView):
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, generic.TemplateView):
    """Vista del menú inicial del sistema."""
    template_name = 'home.html'


class RopaListView(RolRequeridoMixin, generic.ListView):
    """Catálogo general de prendas."""
    roles_permitidos = ['Administrador']
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


class RopaCreateView(RolRequeridoMixin, generic.CreateView):
    """Registrar nueva prenda."""
    roles_permitidos = ['Administrador']
    model = Ropa
    form_class = RopaForm
    template_name = 'ropa_form.html'
    success_url = reverse_lazy('ropa')

    def form_valid(self, form):
        messages.success(self.request, "Prenda registrada con éxito.")
        return super().form_valid(form)


class ClienteListView(RolRequeridoMixin, generic.ListView):
    """Catálogo de clientes con total de compras."""
    roles_permitidos = ['Administrador']
    model = Cliente
    template_name = "clientes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for cliente in context['cliente_list']:
            cliente.ventas = cliente.venta_set.count()
            resultado = cliente.venta_set.aggregate(totalVentas=Sum('total'))
            cliente.ventasTotal = resultado['totalVentas'] or 0

        return context


class ClienteCreateView(RolRequeridoMixin, generic.CreateView):
    """Registrar nuevo cliente."""
    roles_permitidos = ['Administrador']
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_form.html'
    success_url = reverse_lazy('clientes')

    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado con éxito.")
        return super().form_valid(form)


@login_required
def cliente_eliminar_view(request, pk):
    """Eliminar cliente si no tiene historial de compras."""
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        messages.error(request, "No tienes permisos para eliminar clientes.")
        return redirect('clientes')

    cliente = get_object_or_404(Cliente, pk=pk)

    if cliente.venta_set.exists():
        messages.error(request, f'No se puede eliminar al cliente "{cliente}" porque cuenta con un historial de compras.')
        return redirect('clientes')

    if request.method == 'POST':
        nombre_cliente = str(cliente)
        cliente.delete()
        messages.success(request, f'Cliente "{nombre_cliente}" eliminado con éxito.')
        return redirect('clientes')

    return render(request, 'cliente_confirm_delete.html', {'cliente': cliente})


class HistorialVentaClienteListView(RolRequeridoMixin, generic.DetailView):
    """Historial de compras de un cliente."""
    roles_permitidos = ['Administrador']
    model = Cliente
    template_name = "historialCliente.html"
    context_object_name = "cliente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object
        cliente.ventas = cliente.venta_set.count()
        cliente.listaVentas = cliente.venta_set.all().order_by('-fecha')
        return context


class EmpleadoListView(RolRequeridoMixin, generic.ListView):
    """Catálogo de empleados."""
    roles_permitidos = ['Administrador']
    model = Empleado
    template_name = "empleados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for empleado in context['empleado_list']:
            resultado = empleado.venta_set.aggregate(totalVentas=Sum('total'))
            empleado.ventasTotal = resultado['totalVentas'] or 0
        return context


class EmpleadoCreateView(RolRequeridoMixin, generic.CreateView):
    """Registrar nuevo empleado."""
    roles_permitidos = ['Administrador']
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'empleado_form.html'
    success_url = reverse_lazy('empleados')

    def form_valid(self, form):
        messages.success(self.request, "Empleado registrado con éxito.")
        return super().form_valid(form)


class ProveedorListView(RolRequeridoMixin, generic.ListView):
    """Catálogo de proveedores."""
    roles_permitidos = ['Administrador']
    model = Proveedor
    template_name = "proveedores.html"


class ProveedorCreateView(RolRequeridoMixin, generic.CreateView):
    """Registrar nuevo proveedor."""
    roles_permitidos = ['Administrador']
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor_form.html'
    success_url = reverse_lazy('proveedores')

    def form_valid(self, form):
        messages.success(self.request, "Proveedor registrado con éxito.")
        return super().form_valid(form)


class ProveedorProductosListView(RolRequeridoMixin, generic.DetailView):
    """Lista de productos suministrados por un proveedor."""
    roles_permitidos = ['Administrador']
    model = Proveedor
    template_name = "proveedor_productos.html"
    context_object_name = "proveedor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor = self.object
        context['productos'] = (
            proveedor.ropa_set.prefetch_related('modelo_set')
            .all()
            .order_by('marca', 'descripcion')
        )
        return context


class ColoresListView(RolRequeridoMixin, generic.ListView):
    """Catálogo de colores y modelos registrados."""
    roles_permitidos = ['Administrador']
    model = Modelo
    template_name = "colores.html"
    context_object_name = "modelos"

    def get_queryset(self):
        return (
            Modelo.objects.select_related('ropa')
            .all()
            .order_by('ropa__marca', 'color', 'talla')
        )


class ModeloCreateView(RolRequeridoMixin, generic.CreateView):
    """Registrar nuevo color o variante de modelo."""
    roles_permitidos = ['Administrador']
    model = Modelo
    form_class = ModeloForm
    template_name = 'color_form.html'
    success_url = reverse_lazy('colores')

    def form_valid(self, form):
        messages.success(self.request, "Color y modelo registrado con éxito.")
        return super().form_valid(form)


class InventarioListView(RolRequeridoMixin, generic.ListView):
    """Consulta de inventario disponible por producto."""
    roles_permitidos = ['Almacenista']
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


@login_required
def actualizar_inventario_view(request, ropa_id):
    """Actualizar existencias de inventario por color."""
    if not request.user.is_superuser and not request.user.groups.filter(name='Almacenista').exists():
        messages.error(request, "Solo el personal de almacén puede actualizar el inventario.")
        return redirect('home')
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


class VentaListView(RolRequeridoMixin, generic.ListView):
    """Lista de ventas registradas."""
    roles_permitidos = ['Cajero', 'Administrador']
    model = Venta
    template_name = 'ventas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        return (
            Venta.objects.select_related('cliente', 'empleado')
            .prefetch_related('detalleventa_set__modelo__ropa')
            .all()
            .order_by('-fecha')
        )


class VentaDetailView(RolRequeridoMixin, generic.DetailView):
    """Detalle de una venta con sus articulos."""
    roles_permitidos = ['Cajero', 'Administrador']
    model = Venta
    template_name = 'venta_detalle.html'
    context_object_name = 'venta'

    def get_queryset(self):
        return (
            Venta.objects.select_related('cliente', 'empleado')
            .prefetch_related('detalleventa_set__modelo__ropa')
        )


@login_required
def registrar_venta_view(request):
    """Registrar venta y descontar existencias."""
    if not request.user.is_superuser and not request.user.groups.filter(name='Cajero').exists():
        messages.error(request, "Solo el personal de caja puede registrar ventas.")
        return redirect('ventas')

    # cliente default
    cliente_default = Cliente.objects.filter(nombre__iexact="Público general").first()
    if not cliente_default:
        cliente_default = Cliente.objects.filter(nombre__iexact="Público", apellidos__iexact="general").first()
    if not cliente_default:
        cliente_default = Cliente.objects.create(nombre="Público general", apellidos="")

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        empleado_id = request.POST.get('empleado_id')
        modelo_ids = request.POST.getlist('modelo_id')
        cantidades = request.POST.getlist('cantidad')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        if empleado_id:
            empleado = get_object_or_404(Empleado, pk=empleado_id)
        else:
            empleado = Empleado.objects.first()
            if not empleado:
                messages.error(request, "No hay ningún empleado registrado para atender la venta.")
                return redirect('registrar_venta')

        # validar que lleguen productos
        if not modelo_ids or not cantidades:
            messages.error(request, "Debe agregar al menos un producto a la venta.")
            return redirect('registrar_venta')

        items = [(m, c) for m, c in zip(modelo_ids, cantidades) if m and c]
        if not items:
            messages.error(request, "Debe agregar al menos un producto válido a la venta.")
            return redirect('registrar_venta')

        try:
            modelo_ids_int = [int(m) for m, _ in items]
            cantidades_int = [int(c) for _, c in items]
        except ValueError:
            messages.error(request, "Los valores de productos o cantidades no son válidos.")
            return redirect('registrar_venta')

        # revisar productos duplicados
        if len(modelo_ids_int) != len(set(modelo_ids_int)):
            messages.error(
                request,
                "No se permiten productos duplicados en la misma venta."
            )
            return redirect('registrar_venta')

        # revisar cantidades minimas
        if any(c <= 0 for c in cantidades_int):
            messages.error(request, "La cantidad a vender debe ser mayor a cero.")
            return redirect('registrar_venta')

        # verificar existencias y guardar venta
        try:
            with transaction.atomic():
                modelos = list(
                    Modelo.objects.select_for_update()
                    .select_related('ropa')
                    .filter(id__in=modelo_ids_int)
                )
                modelos_dict = {m.id: m for m in modelos}

                if len(modelos_dict) != len(modelo_ids_int):
                    messages.error(request, "Uno o más productos seleccionados no se encuentran en la base de datos.")
                    return redirect('registrar_venta')

                # validar que no falte stock
                errores_stock = []
                for mid, cant in zip(modelo_ids_int, cantidades_int):
                    modelo = modelos_dict[mid]
                    if cant > modelo.stock:
                        nombre_prenda = modelo.ropa.descripcion or modelo.ropa.marca
                        errores_stock.append(
                            f"{nombre_prenda} ({modelo.color}, Talla {modelo.get_talla_display()}): Stock = {modelo.stock}, solicitado = {cant}"
                        )

                if errores_stock:
                    messages.error(
                        request,
                        f"No hay inventario suficiente en: {'; '.join(errores_stock)}."
                    )
                    return redirect('registrar_venta')

                venta = Venta.objects.create(
                    cliente=cliente,
                    empleado=empleado,
                    total=Decimal('0.00'),
                    estado='Completada'
                )

                total_venta = Decimal('0.00')

                # guardar detalle y descontar stock
                for mid, cant in zip(modelo_ids_int, cantidades_int):
                    modelo = modelos_dict[mid]
                    subtotal = modelo.precio * cant
                    total_venta += subtotal

                    DetalleVenta.objects.create(
                        venta=venta,
                        modelo=modelo,
                        precio=modelo.precio,
                        unidades=cant,
                        subtotal=subtotal
                    )

                    modelo.stock -= cant
                    modelo.save(update_fields=['stock'])

                venta.total = total_venta
                venta.save(update_fields=['total'])

                messages.success(
                    request,
                    f"Venta #{venta.id} registrada con éxito. Total: ${total_venta:.2f}."
                )
                return redirect('venta_detalle', pk=venta.id)

        except Exception as e:
            messages.error(request, f"Error al procesar la venta: {str(e)}")
            return redirect('registrar_venta')

    # datos para cargar el formulario
    clientes = Cliente.objects.all().order_by('nombre', 'apellidos')
    empleados = Empleado.objects.all().order_by('nombre', 'apellidos')

    modelos_disponibles = (
        Modelo.objects.select_related('ropa')
        .filter(stock__gt=0)
        .order_by('ropa__marca', 'ropa__descripcion', 'color', 'talla')
    )

    catalogo = {}
    ropas_disponibles = []
    ropas_ids_vistas = set()

    for m in modelos_disponibles:
        r = m.ropa
        r_id = r.id
        if r_id not in catalogo:
            catalogo[r_id] = {
                'id': r_id,
                'nombre': r.descripcion or r.marca,
                'marca': r.marca,
                'colores': {}
            }
        if r_id not in ropas_ids_vistas:
            ropas_ids_vistas.add(r_id)
            ropas_disponibles.append(r)

        color = m.color
        if color not in catalogo[r_id]['colores']:
            catalogo[r_id]['colores'][color] = []

        catalogo[r_id]['colores'][color].append({
            'modelo_id': m.id,
            'talla_codigo': m.talla,
            'talla_nombre': m.get_talla_display(),
            'stock': m.stock,
            'precio': float(m.precio),
        })

    return render(request, 'venta_registrar.html', {
        'clientes': clientes,
        'cliente_default': cliente_default,
        'empleados': empleados,
        'ropas_disponibles': ropas_disponibles,
        'catalogo': catalogo,
        'hay_inventario': len(ropas_disponibles) > 0,
    })



