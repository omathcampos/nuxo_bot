from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Conexão com Supabase estabelecida com sucesso")
            self._criar_tabelas_se_nao_existem()
        except Exception as e:
            logger.error(f"Erro ao conectar com Supabase: {e}")
            raise

    def _criar_tabelas_se_nao_existem(self):
        """
        Cria as tabelas necessárias no Supabase se elas não existirem.
        Na implementação real, isso seria feito com migrations do Supabase.
        Aqui apenas documentamos a estrutura esperada.
        """
        # Tabela de usuários
        # id (primary key)
        # telegram_id (unique)
        # nome
        # data_cadastro
        
        # Tabela de gastos
        # id (primary key)
        # usuario_id (foreign key para users)
        # valor (decimal)
        # forma_pagamento (text)
        # parcelas (integer)
        # categoria (text)
        # local (text)
        # data (date)
        # criado_em (timestamp)
        pass

    def registrar_gasto(self, usuario_id, valor, forma_pagamento, parcelas, categoria, local, data):
        """
        Registra um novo gasto no banco de dados
        """
        try:
            data_obj = {
                "usuario_id": usuario_id,
                "valor": valor,
                "forma_pagamento": forma_pagamento,
                "parcelas": parcelas if forma_pagamento == "Crédito" else None,
                "categoria": categoria,
                "local": local,
                "data": data
            }
            
            result = self.supabase.table('gastos').insert(data_obj).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao registrar gasto: {e}")
            return None

    def obter_gastos(self, usuario_id, ano=None, mes=None, forma_pagamento=None, categoria=None):
        """
        Obtém gastos do usuário, com filtros opcionais por ano, mês, forma de pagamento e categoria
        """
        try:
            query = self.supabase.table('gastos').select('*').eq('usuario_id', usuario_id)
            
            # Filtragem por ano e mês usando abordagem diferente
            if ano:
                # Se temos ano, filtramos com operadores >= e <
                if mes:
                    # Filtro por mês específico
                    mes_str = str(mes).zfill(2)
                    data_inicio = f"{ano}-{mes_str}-01"
                    
                    # Calcula o próximo mês para filtro de fim
                    proximo_mes = mes + 1
                    proximo_ano = ano
                    if proximo_mes > 12:
                        proximo_mes = 1
                        proximo_ano += 1
                    
                    proximo_mes_str = str(proximo_mes).zfill(2)
                    data_fim = f"{proximo_ano}-{proximo_mes_str}-01"
                    
                    query = query.gte('data', data_inicio).lt('data', data_fim)
                else:
                    # Filtro por todo o ano
                    data_inicio = f"{ano}-01-01"
                    data_fim = f"{ano+1}-01-01"
                    query = query.gte('data', data_inicio).lt('data', data_fim)
            
            if forma_pagamento:
                # Filtra por forma de pagamento
                query = query.eq('forma_pagamento', forma_pagamento)
            
            if categoria:
                # Filtra por categoria
                query = query.eq('categoria', categoria)
            
            # Ordena por data
            query = query.order('data', desc=True)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Erro ao obter gastos: {e}")
            return []

    def registrar_usuario(self, telegram_id, nome):
        """
        Registra um novo usuário ou atualiza se já existir
        """
        try:
            # Verifica se o usuário já existe
            result = self.supabase.table('usuarios').select('*').eq('telegram_id', telegram_id).execute()
            
            if result.data:
                # Se já existe, apenas retorna o ID
                return result.data[0]['id']
            
            # Se não existe, insere novo usuário
            data = {
                "telegram_id": telegram_id,
                "nome": nome
            }
            
            result = self.supabase.table('usuarios').insert(data).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao registrar usuário: {e}")
            return None


# Instância global do banco de dados
db = Database() 