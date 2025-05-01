from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from app.db.database import db
from config import CATEGORIAS, FORMAS_PAGAMENTO
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Estados da conversa
VALOR, DATA, FORMA_PAGAMENTO, PARCELAS, CATEGORIA, LOCAL, CONFIRMAR = range(7)

# Comandos de cancelamento
CANCEL_COMMANDS = ['/cancel', '/cancelar', 'cancelar']

def registrar_command(update: Update, context: CallbackContext):
    """
    Inicia o processo de registro de um novo gasto
    """
    return iniciar_registro(update, context)

def registrar_callback(update: Update, context: CallbackContext):
    """
    Handler para o callback de registro de gastos
    """
    query = update.callback_query
    query.answer()
    
    # Edita a mensagem original para iniciar o registro
    query.edit_message_text(
        text="Vamos registrar um novo gasto! 📝\n\n" 
             "Para cancelar a qualquer momento, envie /cancelar.",
        parse_mode='Markdown'
    )
    
    # Pede o valor do gasto
    query.message.reply_text(
        "Qual é o valor do gasto?\n"
        "📌 Digite apenas números (use ponto ou vírgula para centavos).\n"
        "Exemplo: 15.90 ou 15,90",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return VALOR

def iniciar_registro(update: Update, context: CallbackContext):
    """
    Inicia o processo de registro de um novo gasto
    """
    # Mensagem inicial
    update.message.reply_text(
        "Vamos registrar um novo gasto! 📝\n\n" 
        "Para cancelar a qualquer momento, envie /cancelar.",
        parse_mode='Markdown'
    )
    
    # Pede o valor do gasto
    update.message.reply_text(
        "Qual é o valor do gasto?\n"
        "📌 Digite apenas números (use ponto ou vírgula para centavos).\n"
        "Exemplo: 15.90 ou 15,90",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return VALOR

def valor_handler(update: Update, context: CallbackContext):
    """
    Recebe o valor do gasto e pede a data
    """
    user_input = update.message.text
    
    if user_input.lower() in CANCEL_COMMANDS:
        return cancel_handler(update, context)
    
    # Verifica se é um valor válido
    try:
        valor = user_input.replace(',', '.')
        valor = float(valor)
        
        if valor <= 0:
            update.message.reply_text(
                "O valor deve ser maior que zero. Por favor, digite novamente:"
            )
            return VALOR
            
        # Salva na conversa
        context.user_data['valor'] = valor
        
        # Pede a data
        today = datetime.now().strftime('%d/%m/%Y')
        
        keyboard = [
            [InlineKeyboardButton("Hoje", callback_data=f"date_{today}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "Qual a data do gasto?\n"
            "📌 Digite no formato DD/MM/AAAA ou clique em 'Hoje'",
            reply_markup=reply_markup
        )
        
        return DATA
        
    except ValueError:
        update.message.reply_text(
            "Valor inválido! Por favor, digite apenas números.\n"
            "Exemplo: 15.90 ou 15,90"
        )
        return VALOR

def data_handler(update: Update, context: CallbackContext):
    """
    Recebe a data do gasto e pede a forma de pagamento
    """
    # Verifica se veio de um callback (botão) ou texto
    if update.callback_query:
        query = update.callback_query
        query.answer()
        user_input = query.data.replace("date_", "")
        message = query.message
    else:
        user_input = update.message.text
        message = update.message
        
        if user_input.lower() in CANCEL_COMMANDS:
            return cancel_handler(update, context)
    
    # Valida o formato da data
    try:
        if update.callback_query:  # Se for do botão "Hoje", já está no formato correto
            data_obj = datetime.strptime(user_input, '%d/%m/%Y')
        else:
            # Tenta converter para o formato correto
            data_obj = datetime.strptime(user_input, '%d/%m/%Y')
        
        # Salva na conversa (formato ISO para o banco de dados)
        context.user_data['data'] = data_obj.strftime('%Y-%m-%d')
        context.user_data['data_display'] = data_obj.strftime('%d/%m/%Y')
        
        # Pede a forma de pagamento
        keyboard = []
        
        # Cria linhas com 2 botões cada
        row = []
        for i, forma in enumerate(FORMAS_PAGAMENTO):
            row.append(InlineKeyboardButton(forma, callback_data=f"pagamento_{forma}"))
            
            if (i + 1) % 2 == 0 or i == len(FORMAS_PAGAMENTO) - 1:
                keyboard.append(row)
                row = []
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message.reply_text(
            "Qual a forma de pagamento?",
            reply_markup=reply_markup
        )
        
        return FORMA_PAGAMENTO
        
    except ValueError:
        message.reply_text(
            "Formato de data inválido! Por favor, use o formato DD/MM/AAAA.\n"
            "Exemplo: 25/10/2023"
        )
        return DATA

def forma_pagamento_handler(update: Update, context: CallbackContext):
    """
    Recebe a forma de pagamento e, se for crédito, pede o número de parcelas
    """
    query = update.callback_query
    query.answer()
    
    forma_pagamento = query.data.replace("pagamento_", "")
    
    # Salva na conversa
    context.user_data['forma_pagamento'] = forma_pagamento
    
    # Se for crédito, pergunta o número de parcelas
    if forma_pagamento == "Crédito":
        # Cria botões para número de parcelas (1x a 12x)
        keyboard = []
        row = []
        
        for i in range(1, 13):
            texto = f"{i}x"
            row.append(InlineKeyboardButton(texto, callback_data=f"parcelas_{i}"))
            
            if i % 4 == 0:
                keyboard.append(row)
                row = []
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.message.reply_text(
            "Em quantas parcelas?",
            reply_markup=reply_markup
        )
        
        return PARCELAS
    
    # Se não for crédito, vai direto para categoria
    context.user_data['parcelas'] = None
    
    # Pede a categoria
    keyboard = []
    row = []
    
    for i, categoria in enumerate(CATEGORIAS):
        row.append(InlineKeyboardButton(categoria, callback_data=f"categoria_{categoria}"))
        
        if (i + 1) % 2 == 0 or i == len(CATEGORIAS) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.message.reply_text(
        "Qual a categoria do gasto?",
        reply_markup=reply_markup
    )
    
    return CATEGORIA

def parcelas_handler(update: Update, context: CallbackContext):
    """
    Recebe o número de parcelas e pede a categoria
    """
    query = update.callback_query
    query.answer()
    
    parcelas = int(query.data.replace("parcelas_", ""))
    
    # Salva na conversa
    context.user_data['parcelas'] = parcelas
    
    # Pede a categoria
    keyboard = []
    row = []
    
    for i, categoria in enumerate(CATEGORIAS):
        row.append(InlineKeyboardButton(categoria, callback_data=f"categoria_{categoria}"))
        
        if (i + 1) % 2 == 0 or i == len(CATEGORIAS) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.message.reply_text(
        "Qual a categoria do gasto?",
        reply_markup=reply_markup
    )
    
    return CATEGORIA

def categoria_handler(update: Update, context: CallbackContext):
    """
    Recebe a categoria e pede o local/estabelecimento
    """
    query = update.callback_query
    query.answer()
    
    categoria = query.data.replace("categoria_", "")
    
    # Salva na conversa
    context.user_data['categoria'] = categoria
    
    # Pede o local do gasto
    query.message.reply_text(
        "Qual o local/estabelecimento do gasto?\n"
        "📌 Digite o nome do estabelecimento ou loja."
    )
    
    return LOCAL

def local_handler(update: Update, context: CallbackContext):
    """
    Recebe o local/estabelecimento e pede confirmação
    """
    user_input = update.message.text
    
    if user_input.lower() in CANCEL_COMMANDS:
        return cancel_handler(update, context)
    
    # Salva na conversa
    context.user_data['local'] = user_input
    
    # Prepara o resumo para confirmação
    dados = context.user_data
    
    info_parcelas = ""
    if dados.get('forma_pagamento') == "Crédito" and dados.get('parcelas'):
        info_parcelas = f" em {dados['parcelas']}x"
    
    resumo = (
        "*📝 RESUMO DO GASTO*\n\n"
        f"*Valor:* R$ {dados['valor']:.2f}\n"
        f"*Data:* {dados['data_display']}\n"
        f"*Forma de pagamento:* {dados['forma_pagamento']}{info_parcelas}\n"
        f"*Categoria:* {dados['categoria']}\n"
        f"*Local:* {dados['local']}\n\n"
        "Os dados estão corretos?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_sim"),
            InlineKeyboardButton("❌ Cancelar", callback_data="confirmar_nao")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        text=resumo,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return CONFIRMAR

def confirmar_handler(update: Update, context: CallbackContext):
    """
    Processa a confirmação final do registro de gasto
    """
    query = update.callback_query
    query.answer()
    
    resposta = query.data.replace("confirmar_", "")
    
    if resposta == "nao":
        query.message.reply_text(
            "Registro cancelado. Use /registrar para começar novamente."
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    # Confirmado, salva no banco de dados
    dados = context.user_data
    
    # Obter ID do usuário
    usuario_id = db.registrar_usuario(update.effective_user.id, update.effective_user.first_name)
    
    if not usuario_id:
        query.message.reply_text(
            "Erro ao identificar usuário. Por favor, tente novamente mais tarde."
        )
        return ConversationHandler.END
    
    # Registra o gasto
    resultado = db.registrar_gasto(
        usuario_id=usuario_id,
        valor=dados['valor'],
        forma_pagamento=dados['forma_pagamento'],
        parcelas=dados.get('parcelas'),
        categoria=dados['categoria'],
        local=dados['local'],
        data=dados['data']
    )
    
    if resultado:
        # Sucesso!
        query.message.reply_text(
            "✅ Gasto registrado com sucesso!\n\n"
            "Use /registrar para registrar um novo gasto ou /start para voltar ao menu principal."
        )
    else:
        # Falha
        query.message.reply_text(
            "❌ Houve um erro ao registrar o gasto. Por favor, tente novamente."
        )
    
    # Limpa os dados da conversa
    context.user_data.clear()
    
    return ConversationHandler.END

def cancel_handler(update: Update, context: CallbackContext):
    """
    Cancela o registro em andamento
    """
    update.message.reply_text(
        "Operação cancelada. Use /start para voltar ao menu principal."
    )
    
    # Limpa os dados da conversa
    context.user_data.clear()
    
    return ConversationHandler.END

# Definir o conversation handler para registro de gastos
registro_conv_handler = ConversationHandler(
    entry_points=[
        # Comando direto
        # Callback do menu principal já é tratado na função registrar_callback
    ],
    states={
        VALOR: [
            # Handler para o valor digitado
        ],
        DATA: [
            # Handler para a data
        ],
        FORMA_PAGAMENTO: [
            # Handler para a forma de pagamento
        ],
        PARCELAS: [
            # Handler para as parcelas (só se for crédito)
        ],
        CATEGORIA: [
            # Handler para a categoria
        ],
        LOCAL: [
            # Handler para o local
        ],
        CONFIRMAR: [
            # Handler para a confirmação
        ],
    },
    fallbacks=[
        # Comandos para cancelar
    ],
) 