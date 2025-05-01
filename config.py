import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 

# Categorias de gastos disponíveis
CATEGORIAS = [
    "Alimentação", 
    "Transporte", 
    "Moradia", 
    "Saúde", 
    "Educação", 
    "Lazer", 
    "Vestuário", 
    "Outros"
]

# Formas de pagamento
FORMAS_PAGAMENTO = [
    "Débito", 
    "Crédito", 
    "Pix", 
    "Dinheiro", 
    "VR", 
    "VA"
] 