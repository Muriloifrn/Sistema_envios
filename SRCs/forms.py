from django import forms 
from .models import Unidade, Usuario, Envio
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
 
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
    email = forms.EmailField(label="Email")

    class Meta:
        model = Usuario
        fields = ['cartao_postagem', 'perfil']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Já existe um usuário com este email.")
        return email

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )

        usuario = super().save(commit=False)
        usuario.user = user

        if commit:
            usuario.save()

        return usuario

class FormularioEditarUsuario(forms.ModelForm):
    username = forms.CharField(label="Nome de Usuário")
    email = forms.EmailField(label="Email")

    class Meta:
        model = Usuario
        fields = ['cartao_postagem', 'perfil']

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

    def save(self, commit=True):
        usuario = super().save(commit=False)

        if self.usuario_django:
            self.usuario_django.username = self.cleaned_data['username']
            self.usuario_django.email = self.cleaned_data['email']
            if commit:
                self.usuario_django.save()

        if commit:
            usuario.save()

        return usuario



class formularioEnvio(forms.ModelForm):
    class Meta:
        model = Envio
        fields = ('etiqueta', 'user', 'remetente', 'destinatario', 'numero_autorizacao', 'data_solicitacao', 'conteudo', 'quantidade', 'motivo')
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