from django.contrib import admin
from .models import Usuario,Alumno, Calificacion, Curso, Inscripcion

admin.site.register(Usuario)  
admin.site.register(Alumno)
admin.site.register(Calificacion)
admin.site.register(Curso)
admin.site.register(Inscripcion)
