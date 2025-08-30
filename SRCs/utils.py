# SRCs/utils.py
from io import BytesIO
from datetime import date
from decimal import Decimal
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import mm

def _format_currency(value):
    """Formata número Decimal/float para 'R$ 1.234,56'."""
    try:
        v = float(value)
    except Exception:
        v = 0.0
    s = f"{v:,.2f}"
    # troca separadores para formato brasileiro
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

def _format_date_pt(d):
    """Formata uma date para 'DD de mês de AAAA' em pt-BR."""
    meses = [
        "janeiro","fevereiro","março","abril","maio","junho",
        "julho","agosto","setembro","outubro","novembro","dezembro"
    ]
    if not d:
        d = date.today()
    return f"{d.day} de {meses[d.month - 1]} de {d.year}"

def _unidade_to_dict(unidade):
    """Tenta extrair campos comuns de Unidade com fallback para strings vazias."""
    if unidade is None:
        return {"nome":"", "endereco":"", "cidade":"", "cep":"", "cnpj":""}
    return {
        "nome": getattr(unidade, "nome", "") or getattr(unidade, "razao_social", "") or "",
        "endereco": getattr(unidade, "endereco", "") or "",
        "cidade": getattr(unidade, "cidade", "") or "",
        "cep": getattr(unidade, "cep", "") or "",
        "cnpj": getattr(unidade, "cnpj", "") or getattr(unidade, "CNPJ", "") or "",
    }

def gerar_pdf_declaracao(envio):
    """
    Gera um PDF com a 'DECLARAÇÃO DE CONTEÚDO' baseado no modelo enviado.
    Recebe o objeto envio (instância de Envio já salva).
    Retorna: FileResponse (download do PDF).
    """
    buffer = BytesIO()
    # Margens em mm
    left_right_margin = 15 * mm
    top_bottom_margin = 20 * mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=left_right_margin,
        rightMargin=left_right_margin,
        topMargin=top_bottom_margin,
        bottomMargin=top_bottom_margin
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Heading1'], alignment=1, fontSize=14, spaceAfter=8)
    normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=10, leading=12)
    small = ParagraphStyle('small', parent=styles['Normal'], fontSize=9, leading=11)

    elements = []
    elements.append(Paragraph("DECLARAÇÃO DE CONTEÚDO", title_style))
    elements.append(Spacer(1, 6))

    # Remetente / Destinatário
    remet = _unidade_to_dict(envio.remetente)
    dest = _unidade_to_dict(envio.destinatario)

    remet_html = (
        f"<b>NOME:</b> {remet['nome']}<br/>"
        f"<b>ENDEREÇO:</b> {remet['endereco']}<br/>"
        f"<b>CIDADE:</b> {remet['cidade']}<br/>"
        f"<b>CEP:</b> {remet['cep']}<br/>"
        f"<b>CNPJ:</b> {remet['cnpj']}"
    )
    dest_html = (
        f"<b>NOME:</b> {dest['nome']}<br/>"
        f"<b>ENDEREÇO:</b> {dest['endereco']}<br/>"
        f"<b>CIDADE:</b> {dest['cidade']}<br/>"
        f"<b>CEP:</b> {dest['cep']}<br/>"
        f"<b>CNPJ:</b> {dest['cnpj']}"
    )

    two_col = [[Paragraph(remet_html, small), Paragraph(dest_html, small)]]
    # calcula largura disponível (A4 largura - margens)
    page_width, page_height = A4
    usable_width = page_width - (left_right_margin * 2)

    table = Table(two_col, colWidths=[usable_width / 2.0, usable_width / 2.0])
    table.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))

    # Tabela de itens
    items = list(getattr(envio, "itens").all()) if hasattr(envio, "itens") else []
    data = [["ITEM", "CONTEÚDO", "QUANT.", "VALOR"]]
    total = Decimal("0.00")
    for idx, it in enumerate(items, start=1):
        qtd = getattr(it, "quantidade", 0) or 0
        val = getattr(it, "valor_unitario", 0) or 0
        try:
            val_dec = Decimal(str(val))
        except Exception:
            val_dec = Decimal("0.00")
        linha = [
            f"{idx:02d}",
            getattr(it, "conteudo", ""),
            str(qtd),
            _format_currency(val_dec)
        ]
        total += (Decimal(qtd) * val_dec)
        data.append(linha)

    # se não houver itens, adiciona uma linha vazia
    if len(data) == 1:
        data.append(["", "Sem conteúdo", "0", _format_currency(0)])

    # linha de totais
    data.append(["", "", "TOTAIS", _format_currency(total)])

    # col widths: ITEM 20mm, VALOR 30mm, QTD 25mm, resto pra CONTEÚDO
    col_item = 20 * mm
    col_qtd = 25 * mm
    col_val = 35 * mm
    col_conteudo = usable_width - (col_item + col_qtd + col_val)
    tbl = Table(data, colWidths=[col_item, col_conteudo, col_qtd, col_val], repeatRows=1)
    tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-2), 0.5, colors.gray),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (-2,1), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),4),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # Texto de declaração (parágrafo fixo do modelo)
    texto_decl = (
        "Declaro que não me enquadro no conceito de contribuinte previsto no art. 4° da Lei Complementar n° 87/1996, "
        "uma vez que não realizo, com habitualidade ou volume que caracterize intuito comercial, operações de "
        "circulação de mercadoria, ainda que se iniciem no exterior, ou estou dispensado da emissão da nota fiscal por "
        "força da legislação tributária vigente, responsabilizando-me, nos termos da lei e a quem de direito, por "
        "informações inverídicas. "
        "<br/><br/>"
        "Declaro ainda que não estou postando conteúdo inflamável, explosivo, causador de combustão espontânea, "
        "tóxico, corrosivo, gás ou qualquer outro conteúdo que constitua perigo, conforme o art. 13 da Lei Postal n° "
        "6.538/78."
    )
    elements.append(Paragraph(texto_decl, small))
    elements.append(Spacer(1, 18))

    # cidade, data e assinatura
    cidade_para_data = remet.get("cidade", "") or dest.get("cidade", "")
    data_texto = f"{cidade_para_data} - UF, { _format_date_pt(getattr(envio, 'data_solicitacao', None)) }"
    elements.append(Paragraph(data_texto, normal))
    elements.append(Spacer(1, 28))
    elements.append(Paragraph("Assinatura do declarante ____________________________________________", normal))
    elements.append(Spacer(1, 14))
    # Observação
    obs = ("OBSERVAÇÃO: Constitui crime a ordem tributária suprimir ou reduzir tributo, ou contribuição social "
           "e qualquer acessório (Lei 8.137/90 Art. 1°, V)")
    elements.append(Paragraph(obs, small))

    # Gera o PDF
    doc.build(elements)

    buffer.seek(0)
    filename = f"declaracao_{getattr(envio, 'etiqueta', 'envio')}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)
