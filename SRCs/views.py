from django.shortcuts import render, redirect
from rolepermissions.decorators import has_permission_decorator
from .forms import formularioUnidade, formularioUser
from .models import Unidade, Usuario

def index(request):
    return render(request, 'SRCs/index.html')

def home(request):
    return render(request, 'SRCs/home.html')

@has_permission_decorator('cadastrar_user')
def user(request):
    usuarios = Usuario.objects.all()
    return render(request, 'SRCs/user.html', {'usuarios': usuarios})

@has_permission_decorator('cadastrar_user')
def cadastro_user(request):
    if request.method == 'POST':
        form = formularioUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user')
    else:
        form = formularioUser()

    return render(request, 'SRCs/form_user.html', {'form': form})

@has_permission_decorator('cadastrar_unid')
def cadastro_unidade(request):
    if request.method == 'POST':
        form = formularioUnidade(request.POST)
        if form.is_valid():
            form.save()
            return redirect('unidade')
    else:
        form = formularioUnidade()

    return render(request, 'SRCs/form_und.html', {'form': form})

@has_permission_decorator('cadastrar_unid')
def unidade(request):
    unidades = Unidade.objects.all()
    return render(request, 'SRCs/unidade.html', {'unidades': unidades})

@has_permission_decorator('cadastrar_envio')
def cadastro_envio(request):
    return render(request, 'SRCs/form_envio.html')

def rateio(request):
    return render(request, 'SRCs/rateio.html')

@has_permission_decorator('visualizar_graficos')
def dashboard(request):
    return render(request, 'STCs/graficos.html')


 