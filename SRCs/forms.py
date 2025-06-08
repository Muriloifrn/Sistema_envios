from django import forms 
from .models import Unidade, Usuario, Produto, Envio
 
class formularioUnidade(forms.ModelForm):
    class Meta:
        model = Unidade
        fields = ('cnpj', 'centro_custo', 'cep', 'bairro', 'rua', 'numero', 'shopping', 'cidade', 'estado', 'regional', 'numero_unidade', 'empresa' )

class formularioUser(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'cartao_postagem', 'senha', 'centro_custo', 'perfil')
    