# Importa a biblioteca para manipulação de planilhas Excel
import openpyxl

# Importa funções do Django para renderizar templates e redirecionar páginas
from django.shortcuts import render, redirect

# Importa decorador para controle de permissões de acesso às views
from rolepermissions.decorators import has_permission_decorator

# Importa os formulários definidos no projeto
from .forms import formularioUnidade, formularioUser, formularioEnvio, UploadFaturaForm

# Importa os modelos (tabelas do banco de dados)
from .models import Unidade, Usuario, Envio, Rateio

# Para exibir mensagens ao usuário (sucesso, erro etc.)
from django.contrib import messages

# Para trabalhar com datas
from datetime import datetime

# Para trabalhar com valores decimais de forma precisa
from decimal import Decimal, InvalidOperation

#biblioteca usada para criar planilhas excel 
from openpyxl import Workbook

#para enviar o arquivo excel como download
from django.http import HttpResponse


# View da página inicial
def index(request):
    return render(request, 'SRCs/index.html')


# View da home após login
def home(request):
    dados = Envio.objects.select_related('user', 'remetente', 'destinatario').order_by('-data_solicitacao')[:5]
    return render(request, 'SRCs/home.html', {'dados': dados})


# View que lista todos os usuários (acesso apenas para quem tem permissão)
@has_permission_decorator('cadastrar_user')
def user(request):
    usuarios = Usuario.objects.all()
    return render(request, 'SRCs/user.html', {'usuarios': usuarios})


# View para cadastrar novos usuários
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


# View para cadastrar unidades
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


# View que lista todas as unidades
@has_permission_decorator('cadastrar_unid')
def unidade(request):
    unidades = Unidade.objects.all()
    return render(request, 'SRCs/unidade.html', {'unidades': unidades})


# View para cadastrar um envio (ex: envio pelos Correios)
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


# Função auxiliar para converter valores em decimal de forma segura
def safe_decimal(valor):
    try:
        if valor is None:
            return Decimal('0.00')

        valor_str = str(valor).strip()

        # Trata valores vazios ou com traço
        if valor_str in ('', '-', '–'):
            return Decimal('0.00')

        # Formato brasileiro: converte R$ e vírgula para ponto
        valor_str = valor_str.replace('R$', '').replace('.', '').replace(',', '.')
        return Decimal(valor_str)
    
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Valor inválido para Decimal: {valor}")


# View que faz o processamento da fatura (rateio)
def rateio(request):
    if request.method == 'POST':
        form = UploadFaturaForm(request.POST, request.FILES)
        if form.is_valid():
            fatura_file = request.FILES['fatura']
            nome_arquivo = fatura_file.name.rsplit('.', 1)[0]
            try:
                # Abre o arquivo Excel enviado
                wb = openpyxl.load_workbook(fatura_file, data_only=True)
                ws = wb.active

                erros = []       # Lista de erros encontrados
                importados = 0   # Contador de registros importados

                # Começa a ler da linha 6 em diante
                for row in ws.iter_rows(min_row=6, values_only=True):

                    # Verifica se a primeira célula da linha contém número (evita ler linhas inválidas)
                    if not str(row[0]).strip().isdigit():
                        break
                        
                    etiqueta_valor = row[8]
                    if not etiqueta_valor:
                        continue
                    
                    # Tenta encontrar o envio pela etiqueta
                    try:
                        envio = Envio.objects.filter(etiqueta=etiqueta_valor).first()
                    except Envio.DoesNotExist:
                        erros.append(f"Erro: Etiqueta '{etiqueta_valor}' não encontrada.")
                        continue
                    
                    # Cria um novo rateio com os dados da linha
                    try:
                        Rateio.objects.create(
                            etiqueta=envio,
                            etiqueta_original=etiqueta_valor,
                            fatura=nome_arquivo,
                            titular_cartao=row[1],
                            servico=row[3],
                            data_postagem=(
                                datetime.strptime(row[4], '%d/%m/%Y').date()
                                if isinstance(row[4], str) and row[4].strip()
                                else row[4] if isinstance(row[4], datetime)
                                else None
                            ),
                            servico_adicionais=safe_decimal(row[5]),
                            unidade_postagem=row[6],
                            valor_declarado=safe_decimal(row[15]),
                            valor_unitario=safe_decimal(row[11]),
                            peso=safe_decimal(row[10]),
                            desconto=safe_decimal(row[12]),
                            valor_liquido=safe_decimal(row[14]),
                        )
                        importados += 1
                    except Exception as e:
                        erros.append(f"Erro ao importar etiqueta '{etiqueta_valor}': {str(e)}")

                # Mensagem de sucesso/erro
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
    
    # Busca envios e rateios para exibição na página
    envios = Envio.objects.select_related('user', 'remetente', 'destinatario').all().order_by('-data_solicitacao')
    rateios = Rateio.objects.select_related('etiqueta').all()

    # Para evitar repetição de etiquetas
    etiquetas_processadas = set()

    # Associa etiquetas não vinculadas no banco
    for rateio in rateios:
        if not rateio.etiqueta:
            envio = Envio.objects.filter(etiqueta=rateio.etiqueta_original).first()
            if envio:
                rateio.etiqueta = envio
                rateio.save()

    dados_completos = []

    # Monta os dados completos juntando envio + rateio
    for envio in envios:
        rateio = Rateio.objects.filter(etiqueta=envio).order_by('-id').first()
        
        dados_completos.append({
            'fatura': rateio.fatura if rateio else 'PENDENTE',
            'solicitante': envio.user.nome,
            'motivo': envio.motivo,
            'conteudo': envio.conteudo,
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

        etiquetas_processadas.add(envio.etiqueta)

    # Adiciona os rateios que não têm envio correspondente
    for rateio in rateios:
        if rateio.etiqueta and rateio.etiqueta.etiqueta in etiquetas_processadas:
            continue 
        
        dados_completos.append({
            'fatura': rateio.fatura,
            'solicitante': '',
            'motivo': '',
            'cartao_postagem': '',
            'titular_cartao': rateio.titular_cartao,
            'servico': rateio.servico,
            'numero_autorizacao': '',
            'etiqueta': rateio.etiqueta.etiqueta if rateio.etiqueta else rateio.etiqueta_original,
            'data_postagem': rateio.data_postagem,
            'unidade_postagem': rateio.unidade_postagem,
            'remetente': '',
            'destinatario': '',
            'valor_declarado': rateio.valor_declarado,
            'valor_unitario': rateio.valor_unitario,
            'quantidade': '',
            'peso': rateio.peso,
            'servico_adicionais': rateio.servico_adicionais,
            'valor_liquido': rateio.valor_liquido,
            'desconto': rateio.desconto,
            'centro_custo': '',
            'empresa': '',
        })

    # Renderiza a página com os dados e o formulário de upload
    return render(request, 'SRCs/rateio.html', {'form': form, 'dados': dados_completos}) 

def exportar_rateio(request):
    #Mostra os dados completos 
    envios = Envio.objects.select_related('user', 'remetente', 'destinatario').all().order_by('-data_solicitacao')
    rateios = Rateio.objects.select_related('etiqueta').all()

    etiquetas_processadas = set()
    dados_completos = []

    for envio in envios:
       rateio = Rateio.objects.filter(etiqueta=envio).order_by('-id').first()
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
       etiquetas_processadas.add(envio.etiqueta)

    for rateio in rateios:
        if rateio.etiqueta and rateio.etiqueta.etiqueta in etiquetas_processadas:
            continue
        dados_completos.append({
            'fatura': rateio.fatura,
            'solicitante': '',
            'motivo': '',
            'cartao_postagem': '',
            'titular_cartao': rateio.titular_cartao,
            'servico': rateio.servico,
            'numero_autorizacao': '',
            'etiqueta': rateio.etiqueta.etiqueta if rateio.etiqueta else rateio.etiqueta_original,
            'data_postagem': rateio.data_postagem,
            'unidade_postagem': rateio.unidade_postagem,
            'remetente': '',
            'destinatario': '',
            'valor_declarado': rateio.valor_declarado,
            'valor_unitario': rateio.valor_unitario,
            'quantidade': '',
            'peso': rateio.peso,
            'servico_adicionais': rateio.servico_adicionais,
            'valor_liquido': rateio.valor_liquido,
            'desconto': rateio.desconto,
            'centro_custo': '',
            'empresa': '',
        })
    
    #Cria o Excal
    wb = Workbook() 
    ws = wb.active
    ws.title = "Rateio"

    #cabeçalho
    colunas = list(dados_completos[0].keys()) if dados_completos else [] 
    ws.append(colunas)

    #linhas 
    for item in dados_completos:
        ws.append([item.get(c, '') for c in colunas])

    #retorna com dowload 
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=rateio_completo.xlsx'
    wb.save(response)
    return response


# View do painel de gráficos
@has_permission_decorator('visualizar_graficos')
def dashboard(request):
    return render(request, 'STCs/graficos.html')

def editar_unidade(request):
    if request.method == 'POST':
        selecionados = request.POST.getlist('selecionados')
        return redirect('cadastro_unidade', ids=selecionados)
    
def excluir_unidade(request):
    if request.method == 'POST':
        selecionados = request.POST.getlist('selecionados')
        Unidade.objects.filter(id__in=selecionados).delete()
        return redirect('unidade')