# Scratchpad para Bot de Finanças Pessoais

## Ideias para expansão

### Funcionalidades adicionais

- [ ] Implementar relatórios periódicos (semanais, mensais)
- [ ] Adicionar metas de orçamento por categoria
- [ ] Permitir exportação dos dados em CSV/Excel
- [ ] Criar gráficos de gastos
- [ ] Adicionar notificações quando gastos ultrapassarem limites

### Melhorias técnicas

- [ ] Migrar banco de dados para SQLite ou PostgreSQL
- [ ] Adicionar autenticação para aumentar segurança
- [ ] Implementar backup automático dos dados
- [ ] Adicionar suporte a múltiplas moedas
- [ ] Criar testes automatizados

### Interface

- [ ] Desenvolver versão web para complementar o bot do Telegram
- [ ] Criar dashboard com visualização avançada de dados
- [ ] Adicionar suporte a outras plataformas de mensageria (WhatsApp, Discord)

## Fluxo de uso

### Registro de despesa

1. Usuário inicia com `/registrar`
2. Bot solicita valor
3. Bot solicita local
4. Bot oferece categorias para seleção
5. Bot confirma registro e salva dados

### Consulta simplificada (para implementar)

- Permitir registro direto em formato: `registrar 25.50 Supermercado Alimentação`
- Permitir consultas direcionadas: `gastos semana` ou `gastos mês`

## Estrutura do banco de dados (para evolução)

### Tabela de Usuários

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    nome TEXT,
    data_registro TIMESTAMP
);
```

### Tabela de Categorias

```sql
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE,
    descricao TEXT
);
```

### Tabela de Despesas

```sql
CREATE TABLE despesas (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER,
    valor REAL,
    local TEXT,
    categoria_id INTEGER,
    data TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
);
```

## Recursos e bibliotecas para explorar

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [matplotlib](https://matplotlib.org/) para gráficos
- [pandas](https://pandas.pydata.org/) para análise de dados
- [SQLAlchemy](https://www.sqlalchemy.org/) para ORM
- [FastAPI](https://fastapi.tiangolo.com/) para API web (caso implementado)

## Fluxo de desenvolvimento

1. Implementar MVP (versão atual)
2. Coletar feedback dos usuários
3. Priorizar melhorias com base no feedback
4. Implementar recursos adicionais
5. Melhorar UX e expandir plataformas

## Recursos para inspiração

- [YNAB](https://www.youneedabudget.com/) - You Need A Budget
- [Mint](https://mint.intuit.com/) - Sistema de finanças pessoais
- [Splitwise](https://www.splitwise.com/) - Compartilhamento de despesas
