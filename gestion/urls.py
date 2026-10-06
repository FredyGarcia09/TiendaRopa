"""
URL configuration for TiendaRopa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('home/', views.HomeView.as_view(), name='home_alt'),
    path('ropa/', views.RopaListView.as_view(), name='ropa'),
    path('clientes/', views.ClienteListView.as_view(), name='clientes'),
    path('clientes/<int:pk>/',views.HistorialVentaClienteListView.as_view(),name="historialCliente"),
    path('inventario/', views.InventarioListView.as_view(), name='inventario_lista'),
    path('empleados/', views.EmpleadoListView.as_view(), name='empleados'),
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedores'),
    path('inventario/<int:ropa_id>/', views.actualizar_inventario_view, name='actualizar_inventario'),
    path('ventas/', views.VentaListView.as_view(), name='ventas'),
    path('ventas/nueva/', views.registrar_venta_view, name='registrar_venta'),
    path('ventas/<int:pk>/', views.VentaDetailView.as_view(), name='venta_detalle'),
]

