from django import forms 
from .models import Unidade, Usuario, Envio, ItemEnvio
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
 
class formularioUnidade(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ('cnpj', 'centro_custo', 'cep', 'bairro', 'rua', 'numero', 'shopping', 'cidade', 'estado', 'regional', 'numero_unidade', 'empresa')

    def clean_cnpj(self):
        cnpj = self.cleaned_data['cnpj']
        qs = Unidade.objects.filter(cnpj=cnpj)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Já existe uma unidade com este CNPJ.")
        return cnpj

class formularioUser(forms.ModelForm):
    username = forms.CharField(label="Nome de Usuário")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
    confirmar_senha = forms.CharField(label="Confirmar Senha", widget=forms.PasswordInput)
    email = forms.EmailField(label="Email")
    unidade = forms.ModelChoiceField(
        queryset=Unidade.objects.none(),  # será preenchido no __init__
        required=False,
        label="Unidade",
        empty_label="Selecione uma unidade"
    )

    class Meta:
        model = Usuario
        fields = ['cartao_postagem', 'perfil', 'unidade']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # filtra apenas unidades não excluídas
        self.fields['unidade'].queryset = Unidade.objects.filter(excluida=False).order_by('shopping')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Já existe um usuário com este email.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Já existe um usuário com este nome")
        return username  

    def clean_password(self):
        password = self.cleaned_data.get("password")
        # Pelo menos 8 caracteres, 1 letra, 1 número e 1 caractere especial
        regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(regex, password):
            raise ValidationError(
                "A senha deve ter pelo menos 8 caracteres, incluindo letras, números e caracteres especiais."
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha and confirmar and senha != confirmar:
            raise ValidationError("As senhas não coincidem.")
        return cleaned_data

    def save(self, commit=True):
        # Cria o User do Django
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )

        usuario = super().save(commit=False)
        usuario.user = user

        if commit:
            usuario.save()
            usuario.atribuir_grupo()  # associa o usuário ao grupo

        return usuario

class FormularioEditarUsuario(forms.ModelForm):
    username = forms.CharField(label="Nome de Usuário")
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput,
        required=False
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput,
        required=False
    )

    unidade = forms.ModelChoiceField(
        queryset=Unidade.objects.filter(excluida=False).order_by('shopping'),
        required=False,
        label="Unidade",
        empty_label="Selecione uma unidade"
    )

    class Meta:
        model = Usuario
        fields = ['cartao_postagem', 'perfil', 'unidade']

    def __init__(self, *args, **kwargs):
        self.usuario_django = kwargs.pop('usuario_django', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email)

        if self.usuario_django:
            qs = qs.exclude(pk=self.usuario_django.pk)

        if qs.exists():
            raise ValidationError("Já existe um usuário com este email.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # Só valida se o campo foi preenchido (edição não é obrigatória)
        if password:
            regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
            if not re.match(regex, password):
                raise ValidationError(
                    "A senha deve ter pelo menos 8 caracteres, incluindo letras, números e caracteres especiais."
                )
        return password

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirmar_senha")

        if senha:  # só valida se o usuário digitou algo
            regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
            if not re.match(regex, senha):
                raise ValidationError(
                    "A senha deve ter pelo menos 8 caracteres, incluindo letras, números e caracteres especiais."
                )

            if senha != confirmar:
                raise ValidationError("As senhas não coincidem.")
        return cleaned_data


    def save(self, commit=True):
        usuario = super().save(commit=False)

        if self.usuario_django:
            self.usuario_django.username = self.cleaned_data['username']
            self.usuario_django.email = self.cleaned_data['email']

            # Atualiza a senha apenas se o campo foi preenchido
            nova_senha = self.cleaned_data.get('password')
            if nova_senha:
                self.usuario_django.set_password(nova_senha)

            if commit:
                self.usuario_django.save()

        if commit:
            usuario.save()

        return usuario

class formularioEnvio(forms.ModelForm):
    class Meta:
        model = Envio
        fields = (
            'etiqueta',
            'remetente',
            'destinatario',
            'numero_autorizacao',
            'data_solicitacao',
            'motivo'
        )
        widgets = {
            'data_solicitacao': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_etiqueta(self):
        etiqueta = self.cleaned_data['etiqueta']
        if Envio.objects.filter(etiqueta=etiqueta).exists():
            raise ValidationError("Já existe um envio com esta etiqueta.")
        return etiqueta
    
    def clean(self):
        cleaned_data = super().clean()
        remetente = cleaned_data.get('remetente')
        destinatario = cleaned_data.get('destinatario')
        if remetente and destinatario and remetente == destinatario:
            raise ValidationError("Remetente e destinatário não podem ser iguais.")

class UploadFaturaForm(forms.Form):
    fatura = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )

class formularioItemEnvio(forms.ModelForm):
    class Meta:
        model = ItemEnvio
        fields = ('conteudo', 'quantidade', 'valor_unitario')