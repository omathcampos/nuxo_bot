# Bot de Finanças Pessoais

Um bot do Telegram para registro e acompanhamento de despesas pessoais, permitindo categorizar gastos e visualizar relatórios.

## Funcionalidades

- Registro de despesas com valor, local e categoria
- Visualização de gastos agrupados por categoria
- Detalhamento de gastos de uma categoria específica
- Interface simples via Telegram

## Requisitos

- Python 3.7+
- Conta no Telegram
- Token de bot do Telegram (obtido através do [@BotFather](https://t.me/botfather))

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

3. Crie um arquivo `.env` baseado no `.env.example` e adicione seu token de bot:

```
BOT_TOKEN=seu_token_aqui
```

## Como obter um token de bot

1. Abra o Telegram e procure por @BotFather
2. Inicie uma conversa e envie o comando `/newbot`
3. Siga as instruções para criar um novo bot
4. Copie o token gerado para o arquivo `.env`

## Como usar

1. Inicie o bot:

```
python bot.py
```

2. Abra o Telegram e procure pelo seu bot pelo nome que você cadastrou
3. Envie o comando `/start` para começar a usar

### Comandos disponíveis:

- `/start` - Inicia o bot e mostra os comandos disponíveis
- `/registrar` - Inicia o processo de registro de uma nova despesa
- `/gastos` - Mostra um resumo dos gastos por categoria
- `/ajuda` - Exibe instruções detalhadas de uso

### Registrando despesas:

1. Use o comando `/registrar`
2. Informe o valor quando solicitado
3. Informe o local da compra
4. Selecione ou digite a categoria

### Consultando gastos:

- Envie `/gastos` ou simplesmente a palavra "gastos" para ver um resumo por categoria
- Para ver os detalhes de uma categoria específica, envie: `gastos categoria:alimentação` (substitua "alimentação" pela categoria desejada)

## Estrutura de dados

As despesas são armazenadas em um arquivo JSON com a seguinte estrutura:

```json
{
  "despesas": [
    {
      "user_id": 123456789,
      "valor": 25.5,
      "local": "Supermercado",
      "categoria": "alimentação",
      "data": "2023-06-15 14:30:25"
    }
  ]
}
```

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
