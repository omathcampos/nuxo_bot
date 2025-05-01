import pandas as pd
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def exportar_gastos_para_excel(gastos, nome_usuario):
    """
    Exporta os gastos fornecidos para um arquivo Excel
    
    Args:
        gastos: Lista de dicionários contendo os gastos
        nome_usuario: Nome do usuário para incluir no nome do arquivo
        
    Returns:
        str: Caminho para o arquivo Excel gerado
    """
    try:
        if not gastos:
            return None
        
        # Criar diretório para arquivos se não existir
        diretorio = 'exports'
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
        
        # Formatar data para nome do arquivo
        data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"{diretorio}/gastos_{nome_usuario.replace(' ', '_')}_{data_atual}.xlsx"
        
        # Converter para DataFrame
        df = pd.DataFrame(gastos)
        
        # Renomear colunas para português
        colunas = {
            'valor': 'Valor (R$)',
            'forma_pagamento': 'Forma de Pagamento',
            'parcelas': 'Parcelas',
            'categoria': 'Categoria',
            'local': 'Local/Estabelecimento',
            'data': 'Data',
            'criado_em': 'Registrado em'
        }
        
        # Renomear apenas as colunas que existem no DataFrame
        colunas_existentes = {k: v for k, v in colunas.items() if k in df.columns}
        df = df.rename(columns=colunas_existentes)
        
        # Ordenar por data
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df = df.sort_values(by='Data', ascending=False)
            df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')
        
        # Formatação opcional
        if 'Valor (R$)' in df.columns:
            df['Valor (R$)'] = df['Valor (R$)'].astype(float)
        
        # Remover colunas técnicas que não interessam ao usuário
        colunas_a_remover = ['id', 'usuario_id']
        for col in colunas_a_remover:
            if col in df.columns:
                df = df.drop(columns=[col])
        
        # Salvar como Excel
        writer = pd.ExcelWriter(nome_arquivo, engine='openpyxl')
        df.to_excel(writer, sheet_name='Gastos', index=False)
        
        # Autoajustar largura das colunas
        worksheet = writer.sheets['Gastos']
        for i, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + i)].width = max_length
        
        writer.close()
        
        logger.info(f"Arquivo Excel exportado com sucesso: {nome_arquivo}")
        return nome_arquivo
    
    except Exception as e:
        logger.error(f"Erro ao exportar para Excel: {e}")
        return None 