from django.contrib.auth.backends import ModelBackend
from core.models import Usuario

class MatriculaAuthBackend(ModelBackend):
    """
    Autenticación personalizada usando 'matricula' como identificador.
    Compatible con Django admin y login API.
    """
    def authenticate(self, request, matricula=None, password=None, **kwargs):
        if matricula is None or password is None:
            return None
        try:
            user = Usuario.objects.get(matricula=matricula)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
