from django.contrib import admin
from .models import Cliente, Empleado, Proveedor, Ropa, Modelo, Venta, DetalleVenta

admin.site.register(Cliente)
admin.site.register(Empleado)
admin.site.register(Proveedor)
admin.site.register(Ropa)
admin.site.register(Modelo)
admin.site.register(Venta)
admin.site.register(DetalleVenta)