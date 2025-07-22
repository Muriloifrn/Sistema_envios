from zeep import Client, Transport
from requests import Session

# Sessão com cabeçalho User-Agent
session = Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0'
})

# Usa a sessão no cliente zeep
transport = Transport(session=session)
client = Client('https://webservice.correios.com.br/service/rastro/Rastro.wsdl', transport=transport)


# Dados da API - SUBSTITUA PELOS REAIS DO CONTRATO
usuario = 'financeiro@varejomais.com'
senha = 'k3B81'
codigos = 'OY280393896BR'  # Substitua por um código de rastreio real da empresa


# Parâmetros
tipo = 'L'
resultado = 'T'
lingua = '101'

# Faz a consulta
resposta = client.service.buscaEventos(usuario, senha, codigos, tipo, resultado, lingua)
print(resposta)