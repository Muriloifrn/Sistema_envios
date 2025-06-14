import openpyxl
from django.shortcuts import render, redirect
from rolepermissions.decorators import has_permission_decorator
from .forms import formularioUnidade, formularioUser, formularioEnvio, UploadFaturaForm
from .models import Unidade, Usuario, Envio, Rateio
from django.contrib import messages
from datetime import datetime
from decimal import Decimal 


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
    if request.method == 'POST':
        form = formularioEnvio(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = formularioEnvio()

    return render(request, 'SRCs/form_envio.html', {'form': form})

def rateio(request):
    if request.method == 'POST':
        form = UploadFaturaForm(request.POST, request.FILES)
        if form.is_valid():
            fatura_file = request.FILES['fatura']
            try:
                wb = openpyxl.load_workbook(fatura_file, data_only=True)
                ws = wb.active

                erros = []
                importados = 0

                #começa a ler a planilha apartir da linha 5
                for row in ws.iter_rows(min_row=5, values_only=True):
                    etiqueta_valor = row[8]
                    if not etiqueta_valor:
                        continue
                    
                    try:
                        envio = Envio.objects.get(etiqueta=etiqueta_valor)
                    except Envio.DoesNotExist:
                        erros.append(f"Erro: Etiqueta '{etiqueta_valor}' não encontrada. ")
                        continue
                    
                    try:
                        rateio, created = Rateio.objects.get_or_create(
                            etiqueta=envio,
                            defaults={
                                'fatura': None, 
                                'titular_cartao': row[1],
                                'servico': row[3],
                                'data_postagem': (
                                    datetime.strptime(row[4], '%d/%m/%Y').date()
                                    if isinstance(row[4], str) and row[4].strip()
                                    else row[4] if isinstance(row[4], datetime)
                                    else None
                                ),
                                'servico_adicionais': Decimal(row[5] or 0),
                                'unidade_postagem': row[6],
                                'valor_declarado': Decimal(row[15] or 0),
                                'valor_unitario': Decimal(row[11] or 0),
                                'peso': Decimal(row[10] or 0),
                                'desconto': Decimal(row[12] or 0),
                                'valor_liquido': Decimal(row[14] or 0),
                                
                            }
                        )
                        importados += 1
                    except Exception as e:
                        erros.append(f"Erro ao importar etiqueta '{etiqueta_valor}': {str(e)}")
                if importados:
                    messages.success(request, f'{importados} registros importados com sucesso.')
                if erros:
                    for erro in erros:
                        messages.warning(request, erro)
                
                return redirect('rateio')

            except Exception as e:
                messages.error(request,  f'Erro ao processar o arquivo: {str(e)}')
    else:
        form = UploadFaturaForm()
    
    return render(request, 'SRCs/rateio.html', {'form': form, 'rateios': rateios}) 

@has_permission_decorator('visualizar_graficos')
def dashboard(request):
    return render(request, 'STCs/graficos.html')


 