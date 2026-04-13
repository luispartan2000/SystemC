from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import secrets

from core.models import Usuario, Alumno, Calificacion, Curso, Inscripcion



def _is_staf(user):
    return user.is_authenticated and (getattr(user, "tipo", "") == "STAF" or user.is_superuser)


def _is_admin(user):
    return user.is_authenticated and (getattr(user, "tipo", "") == "ADMIN" or user.is_superuser)



@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        files = request.FILES

        matricula = data.get('matricula')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        telefono = data.get('telefono', '')
        password = data.get('password')
        tipo = data.get('tipo', 'ALUMNO')
        area = data.get('area', '')
        identidad_file = files.get('identidad')

        if Usuario.objects.filter(matricula=matricula).exists():
            return Response({"error": "Ya existe un usuario con esa matrícula."}, status=400)
        if Usuario.objects.filter(email=email).exists():
            return Response({"error": "Ya existe un usuario con ese correo."}, status=400)

        usuario = Usuario.objects.create_user(
            matricula=matricula,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            tipo=tipo,
        )

        Alumno.objects.create(
            usuario=usuario,
            telefono=telefono,
            activo=False,
            area=area,
            identidad=identidad_file
        )

        try:
            send_mail(
                subject="Tu cuenta está en proceso de validación",
                message=f"Hola {first_name},\n\nGracias por registrarte. Tu cuenta está en validación por el staff.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"success": "Usuario registrado. Tu cuenta está en validación."}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        matricula = request.data.get('matricula')
        password = request.data.get('password')
        user = authenticate(matricula=matricula, password=password)
        if user is not None:
            if getattr(user, "tipo", "") == "ALUMNO" and hasattr(user, "alumno") and not user.alumno.activo:
                return Response({'error': 'Tu cuenta está en validación. Intenta más tarde.'}, status=403)
            login(request, user)
            return Response({
                'success': 'Login exitoso',
                'tipo': "ADMIN" if user.is_superuser else user.tipo,
                'matricula': user.matricula,
                'must_change_password': getattr(user, 'must_change_password', False)
            })
        else:
            return Response({'error': 'Credenciales inválidas'}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'success': 'Sesión cerrada correctamente'})


@method_decorator(csrf_exempt, name='dispatch')
class RecoveryPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'El correo es obligatorio.'}, status=400)
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({'error': 'No existe una cuenta con ese correo.'}, status=404)

        temp_password = secrets.token_urlsafe(8)
        user.set_password(temp_password)
        user.must_change_password = True
        user.save()

        send_mail(
            subject="Recuperación de contraseña",
            message=f"Hola\nTu contraseña temporal es: {temp_password}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({'success': 'Se ha enviado una contraseña temporal a tu correo.'})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        actual, nueva, confirmar = data.get('actual'), data.get('nueva'), data.get('confirmar')

        if not all([actual, nueva, confirmar]):
            return Response({"error": "Todos los campos son obligatorios."}, status=400)
        if not user.check_password(actual):
            return Response({"error": "La contraseña actual es incorrecta."}, status=400)
        if nueva != confirmar:
            return Response({"error": "La nueva contraseña no coincide."}, status=400)
        if actual == nueva:
            return Response({"error": "La nueva contraseña debe ser diferente."}, status=400)

        user.set_password(nueva)
        user.must_change_password = False
        user.save()
        update_session_auth_hash(request, user)
        return Response({"success": "Contraseña cambiada correctamente."})


class WhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "matricula": user.matricula,
            "tipo": "ADMIN" if user.is_superuser else user.tipo,
            "nombre": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "must_change_password": bool(getattr(user, "must_change_password", False)),
        })


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({'ok': True})


class AlumnoCalificacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, "alumno"):
            return Response({"error": "No eres un alumno"}, status=403)
        alumno = user.alumno
        inscripciones = alumno.inscripcion_set.all()
        calificaciones_list = []
        for inscripcion in inscripciones:
            califs = inscripcion.calificacion_set.all().values('materia', 'calificacion', 'fecha')
            for c in califs:
                calificaciones_list.append(c)
        return Response({'calificaciones': calificaciones_list})


class PendingAlumnosStafView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_staf(request.user):
            return Response({"error": "No autorizado"}, status=403)

        pendientes = Alumno.objects.filter(activo=False).select_related('usuario')
        data = [{
            "id": a.id,
            "matricula": a.usuario.matricula,
            "nombre": f"{a.usuario.first_name} {a.usuario.last_name}",
            "area": a.area or "",
            "identidad_url": request.build_absolute_uri(a.identidad.url) if a.identidad else None,
        } for a in pendientes]
        return Response({"alumnos": data})


@method_decorator(csrf_exempt, name='dispatch')
class ValidarAlumnoStafView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_staf(request.user):
            return Response({"error": "No autorizado"}, status=403)

        alumno_id = request.data.get("alumno_id")
        alumno = get_object_or_404(Alumno.objects.select_related('usuario'), id=alumno_id)

        if alumno.activo:
            return Response({"success": "El alumno ya estaba validado."})

        alumno.activo = True
        alumno.save()
        staf_nombre = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.matricula

        send_mail(
            subject="¡Tu cuenta ha sido validada!",
            message=f"Hola {alumno.usuario.first_name},\n\nTu cuenta ha sido validada por: {staf_nombre}.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[alumno.usuario.email],
            fail_silently=True,
        )

        return Response({"success": "Alumno validado correctamente."})



@method_decorator(csrf_exempt, name='dispatch')
class AdminCreateStaffOrAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        data = request.data
        matricula, first_name, last_name, email = data.get('matricula'), data.get('first_name'), data.get('last_name'), data.get('email')
        tipo = data.get('tipo', 'STAF')

        if not all([matricula, first_name, last_name, email]):
            return Response({"error": "Todos los campos son obligatorios."}, status=400)
        if tipo not in ('STAF', 'ADMIN'):
            return Response({"error": "El tipo de usuario debe ser STAF o ADMIN."}, status=400)

        if Usuario.objects.filter(matricula=matricula).exists():
            return Response({"error": "Ya existe un usuario con esa matrícula."}, status=400)
        if Usuario.objects.filter(email=email).exists():
            return Response({"error": "Ya existe un usuario con ese correo."}, status=400)

        temp_password = secrets.token_urlsafe(8)
        usuario = Usuario.objects.create_user(
            matricula=matricula,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=temp_password,
            tipo=tipo,
        )
        usuario.must_change_password = True
        usuario.save()

        send_mail(
            subject="Tu cuenta fue creada por la administración",
            message=f"Hola {first_name}, se creó tu cuenta con matrícula {matricula} y contraseña temporal {temp_password}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response({"success": "Usuario creado y activado."}, status=201)


class AdminUsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        staff_qs = Usuario.objects.filter(tipo__in=['STAF', 'ADMIN']).order_by('tipo', 'matricula')
        alumnos_qs = Alumno.objects.select_related('usuario').order_by('usuario__matricula')

        staff = [{
            "matricula": u.matricula,
            "nombre": f"{u.first_name} {u.last_name}".strip(),
            "email": u.email,
            "tipo": u.tipo,
            "is_superuser": bool(u.is_superuser),
        } for u in staff_qs]

        alumnos = [{
            "matricula": a.usuario.matricula,
            "nombre": f"{a.usuario.first_name} {a.usuario.last_name}".strip(),
            "email": a.usuario.email,
            "activo": bool(a.activo),
            "area": a.area or "",
        } for a in alumnos_qs]

        return Response({"staff": staff, "alumnos": alumnos})


@method_decorator(csrf_exempt, name='dispatch')
class AdminDeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        matricula = request.data.get('matricula')
        usuario = get_object_or_404(Usuario, matricula=matricula)

        if usuario.id == request.user.id:
            return Response({"error": "No puedes eliminar tu propia cuenta."}, status=400)
        if usuario.is_superuser and not request.user.is_superuser:
            return Response({"error": "No puedes eliminar un superusuario."}, status=403)

        if hasattr(usuario, 'alumno'):
            usuario.alumno.delete()

        usuario.delete()
        return Response({"success": "Usuario eliminado correctamente."})



class AdminCursosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        cursos = Curso.objects.all().order_by("nombre", "nivel")
        data = [{
            "id": c.id,
            "nombre": c.nombre,
            "nivel": c.nivel,
            "profesor": c.profesor,
            "cupo_minimo": c.cupo_minimo,
            "cupo_maximo": c.cupo_maximo,
            "fecha_limite": c.fecha_limite,
            "activo": c.activo
        } for c in cursos]
        return Response({"cursos": data})

    def post(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        data = request.data
        curso = Curso.objects.create(
            nombre=data.get("nombre"),
            nivel=data.get("nivel"),
            profesor=data.get("profesor"),
            cupo_minimo=data.get("cupo_minimo", 1),
            cupo_maximo=data.get("cupo_maximo", 30),
            fecha_limite=data.get("fecha_limite"),
            activo=True
        )
        return Response({"success": "Curso creado", "id": curso.id}, status=201)
    
class AdminCursoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, curso_id):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        curso = get_object_or_404(Curso, id=curso_id)
        data = request.data

        curso.nombre = data.get("nombre", curso.nombre)
        curso.nivel = data.get("nivel", curso.nivel)
        curso.profesor = data.get("profesor", curso.profesor)
        curso.cupo_minimo = data.get("cupo_minimo", curso.cupo_minimo)
        curso.cupo_maximo = data.get("cupo_maximo", curso.cupo_maximo)
        curso.fecha_limite = data.get("fecha_limite", curso.fecha_limite)
        curso.activo = data.get("activo", curso.activo)
        curso.save()

        return Response({"success": "Curso actualizado"}, status=200)

    def delete(self, request, curso_id):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        curso = get_object_or_404(Curso, id=curso_id)
        curso.delete()
        return Response({"success": "Curso eliminado"}, status=200)



class AdminInscripcionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)

        inscripciones = Inscripcion.objects.select_related("alumno__usuario", "curso").all()
        data = []
        for ins in inscripciones:
            data.append({
                "id": ins.id,
                "matricula": ins.alumno.usuario.matricula,
                "alumno": f"{ins.alumno.usuario.first_name} {ins.alumno.usuario.last_name}",
                "curso": ins.curso.nombre,
                "nivel": ins.curso.nivel,
                "aprobado": ins.aprobado,
            })
        return Response({"inscripciones": data}, status=200)


class AdminAprobarInscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, inscripcion_id):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)
        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
        inscripcion.aprobado = True
        inscripcion.save()
        return Response({"success": "Inscripción aprobada"}, status=200)


class AdminRevocarInscripcionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, inscripcion_id):
        if not _is_admin(request.user):
            return Response({"error": "No autorizado"}, status=403)
        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
        inscripcion.aprobado = False
        inscripcion.save()
        return Response({"success": "Inscripción revocada"}, status=200)



class AlumnoCursosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.tipo != "ALUMNO":
            return Response({"error": "No autorizado"}, status=403)

        alumno = request.user.alumno
        cursos = Curso.objects.filter(activo=True).order_by("nivel")

        data = []
        for curso in cursos:
            inscripcion = Inscripcion.objects.filter(alumno=alumno, curso=curso).first()
            if inscripcion:
                estado = inscripcion.estado_pago
                inscripcion_id = inscripcion.id
            else:
                estado = "DISPONIBLE"
                inscripcion_id = None

            data.append({
                "id": curso.id,
                "nombre": curso.nombre,
                "nivel": curso.nivel,
                "profesor": curso.profesor,
                "cupo_maximo": curso.cupo_maximo,
                "fecha_limite": curso.fecha_limite.isoformat(),
                "estado": estado,
                "inscritos": Inscripcion.objects.filter(curso=curso).count(),
                "inscripcion_id": inscripcion_id,   # 👈 agregado
            })

        return Response({"cursos": data}, status=200)



class AlumnoInscribirseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.tipo != "ALUMNO":
            return Response({"error": "No autorizado"}, status=403)

        curso_id = request.data.get("curso_id")
        curso = get_object_or_404(Curso, id=curso_id)

        alumno = request.user.alumno
        inscripcion, created = Inscripcion.objects.get_or_create(alumno=alumno, curso=curso)

        if not created:
            return Response({"error": "Ya estás inscrito en este curso"}, status=400)

   
        inscripcion.estado_pago = "EN_PROCESO"
        inscripcion.save()

   
        try:
            send_mail(
                subject=f"Instrucciones de pago - {curso.nombre} Nivel {curso.nivel}",
                message=(
                    f"Hola {alumno.usuario.first_name},\n\n"
                    f"Te has inscrito al curso {curso.nombre} (nivel {curso.nivel}).\n"
                    "Por favor realiza el pago correspondiente:\n\n"
                    "Banco: XXXX\nCuenta: 123456789\nMonto: $$$\n"
                    f"Fecha límite de pago: {curso.fecha_limite}\n\n"
                    "Luego deberás subir tu comprobante en formato JPG/PNG en el sistema.\n\n"
                    "Atentamente,\nCoordinación de Cursos"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[alumno.usuario.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"success": "Inscripción realizada. Revisa tu correo con las instrucciones de pago."}, status=201)



class RevisarVoucherView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, inscripcion_id):
        if not _is_staf(request.user):
            return Response({"error": "No autorizado"}, status=403)

        insc = get_object_or_404(Inscripcion, id=inscripcion_id)
        data = request.data
        estado = data.get("estado_pago")
        monto_faltante = data.get("monto_faltante", 0)

        if estado not in dict(Inscripcion.ESTADOS_PAGO):
            return Response({"error": "Estado inválido"}, status=400)

        insc.estado_pago = estado
        insc.monto_faltante = monto_faltante
        insc.revisado_por = request.user
        insc.save()

        firma = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.matricula
        send_mail(
            subject=f"Actualización de pago - {insc.curso.nombre} Nivel {insc.curso.nivel}",
            message=f"Hola {insc.alumno.usuario.first_name}, tu estado de pago ahora es {insc.get_estado_pago_display()}.\nRevisado por: {firma}\nMonto faltante: {insc.monto_faltante}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[insc.alumno.usuario.email],
            fail_silently=True,
        )
        return Response({"success": "Estado de pago actualizado"})

@method_decorator(csrf_exempt, name='dispatch')
class AlumnoSubirVoucherView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, inscripcion_id):
        if request.user.tipo != "ALUMNO":
            return Response({"error": "No autorizado"}, status=403)

        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id, alumno=request.user.alumno)

        archivo = request.FILES.get("voucher")
        if not archivo:
            return Response({"error": "Debes subir un archivo"}, status=400)

        inscripcion.voucher = archivo
        inscripcion.estado_pago = "EN_REVISION"  # cambia estado a revisión
        inscripcion.save()

        return Response({"success": "Voucher subido. Será revisado por el staff."}, status=200)

class StafListaInscripcionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_staf(request.user):
            return Response({"error": "No autorizado"}, status=403)

        inscripciones = (
            Inscripcion.objects
            .select_related("alumno__usuario", "curso")
            .all()
            .order_by("curso__nombre", "curso__nivel")
        )

        data = []
        for i in inscripciones:
            data.append({
                "id": i.id,
                "alumno": {
                    "matricula": i.alumno.usuario.matricula,
                    "nombre": f"{i.alumno.usuario.first_name} {i.alumno.usuario.last_name}",
                    "email": i.alumno.usuario.email,
                },
                "curso": {
                    "id": i.curso.id,
                    "nombre": i.curso.nombre,
                    "nivel": i.curso.nivel,
                },
                "estado_pago": i.estado_pago,
                "monto_faltante": i.monto_faltante,
                "voucher_url": request.build_absolute_uri(i.voucher.url) if i.voucher else None,
            })

        return Response({"inscripciones": data}, status=200)
    
class StafValidarPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, inscripcion_id):
        if not _is_staf(request.user):
            return Response({"error": "No autorizado"}, status=403)

        inscripcion = get_object_or_404(Inscripcion, id=inscripcion_id)
        data = request.data
        estado = data.get("estado_pago") 
        monto_faltante = data.get("monto_faltante", 0)

        if estado not in ["PAGADO", "FALTANTE"]:
            return Response({"error": "Estado inválido, debe ser PAGADO o FALTANTE"}, status=400)

        inscripcion.estado_pago = estado
        inscripcion.monto_faltante = monto_faltante if estado == "FALTANTE" else 0
        inscripcion.revisado_por = request.user
        inscripcion.save()

        firma = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.matricula

        if estado == "PAGADO":
            mensaje = (
                f"Hola {inscripcion.alumno.usuario.first_name},\n\n"
                f"Tu pago para el curso {inscripcion.curso.nombre} (nivel {inscripcion.curso.nivel}) "
                f"ha sido confirmado como COMPLETO.\n\n"
                f"Revisado por: {firma}\n\n"
                "¡Bienvenido al curso!"
            )
        else:  
            mensaje = (
                f"Hola {inscripcion.alumno.usuario.first_name},\n\n"
                f"Al revisar tu pago para el curso {inscripcion.curso.nombre} (nivel {inscripcion.curso.nivel}), "
                f"se detectó un FALTANTE de ${monto_faltante}.\n\n"
                f"Por favor completa el pago antes de la fecha límite ({inscripcion.curso.fecha_limite}) "
                f"para asegurar tu lugar en el curso.\n\n"
                f"Revisado por: {firma}"
            )

        try:
            send_mail(
                subject=f"Estado de tu pago - {inscripcion.curso.nombre} Nivel {inscripcion.curso.nivel}",
                message=mensaje,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[inscripcion.alumno.usuario.email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({"success": f"Estado de pago actualizado a {estado}"}, status=200)