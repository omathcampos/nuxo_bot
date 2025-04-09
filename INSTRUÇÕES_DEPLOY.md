# Instruções de Deploy - Bot de Finanças Pessoais

Este documento contém instruções detalhadas para fazer o deploy do Bot de Finanças Pessoais no Railway ou Render, utilizando o banco de dados PostgreSQL do Supabase.

## Configuração do Banco de Dados (Supabase)

### Criar uma conta e projeto no Supabase

1. Acesse [supabase.com](https://supabase.com/) e crie uma conta gratuita
2. Clique em "New Project"
3. Dê um nome ao seu projeto (ex: "finances-bot")
4. Defina uma senha segura para o banco de dados
5. Escolha uma região próxima à sua localização
6. Clique em "Create new project"

### Obter credenciais de conexão

1. Após a criação do projeto, vá para "Project Settings" > "Database"
2. Localize as seguintes informações:
   - Host: Endpoint para conexão (ex: db.xyzsupabase.co)
   - Database name: postgres (por padrão)
   - User: postgres (por padrão)
   - Password: A senha que você definiu
   - Port: 5432 (por padrão)

### Configuração adicional (opcional)

Se desejar, você pode configurar políticas de backup, monitoramento e alertas nas configurações do projeto.

## Deploy no Railway

### Preparação

1. Crie uma conta no [Railway](https://railway.app/)
2. Tenha seu código em um repositório Git (GitHub, GitLab, etc.)

### Passos para deploy

1. No dashboard do Railway, clique em "New Project" > "Deploy from GitHub repo"
2. Selecione o repositório com o código do bot
3. Adicione as variáveis de ambiente em "Variables":
   - `BOT_TOKEN` = token do seu bot do Telegram
   - `SUPABASE_HOST` = host do Supabase
   - `SUPABASE_DATABASE` = postgres
   - `SUPABASE_USER` = postgres
   - `SUPABASE_PASSWORD` = sua senha do banco de dados
4. Em "Settings", verifique se a configuração da implantação está correta:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
5. O Railway iniciará automaticamente o deploy do bot

### Monitoramento

- Você pode verificar os logs em tempo real na guia "Deployments"
- Configure alertas em "Settings" > "Alerts" para ser notificado sobre falhas

## Deploy no Render

### Preparação

1. Crie uma conta no [Render](https://render.com/)
2. Tenha seu código em um repositório Git (GitHub, GitLab, etc.)

### Passos para deploy

1. No dashboard do Render, clique em "New" > "Web Service"
2. Conecte seu repositório Git
3. Configure o serviço:
   - Nome: `bot-financas` (ou outro nome de sua escolha)
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Plano: "Free" (para testes) ou "Starter" ($7/mês, recomendado para evitar suspensão automática)
4. Em "Environment Variables", adicione:
   - `BOT_TOKEN` = token do seu bot do Telegram
   - `SUPABASE_HOST` = host do Supabase
   - `SUPABASE_DATABASE` = postgres
   - `SUPABASE_USER` = postgres
   - `SUPABASE_PASSWORD` = sua senha do banco de dados
5. Clique em "Create Web Service"

### Manter serviço ativo (para plano Free)

O plano gratuito do Render suspende serviços após 15 minutos de inatividade. Você pode evitar isso configurando um serviço de ping:

1. **Opção 1: UptimeRobot**

   - Crie uma conta gratuita em [UptimeRobot](https://uptimerobot.com/)
   - Adicione um novo monitor do tipo HTTP(s)
   - URL: `https://seu-app-no-render.onrender.com/ping`
   - Intervalo: 5 minutos

2. **Opção 2: Cron-job.org**

   - Crie uma conta gratuita em [Cron-job.org](https://cron-job.org/)
   - Adicione um novo cronjob
   - URL: `https://seu-app-no-render.onrender.com/ping`
   - Frequência: a cada 10 minutos

3. **Opção 3: Script local**
   - Crie um script simples em seu computador:
     ```bash
     */14 * * * * curl -s https://seu-app-no-render.onrender.com/ping > /dev/null
     ```

## Verificando o funcionamento

1. Abra o Telegram e procure pelo seu bot (pelo nome que você definiu no BotFather)
2. Envie o comando `/start`
3. Se o bot responder, significa que está funcionando corretamente
4. Envie o comando `/registrar` para testar o registro de uma despesa

## Resolução de problemas

### Bot não responde

1. Verifique os logs no Railway/Render
2. Confirme se o token do bot está correto
3. Reinicie o serviço se necessário

### Erros de conexão com banco de dados

1. Verifique se as credenciais do Supabase estão corretas
2. Confirme se o IP do serviço de hospedagem não está bloqueado no Supabase
3. Verifique os logs para mensagens de erro específicas

### Serviço fica inativo no plano gratuito do Render

1. Verifique se o serviço de ping está funcionando
2. Confirme que a URL do endpoint `/ping` está correta
3. Considere usar o plano Starter ($7/mês) para evitar suspensão automática

## Monitoramento e manutenção

### Backups do banco de dados

O Supabase oferece backups automáticos no plano Pro, mas você pode realizar backups manuais:

1. Acesse o painel do Supabase
2. Vá para "Table Editor"
3. Selecione suas tabelas
4. Use a opção "Export" para fazer download dos dados em formato CSV

### Atualizações

Para atualizar seu bot:

1. Faça alterações no código em seu repositório
2. Commit e push para o branch principal
3. O serviço de hospedagem detectará as alterações e fará o redeploy automaticamente

## Considerações para escala

À medida que o número de usuários cresce:

1. **Railway**: Considere planos mais robustos conforme o uso aumenta
2. **Render**: Upgrade para planos Standard ou Plus para mais recursos
3. **Supabase**: Monitore o uso do banco de dados, o plano gratuito oferece 500MB de armazenamento
