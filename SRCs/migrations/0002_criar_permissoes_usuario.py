from django.db import migrations

def criar_permissoes(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Usuario = apps.get_model('SRCs', 'Usuario')
    
    content_type = ContentType.objects.get_for_model(Usuario)

    permissoes = [
        ('cadastrar_usuario', 'Cadastrar Usuário'),
        ('editar_usuario', 'Editar Usuário'),
        ('cadastrar_unidade', 'Cadastrar Unidade'),
        ('editar_unidade', 'Editar Unidade'),
        ('cadastrar_envio', 'Cadastrar Envio'),
        ('consultar_rateio', 'Consultar Rateio'),
        ('consultar_dashboard', 'Consultar Dashboard'),
        ('acompanhar_envio', 'Acompanhar Envio'),
    ]

    for codename, name in permissoes:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )

class Migration(migrations.Migration):

    dependencies = [
        ('SRCs', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(criar_permissoes),
    ]
