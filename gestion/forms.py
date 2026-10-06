from django import forms
from .models import Ropa, Cliente, Proveedor, Modelo


class RopaForm(forms.ModelForm):
    class Meta:
        model = Ropa
        fields = ['marca', 'descripcion', 'proveedor']
        labels = {
            'marca': 'Marca',
            'descripcion': 'Descripción',
            'proveedor': 'Proveedor',
        }
        widgets = {
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca de la prenda',
                'required': True,
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción detallada de la prenda',
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellidos']
        labels = {
            'nombre': 'Nombre(s)',
            'apellidos': 'Apellidos',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre(s) del cliente',
                'required': True,
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del cliente',
                'required': True,
            }),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono']
        labels = {
            'nombre': 'Nombre del Proveedor',
            'direccion': 'Dirección',
            'telefono': 'Teléfono de Contacto',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre comercial o razón social',
                'required': True,
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle, número, colonia, ciudad',
                'required': True,
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono a 10 dígitos',
                'required': True,
            }),
        }


class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['ropa', 'color', 'talla', 'precio', 'stock']
        labels = {
            'ropa': 'Prenda',
            'color': 'Color',
            'talla': 'Talla',
            'precio': 'Precio Unitario ($)',
            'stock': 'Stock Inicial',
        }
        widgets = {
            'ropa': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Negro, Azul, Blanco',
                'required': True,
            }),
            'talla': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'required': True,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
                'required': True,
            }),
        }
