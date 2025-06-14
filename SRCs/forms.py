from django import forms 
from .models import Unidade, Usuario, Envio
 
class formularioUnidade(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ('cnpj', 'centro_custo', 'cep', 'bairro', 'rua', 'numero', 'shopping', 'cidade', 'estado', 'regional', 'numero_unidade', 'empresa' )

class formularioUser(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'cartao_postagem', 'senha', 'centro_custo', 'perfil')

class formularioEnvio(forms.ModelForm):
    class Meta:
        model = Envio
        fields = ('etiqueta', 'user', 'remetente', 'destinatario', 'numero_autorizacao', 'data_solicitacao', 'conteudo', 'quantidade' )

class UploadFaturaForm(forms.Form):
    fatura = forms.FileField(
        label='Selecione a planilha da fatura (.xlsx)',
        required=True,
        widget=forms..ClearableFileInput(attrs={'accept': '.xlsx'})
    )