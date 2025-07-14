from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

class Unidade(models.Model):
    id = models.AutoField(primary_key=True)
    cnpj = models.CharField("CNPJ", db_column='CNPJ', max_length=18, unique=True) 
    centro_custo = models.IntegerField("CENTRO DE CUSTO")
    cep = models.CharField("CEP", max_length=10)
    bairro = models.CharField("BAIRRO", max_length=50)
    rua = models.CharField("RUA", max_length=100)
    numero = models.CharField("NÚMERO", max_length=10)
    shopping = models.CharField("SHOPPING", max_length=100, blank=True, null=True)
    cidade = models.CharField("CIDADE", max_length=50)
    estado = models.CharField("ESTADO", max_length=2, blank=True, null=True)
    regional = models.CharField("REGIONAL", max_length=2, blank=True, null=True)
    numero_unidade = models.CharField("NUMERO DA UNIDADE", max_length=10, blank=True, null=True)
    empresa = models.CharField("EMPRESA", max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.shopping}"

    class Meta:
        managed = True
        db_table = 'unidade'
        verbose_name = "unidade"
        verbose_name_plural = "unidades"

class Usuario(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    PERFIS = [
        ('Admin', 'Admin'),
        ('Analista', 'Analista'),
        ('Basic', 'Basic'),
        ('Supervisor', 'Supervisor'),
    ]
    cartao_postagem = models.CharField("CARTÃO POSTAGEM", max_length=30)
    perfil = models.CharField("TIPO PERFIL", max_length=10, choices=PERFIS, default='basic')

    def __str__(self):
        return self.user.username

    class Meta:
        permissions = [
            ('cadastrar_usuario', 'Cadastrar Usuário'),
            ('editar_usuario', 'Editar Usuário'),
            ('cadastrar_unidade', 'Cadastrar Unidade'),
            ('editar_unidade', 'Editar Unidade'),
            ('cadastrar_envio', 'Cadastrar Envio'),
            ('consultar_rateio', 'Consultar Rateio'),
            ('consultar_dashboard', 'Consultar Dashboard'),
            ('acompanhar_envio', 'Acompanhar Envio'),
        ]
    def atribuir_grupo(self):
        grupo_nome = self.perfil.lower()
        grupo = Group.objects.get(name=grupo_nome)
        self.user.groups.add(grupo)

    def __str__(self):
        return self.user.username

    class Meta:
        managed = True
        db_table = 'usuario'
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
    

        
    
class Envio(models.Model):
    etiqueta = models.CharField("ETIQUETA", max_length=50, unique=True, primary_key=True)
    user = models.ForeignKey('Usuario', models.DO_NOTHING, verbose_name="USUÁRIO")
    remetente = models.ForeignKey('Unidade', models.DO_NOTHING, db_column='remetente', verbose_name="REMETENTE")
    destinatario = models.ForeignKey('Unidade', models.DO_NOTHING, db_column='destinatario', related_name='envio_destinatario_set', verbose_name="DESTINATÁRIO")
    numero_autorizacao = models.CharField("NÚMERO DE AUTORIZAÇÃO", max_length=20)
    data_solicitacao = models.DateField("DATA DA SOLICITAÇÃO")
    conteudo = models.CharField(max_length=200, default='Sem conteúdo')
    quantidade = models.IntegerField("QUANTIDADE")
    motivo = models.CharField("MOTIVO",max_length=100)

    def __str__(self):
        return f"{self.etiqueta}"

    class Meta:
        managed = True
        db_table = 'envio'
        verbose_name = "envio"
        verbose_name_plural = "envios"

class Rateio(models.Model):
    id = models.AutoField(primary_key=True)
    fatura = models.CharField("FATURA", max_length=20, blank=True, null=True)
    etiqueta = models.ForeignKey(Envio, models.DO_NOTHING, db_column='etiqueta', verbose_name="ETIQUETA", null=True, blank=True)
    etiqueta_original = models.CharField('ETIQUETA', max_length=50)
    titular_cartao = models.CharField("TITULAR CARTÃO", max_length=100, blank=True, null=True)
    servico = models.CharField("SERVIÇO", max_length=100, blank=True, null=True)
    data_postagem = models.DateField("DATA DA POSTAGEM", blank=True, null=True)
    unidade_postagem = models.CharField("UNIDADE POSTAGEM", max_length=100, blank=True, null=True)
    valor_declarado = models.DecimalField("VALOR DECLARADO", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_unitario = models.DecimalField("VALOR UNITÁRIO", max_digits=10, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField("PESO", max_digits=10, decimal_places=2, blank=True, null=True)
    servico_adicionais = models.DecimalField("SERVIÇOS ADICIONAIS", max_digits=10, decimal_places=2, blank=True, null=True)
    desconto = models.DecimalField("DESCONTO", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_liquido = models.DecimalField("VALOR LIQUIDO", max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.fatura}"

    class Meta:
        managed = True
        db_table = 'rateio'
        verbose_name = "rateio"
        verbose_name_plural = "rateios"








