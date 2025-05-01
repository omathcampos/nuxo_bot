# Nuxo Bot

**Organização que parece mágica, mas é só Nuxo.**

Um bot do Telegram para gerenciamento financeiro que ajuda você a controlar seus gastos de forma simples e eficiente.

## Funcionalidades

O Nuxo Bot oferece as seguintes funcionalidades:

- **Registro de gastos**: Registre seus gastos com detalhes como valor, forma de pagamento, categoria, local e data. Para pagamentos com cartão de crédito, você pode especificar o número de parcelas.

- **Visualização de gastos**: Consulte seus gastos por período (ano e mês) e forma de pagamento, com resumo por categoria e lista detalhada.

- **Exportação para Excel**: Exporte seus gastos para uma planilha Excel para análises mais complexas.

- **Ajuda integrada**: Obtenha instruções completas diretamente no bot.

## Formas de Pagamento Suportadas

- Débito
- Crédito (com opção de parcelas)
- Pix
- Dinheiro
- VR (Vale Refeição)
- VA (Vale Alimentação)

## Categorias de Gastos

- Alimentação
- Transporte
- Moradia
- Saúde
- Educação
- Lazer
- Vestuário
- Outros

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **python-telegram-bot**: Framework para criação de bots no Telegram
- **Supabase**: Plataforma de banco de dados para armazenamento dos dados
- **pandas**: Biblioteca para manipulação de dados e exportação para Excel
- **openpyxl**: Biblioteca para criação de arquivos Excel

## Configuração e Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Conta no Telegram
- Conta no Supabase (gratuita ou paga)

### Instalação

1. Clone este repositório:

```
git clone https://github.com/seu-usuario/nuxo-bot.git
cd nuxo-bot
```

2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (crie um arquivo `.env` baseado no exemplo `.env.example`):

```
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

Ou edite diretamente o arquivo `config.py`.

### Criação das Tabelas no Supabase

Crie as seguintes tabelas no Supabase:

**Tabela `usuarios`**

- `id` (bigint, primary key, auto-increment)
- `telegram_id` (bigint, unique)
- `nome` (text)
- `data_cadastro` (timestamp with timezone, default: now())

**Tabela `gastos`**

- `id` (bigint, primary key, auto-increment)
- `usuario_id` (bigint, foreign key referenciando usuarios.id)
- `valor` (decimal)
- `forma_pagamento` (text)
- `parcelas` (integer, nullable)
- `categoria` (text)
- `local` (text)
- `data` (date)
- `criado_em` (timestamp with timezone, default: now())

### Execução

Para iniciar o bot:

```
python main.py
```

## Uso

1. Inicie uma conversa com seu bot no Telegram (usando o link fornecido pelo BotFather)
2. Envie o comando `/start` para ver o menu principal
3. Use os botões ou comandos para navegar pelas funcionalidades:
   - `/registrar` - Registrar um novo gasto
   - `/visualizar` - Visualizar seus gastos
   - `/exportar` - Exportar para Excel
   - `/ajuda` - Obter ajuda

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
