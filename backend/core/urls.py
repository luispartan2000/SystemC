from django.urls import path
from .views import (

    RegisterUserView, LoginView, LogoutView, WhoAmIView, ChangePasswordView,
    RecoveryPasswordView, csrf,

    AlumnoCalificacionesView,
    AlumnoCursosView, AlumnoInscribirseView, AlumnoSubirVoucherView,

    PendingAlumnosStafView, ValidarAlumnoStafView,
    StafListaInscripcionesView, StafValidarPagoView,

    AdminCreateStaffOrAdminView, AdminDeleteUserView, AdminUsersListView,
    AdminCursosView,AdminCursoDetailView,
)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('whoami/', WhoAmIView.as_view(), name='whoami'),
    path('cambiar-contrasena/', ChangePasswordView.as_view(), name='cambiar-contrasena'),
    path('recuperar-password/', RecoveryPasswordView.as_view(), name='recuperar-password'),
    path('csrf/', csrf, name='csrf'),

  
    path('alumno/calificaciones/', AlumnoCalificacionesView.as_view(), name='alumno-calificaciones'),
    path('alumno/cursos/', AlumnoCursosView.as_view(), name='alumno-cursos'),
    path('alumno/inscribirse/', AlumnoInscribirseView.as_view(), name='alumno-inscribirse'),
    path('alumno/voucher/<int:inscripcion_id>/', AlumnoSubirVoucherView.as_view(), name='alumno-subir-voucher'),

    path('staf/alumnos-pendientes/', PendingAlumnosStafView.as_view(), name='staf-alumnos-pendientes'),
    path('staf/validar-alumno/', ValidarAlumnoStafView.as_view(), name='staf-validar-alumno'),
    path('staf/inscripciones/', StafListaInscripcionesView.as_view(), name='staf-lista-inscripciones'),
    path('staf/validar-pago/<int:inscripcion_id>/', StafValidarPagoView.as_view(), name='staf-validar-pago'),

    path('admin/create-user/', AdminCreateStaffOrAdminView.as_view(), name='admin-create-user'),
    path('admin/users/', AdminUsersListView.as_view(), name='admin-users-list'),
    path('admin/delete-user/', AdminDeleteUserView.as_view(), name='admin-delete-user'),
    path('admin/cursos/', AdminCursosView.as_view(), name='admin-cursos'),
    path('admin/cursos/<int:curso_id>/', AdminCursoDetailView.as_view(), name='admin-curso-detail'),
]
