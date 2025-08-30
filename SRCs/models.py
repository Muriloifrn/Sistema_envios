from django.db import models
from django.contrib.auth.models import User, Group

class Unidade(models.Model):
    id = models.AutoField(primary_key=True)
    cnpj = models.CharField("CNPJ", db_column='CNPJ', max_length=18, unique=True, null=True, blank=True)
    excluida = models.BooleanField(default=False)
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
    ativo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='fotos_usuarios/', blank=True, null=True)

    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE, null=True, blank=True)

    PERFIS = [
        ('Admin', 'Admin'),
        ('Analista', 'Analista'),
        ('Agente', 'Agente'),
        ('Supervisor', 'Supervisor'),
        ('Cliente', 'Cliente'),
    ]
    cartao_postagem = models.CharField("Cartão Postagem", max_length=30)
    perfil = models.CharField("Perfil", max_length=15, choices=PERFIS, default='Cliente')

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
        managed = True
        db_table = 'usuario'
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def atribuir_grupo(self):
        grupo_nome = self.perfil.lower()
        grupo = Group.objects.get(name=grupo_nome)
        self.user.groups.add(grupo)

    def foto_url(self):
        if self.foto and self.foto.url:
            return self.foto.url
        return '/static/SRCs/imagens/user-icon.png'  # foto padrão


class Envio(models.Model):
    STATUS_CHOICES = [
        ('pendente_envio', 'Pendente de Envio'),
        ('aguardando_recebimento', 'Aguardando Recebimento'),
        ('entregue', 'Entregue'),
    ]

    etiqueta = models.CharField("ETIQUETA", max_length=50, unique=True, primary_key=True)
    id_visual = models.IntegerField("ID Visual", unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="USUÁRIO", related_name="envios_cadastrados")
    remetente = models.ForeignKey('Unidade', models.DO_NOTHING, verbose_name="REMETENTE")
    destinatario = models.ForeignKey('Unidade', models.DO_NOTHING, related_name='envio_destinatario_set', verbose_name="DESTINATÁRIO")
    usuario_destinatario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, blank=True, null=True, related_name='envios_recebidos')
    numero_autorizacao = models.CharField("NÚMERO DE AUTORIZAÇÃO", max_length=20)
    data_solicitacao = models.DateField("DATA DA SOLICITAÇÃO")
    motivo = models.CharField("MOTIVO", max_length=100)
    data_postagem = models.DateField("Data da Postagem", blank=True, null=True)
    previsao_chegada = models.DateField("Previsão de Chegada", blank=True, null=True)
    data_chegada = models.DateField("Data de chegada", blank=True, null=True)
    status = models.CharField("Status", max_length=30, choices=STATUS_CHOICES, default='pendente_envio')

    def save(self, *args, **kwargs):
        if not self.id_visual:
            last_id = Envio.objects.aggregate(models.Max('id_visual'))['id_visual__max'] or 0
            self.id_visual = last_id + 1
        super().save(*args, **kwargs)       

    def __str__(self):
        return f"{self.etiqueta}"

    class Meta:
        managed = True
        db_table = 'envio'
        verbose_name = "envio"
        verbose_name_plural = "envios"

class ItemEnvio(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name="itens")
    conteudo = models.CharField("CONTEÚDO", max_length=200)
    quantidade = models.IntegerField("QUANTIDADE")
    valor_unitario = models.DecimalField("VALOR UNITÁRIO", max_digits=10, decimal_places=2)

    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __str__(self):
        return f"{self.conteudo} ({self.quantidade}x)"



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
