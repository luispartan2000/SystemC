from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# -------------------------------
# Usuario personalizado
# -------------------------------
class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, matricula, password=None, **extra_fields):
        if not matricula:
            raise ValueError('El campo matrícula es obligatorio')
        user = self.model(matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricula, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(matricula, password, **extra_fields)


class Usuario(AbstractUser):
    TIPOS = (
        ('ALUMNO', 'Alumno'),
        ('PROFESOR', 'Profesor'),  # 👈 nuevo rol
        ('STAF', 'Staff'),
        ('ADMIN', 'Admin')
    )
    matricula = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default='ALUMNO')
    must_change_password = models.BooleanField(default=False)

    username = None
    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.matricula} ({self.get_tipo_display()})"


# -------------------------------
# Profesor
# -------------------------------
def profesor_documento_upload_to(instance, filename):
    return f'profesores/{instance.usuario.matricula}/documentos/{filename}'


class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    documentos = models.FileField(
        upload_to=profesor_documento_upload_to,
        blank=True,
        null=True,
        help_text="Documentos subidos por el profesor"
    )

    def __str__(self):
        return f"Profesor: {self.usuario.first_name} {self.usuario.last_name} ({self.usuario.matricula})"


# -------------------------------
# Curso
# -------------------------------
def curso_horario_upload_to(instance, filename):
    return f'cursos/horarios/{instance.nombre}_nivel{instance.nivel}/{filename}'


class Curso(models.Model):
    nombre = models.CharField(max_length=50)
    nivel = models.PositiveIntegerField(default=1)  # CCNA1, CCNA2, etc.
    profesor = models.ForeignKey(   # 👈 ahora es relación con Profesor
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cursos"
    )
    imagen_horario = models.FileField(upload_to=curso_horario_upload_to, blank=True, null=True)

    cupo_minimo = models.PositiveIntegerField(default=1)
    cupo_maximo = models.PositiveIntegerField(default=30)
    fecha_limite = models.DateField()

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} Nivel {self.nivel}"


# -------------------------------
# Alumno
# -------------------------------
def alumno_identidad_upload_to(instance, filename):
    return f'identidad/{instance.usuario.matricula}/{filename}'


class Alumno(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    area = models.CharField(max_length=100, blank=True)
    identidad = models.FileField(
        upload_to=alumno_identidad_upload_to, blank=True, null=True
    )
    cursos = models.ManyToManyField(Curso, through='Inscripcion')

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.usuario.matricula}) - {estado}"


# -------------------------------
# Inscripción
# -------------------------------
def voucher_upload_to(instance, filename):
    return f'vouchers/{instance.alumno.usuario.matricula}/{instance.curso.nombre}_nivel{instance.curso.nivel}/{filename}'


class Inscripcion(models.Model):
    ESTADOS_PAGO = (
        ("pendiente", "Pendiente"),
        ("en_proceso", "En proceso"),
        ("faltante", "Faltante"),
        ("pagado", "Pagado"),
    )

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    aprobado = models.BooleanField(default=False)
    certificado = models.FileField(upload_to='certificados/', blank=True, null=True)

    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default="pendiente")
    voucher = models.FileField(upload_to=voucher_upload_to, blank=True, null=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_faltante = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    revisado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="inscripciones_revisadas"
    )

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alumno} en {self.curso} [{self.estado_pago}]"


# -------------------------------
# Calificación
# -------------------------------
def calificacion_file_upload_to(instance, filename):
    return f'calificaciones/{instance.inscripcion.alumno.usuario.matricula}/{filename}'


class Calificacion(models.Model):
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    materia = models.CharField(max_length=100)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2)
    fecha = models.DateField()
    archivo = models.FileField(upload_to=calificacion_file_upload_to, blank=True, null=True)

    def __str__(self):
        return f"{self.materia} - {self.calificacion} ({self.inscripcion.alumno.usuario.matricula})"
