import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from .forms import formularioUnidade, formularioUser, formularioEnvio, UploadFaturaForm, FormularioEditarUsuario
from .models import Unidade, Usuario, Envio, Rateio
from django.contrib import messages
import datetime
from decimal import Decimal, InvalidOperation
from openpyxl import Workbook
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from urllib.parse import urlencode
from django.db.models.functions import TruncMonth
from django.db.models import Count
import json
import calendar


# View da página inicial
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')

        user = authenticate(request, username=username, password=senha)

        if user is not None:
            login(request, user)
            return redirect('home')  # ou a página inicial do sistema
        else:
            messages.error(request, "Usuário ou senha inválidos.")

    return render(request, 'SRCs/login.html')

# View da home após login
@login_required
def home(request):
    dados = Envio.objects.select_related('user', 'remetente', 'destinatario').order_by('-data_solicitacao')[:5]
    return render(request, 'SRCs/home.html', {'dados': dados})

# View que lista todos os usuários (acesso apenas para quem tem permissão)
@login_required
@permission_required('SRCs.editar_usuario', raise_exception=True)
def user(request):
    usuarios = Usuario.objects.filter(ativo=True)
    return render(request, 'SRCs/user.html', {'usuarios': usuarios})


# View para cadastrar novos usuários
@login_required
@permission_required('SRCs.cadastrar_usuario', raise_exception=True)
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
@login_required
@permission_required('SRCs.cadastrar_unidade', raise_exception=True)
def cadastro_unidade(request):
    id_unidade = request.GET.get('ids') or request.POST.get('id')  # <- IMPORTANTE: buscar o id no GET (GET request) ou POST (ao submeter)
    unidade = Unidade.objects.filter(id=id_unidade).first() if id_unidade else None
    print('Form instância:', unidade)

    if request.method == 'POST':
        form = formularioUnidade(request.POST, instance=unidade)  # <- Aqui está a chave
        if form.is_valid():
            form.save()
            return redirect('unidade')  # ou onde quiser redirecionar
    else:
        form = formularioUnidade(instance=unidade)

    modo = 'editar' if unidade else 'cadastrar'

    return render(request, 'SRCs/form_und.html', {'form': form, 'modo': modo})


# View que lista todas as unidades
@login_required
@permission_required('SRCs.editar_unidade', raise_exception=True)
def unidade(request):
    unidades = Unidade.objects.filter(excluida=False)
    return render(request, 'SRCs/unidade.html', {'unidades': unidades})


# View para cadastrar um envio (ex: envio pelos Correios)
@login_required
@permission_required('SRCs.cadastrar_envio', raise_exception=True)
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
@login_required
@permission_required('SRCs.consultar_rateio', raise_exception=True)
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
                    print(f"Lendo linha: {row}")

                    if row[0] is None or not isinstance(row[0], (int, float)):
                        print(f"Encerrando leitura por linha inválida: {row[0]}")
                        break

                    etiqueta_valor = str(row[8]).strip().upper()
                    print(f"Etiqueta buscada (ajustada): '{etiqueta_valor}'")

                    envio = Envio.objects.filter(etiqueta__iexact=etiqueta_valor).first()
                    print(f"Envio encontrado? {'Sim' if envio else 'Não'}")

                    if not envio:
                        print(f"[INFO] Etiqueta '{etiqueta_valor}' não encontrada. Criando rateio sem envio.")



                    # Aqui vai o try de criação do rateio
                    try:

                        Rateio.objects.filter(etiqueta_original=etiqueta_valor).delete()


                        Rateio.objects.create(
                            etiqueta=envio,
                            etiqueta_original=etiqueta_valor,
                            fatura=nome_arquivo,
                            titular_cartao=row[1],
                            servico=row[3],
                            data_postagem = (
                                datetime.datetime.strptime(row[4], '%d/%m/%Y').date()
                                if isinstance(row[4], str) and row[4].strip()
                                else row[4] if isinstance(row[4], datetime.datetime)
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
                        print(f"Rateio criado com sucesso para a etiqueta {etiqueta_valor}")
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
            'solicitante': envio.user.user.get_full_name() or envio.user.user.username,
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
        'solicitante': envio.user.user.get_full_name() or envio.user.user.username,
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
@login_required
@permission_required('SRCs.consultar_dashboard', raise_exception=True)

def dashboard(request):

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Gráfico 1: Envios por mês (Rateio)
    rateios = Rateio.objects.exclude(data_postagem=None)
    if data_inicio:
        rateios = rateios.filter(data_postagem__gte=data_inicio)
    if data_fim:
        rateios = rateios.filter(data_postagem__lte=data_fim)

    dados = (
        rateios
        .annotate(mes=TruncMonth('data_postagem'))
        .values('mes')
        .annotate(qtd=Count('id'))
        .order_by('mes')
    )

    labels = [f"{item['mes'].strftime('%b/%Y')}" for item in dados]
    valores = [item['qtd'] for item in dados]

    # Inicializa contexto
    context = {
        'labels': json.dumps(labels),
        'valores': json.dumps(valores),
    }

    # Filtro aplicado ao Envio também
    envios = Envio.objects.all()
    if data_inicio:
        envios = envios.filter(data_solicitacao__gte=data_inicio)
    if data_fim:
        envios = envios.filter(data_solicitacao__lte=data_fim)

    # Gráfico 2: Envios por unidade remetente
    envios_por_remetente = (
        envios
        .values('remetente__shopping')
        .annotate(total=Count('etiqueta'))
        .order_by('-total')
    )
    remetentes = [item['remetente__shopping'] or "Não informado" for item in envios_por_remetente]
    envios_qtd = [item['total'] for item in envios_por_remetente]
    context['remetentes'] = json.dumps(remetentes)
    context['qtd_envios'] = json.dumps(envios_qtd)

    # Gráfico 3: Envios por unidade destinatária
    envios_por_destinatario = (
        envios
        .values('destinatario__shopping')
        .annotate(total=Count('etiqueta'))
        .order_by('-total')
    )
    destinatarios = [item.get('destinatario__shopping') or 'Não informado' for item in envios_por_destinatario]
    destinatarios_qtd = [item.get('total', 0) for item in envios_por_destinatario]
    context['destinatarios'] = json.dumps(destinatarios)
    context['qtd_destinatarios'] = json.dumps(destinatarios_qtd)

    return render(request, 'SRCs/graficos.html', context)


@login_required
@permission_required('SRCs.acompanhar_envio', raise_exception=True)
def acompanhamento(request):
    return render(request, 'SRCs/acompanhamento.html')

def editar_unidade(request):
    if request.method == 'POST':
        selecionados = request.POST.getlist('selecionados')
        params = urlencode({'ids': ','.join(selecionados)})
        return redirect(f'/home/unidades/novo?{params}')
    return redirect('cadastro_unidade')
    
def excluir_unidade(request, unidade_id):
    unidade = get_object_or_404(Unidade, id=unidade_id)
    unidade.excluida = True
    unidade.cnpj = None
    unidade.save()
    return redirect('unidade')

def excluir_unidades_multiplo(request):
    if request.method == 'POST':
        print('POST recebido')
        ids = request.POST.getlist('selecionados')
        print('IDs selecionados:', ids)
        for unidade_id in ids:
            unidade = get_object_or_404(Unidade, id=unidade_id)
            unidade.excluida = True
            unidade.cnpj = None
            unidade.save()
        return redirect('unidade')
    else:
        print('Não é POST')
    # Se não for POST, apenas redireciona
    return redirect('unidade')

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        form = FormularioEditarUsuario(request.POST, instance=usuario, usuario_django=usuario.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('user') 
    else:
        form = FormularioEditarUsuario(instance=usuario, usuario_django=usuario.user)

    return render(request, 'SRCs/form_editar_usuario.html', {'form': form, 'usuario': usuario})

def excluir_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    usuario.ativo = False
    usuario.save()

    # Marcar e-mail como desativado, mas mantendo histórico
    usuario.user.email = f"{usuario.user.email}-desativado-{usuario.id}"
    usuario.user.save()

    messages.success(request, 'Usuário desativado com sucesso!')
    return redirect('user')

