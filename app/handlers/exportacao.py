from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from app.db.database import db
from app.exports.excel_exporter import exportar_gastos_para_excel
from app.utils.formatters import obter_nome_mes
from config import CATEGORIAS
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Estados da conversa
ESCOLHER_ANO, ESCOLHER_MES, ESCOLHER_CATEGORIA = range(3)

def exportar_command(update: Update, context: CallbackContext):
    """
    Comando para iniciar a exportação de gastos para Excel
    """
    return iniciar_exportacao(update, context)

def exportar_callback(update: Update, context: CallbackContext):
    """
    Handler para o callback de exportação de gastos
    """
    query = update.callback_query
    query.answer()
    
    # Edita a mensagem original para iniciar a exportação
    query.edit_message_text(
        "Vamos exportar seus gastos para uma planilha Excel! 📊\n\n"
        "Primeiro, vamos definir o período."
    )
    
    # Pergunta o ano
    return perguntar_ano(query.message, context)

def iniciar_exportacao(update: Update, context: CallbackContext):
    """
    Inicia o processo de exportação de gastos
    """
    # Mensagem inicial
    update.message.reply_text(
        "Vamos exportar seus gastos para uma planilha Excel! 📊\n\n"
        "Primeiro, vamos definir o período."
    )
    
    # Pergunta o ano
    return perguntar_ano(update.message, context)

def perguntar_ano(message, context: CallbackContext):
    """
    Pergunta o ano para exportação
    """
    # Anos disponíveis (próximo ano, ano atual e 2 anteriores)
    ano_atual = datetime.now().year
    anos = [ano_atual + 1, ano_atual, ano_atual - 1, ano_atual - 2]
    
    # Botões para os anos
    keyboard = []
    
    # Adiciona os anos como botões
    for ano in anos:
        keyboard.append([InlineKeyboardButton(str(ano), callback_data=f"exp_ano_{ano}")])
    
    # Opção para todos os anos
    keyboard.append([InlineKeyboardButton("Todos os anos", callback_data="exp_ano_todos")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message.reply_text(
        "Selecione o ano para exportação:",
        reply_markup=reply_markup
    )
    
    return ESCOLHER_ANO

def ano_handler(update: Update, context: CallbackContext):
    """
    Recebe o ano escolhido e pergunta o mês
    """
    query = update.callback_query
    query.answer()
    
    ano_str = query.data.replace("exp_ano_", "")
    
    if ano_str == "todos":
        # Usuário escolheu todos os anos
        context.user_data['exp_ano'] = None
        
        # Exportar todos os gastos
        query.edit_message_text(
            "Preparando exportação de todos os gastos...\n"
            "Isso pode levar alguns segundos."
        )
        
        return exportar_gastos(update, context)
    else:
        # Ano específico
        context.user_data['exp_ano'] = int(ano_str)
        
        # Pergunta o mês
        keyboard = []
        row = []
        
        # Adiciona os meses em grupos de 3
        for i in range(1, 13):
            nome_mes = obter_nome_mes(i)
            row.append(InlineKeyboardButton(nome_mes, callback_data=f"exp_mes_{i}"))
            
            if i % 3 == 0:
                keyboard.append(row)
                row = []
        
        # Adiciona opção para todos os meses
        keyboard.append([InlineKeyboardButton("Todos os meses", callback_data="exp_mes_todos")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            f"Ano selecionado: {ano_str}\n\n"
            "Agora selecione o mês:",
            reply_markup=reply_markup
        )
        
        return ESCOLHER_MES

def mes_handler(update: Update, context: CallbackContext):
    """
    Recebe o mês escolhido e pergunta a categoria
    """
    query = update.callback_query
    query.answer()
    
    mes_str = query.data.replace("exp_mes_", "")
    
    if mes_str == "todos":
        # Usuário escolheu todos os meses
        context.user_data['exp_mes'] = None
    else:
        # Mês específico
        mes = int(mes_str)
        context.user_data['exp_mes'] = mes
        context.user_data['exp_nome_mes'] = obter_nome_mes(mes)
    
    # Pergunta a categoria
    return categoria_handler(update, context)

def categoria_handler(update: Update, context: CallbackContext):
    """
    Pergunta e processa a categoria para exportação
    """
    query = update.callback_query
    
    # Prepara os botões para categorias
    keyboard = []
    row = []
    
    # Adiciona as categorias em grupos de 2
    for i, categoria in enumerate(CATEGORIAS):
        row.append(InlineKeyboardButton(categoria, callback_data=f"exp_cat_{categoria}"))
        
        if (i + 1) % 2 == 0 or i == len(CATEGORIAS) - 1:
            keyboard.append(row)
            row = []
    
    # Adiciona opção para todas as categorias
    keyboard.append([InlineKeyboardButton("Todas as categorias", callback_data="exp_cat_todas")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Texto da mensagem com base no período selecionado
    ano = context.user_data.get('exp_ano')
    mes = context.user_data.get('exp_mes')
    
    if ano and mes:
        periodo = f"{obter_nome_mes(mes)} de {ano}"
    elif ano:
        periodo = f"Ano de {ano}"
    else:
        periodo = "Todo o período"
    
    query.edit_message_text(
        f"Período selecionado: {periodo}\n\n"
        "Agora selecione a categoria para exportação:",
        reply_markup=reply_markup
    )
    
    return ESCOLHER_CATEGORIA

def categoria_callback(update: Update, context: CallbackContext):
    """
    Recebe a categoria escolhida e exporta os gastos
    """
    query = update.callback_query
    query.answer()
    
    categoria_str = query.data.replace("exp_cat_", "")
    
    if categoria_str == "todas":
        # Usuário escolheu todas as categorias
        context.user_data['exp_categoria'] = None
    else:
        # Categoria específica
        context.user_data['exp_categoria'] = categoria_str
    
    # Mensagem de preparação
    query.edit_message_text(
        "Preparando exportação...\n"
        "Isso pode levar alguns segundos."
    )
    
    # Exporta os gastos
    return exportar_gastos(update, context)

def exportar_gastos(update: Update, context: CallbackContext):
    """
    Exporta os gastos para um arquivo Excel
    """
    query = update.callback_query
    
    # Obter dados do usuário
    usuario_id = db.registrar_usuario(update.effective_user.id, update.effective_user.first_name)
    nome_usuario = update.effective_user.first_name
    
    if not usuario_id:
        query.edit_message_text(
            "Erro ao identificar usuário. Por favor, tente novamente mais tarde."
        )
        return ConversationHandler.END
    
    # Obter filtros
    filtros = context.user_data
    ano = filtros.get('exp_ano')
    mes = filtros.get('exp_mes')
    categoria = filtros.get('exp_categoria')
    
    # Buscar gastos
    gastos = db.obter_gastos(
        usuario_id=usuario_id,
        ano=ano,
        mes=mes,
        categoria=categoria
    )
    
    if not gastos:
        # Sem gastos para exportar
        keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "Não há gastos para exportar no período selecionado.",
            reply_markup=reply_markup
        )
        
        # Limpa os dados da consulta
        context.user_data.clear()
        
        return ConversationHandler.END
    
    # Exportar para Excel
    arquivo_excel = exportar_gastos_para_excel(gastos, nome_usuario)
    
    if not arquivo_excel or not os.path.exists(arquivo_excel):
        # Falha na exportação
        keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "Houve um erro ao exportar os gastos. Por favor, tente novamente.",
            reply_markup=reply_markup
        )
        
        # Limpa os dados da consulta
        context.user_data.clear()
        
        return ConversationHandler.END
    
    # Preparar texto do período para exibição
    if ano and mes:
        periodo = f"{obter_nome_mes(mes)} de {ano}"
    elif ano:
        periodo = f"Ano de {ano}"
    else:
        periodo = "Todo o período"
    
    # Adicionar informação da categoria se houver
    if categoria:
        periodo += f" - Categoria: {categoria}"
    
    # Enviar o arquivo
    try:
        with open(arquivo_excel, 'rb') as arquivo:
            query.message.reply_document(
                document=arquivo,
                filename=os.path.basename(arquivo_excel),
                caption=f"📊 Gastos exportados - {periodo}"
            )
        
        # Atualiza a mensagem original
        keyboard = [
            [InlineKeyboardButton("📊 Nova exportação", callback_data="exportar_excel")],
            [InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            f"✅ Exportação concluída para o período: {periodo}\n\n"
            "A planilha foi enviada como um documento.",
            reply_markup=reply_markup
        )
        
        # Remover o arquivo após enviar
        try:
            os.remove(arquivo_excel)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Erro ao enviar arquivo Excel: {e}")
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            "Houve um erro ao enviar o arquivo. Por favor, tente novamente.",
            reply_markup=reply_markup
        )
    
    # Limpa os dados da consulta
    context.user_data.clear()
    
    return ConversationHandler.END

# Definir o conversation handler para exportação de gastos
exportar_conv_handler = ConversationHandler(
    entry_points=[
        # Comando direto
        # Callback do menu principal já é tratado na função exportar_callback
    ],
    states={
        ESCOLHER_ANO: [
            # Handler para o ano escolhido
        ],
        ESCOLHER_MES: [
            # Handler para o mês escolhido
        ],
        ESCOLHER_CATEGORIA: [
            # Handler para a categoria escolhida
        ],
    },
    fallbacks=[
        # Comandos para cancelar
    ],
) 