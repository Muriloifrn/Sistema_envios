# Generated by Django 5.2.1 on 2025-06-08 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Envio',
            fields=[
                ('etiqueta', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='ETIQUETA')),
                ('numero_autorizacao', models.CharField(max_length=20, verbose_name='NÚMERO DE AUTORIZAÇÃO')),
                ('data_solicitacao', models.DateField(verbose_name='DATA DA SOLICITAÇÃO')),
                ('status_envio', models.CharField(blank=True, max_length=9, null=True)),
            ],
            options={
                'verbose_name': 'envio',
                'verbose_name_plural': 'envios',
                'db_table': 'envio',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('conteudo', models.CharField(max_length=100, verbose_name='CONTEÚDO')),
                ('quantidade', models.IntegerField(verbose_name='QUANTIDADE')),
            ],
            options={
                'db_table': 'produto',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Rateio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fatura', models.CharField(blank=True, max_length=20, null=True, verbose_name='FATURA')),
                ('titular_cartao', models.CharField(blank=True, max_length=100, null=True, verbose_name='TITULAR CARTÃO')),
                ('servico', models.CharField(blank=True, max_length=10, null=True, verbose_name='SERVIÇO')),
                ('data_postagem', models.DateField(blank=True, null=True, verbose_name='DATA DA POSTAGEM')),
                ('unidade_postagem', models.CharField(blank=True, max_length=100, null=True, verbose_name='UNIDADE POSTAGEM')),
                ('valor_declarado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='VALOR DECLARADO')),
                ('valor_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='VALOR UNITÁRIO')),
                ('quantidade', models.IntegerField(blank=True, null=True, verbose_name='QUANTIDADE')),
                ('peso', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='PESO')),
                ('servico_adicionais', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='SERVIÇOS ADICIONAIS')),
                ('desconto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='DESCONTO')),
                ('valor_liquido', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='VALOR LIQUIDO')),
            ],
            options={
                'verbose_name': 'rateio',
                'verbose_name_plural': 'rateios',
                'db_table': 'rateio',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Unidade',
            fields=[
                ('cnpj', models.CharField(db_column='CNPJ', max_length=18, primary_key=True, serialize=False, verbose_name='CNPJ')),
                ('centro_custo', models.IntegerField(verbose_name='CENTRO DE CUSTO')),
                ('cep', models.CharField(max_length=10, verbose_name='CEP')),
                ('bairro', models.CharField(max_length=50, verbose_name='BAIRRO')),
                ('rua', models.CharField(max_length=100, verbose_name='RUA')),
                ('numero', models.CharField(max_length=10, verbose_name='NÚMERO')),
                ('shopping', models.CharField(blank=True, max_length=100, null=True, verbose_name='SHOPPING')),
                ('cidade', models.CharField(max_length=50, verbose_name='CIDADE')),
                ('estado', models.CharField(blank=True, max_length=2, null=True, verbose_name='ESTADO')),
                ('regional', models.CharField(blank=True, max_length=2, null=True, verbose_name='REGIONAL')),
                ('numero_unidade', models.CharField(blank=True, max_length=10, null=True, verbose_name='NUMERO DA UNIDADE')),
                ('empresa', models.CharField(blank=True, max_length=50, null=True, verbose_name='EMPRESA')),
            ],
            options={
                'verbose_name': 'unidade',
                'verbose_name_plural': 'unidades',
                'db_table': 'unidade',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('email', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='EMAIL')),
                ('nome', models.CharField(max_length=50, verbose_name='NOME')),
                ('cartao_postagem', models.CharField(max_length=30, verbose_name='CARTÃO POSTAGEM')),
                ('senha', models.CharField(max_length=128, verbose_name='SENHA (hash)')),
                ('centro_custo', models.IntegerField(verbose_name='CENTRO DE CUSTO')),
                ('perfil', models.CharField(max_length=10, verbose_name='TIPO PERFIL')),
            ],
            options={
                'verbose_name': 'usuario',
                'verbose_name_plural': 'usuarios',
                'db_table': 'usuario',
                'managed': False,
            },
        ),
    ]
