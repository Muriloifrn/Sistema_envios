import requests
from bs4 import BeautifulSoup

def rastrear_correios(codigo):
    url = f'https://www2.correios.com.br/sistemas/rastreamento/resultado.cfm'

    headers = {
        'User-Agent': 'Mozilla/5.0',
    }

    data = {
        'objetos': codigo
    }

    response = requests.post(url, data=data, headers=headers)

    if response.status_code != 200:
        print("Erro ao acessar os Correios")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    eventos = []

    linhas = soup.select('table.listEvent.sro > tbody > tr')

    for i in range(0, len(linhas), 2):
        status_linha = linhas[i]
        detalhe_linha = linhas[i + 1]

        data_hora_local = status_linha.select_one('td > strong').text.strip()
        status = status_linha.select_one('td > span').text.strip()
        local = detalhe_linha.select_one('td').text.strip()

        eventos.append({
            'data': data_hora_local,
            'status': status,
            'local': local
        })

    return eventos

# 🔄 Teste com sua etiqueta real
etiqueta = "OY234692805BR"
eventos = rastrear_correios(etiqueta)

for evento in eventos:
    print("🗓 Data:", evento['data'])
    print("📦 Status:", evento['status'])
    print("📍 Local:", evento['local'])
    print('-' * 40)
