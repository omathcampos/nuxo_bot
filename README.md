# Bot de Finanças Pessoais

Um bot do Telegram para registro e acompanhamento de despesas pessoais, permitindo categorizar gastos, visualizar relatórios e exportar dados em formato Excel.

## Funcionalidades

- Registro de despesas com valor, local e categoria
- Suporte a diferentes formas de pagamento (dinheiro, Pix, cartão de débito e crédito)
- Controle de parcelas para compras no cartão de crédito
- Visualização de gastos agrupados por categoria
- Visualização de gastos por forma de pagamento
- Detalhamento de gastos de uma categoria específica
- Exportação de relatórios em formato Excel
- Interface simples via Telegram

## Requisitos

- Python 3.7+
- Conta no Telegram
- Token de bot do Telegram (obtido através do [@BotFather](https://t.me/botfather))
- Banco de dados PostgreSQL (recomendado via [Supabase](https://supabase.com))

## Tecnologias utilizadas

- Python-telegram-bot para interação com a API do Telegram
- PostgreSQL para armazenamento de dados
- Flask para servidor web com endpoint de ping
- Pandas e openpyxl para geração de relatórios

## Instalação

1. Clone este repositório:

```
git clone https://github.com/seu-usuario/bot-financas-pessoais.git
cd bot-financas-pessoais
```

2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Crie um arquivo `.env` baseado no `.env.example` e adicione suas credenciais:

```
# Token do Bot Telegram
BOT_TOKEN=seu_token_aqui

# Credenciais do Supabase PostgreSQL
SUPABASE_HOST=db.xyzsupabase.co
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=sua_senha_secreta
```

## Como obter um token de bot

1. Abra o Telegram e procure por @BotFather
2. Inicie uma conversa e envie o comando `/newbot`
3. Siga as instruções para criar um novo bot
4. Copie o token gerado para o arquivo `.env`

## Como configurar o banco de dados

1. Crie uma conta no [Supabase](https://supabase.com) (plano gratuito disponível)
2. Crie um novo projeto
3. Vá para Project Settings > Database para obter suas credenciais de conexão
4. Adicione as credenciais ao arquivo `.env`

As tabelas necessárias serão criadas automaticamente na primeira execução do bot.

## Como usar localmente

1. Inicie o bot:

```
python bot.py
```

2. Abra o Telegram e procure pelo seu bot pelo nome que você cadastrou
3. Envie o comando `/start` para começar a usar

## Deploy em serviços de hospedagem

### Deploy no Railway

1. Crie uma conta no [Railway](https://railway.app/)
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente (BOT_TOKEN, SUPABASE_HOST, etc.)
4. O projeto será implantado automaticamente

### Deploy no Render

1. Crie uma conta no [Render](https://render.com/)
2. Crie um novo Web Service e conecte seu repositório
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
4. Adicione as variáveis de ambiente necessárias
5. Se usar o plano gratuito, configure um serviço de ping periódico para o endpoint `/ping` para evitar suspensão automática após 15 minutos de inatividade

## Evitando suspensão automática no plano gratuito do Render

O bot inclui um servidor Flask com um endpoint `/ping` que pode ser acessado para manter o serviço ativo. Configure um serviço de ping como:

1. [UptimeRobot](https://uptimerobot.com/) (gratuito)
2. Cron job em outro servidor ou seu computador
3. [Cron-job.org](https://cron-job.org) (gratuito)

Configure o serviço para enviar uma solicitação HTTP GET para `https://seu-app.onrender.com/ping` a cada 10-14 minutos.

## Comandos disponíveis:

- `/start` - Inicia o bot e mostra os comandos disponíveis
- `/registrar` - Inicia o processo de registro de uma nova despesa
- `/gastos` - Mostra um resumo dos gastos por categoria
- `/pagamentos` - Mostra um resumo dos gastos por forma de pagamento
- `/relatorio` - Gera um relatório em formato Excel das suas despesas
- `/ajuda` - Exibe instruções detalhadas de uso

### Registrando despesas:

1. Use o comando `/registrar`
2. Informe o valor quando solicitado
3. Informe o local da compra
4. Selecione ou digite a categoria
5. Selecione a forma de pagamento
6. Se for cartão de crédito, escolha o número de parcelas

### Consultando gastos:

- Envie `/gastos` ou simplesmente a palavra "gastos" para ver um resumo por categoria
- Para ver os detalhes de uma categoria específica, envie: `gastos categoria:alimentação` (substitua "alimentação" pela categoria desejada)

### Consultando por forma de pagamento:

- Envie `/pagamentos` ou simplesmente a palavra "pagamentos" para ver um resumo por forma de pagamento
- Para ver os detalhes de uma forma de pagamento específica, envie: `pagamentos forma:pix` (substitua "pix" pela forma de pagamento desejada)

### Gerando relatórios Excel:

1. Use o comando `/relatorio`
2. Escolha entre:
   - Relatório completo com todas as despesas
   - Filtrar por período (mês atual, ano atual)
   - Filtrar por categoria
   - Filtrar por forma de pagamento
3. O bot enviará o arquivo Excel com os dados solicitados

## Estrutura do projeto

- `bot.py`: Código principal do bot com handlers e lógica de interação
- `database.py`: Gerenciamento do banco de dados PostgreSQL
- `requirements.txt`: Lista de dependências
- `Procfile`: Configuração para deployment no Render
- `.env`: Variáveis de ambiente (não incluído no repositório)

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
