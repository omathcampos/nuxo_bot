import logging
import os
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    Filters
)
from flask import Flask
import threading

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importar configurações e handlers
from config import TELEGRAM_BOT_TOKEN
from app.handlers.start import start_command, help_command, menu_callback
from app.handlers.registro_gastos import (
    registrar_command, registrar_callback, valor_handler, data_handler,
    forma_pagamento_handler, parcelas_handler, categoria_handler,
    local_handler, confirmar_handler, cancel_handler, VALOR, DATA,
    FORMA_PAGAMENTO, PARCELAS, CATEGORIA, LOCAL, CONFIRMAR
)
from app.handlers.visualizacao import (
    visualizar_command, visualizar_callback, ano_handler, mes_handler,
    forma_pagamento_handler as visualizar_forma_handler, visualizar_novo_callback,
    categoria_handler as visualizar_categoria_handler,
    ESCOLHER_ANO, ESCOLHER_MES, ESCOLHER_FORMA_PAGAMENTO, ESCOLHER_CATEGORIA
)
from app.handlers.exportacao import (
    exportar_command, exportar_callback, ano_handler as exportar_ano_handler,
    mes_handler as exportar_mes_handler, categoria_handler as exportar_categoria_handler,
    categoria_callback as exportar_categoria_callback,
    ESCOLHER_ANO as EXP_ESCOLHER_ANO, ESCOLHER_MES as EXP_ESCOLHER_MES,
    ESCOLHER_CATEGORIA as EXP_ESCOLHER_CATEGORIA
)
from app.db.database import db

# Criar aplicação Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Nuxo Bot está funcionando!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def main():
    """Inicia o bot"""
    
    # Verificar se as variáveis de ambiente necessárias estão configuradas
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Token do Telegram não configurado!")
        return
    
    # Inicializar o Updater
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Handlers dos comandos básicos
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("ajuda", help_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # Conversation handler para registro de gastos
    registro_handler = ConversationHandler(
        entry_points=[
            CommandHandler("registrar", registrar_command),
            CallbackQueryHandler(registrar_callback, pattern="^registrar_gasto$")
        ],
        states={
            VALOR: [MessageHandler(Filters.text & ~Filters.command, valor_handler)],
            DATA: [
                MessageHandler(Filters.text & ~Filters.command, data_handler),
                CallbackQueryHandler(data_handler, pattern="^date_")
            ],
            FORMA_PAGAMENTO: [
                CallbackQueryHandler(forma_pagamento_handler, pattern="^pagamento_")
            ],
            PARCELAS: [
                CallbackQueryHandler(parcelas_handler, pattern="^parcelas_")
            ],
            CATEGORIA: [
                CallbackQueryHandler(categoria_handler, pattern="^categoria_")
            ],
            LOCAL: [
                MessageHandler(Filters.text & ~Filters.command, local_handler)
            ],
            CONFIRMAR: [
                CallbackQueryHandler(confirmar_handler, pattern="^confirmar_")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            CommandHandler("cancelar", cancel_handler),
        ],
    )
    dispatcher.add_handler(registro_handler)
    
    # Conversation handler para visualização de gastos
    visualizacao_handler = ConversationHandler(
        entry_points=[
            CommandHandler("visualizar", visualizar_command),
            CallbackQueryHandler(visualizar_callback, pattern="^visualizar_gastos$")
        ],
        states={
            ESCOLHER_ANO: [
                CallbackQueryHandler(ano_handler, pattern="^ano_")
            ],
            ESCOLHER_MES: [
                CallbackQueryHandler(mes_handler, pattern="^mes_")
            ],
            ESCOLHER_FORMA_PAGAMENTO: [
                CallbackQueryHandler(visualizar_forma_handler, pattern="^forma_")
            ],
            ESCOLHER_CATEGORIA: [
                CallbackQueryHandler(visualizar_categoria_handler, pattern="^cat_")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            CommandHandler("cancelar", cancel_handler),
        ],
    )
    dispatcher.add_handler(visualizacao_handler)
    
    # Conversation handler para exportação de gastos
    exportacao_handler = ConversationHandler(
        entry_points=[
            CommandHandler("exportar", exportar_command),
            CallbackQueryHandler(exportar_callback, pattern="^exportar_excel$")
        ],
        states={
            EXP_ESCOLHER_ANO: [
                CallbackQueryHandler(exportar_ano_handler, pattern="^exp_ano_")
            ],
            EXP_ESCOLHER_MES: [
                CallbackQueryHandler(exportar_mes_handler, pattern="^exp_mes_")
            ],
            EXP_ESCOLHER_CATEGORIA: [
                CallbackQueryHandler(exportar_categoria_callback, pattern="^exp_cat_")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_handler),
            CommandHandler("cancelar", cancel_handler),
        ],
    )
    dispatcher.add_handler(exportacao_handler)
    
    # Handler para callbacks do menu principal
    dispatcher.add_handler(CallbackQueryHandler(menu_callback, pattern="^(start|ajuda)$"))
    
    # Handler para nova consulta de visualização
    dispatcher.add_handler(CallbackQueryHandler(visualizar_novo_callback, pattern="^visualizar_novo$"))
    
    # Iniciar o bot em um thread separado
    updater.start_polling()
    
    # Iniciar o servidor web
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Manter o bot em execução
    updater.idle()
    
    logger.info("Bot iniciado!")

if __name__ == "__main__":
    try:
        # Verificar conexão com o banco de dados
        logger.info("Verificando conexão com o banco de dados...")
        
        # Criar diretório de exportação se não existir
        if not os.path.exists('exports'):
            os.makedirs('exports')
            
        main()
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}") 