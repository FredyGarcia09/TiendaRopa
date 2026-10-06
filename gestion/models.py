from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    puesto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.puesto}"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Ropa(models.Model):
    descripcion = models.TextField(null=True, blank=True)
    marca = models.CharField(max_length=100)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        if self.descripcion:
            return f"{self.marca} - {self.descripcion}"
        return self.marca

    @property
    def nombre(self):
        """Compatibilidad: devuelve la descripción o marca de la prenda."""
        return self.descripcion or self.marca

    @property
    def tallas_disponibles(self):
        """Devuelve las tallas de los modelos registrados."""
        tallas = list(self.modelo_set.values_list('talla', flat=True).distinct())
        return ", ".join(tallas) if tallas else "Sin tallas"

    @property
    def colores_disponibles(self):
        """Devuelve los colores de los modelos registrados."""
        colores = list(self.modelo_set.values_list('color', flat=True).distinct())
        return ", ".join(colores) if colores else "Sin colores"

    @property
    def stock_total(self):
        """Calcula el stock total disponible entre todos los modelos."""
        return sum(m.stock for m in self.modelo_set.all())

    @property
    def precios_display(self):
        """Formatea el rango de precios o precio unitario."""
        precios = list(self.modelo_set.values_list('precio', flat=True).distinct())
        if not precios:
            return "N/A"
        if len(precios) == 1:
            return f"${precios[0]:.2f}"
        return f"${min(precios):.2f} - ${max(precios):.2f}"

    @property
    def precio(self):
        """Compatibilidad con plantillas que acceden a ropa.precio."""
        return self.precios_display

    @property
    def talla(self):
        """Compatibilidad con plantillas que acceden a ropa.talla."""
        return self.tallas_disponibles

    @property
    def color(self):
        """Compatibilidad con plantillas que acceden a ropa.color."""
        return self.colores_disponibles

class Modelo(models.Model):
    TALLAS_CHOICES = [
        ('U', 'Unitalla'),
        ('XS', 'Extra Chica'),
        ('S', 'Chica'),
        ('M', 'Mediana'),
        ('L', 'Grande'),
        ('XL', 'Extra Grande'),
    ]
    talla = models.CharField(max_length=2, choices=TALLAS_CHOICES)
    color = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    ropa = models.ForeignKey(Ropa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ropa.marca} - {self.color} ({self.talla})"

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('En progreso', 'En progreso'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='En progreso')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)

    def __str__(self):
        return f"Venta {self.id} - {self.estado}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle de Venta {self.venta.id}"