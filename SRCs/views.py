import openpyxl
from django.shortcuts import render, redirect
from rolepermissions.decorators import has_permission_decorator
from .forms import formularioUnidade, formularioUser, formularioEnvio, UploadFaturaForm
from .models import Unidade, Usuario, Envio, Rateio
from django.contrib import messages
from datetime import datetime
from decimal import Decimal, InvalidOperation


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

def safe_decimal(valor):
    try:
        if valor is None:
            return Decimal('0.00')

        valor_str = str(valor).strip()

        # Corrige traços ou campos com hífens
        if valor_str in ('', '-', '–'):
            return Decimal('0.00')

        # Corrige valores com formato brasileiro: "5.553,32"
        valor_str = valor_str.replace('R$', '').replace('.', '').replace(',', '.')
        return Decimal(valor_str)
    
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Valor inválido para Decimal: {valor}")

def rateio(request):
    if request.method == 'POST':
        form = UploadFaturaForm(request.POST, request.FILES)
        if form.is_valid():
            fatura_file = request.FILES['fatura']
            nome_arquivo = fatura_file.name.rsplit('.', 1)[0]
            try:
                wb = openpyxl.load_workbook(fatura_file, data_only=True)
                ws = wb.active

                erros = []
                importados = 0

                #começa a ler a planilha apartir da linha 5
                for row in ws.iter_rows(min_row=6, values_only=True):
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
                                'fatura': nome_arquivo, 
                                'titular_cartao': row[1],
                                'servico': row[3],
                                'data_postagem': (
                                    datetime.strptime(row[4], '%d/%m/%Y').date()
                                    if isinstance(row[4], str) and row[4].strip()
                                    else row[4] if isinstance(row[4], datetime)
                                    else None
                                ),
                                'servico_adicionais': safe_decimal(row[5]),
                                'unidade_postagem': row[6],
                                'valor_declarado': safe_decimal(row[15]),
                                'valor_unitario': safe_decimal(row[11]),
                                'peso': safe_decimal(row[10]),
                                'desconto': safe_decimal(row[12]),
                                'valor_liquido': safe_decimal(row[14]),
                                
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
    
    envios = Envio.objects.select_related('user', 'remetente', 'destinatario').all().order_by('-data_solicitacao')

    dados_completos = []

    for envio in envios:
        try:
            rateio = Rateio.objects.get(etiqueta=envio)
        except Rateio.DoesNotExist:
            rateio = None
        
        dados_completos.append({
            'fatura': rateio.fatura if rateio else 'PENDENTE',
            'solicitante': envio.user.nome,
            'motivo': envio.conteudo,
            'cartao_postagem': envio.user.cartao_postagem,
            'titular_cartao': rateio.titular_cartao if rateio else '',
            'servico': rateio.servico if rateio else '',
            'numero_autorizacao': envio.numero_autorizacao,
            'etiqueta': envio.etiqueta,
            'data_postagem': rateio.data_postagem if rateio else '',
            'unidade_postagem': rateio.unidade_postagem if rateio else '',
            'remetente': envio.remetente.shopping,
            'destinatario': envio.destinatario.shopping,
            'valor_declarado': rateio.valor_declarado if rateio else '',
            'valor_unitario': rateio.valor_unitario if rateio else '',
            'quantidade': envio.quantidade,
            'peso': rateio.peso if rateio else '',
            'servico_adicionais': rateio.servico_adicionais if rateio else '',
            'valor_liquido': rateio.valor_liquido if rateio else '',
            'desconto': rateio.desconto if rateio else '',
            'centro_custo': envio.destinatario.centro_custo,
            'empresa': envio.destinatario.empresa,
        })
    return render(request, 'SRCs/rateio.html', {'form': form, 'dados': dados_completos}) 

@has_permission_decorator('visualizar_graficos')
def dashboard(request):
    return render(request, 'STCs/graficos.html')


 