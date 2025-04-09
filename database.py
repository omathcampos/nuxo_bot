import json
import os
from datetime import datetime
import psycopg2
import psycopg2.extras
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        try:
            # Conectar ao PostgreSQL
            self.conn = psycopg2.connect(
                host="aws-0-sa-east-1.pooler.supabase.com",
                database="postgres",
                user="postgres.zxgeldbzeceugqvgwkcf",
                password="Santista65@",
                port="6543"
            )
            # Configurar para autocommit e usar cursor que retorna dicionários
            self.conn.autocommit = True
            print("Conexão estabelecida com sucesso!")
            
            # Criar as tabelas se não existirem
            self._create_tables()
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            raise e
    
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
            
            # Tabela de categorias personalizadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias_personalizadas (
                    id SERIAL PRIMARY KEY,
                    usuario_id BIGINT REFERENCES usuarios(telegram_id),
                    nome TEXT NOT NULL,
                    UNIQUE (usuario_id, nome)
                )
            """)
            
            print("Tabelas criadas/verificadas com sucesso!")
    
    def _load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {"despesas": [], "versao": 2}
        else:
            return {"despesas": [], "versao": 2}
    
    def _save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
    
    def adicionar_despesa(self, user_id, valor, local, categoria, forma_pagamento="Dinheiro", parcelas=1, data_compra=None):
        # Se não for fornecida data específica, usa a data atual
        if not data_compra:
            data_compra = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Converter valor para float
        valor_total = float(valor)
        
        # Criar despesa
        despesa = {
            "user_id": user_id,
            "valor": valor_total,
            "local": local,
            "categoria": categoria.lower(),
            "forma_pagamento": forma_pagamento,
            "data": data_compra
        }
        
        # Para pagamentos parcelados (apenas quando for cartão de crédito)
        if forma_pagamento == "Cartão de Crédito" and parcelas > 1:
            valor_parcela = round(valor_total / parcelas, 2)
            despesa["parcelas"] = parcelas
            despesa["valor_parcela"] = valor_parcela
            despesa["parcelado"] = True
        
        # Adicionar despesa à lista
        self.data["despesas"].append(despesa)
        self._save_data()
        return True
    
    def migrar_dados(self):
        """Migra dados do formato antigo para o novo formato"""
        if "versao" in self.data and self.data["versao"] >= 2:
            # Já está no formato novo
            return
        
        novas_despesas = []
        despesas_parceladas_processadas = {}
        
        for despesa in self.data["despesas"]:
            # Verificar se é uma parcela
            if "é_parcela" in despesa and despesa["é_parcela"]:
                # Criar identificador para a compra parcelada
                identificador = f"{despesa['user_id']}_{despesa['local']}_{despesa['valor_total']}_{despesa['data']}"
                
                # Se já processamos essa compra parcelada, pular
                if identificador in despesas_parceladas_processadas:
                    continue
                
                # Marcar como processada
                despesas_parceladas_processadas[identificador] = True
                
                # Criar nova entrada para a compra parcelada
                nova_despesa = {
                    "user_id": despesa["user_id"],
                    "valor": despesa["valor_total"],
                    "local": despesa["local"],
                    "categoria": despesa["categoria"],
                    "forma_pagamento": despesa["forma_pagamento"],
                    "data": despesa["data"],
                    "parcelas": despesa["parcelas"],
                    "valor_parcela": despesa["valor_parcela"],
                    "parcelado": True
                }
                
                novas_despesas.append(nova_despesa)
            elif "é_parcela" not in despesa:
                # Despesa normal, não é parcela
                novas_despesas.append(despesa)
        
        # Atualizar dados
        self.data["despesas"] = novas_despesas
        self.data["versao"] = 2
        self._save_data()
    
    def listar_categorias(self, user_id):
        """Retorna o total gasto por categoria"""
        categorias = {}
        
        for despesa in self.data["despesas"]:
            if despesa["user_id"] == user_id:
                categoria = despesa["categoria"]
                
                if categoria in categorias:
                    categorias[categoria] += despesa["valor"]
                else:
                    categorias[categoria] = despesa["valor"]
        
        return categorias
    
    def listar_formas_pagamento(self, user_id):
        """Retorna o total gasto por forma de pagamento"""
        formas = {}
        
        for despesa in self.data["despesas"]:
            if despesa["user_id"] == user_id:
                forma = despesa["forma_pagamento"]
                
                if forma in formas:
                    formas[forma] += despesa["valor"]
                else:
                    formas[forma] = despesa["valor"]
        
        return formas
    
    def listar_despesas_por_categoria(self, user_id, categoria):
        """Lista despesas de uma categoria específica"""
        despesas = []
        
        for despesa in self.data["despesas"]:
            if despesa["user_id"] == user_id and despesa["categoria"].lower() == categoria.lower():
                despesas.append(despesa)
        
        return despesas
    
    def listar_despesas_por_forma_pagamento(self, user_id, forma_pagamento):
        """Retorna as despesas de uma forma de pagamento específica"""
        despesas = []
        
        for despesa in self.data["despesas"]:
            if despesa["user_id"] == user_id and despesa["forma_pagamento"] == forma_pagamento:
                despesas.append(despesa)
        
        return despesas

    def gerar_relatorio_excel(self, user_id, periodo=None, categoria=None, forma_pagamento=None):
        """
        Gera um relatório Excel com as despesas do usuário.
        
        Args:
            user_id: ID do usuário no Telegram
            periodo: "mes" ou "ano" para filtrar por período atual
            categoria: Filtrar por categoria específica
            forma_pagamento: Filtrar por forma de pagamento específica
            
        Returns:
            caminho: Caminho para o arquivo Excel gerado
        """
        # Filtrar despesas do usuário
        despesas_usuario = [d for d in self.data["despesas"] if d["user_id"] == user_id]
        
        if not despesas_usuario:
            return None
            
        # Aplicar filtros adicionais
        if periodo:
            hoje = datetime.now()
            if periodo == "mes":
                inicio_periodo = datetime(hoje.year, hoje.month, 1)
            elif periodo == "ano":
                inicio_periodo = datetime(hoje.year, 1, 1)
            else:
                inicio_periodo = datetime(1900, 1, 1)  # Sem filtro temporal
                
            despesas_filtradas = []
            for d in despesas_usuario:
                try:
                    data_despesa = datetime.strptime(d["data"], "%Y-%m-%d %H:%M:%S")
                    if data_despesa >= inicio_periodo:
                        despesas_filtradas.append(d)
                except:
                    # Se houver erro no formato da data, mantém a despesa
                    despesas_filtradas.append(d)
            
            despesas_usuario = despesas_filtradas
            
        # Filtrar por categoria
        if categoria:
            despesas_usuario = [d for d in despesas_usuario if d["categoria"].lower() == categoria.lower()]
            
        # Filtrar por forma de pagamento
        if forma_pagamento:
            despesas_usuario = [d for d in despesas_usuario if d["forma_pagamento"] == forma_pagamento]
            
        # Criar DataFrame do pandas
        dados = []
        for d in despesas_usuario:
            item = {
                "Data": d["data"],
                "Valor": d["valor"],
                "Local": d["local"],
                "Categoria": d["categoria"].capitalize(),
                "Forma de Pagamento": d["forma_pagamento"]
            }
            
            # Adicionar informações de parcelamento, se existirem
            if "parcelado" in d and d["parcelado"]:
                item["Parcelas"] = d["parcelas"]
                item["Valor por Parcela"] = d["valor_parcela"]
            
            dados.append(item)
            
        df = pd.DataFrame(dados)
        
        # Ordenar por data (mais recente primeiro)
        try:
            df["Data"] = pd.to_datetime(df["Data"])
            df = df.sort_values("Data", ascending=False)
        except:
            pass
            
        # Caminho para salvar o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_despesas_{timestamp}.xlsx"
        
        # Criar o arquivo Excel
        writer = pd.ExcelWriter(nome_arquivo, engine='openpyxl')
        
        # Planilha principal com todas as despesas
        df.to_excel(writer, sheet_name="Despesas", index=False)
        
        # Planilha resumo por categoria
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