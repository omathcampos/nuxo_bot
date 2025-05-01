from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from app.db.database import db
import logging

logger = logging.getLogger(__name__)

def start_command(update: Update, context: CallbackContext):
    """
    Manipula o comando /start, registra o usuário e exibe as boas-vindas
    """
    user = update.effective_user
    
    # Registrar usuário no banco de dados
    usuario_id = db.registrar_usuario(user.id, user.first_name)
    
    if not usuario_id:
        logger.error(f"Falha ao registrar usuário: {user.id}")
    
    # Mensagem de boas-vindas
    welcome_message = (
        f"Olá, *{user.first_name}*! Bem-vindo ao *Nuxo Bot* 🤖\n\n"
        f"*Organização que parece mágica, mas é só Nuxo.*\n\n"
        f"Estou aqui para ajudar com suas finanças. Confira o que posso fazer por você:"
    )
    
    # Menu principal com botões
    keyboard = [
        [InlineKeyboardButton("📝 Registrar Gasto", callback_data="registrar_gasto")],
        [InlineKeyboardButton("📊 Visualizar Gastos", callback_data="visualizar_gastos")],
        [InlineKeyboardButton("📋 Exportar para Excel", callback_data="exportar_excel")],
        [InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        text=welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def help_command(update: Update, context: CallbackContext):
    """
    Manipula o comando /ajuda, mostrando instruções de uso do bot
    """
    help_text = (
        "*🤖 Ajuda do Nuxo Bot 🤖*\n\n"
        "Aqui estão os comandos que você pode usar:\n\n"
        "*/start* - Inicia o bot e mostra o menu principal\n"
        "*/registrar* - Inicia o processo de registro de um novo gasto\n"
        "*/visualizar* - Mostra opções para visualizar seus gastos\n"
        "*/exportar* - Exporta seus gastos para uma planilha Excel\n"
        "*/ajuda* - Mostra esta mensagem de ajuda\n\n"
        
        "*Como registrar um gasto:*\n"
        "1. Use o comando /registrar ou o botão \"Registrar Gasto\"\n"
        "2. Siga as instruções para informar valor, data, categoria, etc.\n"
        "3. Para pagamentos com cartão de crédito, você poderá informar o número de parcelas\n\n"
        
        "*Como visualizar gastos:*\n"
        "1. Use o comando /visualizar ou o botão \"Visualizar Gastos\"\n"
        "2. Escolha o período desejado (ano e mês)\n"
        "3. Você também pode filtrar por forma de pagamento\n\n"
        
        "*Dicas:*\n"
        "• Registre seus gastos regularmente para ter um controle preciso\n"
        "• Exporte para Excel para análises mais detalhadas\n"
        "• Use categorias consistentes para facilitar o acompanhamento\n\n"
        
        "Qualquer dúvida, use o comando /ajuda a qualquer momento."
    )
    
    update.message.reply_text(
        text=help_text,
        parse_mode='Markdown'
    )

def menu_callback(update: Update, context: CallbackContext):
    """
    Manipula callbacks do menu principal
    """
    query = update.callback_query
    query.answer()
    
    option = query.data
    
    # Encaminha para o handler apropriado
    if option == "ajuda":
        help_text = (
            "*🤖 Ajuda do Nuxo Bot 🤖*\n\n"
            "Aqui estão os comandos que você pode usar:\n\n"
            "*/start* - Inicia o bot e mostra o menu principal\n"
            "*/registrar* - Inicia o processo de registro de um novo gasto\n"
            "*/visualizar* - Mostra opções para visualizar seus gastos\n"
            "*/exportar* - Exporta seus gastos para uma planilha Excel\n"
            "*/ajuda* - Mostra esta mensagem de ajuda\n\n"
            
            "*Como registrar um gasto:*\n"
            "1. Use o comando /registrar ou o botão \"Registrar Gasto\"\n"
            "2. Siga as instruções para informar valor, data, categoria, etc.\n"
            "3. Para pagamentos com cartão de crédito, você poderá informar o número de parcelas\n\n"
            
            "*Como visualizar gastos:*\n"
            "1. Use o comando /visualizar ou o botão \"Visualizar Gastos\"\n"
            "2. Escolha o período desejado (ano e mês)\n"
            "3. Você também pode filtrar por forma de pagamento\n\n"
            
            "*Dicas:*\n"
            "• Registre seus gastos regularmente para ter um controle preciso\n"
            "• Exporte para Excel para análises mais detalhadas\n"
            "• Use categorias consistentes para facilitar o acompanhamento\n\n"
            
            "Qualquer dúvida, use o comando /ajuda a qualquer momento."
        )
        
        # Botão para voltar ao menu principal
        keyboard = [[InlineKeyboardButton("🔙 Voltar ao Menu Principal", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            text=help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif option == "start":
        # Volta para o menu principal
        welcome_message = (
            f"Olá, *{update.effective_user.first_name}*! Bem-vindo ao *Nuxo Bot* 🤖\n\n"
            f"*Organização que parece mágica, mas é só Nuxo.*\n\n"
            f"Estou aqui para ajudar com suas finanças. Confira o que posso fazer por você:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📝 Registrar Gasto", callback_data="registrar_gasto")],
            [InlineKeyboardButton("📊 Visualizar Gastos", callback_data="visualizar_gastos")],
            [InlineKeyboardButton("📋 Exportar para Excel", callback_data="exportar_excel")],
            [InlineKeyboardButton("❓ Ajuda", callback_data="ajuda")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.edit_message_text(
            text=welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # Outros callbacks serão tratados em seus respectivos módulos 