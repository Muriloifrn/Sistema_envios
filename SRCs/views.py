from django.shortcuts import render
from rolepermissions.decorators import has_permission_decorator

def index(request):
    return render(request, 'SRCs/index.html')

def home(request):
    return render(request, 'SRCs/home.html')

@has_permission_decorator('cadastrar_user')
def user(request):
    return render(request, 'SRCs/user.html')

@has_permission_decorator('cadastrar_user')
def cadastro_user(request):
    return render(request, 'SRCs/fomr_user.html')

@has_permission_decorator('cadastrar_unid')
def unidade(request):
    return render(request, 'SRCs/unidade.html')

@has_permission_decorator('cadastrar_unid')
def cadastro_unidade(request):
    return render(request, 'SRCs/form_und.html')

@has_permission_decorator('cadastrar_envio')
def cadastro_envio(request):
    return render(request, 'SRCs/form_envio.html')

def rateio(request):
    return render(request, 'SRCs/rateio.html')

@has_permission_decorator('visualizar_graficos')
def dashboard(request):
    return render(request, 'STCs/graficos.html')


