# Implementação de Sistema de Assinaturas para o Bot de Finanças

Este documento descreve como implementar um sistema de assinaturas pagas para o Bot de Finanças Pessoais, permitindo oferecer recursos premium e gerar receita.

## Visão Geral da Arquitetura

### Componentes necessários:

1. **Gerenciamento de usuários e assinaturas** no banco de dados PostgreSQL
2. **Integração com gateway de pagamento** (Mercado Pago, PagSeguro, etc.)
3. **Verificação de permissões** em recursos premium
4. **Sistema de notificações** para renovação e expiração de assinaturas

## 1. Estrutura do Banco de Dados

As tabelas de usuários já estão implementadas. Adicione os seguintes campos e tabelas:

```sql
-- Adicionar campos à tabela de usuários
ALTER TABLE usuarios ADD COLUMN plano VARCHAR(20) DEFAULT 'free';
ALTER TABLE usuarios ADD COLUMN data_assinatura TIMESTAMP;
ALTER TABLE usuarios ADD COLUMN data_expiracao TIMESTAMP;

-- Criar tabela de transações de pagamento
CREATE TABLE pagamentos (
    id SERIAL PRIMARY KEY,
    usuario_id BIGINT REFERENCES usuarios(telegram_id),
    valor DECIMAL(10,2) NOT NULL,
    referencia_externa VARCHAR(100),
    gateway VARCHAR(50),
    status VARCHAR(20),
    data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    plano VARCHAR(20),
    duracao_meses INTEGER
);
```

## 2. Integração com Gateway de Pagamento

### Mercado Pago (exemplo)

1. Crie uma conta no [Mercado Pago Developers](https://developers.mercadopago.com/)
2. Obtenha suas credenciais de API
3. Instale a biblioteca: `pip install mercadopago`

Adicione ao requirements.txt:

```
mercadopago==2.2.0
```

Exemplo de implementação:

```python
# Em um novo arquivo payment.py
import mercadopago
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class PaymentGateway:
    def __init__(self):
        self.sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

    def criar_link_pagamento(self, user_id, plano, valor, descricao, duracao_meses):
        """Cria um link de pagamento para assinatura"""
        # Criar preferência de pagamento
        preference_data = {
            "items": [
                {
                    "title": descricao,
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(valor)
                }
            ],
            "back_urls": {
                "success": os.getenv("WEBHOOK_URL") + "/payment/success",
                "failure": os.getenv("WEBHOOK_URL") + "/payment/failure"
            },
            "external_reference": f"{user_id}_{plano}_{duracao_meses}"
        }

        result = self.sdk.preference().create(preference_data)
        preference = result["response"]

        # Registrar pagamento pendente no banco
        self.registrar_pagamento_pendente(user_id, preference["id"], plano, valor, duracao_meses)

        return preference["init_point"]

    def registrar_pagamento_pendente(self, user_id, referencia, plano, valor, duracao_meses):
        """Registra um pagamento pendente no banco de dados"""
        # Implementar lógica para registrar na tabela pagamentos
        pass

    def processar_webhook(self, data):
        """Processa notificações de pagamento do gateway"""
        # Implementar lógica para atualizar status de pagamento
        # e ativar assinatura se aprovado
        pass

    def ativar_assinatura(self, user_id, plano, duracao_meses):
        """Ativa a assinatura para um usuário"""
        # Atualizar os campos na tabela usuarios
        data_atual = datetime.now()
        data_expiracao = data_atual + timedelta(days=30*duracao_meses)

        # Implementar lógica para atualizar no banco de dados
        pass
```

## 3. Implementação no Bot

### Comandos de assinatura

Adicione os handlers para comandos de assinatura no bot.py:

```python
# Adicionar no bot.py
async def planos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe os planos disponíveis para assinatura"""
    keyboard = [
        [
            InlineKeyboardButton("🌟 Plano Mensal - R$ 19,90", callback_data="plano_mensal"),
        ],
        [
            InlineKeyboardButton("🔥 Plano Anual - R$ 199,90 (2 meses grátis!)", callback_data="plano_anual"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📊 *Planos de Assinatura*\n\n"
        "👉 *Plano Gratuito*\n"
        "- Registro limitado a 15 despesas/mês\n"
        "- Visualização básica de categorias\n\n"
        "👉 *Plano Premium*\n"
        "- Despesas ilimitadas\n"
        "- Relatórios detalhados em Excel\n"
        "- Análises por período\n"
        "- Gráficos e estatísticas\n"
        "- Categorias personalizadas\n\n"
        "Escolha seu plano:",
        reply_markup=reply_markup
    )

async def processar_escolha_plano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa a escolha do plano e gera link de pagamento"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data == "plano_mensal":
        plano = "mensal"
        valor = 19.90
        duracao = 1
        descricao = "Assinatura Mensal - Bot Finanças"
    else:
        plano = "anual"
        valor = 199.90
        duracao = 12
        descricao = "Assinatura Anual - Bot Finanças"

    # Criar link de pagamento
    payment_gateway = PaymentGateway()
    payment_link = payment_gateway.criar_link_pagamento(
        user_id, plano, valor, descricao, duracao
    )

    # Enviar link de pagamento
    keyboard = [[InlineKeyboardButton("💰 Pagar agora", url=payment_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"✨ *Assinatura {plano.capitalize()}*\n\n"
        f"Valor: R$ {valor:.2f}\n"
        f"Duração: {duracao} {'mês' if duracao == 1 else 'meses'}\n\n"
        "Clique no botão abaixo para efetuar o pagamento:",
        reply_markup=reply_markup
    )

# Adicionar handlers no main()
application.add_handler(CommandHandler("planos", planos))
application.add_handler(CallbackQueryHandler(processar_escolha_plano, pattern=r"^plano_"))
```

### Verificação de acesso premium

Crie um decorator para verificar permissões em recursos premium:

```python
# Em um novo arquivo permissions.py
from functools import wraps
from datetime import datetime
from telegram.ext import ConversationHandler

def verificar_assinatura_ativa(user_id, db_conn):
    """Verifica se o usuário tem assinatura ativa"""
    with db_conn.cursor() as cursor:
        cursor.execute(
            "SELECT plano, data_expiracao FROM usuarios WHERE telegram_id = %s",
            (user_id,)
        )
        resultado = cursor.fetchone()

        if not resultado or resultado[0] == 'free':
            return False

        # Se tem plano pago, verificar validade
        if resultado[1] is None:
            return False

        return datetime.now() < resultado[1]

def requer_assinatura(f):
    """Decorator para verificar se usuário tem assinatura ativa"""
    @wraps(f)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        # Verificar assinatura
        from database import Database
        db = Database()
        tem_acesso = verificar_assinatura_ativa(user_id, db.conn)

        if not tem_acesso:
            await update.message.reply_text(
                "🔒 Este recurso está disponível apenas para assinantes.\n"
                "Use o comando /planos para conhecer os planos de assinatura."
            )
            return ConversationHandler.END

        return await f(update, context, *args, **kwargs)
    return wrapped
```

Aplicar o decorator nos recursos premium:

```python
# No bot.py
from permissions import requer_assinatura

@requer_assinatura
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Código existente...
```

## 4. Webhook para Notificações de Pagamento

Adicionar um endpoint no servidor Flask para receber notificações:

```python
# No bot.py, expandir a parte do Flask
from flask import Flask, request, jsonify

# ... código existente ...

@app.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    """Recebe notificações de pagamento do gateway"""
    data = request.json
    payment_gateway = PaymentGateway()
    result = payment_gateway.processar_webhook(data)
    return jsonify({"status": "ok"})

@app.route('/payment/success')
def payment_success():
    """Página de sucesso de pagamento"""
    # A URL de retorno após pagamento bem-sucedido
    return "Pagamento realizado com sucesso! Você pode retornar ao Telegram."

@app.route('/payment/failure')
def payment_failure():
    """Página de falha de pagamento"""
    # A URL de retorno após falha no pagamento
    return "Houve um problema com seu pagamento. Por favor, tente novamente pelo Telegram."
```

## 5. Sistema de Notificações

Criar uma função para verificar assinaturas prestes a expirar:

```python
# Em um novo arquivo scheduler.py
from datetime import datetime, timedelta
import asyncio
import telegram

async def verificar_assinaturas_expirando():
    """Verifica assinaturas prestes a expirar e notifica usuários"""
    from database import Database
    db = Database()

    # Buscar assinaturas que expiram em 3 dias
    data_limite = datetime.now() + timedelta(days=3)

    with db.conn.cursor() as cursor:
        cursor.execute("""
            SELECT telegram_id, plano, data_expiracao
            FROM usuarios
            WHERE plano != 'free' AND data_expiracao < %s AND data_expiracao > %s
        """, (data_limite, datetime.now()))

        usuarios = cursor.fetchall()

    # Notificar cada usuário
    bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))

    for user_id, plano, data_expiracao in usuarios:
        dias_restantes = (data_expiracao - datetime.now()).days

        mensagem = (
            f"⚠️ *Atenção: Sua assinatura expira em breve!*\n\n"
            f"Seu plano {plano} expira em {dias_restantes} dias.\n"
            "Para renovar sua assinatura, use o comando /planos.\n"
            "Não perca acesso aos recursos premium!"
        )

        try:
            await bot.send_message(chat_id=user_id, text=mensagem, parse_mode='Markdown')
        except Exception as e:
            print(f"Erro ao notificar usuário {user_id}: {e}")

# Função para executar o agendador
async def executar_verificacoes_periodicas():
    """Executa verificações periódicas em background"""
    while True:
        await verificar_assinaturas_expirando()
        # Verificar a cada 24 horas
        await asyncio.sleep(24 * 60 * 60)

# Iniciar o agendador em uma thread separada
def iniciar_agendador():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(executar_verificacoes_periodicas())

# Chamar no main() do bot.py
scheduler_thread = threading.Thread(target=iniciar_agendador)
scheduler_thread.daemon = True
scheduler_thread.start()
```

## 6. Atualizações no arquivo .env

Adicione as seguintes variáveis ao .env:

```
# Gateway de pagamento
MP_ACCESS_TOKEN=TEST-0000000000000000000000000000000-000000000
MP_PUBLIC_KEY=TEST-00000000-0000-0000-0000-000000000000

# URL do webhook para notificações de pagamento
WEBHOOK_URL=https://seu-app.onrender.com
```

## Testando o Sistema

1. Configure as credenciais de teste do gateway de pagamento
2. Implante as alterações no servidor
3. Use o comando `/planos` para testar o fluxo de assinatura
4. Verifique se as notificações de webhook estão sendo recebidas
5. Teste os recursos premium com e sem assinatura ativa

## Considerações para produção

1. **Segurança**: Certifique-se de validar todas as notificações de pagamento
2. **Backup**: Faça backup regular dos dados de assinatura
3. **Monitoramento**: Implemente logs detalhados para rastrear problemas
4. **Suporte**: Adicione um comando `/ajuda_assinatura` para dúvidas específicas
5. **Cancelamento**: Implemente a opção de cancelar assinaturas antes da renovação automática
