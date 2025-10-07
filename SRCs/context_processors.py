from .models import Usuario

def perfil_usuario(request):
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(user=request.user)
            return {'perfil': usuario.perfil}
        except Usuario.DoesNotExist:
            return {'perfil': None}
    return {'perfil': None}
