from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from app.db.database import db
from app.utils.formatters import formatar_lista_gastos, obter_nome_mes, resumo_gastos_por_categoria
from config import FORMAS_PAGAMENTO, CATEGORIAS
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Estados da conversa
ESCOLHER_ANO, ESCOLHER_MES, ESCOLHER_FORMA_PAGAMENTO, ESCOLHER_CATEGORIA = range(4)

def visualizar_command(update: Update, context: CallbackContext):
    """
    Comando para iniciar a visualização de gastos
    """
    return iniciar_visualizacao(update, context)

def visualizar_callback(update: Update, context: CallbackContext):
    """
    Handler para o callback de visualização de gastos
    """
    query = update.callback_query
    query.answer()
    
    # Edita a mensagem original para iniciar a visualização
    query.edit_message_text(
        "Vamos visualizar seus gastos! 📊\n\n"
        "Primeiro, vamos definir o período."
    )
    
    # Pergunta o ano
    return perguntar_ano(query.message, context)

def iniciar_visualizacao(update: Update, context: CallbackContext):
    """
    Inicia o processo de visualização de gastos
    """
    # Mensagem inicial
    update.message.reply_text(
        "Vamos visualizar seus gastos! 📊\n\n"
        "Primeiro, vamos definir o período."
    )
    
    # Pergunta o ano
    return perguntar_ano(update.message, context)

def perguntar_ano(message, context: CallbackContext):
    """
    Pergunta o ano para visualização
    """
    # Anos disponíveis (próximo ano, ano atual e 2 anteriores)
    ano_atual = datetime.now().year
    anos = [ano_atual + 1, ano_atual, ano_atual - 1, ano_atual - 2]
    
    # Botões para os anos
    keyboard = []
    
    # Adiciona os anos como botões
    for ano in anos:
        keyboard.append([InlineKeyboardButton(str(ano), callback_data=f"ano_{ano}")])
    
    # Opção para todos os anos
    keyboard.append([InlineKeyboardButton("Todos os anos", callback_data="ano_todos")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message.reply_text(
        "Selecione o ano:",
        reply_markup=reply_markup
    )
    
    return ESCOLHER_ANO

def ano_handler(update: Update, context: CallbackContext):
    """
    Recebe o ano escolhido e pergunta o mês
    """
    query = update.callback_query
    query.answer()
    
    ano_str = query.data.replace("ano_", "")
    
    if ano_str == "todos":
        # Usuário escolheu todos os anos
        context.user_data['ano'] = None
        
        # Pula a seleção de mês e vai para forma de pagamento
        return forma_pagamento_handler(update, context, perguntar=True)
    else:
        # Ano específico
        context.user_data['ano'] = int(ano_str)
        
        # Pergunta o mês
        keyboard = []
        row = []
        
        # Adiciona os meses em grupos de 3
        for i in range(1, 13):
            nome_mes = obter_nome_mes(i)
            row.append(InlineKeyboardButton(nome_mes, callback_data=f"mes_{i}"))
            
            if i % 3 == 0:
                keyboard.append(row)
                row = []
        
        # Adiciona opção para todos os meses
        keyboard.append([InlineKeyboardButton("Todos os meses", callback_data="mes_todos")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            f"Ano selecionado: {ano_str}\n\n"
            "Agora selecione o mês:",
            reply_markup=reply_markup
        )
        
        return ESCOLHER_MES

def mes_handler(update: Update, context: CallbackContext):
    """
    Recebe o mês escolhido e pergunta a forma de pagamento
    """
    query = update.callback_query
    query.answer()
    
    mes_str = query.data.replace("mes_", "")
    
    if mes_str == "todos":
        # Usuário escolheu todos os meses
        context.user_data['mes'] = None
    else:
        # Mês específico
        mes = int(mes_str)
        context.user_data['mes'] = mes
        context.user_data['nome_mes'] = obter_nome_mes(mes)
    
    # Pergunta a forma de pagamento
    return forma_pagamento_handler(update, context, perguntar=True)

def forma_pagamento_handler(update: Update, context: CallbackContext, perguntar=False):
    """
    Pergunta ou processa a forma de pagamento escolhida
    """
    if perguntar:
        # É uma pergunta, não uma resposta
        query = update.callback_query
        
        # Prepara os botões para formas de pagamento
        keyboard = []
        
        # Adiciona as formas de pagamento
        for forma in FORMAS_PAGAMENTO:
            keyboard.append([InlineKeyboardButton(forma, callback_data=f"forma_{forma}")])
        
        # Adiciona opção para todas as formas
        keyboard.append([InlineKeyboardButton("Todas as formas", callback_data="forma_todas")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Texto da mensagem com base no período selecionado
        ano = context.user_data.get('ano')
        mes = context.user_data.get('mes')
        
        if ano and mes:
            periodo = f"{obter_nome_mes(mes)} de {ano}"
        elif ano:
            periodo = f"Ano de {ano}"
        else:
            periodo = "Todo o período"
        
        query.edit_message_text(
            f"Período selecionado: {periodo}\n\n"
            "Agora selecione a forma de pagamento:",
            reply_markup=reply_markup
        )
        
        return ESCOLHER_FORMA_PAGAMENTO
    
    else:
        # É uma resposta com a forma escolhida
        query = update.callback_query
        query.answer()
        
        forma_str = query.data.replace("forma_", "")
        
        if forma_str == "todas":
            # Usuário escolheu todas as formas
            context.user_data['forma_pagamento'] = None
        else:
            # Forma específica
            context.user_data['forma_pagamento'] = forma_str
        
        # Pergunta a categoria
        return categoria_handler(update, context, perguntar=True)

def categoria_handler(update: Update, context: CallbackContext, perguntar=False):
    """
    Pergunta ou processa a categoria escolhida
    """
    if perguntar:
        # É uma pergunta, não uma resposta
        query = update.callback_query
        
        # Prepara os botões para categorias
        keyboard = []
        row = []
        
        # Adiciona as categorias em grupos de 2
        for i, categoria in enumerate(CATEGORIAS):
            row.append(InlineKeyboardButton(categoria, callback_data=f"cat_{categoria}"))
            
            if (i + 1) % 2 == 0 or i == len(CATEGORIAS) - 1:
                keyboard.append(row)
                row = []
        
        # Adiciona opção para todas as categorias
        keyboard.append([InlineKeyboardButton("Todas as categorias", callback_data="cat_todas")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Texto da mensagem com base no período e forma de pagamento selecionados
        ano = context.user_data.get('ano')
        mes = context.user_data.get('mes')
        forma_pagamento = context.user_data.get('forma_pagamento')
        
        # Preparar descrição do período
        if ano and mes:
            periodo = f"{obter_nome_mes(mes)} de {ano}"
        elif ano:
            periodo = f"Ano de {ano}"
        else:
            periodo = "Todo o período"
        
        # Adicionar informação da forma de pagamento
        if forma_pagamento:
            periodo += f" - {forma_pagamento}"
        
        query.edit_message_text(
            f"Filtros selecionados: {periodo}\n\n"
            "Agora selecione a categoria:",
            reply_markup=reply_markup
        )
        
        return ESCOLHER_CATEGORIA
    
    else:
        # É uma resposta com a categoria escolhida
        query = update.callback_query
        query.answer()
        
        categoria_str = query.data.replace("cat_", "")
        
        if categoria_str == "todas":
            # Usuário escolheu todas as categorias
            context.user_data['categoria'] = None
        else:
            # Categoria específica
            context.user_data['categoria'] = categoria_str
        
        # Busca os gastos com os filtros
        return mostrar_gastos(update, context)

def mostrar_gastos(update: Update, context: CallbackContext):
    """
    Mostra a lista de gastos com os filtros selecionados
    """
    query = update.callback_query
    
    # Obter dados do usuário
    usuario_id = db.registrar_usuario(update.effective_user.id, update.effective_user.first_name)
    
    if not usuario_id:
        query.edit_message_text(
            "Erro ao identificar usuário. Por favor, tente novamente mais tarde."
        )
        return ConversationHandler.END
    
    # Obter filtros
    filtros = context.user_data
    ano = filtros.get('ano')
    mes = filtros.get('mes')
    forma_pagamento = filtros.get('forma_pagamento')
    categoria = filtros.get('categoria')
    
    # Buscar gastos
    gastos = db.obter_gastos(
        usuario_id=usuario_id,
        ano=ano,
        mes=mes,
        forma_pagamento=forma_pagamento,
        categoria=categoria
    )
    
    # Preparar texto do período para exibição
    if ano and mes:
        periodo = f"{obter_nome_mes(mes)} de {ano}"
    elif ano:
        periodo = f"Ano de {ano}"
    else:
        periodo = "Todo o período"
    
    # Adicionar informação dos filtros aplicados
    filtros_texto = []
    
    if forma_pagamento:
        filtros_texto.append(f"Forma: {forma_pagamento}")
    
    if categoria:
        filtros_texto.append(f"Categoria: {categoria}")
    
    if filtros_texto:
        periodo += f" ({', '.join(filtros_texto)})"
    
    # Formatar os gastos
    texto_gastos = formatar_lista_gastos(gastos)
    
    # Texto resumo por categoria
    texto_categorias = resumo_gastos_por_categoria(gastos)
    
    # Botões para navegar
    keyboard = [
        [InlineKeyboardButton("🔍 Nova consulta", callback_data="visualizar_novo")],
        [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="start")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Exibe o resultado
    try:
        # Tenta enviar o resumo por categoria primeiro
        query.edit_message_text(
            f"*📊 GASTOS: {periodo}*\n\n"
            f"{texto_categorias}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Depois envia a lista completa de gastos
        query.message.reply_text(
            f"*📋 DETALHAMENTO: {periodo}*\n\n"
            f"{texto_gastos}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Erro ao exibir gastos: {e}")
        query.edit_message_text(
            "Houve um erro ao exibir os gastos. Por favor, tente novamente."
        )
    
    # Limpa os dados da consulta
    context.user_data.clear()
    
    return ConversationHandler.END

def visualizar_novo_callback(update: Update, context: CallbackContext):
    """
    Callback para iniciar uma nova consulta
    """
    query = update.callback_query
    query.answer()
    
    # Limpa dados anteriores
    context.user_data.clear()
    
    # Inicia nova consulta
    query.edit_message_text(
        "Vamos visualizar seus gastos! 📊\n\n"
        "Primeiro, vamos definir o período."
    )
    
    # Pergunta o ano
    return perguntar_ano(query.message, context)

# Definir o conversation handler para visualização de gastos
visualizacao_conv_handler = ConversationHandler(
    entry_points=[
        # Comando direto
        # Callback do menu principal já é tratado na função visualizar_callback
    ],
    states={
        ESCOLHER_ANO: [
            # Handler para o ano escolhido
        ],
        ESCOLHER_MES: [
            # Handler para o mês escolhido
        ],
        ESCOLHER_FORMA_PAGAMENTO: [
            # Handler para a forma de pagamento
        ],
        ESCOLHER_CATEGORIA: [
            # Handler para a categoria escolhida
        ],
    },
    fallbacks=[
        # Comandos para cancelar
    ],
) 