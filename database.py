import psycopg2
import psycopg2.extras
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        # Conectar ao PostgreSQL
        self.conn = psycopg2.connect(
            host=os.getenv("SUPABASE_HOST"),
            database=os.getenv("SUPABASE_DATABASE"),
            user=os.getenv("SUPABASE_USER"),
            password=os.getenv("SUPABASE_PASSWORD"),
            port=os.getenv("SUPABASE_PORT")
        )
        # Configurar para autocommit e usar cursor que retorna dicionários
        self.conn.autocommit = True
        
        # Criar as tabelas se não existirem
        self._create_tables()
    
    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        with self.conn.cursor() as cursor:
            # Tabela de usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    nome TEXT,
                    username TEXT,
                    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    plano TEXT DEFAULT 'free',
                    data_expiracao TIMESTAMP
                )
            """)
            
            # Tabela de despesas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS despesas (
                    id SERIAL PRIMARY KEY,
                    usuario_id BIGINT REFERENCES usuarios(telegram_id),
                    valor DECIMAL(10,2) NOT NULL,
                    local TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    forma_pagamento TEXT NOT NULL,
                    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parcelas INTEGER DEFAULT 1,
                    valor_parcela DECIMAL(10,2),
                    parcelado BOOLEAN DEFAULT FALSE,
                    CONSTRAINT check_valor_positivo CHECK (valor > 0)
                )
            """)
            
            # Tabela de categorias personalizadas (para o futuro)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias_personalizadas (
                    id SERIAL PRIMARY KEY,
                    usuario_id BIGINT REFERENCES usuarios(telegram_id),
                    nome TEXT NOT NULL,
                    UNIQUE (usuario_id, nome)
                )
            """)
    
    def adicionar_despesa(self, user_id, valor, local, categoria, forma_pagamento="Dinheiro", parcelas=1, data_compra=None):
        """Adiciona uma nova despesa ao banco de dados"""
        # Se não for fornecida data específica, usa a data atual
        if not data_compra:
            data_compra = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Converter valor para float
        valor_total = float(valor)
        
        # Verificar se o usuário existe, se não, criar
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM usuarios WHERE telegram_id = %s", (user_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO usuarios (telegram_id, plano) VALUES (%s, %s)",
                    (user_id, "free")
                )
        
        # Parâmetros para a inserção
        parcelado = False
        valor_parcela = None
        
        # Para pagamentos parcelados (apenas quando for cartão de crédito)
        if forma_pagamento == "Cartão de Crédito" and parcelas > 1:
            valor_parcela = round(valor_total / parcelas, 2)
            parcelado = True
        
        # Inserir despesa no banco
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO despesas 
                (usuario_id, valor, local, categoria, forma_pagamento, data, parcelas, valor_parcela, parcelado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, valor_total, local, categoria.lower(), forma_pagamento,
                data_compra, parcelas, valor_parcela, parcelado
            ))
        
        return True
    
    def listar_categorias(self, user_id):
        """Retorna o total gasto por categoria"""
        categorias = {}
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT categoria, SUM(valor) as total
                FROM despesas
                WHERE usuario_id = %s
                GROUP BY categoria
                ORDER BY total DESC
            """, (user_id,))
            
            for row in cursor.fetchall():
                categorias[row['categoria']] = float(row['total'])
        
        return categorias
    
    def listar_formas_pagamento(self, user_id):
        """Retorna o total gasto por forma de pagamento"""
        formas = {}
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT forma_pagamento, SUM(valor) as total
                FROM despesas
                WHERE usuario_id = %s
                GROUP BY forma_pagamento
                ORDER BY total DESC
            """, (user_id,))
            
            for row in cursor.fetchall():
                formas[row['forma_pagamento']] = float(row['total'])
        
        return formas
    
    def listar_despesas_por_categoria(self, user_id, categoria):
        """Lista despesas de uma categoria específica"""
        despesas = []
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM despesas
                WHERE usuario_id = %s AND LOWER(categoria) = LOWER(%s)
                ORDER BY data DESC
            """, (user_id, categoria))
            
            for row in cursor.fetchall():
                despesa = dict(row)
                # Converter Decimal para float para compatibilidade
                despesa['valor'] = float(despesa['valor'])
                if despesa['valor_parcela']:
                    despesa['valor_parcela'] = float(despesa['valor_parcela'])
                despesas.append(despesa)
        
        return despesas
    
    def listar_despesas_por_forma_pagamento(self, user_id, forma_pagamento):
        """Retorna as despesas de uma forma de pagamento específica"""
        despesas = []
        
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM despesas
                WHERE usuario_id = %s AND forma_pagamento = %s
                ORDER BY data DESC
            """, (user_id, forma_pagamento))
            
            for row in cursor.fetchall():
                despesa = dict(row)
                # Converter Decimal para float para compatibilidade
                despesa['valor'] = float(despesa['valor'])
                if despesa['valor_parcela']:
                    despesa['valor_parcela'] = float(despesa['valor_parcela'])
                despesas.append(despesa)
        
        return despesas

    def gerar_relatorio_excel(self, user_id, periodo=None, categoria=None, forma_pagamento=None):
        """Gera um relatório Excel com as despesas do usuário."""
        # Construir a consulta SQL base
        query = """
            SELECT 
                TO_CHAR(data, 'YYYY-MM-DD HH24:MI:SS') as data,
                valor,
                local,
                INITCAP(categoria) as categoria,
                forma_pagamento,
                parcelas,
                valor_parcela,
                parcelado
            FROM despesas
            WHERE usuario_id = %s
        """
        params = [user_id]
        
        # Aplicar filtros adicionais
        if periodo:
            hoje = datetime.now()
            if periodo == "mes":
                inicio_periodo = datetime(hoje.year, hoje.month, 1)
                query += " AND data >= %s"
                params.append(inicio_periodo)
            elif periodo == "ano":
                inicio_periodo = datetime(hoje.year, 1, 1)
                query += " AND data >= %s"
                params.append(inicio_periodo)
                
        # Filtrar por categoria
        if categoria:
            query += " AND LOWER(categoria) = LOWER(%s)"
            params.append(categoria)
            
        # Filtrar por forma de pagamento
        if forma_pagamento:
            query += " AND forma_pagamento = %s"
            params.append(forma_pagamento)
            
        # Ordenar por data (mais recente primeiro)
        query += " ORDER BY data DESC"
        
        # Executar a consulta
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params)
            despesas = cursor.fetchall()
            
        if not despesas:
            return None
            
        # Criar DataFrame do pandas
        dados = []
        for d in despesas:
            item = {
                "Data": d["data"],
                "Valor": float(d["valor"]),
                "Local": d["local"],
                "Categoria": d["categoria"],
                "Forma de Pagamento": d["forma_pagamento"]
            }
            
            # Adicionar informações de parcelamento, se existirem
            if d["parcelado"]:
                item["Parcelas"] = d["parcelas"]
                item["Valor por Parcela"] = float(d["valor_parcela"])
            
            dados.append(item)
            
        df = pd.DataFrame(dados)
        
        # Caminho para salvar o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_despesas_{timestamp}.xlsx"
        
        # Criar o arquivo Excel
        writer = pd.ExcelWriter(nome_arquivo, engine='openpyxl')
        
        # Planilha principal com todas as despesas
        df.to_excel(writer, sheet_name="Despesas", index=False)
        
        # Planilha resumo por categoria
        if len(df) > 0:
            resumo_categoria = df.groupby("Categoria")["Valor"].sum().reset_index()
            resumo_categoria = resumo_categoria.sort_values("Valor", ascending=False)
            resumo_categoria.to_excel(writer, sheet_name="Resumo por Categoria", index=False)
            
            # Planilha resumo por forma de pagamento
            resumo_pagamento = df.groupby("Forma de Pagamento")["Valor"].sum().reset_index()
            resumo_pagamento = resumo_pagamento.sort_values("Valor", ascending=False)
            resumo_pagamento.to_excel(writer, sheet_name="Resumo por Pagamento", index=False)
        
        # Salvar o arquivo
        writer.close()
        
        return nome_arquivo 