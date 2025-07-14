from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from SRCs.models import Usuario

@receiver(post_migrate)
def criar_grupos_com_permissoes(sender, **kwargs):
    # Verifica se as permissões já existem
    permissoes_por_grupo = {
        'admin': [
            'cadastrar_usuario', 'editar_usuario',
            'cadastrar_unidade', 'editar_unidade',
            'cadastrar_envio', 'consultar_rateio',
            'consultar_dashboard', 'acompanhar_envio'
        ],
        'analista': [
            'cadastrar_envio', 'consultar_rateio',
            'acompanhar_envio', 'consultar_dashboard'
        ],
        'basic': [
            'cadastrar_envio', 'consultar_rateio', 'acompanhar_envio'
        ],
        'supervisor': [
            'consultar_rateio', 'acompanhar_envio', 'consultar_dashboard'
        ]
    }

    content_type = ContentType.objects.get(app_label='SRCs', model='usuario')

    for grupo_nome, permissoes in permissoes_por_grupo.items():
        grupo, _ = Group.objects.get_or_create(name=grupo_nome)
        grupo.permissions.clear()
        for codename in permissoes:
            try:
                perm = Permission.objects.get(codename=codename, content_type=content_type)
                grupo.permissions.add(perm)
            except Permission.DoesNotExist:
                print(f'Permissão {codename} não encontrada')

@receiver(post_save, sender=Usuario)
def atribuir_grupo_usuario(sender, instance, created, **kwargs):
    if instance.user and instance.perfil:
        grupo_nome = instance.perfil.lower()
        grupo = Group.objects.get(name=grupo_nome)
        instance.user.groups.clear()
        instance.user.groups.add(grupo)
