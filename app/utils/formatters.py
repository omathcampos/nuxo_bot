import locale
from datetime import datetime

# Configurar locale para formatação de moeda em português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass  # Se não conseguir configurar, usa o padrão

def formatar_valor(valor):
    """Formata um valor monetário"""
    try:
        return locale.currency(float(valor), grouping=True)
    except:
        return f"R$ {valor:.2f}".replace('.', ',')

def formatar_data(data, formato='%d/%m/%Y'):
    """Formata uma data"""
    if isinstance(data, str):
        try:
            data = datetime.strptime(data, '%Y-%m-%d')
        except:
            return data
    
    return data.strftime(formato)

def formatar_lista_gastos(gastos):
    """Formata uma lista de gastos para exibição"""
    if not gastos:
        return "Nenhum gasto encontrado."
    
    resultado = "📊 *LISTA DE GASTOS* 📊\n\n"
    total = 0
    
    for gasto in gastos:
        valor = float(gasto.get('valor', 0))
        total += valor
        
        data = formatar_data(gasto.get('data', ''))
        categoria = gasto.get('categoria', 'Não especificada')
        local = gasto.get('local', 'Não especificado')
        forma = gasto.get('forma_pagamento', 'Não especificada')
        
        parcelas = gasto.get('parcelas')
        info_parcelas = f" ({parcelas}x)" if parcelas and forma == "Crédito" else ""
        
        resultado += (f"*{data}*: {formatar_valor(valor)}{info_parcelas}\n"
                    f"📍 {local}\n"
                    f"🏷️ {categoria}\n"
                    f"💳 {forma}\n\n")
    
    resultado += f"\n*TOTAL: {formatar_valor(total)}*"
    return resultado

def obter_nome_mes(numero_mes):
    """Retorna o nome do mês a partir do número (1-12)"""
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    return meses.get(int(numero_mes), str(numero_mes))

def resumo_gastos_por_categoria(gastos):
    """Cria um resumo dos gastos agrupados por categoria"""
    if not gastos:
        return "Nenhum gasto encontrado para gerar o resumo."
    
    categorias = {}
    total = 0
    
    for gasto in gastos:
        valor = float(gasto.get('valor', 0))
        categoria = gasto.get('categoria', 'Não especificada')
        
        if categoria not in categorias:
            categorias[categoria] = 0
        
        categorias[categoria] += valor
        total += valor
    
    resultado = "📊 *RESUMO POR CATEGORIA* 📊\n\n"
    
    # Ordenar categorias por valor gasto (maior para menor)
    for categoria, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        porcentagem = (valor / total) * 100 if total > 0 else 0
        resultado += f"*{categoria}*: {formatar_valor(valor)} ({porcentagem:.1f}%)\n"
    
    resultado += f"\n*TOTAL: {formatar_valor(total)}*"
    return resultado 