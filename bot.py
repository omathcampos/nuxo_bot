import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    filters
)
from database import Database

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Estados para a conversa de adicionar despesa
VALOR, LOCAL, CATEGORIA, FORMA_PAGAMENTO, PARCELAS = range(5)

# Estados para a conversa de gerar relatório
TIPO_RELATORIO, PERIODO_RELATORIO, FILTRO_RELATORIO = range(5, 8)

# Categorias pré-definidas
CATEGORIAS = [
    "Alimentação", "Transporte", "Moradia", "Saúde", 
    "Educação", "Lazer", "Vestuário", "Outros"
]

# Formas de pagamento
FORMAS_PAGAMENTO = [
    "Dinheiro", "Pix", "Cartão de Débito", "Cartão de Crédito"
]

# Opções de parcelas
PARCELAS_OPCOES = ["1", "2", "3", "4", "5", "6", "8", "10", "12"]

# Instância do banco de dados
db = Database()

# Migrar dados antigos se necessário
try:
    db.migrar_dados()
    logger.info("Verificação de migração de dados concluída")
except Exception as e:
    logger.error(f"Erro ao migrar dados: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para iniciar o bot"""
    await update.message.reply_text(
        f"Olá, {update.effective_user.first_name}! Bem-vindo ao seu bot de finanças pessoais.\n\n"
        "Comandos disponíveis:\n"
        "/registrar - Registrar nova despesa\n"
        "/gastos - Ver resumo de gastos por categoria\n"
        "/pagamentos - Ver gastos por forma de pagamento\n"
        "/relatorio - Gerar relatório em Excel\n"
        "/ajuda - Mostrar ajuda\n"
    )

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe as instruções de uso do bot"""
    await update.message.reply_text(
        "🤖 *Como usar o Bot de Finanças Pessoais* 🤖\n\n"
        "*Comandos:*\n"
        "/registrar - Inicia o processo de registrar uma nova despesa\n"
        "/gastos - Mostra um resumo dos seus gastos por categoria\n"
        "/pagamentos - Mostra gastos por forma de pagamento\n"
        "/relatorio - Gera um relatório em Excel das suas despesas\n\n"
        "*Registrando despesas:*\n"
        "1. Iniciar com /registrar\n"
        "2. Informar o valor (apenas números)\n"
        "3. Informar o local da compra\n"
        "4. Selecionar ou digitar a categoria\n"
        "5. Escolher a forma de pagamento\n"
        "6. Se for cartão de crédito, escolher o número de parcelas\n\n"
        "*Consultar gastos:*\n"
        "Digite 'gastos' ou use o comando /gastos para ver um resumo.\n"
        "Para ver detalhes de uma categoria, digite:\n"
        "'gastos categoria:nome_da_categoria'\n\n"
        "*Consultar por forma de pagamento:*\n"
        "Digite 'pagamentos' ou use o comando /pagamentos para ver um resumo.\n"
        "Para ver detalhes, digite: 'pagamentos forma:nome_da_forma'\n"
        "Exemplo: pagamentos forma:pix\n\n"
        "*Gerar relatórios:*\n"
        "Use /relatorio para gerar um relatório Excel com suas despesas.\n"
        "Você pode filtrar por período, categoria ou forma de pagamento."
    )

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o fluxo de registro de despesa"""
    await update.message.reply_text("Por favor, informe o valor da despesa:")
    return VALOR

async def receber_valor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o valor da despesa e pede o local"""
    valor_texto = update.message.text.replace(",", ".")
    
    # Verifica se o valor é um número válido
    try:
        valor = float(valor_texto)
        context.user_data["valor"] = valor
        await update.message.reply_text("Agora, informe o local da despesa:")
        return LOCAL
    except ValueError:
        await update.message.reply_text(
            "Por favor, informe um valor válido usando apenas números e ponto ou vírgula como separador decimal."
        )
        return VALOR

async def receber_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o local da despesa e pede a categoria"""
    context.user_data["local"] = update.message.text
    
    keyboard = [CATEGORIAS[i:i+2] for i in range(0, len(CATEGORIAS), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Selecione uma categoria ou digite uma nova:",
        reply_markup=reply_markup
    )
    return CATEGORIA

async def receber_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a categoria e pergunta a forma de pagamento"""
    context.user_data["categoria"] = update.message.text
    
    keyboard = [FORMAS_PAGAMENTO[i:i+2] for i in range(0, len(FORMAS_PAGAMENTO), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Selecione a forma de pagamento:",
        reply_markup=reply_markup
    )
    return FORMA_PAGAMENTO

async def receber_forma_pagamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe a forma de pagamento e pede parcelas se for cartão de crédito"""
    forma_pagamento = update.message.text
    context.user_data["forma_pagamento"] = forma_pagamento
    
    # Se for cartão de crédito, perguntar o número de parcelas
    if forma_pagamento == "Cartão de Crédito":
        keyboard = [PARCELAS_OPCOES[i:i+3] for i in range(0, len(PARCELAS_OPCOES), 3)]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "Em quantas parcelas?",
            reply_markup=reply_markup
        )
        return PARCELAS
    
    # Se não for crédito, finalizar o registro
    return await finalizar_registro(update, context)

async def receber_parcelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recebe o número de parcelas e finaliza o registro"""
    try:
        parcelas = int(update.message.text)
        context.user_data["parcelas"] = parcelas
        return await finalizar_registro(update, context)
    except ValueError:
        await update.message.reply_text(
            "Por favor, informe um número válido de parcelas."
        )
        return PARCELAS

async def finalizar_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Finaliza o registro da despesa com todos os dados coletados"""
    user_id = update.effective_user.id
    valor = context.user_data["valor"]
    local = context.user_data["local"]
    categoria = context.user_data["categoria"]
    forma_pagamento = context.user_data["forma_pagamento"]
    parcelas = context.user_data.get("parcelas", 1)  # Default é 1 parcela
    
    # Adicionar a despesa ao banco de dados
    db.adicionar_despesa(
        user_id=user_id, 
        valor=valor, 
        local=local, 
        categoria=categoria, 
        forma_pagamento=forma_pagamento, 
        parcelas=parcelas
    )
    
    # Mensagem de confirmação
    mensagem = f"✅ Despesa registrada com sucesso!\n\n"
    mensagem += f"Valor: R$ {valor:.2f}\n"
    mensagem += f"Local: {local}\n"
    mensagem += f"Categoria: {categoria}\n"
    mensagem += f"Forma de pagamento: {forma_pagamento}\n"
    
    if forma_pagamento == "Cartão de Crédito" and parcelas > 1:
        valor_parcela = round(valor / parcelas, 2)
        mensagem += f"Parcelas: {parcelas}x de R$ {valor_parcela:.2f}\n"
    
    await update.message.reply_text(mensagem)
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a operação atual"""
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END

async def gastos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o resumo de gastos por categoria"""
    user_id = update.effective_user.id
    texto = update.message.text.lower()
    
    # Verificar se há filtro de categoria
    match = re.search(r"categoria:(\w+)", texto)
    
    if match:
        # Mostrar gastos de uma categoria específica
        categoria = match.group(1)
        despesas = db.listar_despesas_por_categoria(user_id, categoria)
        
        if not despesas:
            await update.message.reply_text(f"Nenhuma despesa encontrada na categoria '{categoria}'.")
            return
        
        total = sum(d["valor"] for d in despesas)
        resposta = f"📊 *Despesas na categoria '{categoria}'*\n\n"
        
        for d in sorted(despesas, key=lambda x: x["data"], reverse=True):
            info_adicional = ""
            
            # Verificar se é uma compra parcelada
            if "parcelado" in d and d["parcelado"]:
                info_adicional = f" (Parcelado em {d['parcelas']}x de R$ {d['valor_parcela']:.2f})"
            elif "forma_pagamento" in d:
                info_adicional = f" ({d['forma_pagamento']})"
                    
            resposta += f"🔹 R$ {d['valor']:.2f} - {d['local']}{info_adicional} ({d['data']})\n"
        
        resposta += f"\n*Total:* R$ {total:.2f}"
        
        await update.message.reply_text(resposta)
    else:
        # Mostrar resumo por categoria
        categorias = db.listar_categorias(user_id)
        
        if not categorias:
            await update.message.reply_text("Você ainda não registrou nenhuma despesa.")
            return
        
        total_geral = sum(categorias.values())
        resposta = "📊 *Resumo de gastos por categoria*\n\n"
        
        for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            percentual = (valor / total_geral) * 100
            resposta += f"🔹 {cat.capitalize()}: R$ {valor:.2f} ({percentual:.1f}%)\n"
        
        resposta += f"\n*Total geral:* R$ {total_geral:.2f}"
        
        await update.message.reply_text(
            resposta + "\n\nPara ver detalhes de uma categoria, digite:\n"
            "'gastos categoria:nome_da_categoria'"
        )

async def pagamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe o resumo de gastos por forma de pagamento"""
    user_id = update.effective_user.id
    texto = update.message.text.lower()
    
    # Verificar se há filtro de forma de pagamento
    match = re.search(r"forma:(\w+)", texto)
    
    if match:
        # Converter o texto para o formato correto da forma de pagamento
        forma_text = match.group(1).lower()
        forma_pagamento = None
        
        # Tentar encontrar a forma de pagamento correspondente
        for forma in FORMAS_PAGAMENTO:
            if forma.lower().startswith(forma_text):
                forma_pagamento = forma
                break
        
        if not forma_pagamento:
            await update.message.reply_text(
                f"Forma de pagamento '{forma_text}' não encontrada. Opções disponíveis: {', '.join(FORMAS_PAGAMENTO)}"
            )
            return
        
        # Mostrar gastos de uma forma de pagamento específica
        despesas = db.listar_despesas_por_forma_pagamento(user_id, forma_pagamento)
        
        if not despesas:
            await update.message.reply_text(f"Nenhuma despesa encontrada com a forma de pagamento '{forma_pagamento}'.")
            return
        
        total = sum(d["valor"] for d in despesas)
        resposta = f"💳 *Despesas com {forma_pagamento}*\n\n"
        
        for d in sorted(despesas, key=lambda x: x["data"], reverse=True):
            info_parcela = ""
            # Verificar se é uma compra parcelada
            if "parcelado" in d and d["parcelado"]:
                info_parcela = f" (Parcelado em {d['parcelas']}x de R$ {d['valor_parcela']:.2f})"
                
            resposta += f"🔹 R$ {d['valor']:.2f} - {d['local']} - {d['categoria'].capitalize()}{info_parcela} ({d['data']})\n"
        
        resposta += f"\n*Total:* R$ {total:.2f}"
        
        await update.message.reply_text(resposta)
    else:
        # Mostrar resumo por forma de pagamento
        formas = db.listar_formas_pagamento(user_id)
        
        if not formas:
            await update.message.reply_text("Você ainda não registrou nenhuma despesa.")
            return
        
        total_geral = sum(formas.values())
        resposta = "💳 *Resumo de gastos por forma de pagamento*\n\n"
        
        for forma, valor in sorted(formas.items(), key=lambda x: x[1], reverse=True):
            percentual = (valor / total_geral) * 100
            resposta += f"🔹 {forma}: R$ {valor:.2f} ({percentual:.1f}%)\n"
        
        resposta += f"\n*Total geral:* R$ {total_geral:.2f}"
        
        await update.message.reply_text(
            resposta + "\n\nPara ver detalhes de uma forma de pagamento, digite:\n"
            "'pagamentos forma:nome_da_forma'"
        )

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o fluxo para gerar um relatório de despesas em Excel"""
    keyboard = [
        [
            InlineKeyboardButton("Relatório Completo", callback_data="relatorio_completo"),
        ],
        [
            InlineKeyboardButton("Filtrar por Período", callback_data="filtro_periodo"),
        ],
        [
            InlineKeyboardButton("Filtrar por Categoria", callback_data="filtro_categoria"),
        ],
        [
            InlineKeyboardButton("Filtrar por Forma de Pagamento", callback_data="filtro_pagamento"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Escolha o tipo de relatório que deseja gerar:",
        reply_markup=reply_markup
    )
    return TIPO_RELATORIO

async def processar_tipo_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do tipo de relatório"""
    query = update.callback_query
    await query.answer()
    
    tipo_relatorio = query.data
    context.user_data["tipo_relatorio"] = tipo_relatorio
    
    if tipo_relatorio == "relatorio_completo":
        # Gerar relatório completo sem filtros
        return await gerar_e_enviar_relatorio(update, context)
    
    elif tipo_relatorio == "filtro_periodo":
        # Oferecer opções de período
        keyboard = [
            [
                InlineKeyboardButton("Mês Atual", callback_data="periodo_mes"),
                InlineKeyboardButton("Ano Atual", callback_data="periodo_ano"),
            ],
            [
                InlineKeyboardButton("Todo o Histórico", callback_data="periodo_tudo"),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Selecione o período do relatório:",
            reply_markup=reply_markup
        )
        return PERIODO_RELATORIO
    
    elif tipo_relatorio == "filtro_categoria":
        # Oferecer opções de categorias
        keyboard = []
        for i in range(0, len(CATEGORIAS), 2):
            row = []
            row.append(InlineKeyboardButton(CATEGORIAS[i], callback_data=f"categoria_{CATEGORIAS[i].lower()}"))
            if i + 1 < len(CATEGORIAS):
                row.append(InlineKeyboardButton(CATEGORIAS[i+1], callback_data=f"categoria_{CATEGORIAS[i+1].lower()}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Selecione a categoria para o relatório:",
            reply_markup=reply_markup
        )
        return FILTRO_RELATORIO
    
    elif tipo_relatorio == "filtro_pagamento":
        # Oferecer opções de forma de pagamento
        keyboard = []
        for i in range(0, len(FORMAS_PAGAMENTO), 2):
            row = []
            row.append(InlineKeyboardButton(FORMAS_PAGAMENTO[i], callback_data=f"pagamento_{FORMAS_PAGAMENTO[i]}"))
            if i + 1 < len(FORMAS_PAGAMENTO):
                row.append(InlineKeyboardButton(FORMAS_PAGAMENTO[i+1], callback_data=f"pagamento_{FORMAS_PAGAMENTO[i+1]}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Selecione a forma de pagamento para o relatório:",
            reply_markup=reply_markup
        )
        return FILTRO_RELATORIO

async def processar_periodo_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do período do relatório"""
    query = update.callback_query
    await query.answer()
    
    periodo = query.data.replace("periodo_", "")
    context.user_data["periodo"] = periodo
    
    # Gerar relatório com o período selecionado
    return await gerar_e_enviar_relatorio(update, context)

async def processar_filtro_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do filtro de categoria ou forma de pagamento"""
    query = update.callback_query
    await query.answer()
    
    filtro = query.data
    
    if filtro.startswith("categoria_"):
        categoria = filtro.replace("categoria_", "")
        context.user_data["categoria"] = categoria
        context.user_data["forma_pagamento"] = None
    elif filtro.startswith("pagamento_"):
        forma_pagamento = filtro.replace("pagamento_", "")
        context.user_data["forma_pagamento"] = forma_pagamento
        context.user_data["categoria"] = None
    
    # Gerar relatório com o filtro selecionado
    return await gerar_e_enviar_relatorio(update, context)

async def gerar_e_enviar_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera e envia o relatório Excel"""
    user_id = update.effective_user.id
    query = update.callback_query
    
    # Informar que o relatório está sendo gerado
    await query.edit_message_text("🔄 Gerando relatório... Por favor, aguarde um momento.")
    
    # Obter parâmetros do relatório
    tipo_relatorio = context.user_data.get("tipo_relatorio")
    periodo = None
    categoria = None
    forma_pagamento = None
    
    if tipo_relatorio == "filtro_periodo" or "periodo" in context.user_data:
        periodo = context.user_data.get("periodo")
        if periodo == "tudo":
            periodo = None
    
    if tipo_relatorio == "filtro_categoria" or "categoria" in context.user_data:
        categoria = context.user_data.get("categoria")
    
    if tipo_relatorio == "filtro_pagamento" or "forma_pagamento" in context.user_data:
        forma_pagamento = context.user_data.get("forma_pagamento")
    
    # Gerar o relatório
    try:
        caminho_relatorio = db.gerar_relatorio_excel(
            user_id=user_id,
            periodo=periodo,
            categoria=categoria,
            forma_pagamento=forma_pagamento
        )
        
        if not caminho_relatorio:
            await query.edit_message_text("❌ Não foi possível gerar o relatório. Não há despesas registradas para os filtros selecionados.")
            return ConversationHandler.END
        
        # Enviar o arquivo Excel
        with open(caminho_relatorio, 'rb') as file:
            await context.bot.send_document(
                chat_id=user_id,
                document=file,
                filename=os.path.basename(caminho_relatorio),
                caption="📊 Aqui está seu relatório de despesas! 📊"
            )
        
        # Atualizar a mensagem
        await query.edit_message_text("✅ Relatório gerado e enviado com sucesso!")
        
        # Remover o arquivo após enviar
        os.remove(caminho_relatorio)
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        await query.edit_message_text(f"❌ Ocorreu um erro ao gerar o relatório: {str(e)}")
    
    return ConversationHandler.END

async def processar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto que não são comandos"""
    text = update.message.text.lower()
    
    if "gastos" in text:
        await gastos(update, context)
    elif "pagamentos" in text or "pagamento" in text:
        await pagamentos(update, context)
    else:
        await update.message.reply_text(
            "Não entendi. Use /registrar para adicionar uma despesa, /gastos para ver o resumo por categorias ou /pagamentos para ver o resumo por formas de pagamento.\n"
            "Digite /ajuda para ver todos os comandos disponíveis."
        )

def main():
    """Função principal"""
    # Obter o token do bot
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("Token do bot não encontrado. Configure a variável BOT_TOKEN no arquivo .env")
        return
    
    # Criar o aplicativo
    application = Application.builder().token(token).build()
    
    # Adicionar handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registrar", registrar)],
        states={
            VALOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_valor)],
            LOCAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_local)],
            CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_categoria)],
            FORMA_PAGAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_forma_pagamento)],
            PARCELAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_parcelas)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    
    # Handler para geração de relatórios
    relatorio_handler = ConversationHandler(
        entry_points=[CommandHandler("relatorio", relatorio)],
        states={
            TIPO_RELATORIO: [CallbackQueryHandler(processar_tipo_relatorio)],
            PERIODO_RELATORIO: [CallbackQueryHandler(processar_periodo_relatorio)],
            FILTRO_RELATORIO: [CallbackQueryHandler(processar_filtro_relatorio)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("gastos", gastos))
    application.add_handler(CommandHandler("pagamentos", pagamentos))
    application.add_handler(conv_handler)
    application.add_handler(relatorio_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem))
    
    # Iniciar o bot
    application.run_polling()

if __name__ == "__main__":
    main() 