# database/database_manager.py
import sqlite3
import os
import datetime
from pathlib import Path
from utils.config import Config

class DatabaseManager:
    def __init__(self, db_file=None):
        config = Config()
        self.db_file = db_file or config.get_database_file()
        self.conn = None
        self.create_tables_if_not_exist()
    
    def get_connection(self):
        """Estabelece conexão com o banco de dados SQLite"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables_if_not_exist(self):
        """Cria as tabelas no banco de dados se elas não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Criando tabela contagem_lojas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contagem_lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loja TEXT NOT NULL,
            regional TEXT,
            setor TEXT,
            data TEXT,
            caixa_hb_623 INTEGER DEFAULT 0,
            caixa_hb_618 INTEGER DEFAULT 0,
            caixa_hnt_g INTEGER DEFAULT 0,
            caixa_hnt_p INTEGER DEFAULT 0,
            caixa_chocolate INTEGER DEFAULT 0,
            caixa_bin INTEGER DEFAULT 0,
            pallets_pbr INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            usuario TEXT,
            created_at TEXT,
            updated_at TEXT,
            cod_inventario TEXT NOT NULL
        )
        ''')
        
        # Criando tabela contagem_cd
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contagem_cd (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor TEXT NOT NULL,
            data TEXT,
            caixa_hb_623 INTEGER DEFAULT 0,
            caixa_hb_618 INTEGER DEFAULT 0,
            caixa_hnt_g INTEGER DEFAULT 0,
            caixa_hnt_p INTEGER DEFAULT 0,
            caixa_chocolate INTEGER DEFAULT 0,
            caixa_bin INTEGER DEFAULT 0,
            pallets_pbr INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            usuario TEXT,
            created_at TEXT,
            updated_at TEXT,
            cod_inventario TEXT NOT NULL
        )
        ''')
        
        # Criando tabela dados_transito
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_transito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setor TEXT,
            data TEXT,
            tipo_caixa TEXT NOT NULL,
            quantidade INTEGER DEFAULT 0,
            usuario TEXT,
            created_at TEXT,
            updated_at TEXT,
            cod_inventario TEXT NOT NULL
        )
        ''')
        
        # Criando tabela dados_fornecedor
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_fornecedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_fornecedor TEXT NOT NULL,
            tipo_caixa TEXT NOT NULL,
            quantidade INTEGER DEFAULT 0,
            created_at TEXT,
            cod_inventario TEXT NOT NULL
        )
        ''')
        
        # Criando tabela inventario_meta
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario_meta (
            cod_inventario TEXT PRIMARY KEY,
            data_inicio TEXT,
            data_fim TEXT,
            status TEXT DEFAULT 'em_andamento',
            descricao TEXT
        )
        ''')
        
        conn.commit()
    
    def gerar_codigo_inventario(self):
        """Gera um novo código de inventário com base na data"""
        agora = datetime.datetime.now()
        codigo = f"INV-{agora.strftime('%Y%m%d-%H%M%S')}"
        return codigo
    
    def iniciar_novo_inventario(self, descricao=""):
        """Inicia um novo inventário no sistema"""
        cod_inventario = self.gerar_codigo_inventario()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data_inicio = datetime.datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO inventario_meta (cod_inventario, data_inicio, descricao, status)
        VALUES (?, ?, ?, ?)
        ''', (cod_inventario, data_inicio, descricao, 'em_andamento'))
        
        conn.commit()
        return cod_inventario
    
    def get_inventarios_ativos(self):
        """Retorna todos os inventários em andamento"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM inventario_meta WHERE status = 'em_andamento'
        ORDER BY data_inicio DESC
        ''')
        
        return cursor.fetchall()
    
    def get_todos_inventarios(self):
        """Retorna todos os inventários"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM inventario_meta
        ORDER BY data_inicio DESC
        ''')
        
        return cursor.fetchall()
    
    def finalizar_inventario(self, cod_inventario):
        """Marca um inventário como finalizado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data_fim = datetime.datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE inventario_meta
        SET status = 'finalizado', data_fim = ?
        WHERE cod_inventario = ?
        ''', (data_fim, cod_inventario))
        
        conn.commit()
    
    def inserir_contagem_loja(self, dados, cod_inventario):
        """Insere ou atualiza dados de contagem de loja"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existe um registro para esta loja neste inventário
        cursor.execute('''
        SELECT id FROM contagem_lojas 
        WHERE loja = ? AND cod_inventario = ?
        ''', (dados['loja'], cod_inventario))
        
        resultado = cursor.fetchone()
        timestamp = datetime.datetime.now().isoformat()
        
        if resultado:
            # Atualizar registro existente
            id_loja = resultado['id']
            cursor.execute('''
            UPDATE contagem_lojas SET
            setor = ?,
            data = ?,
            caixa_hb_623 = ?,
            caixa_hb_618 = ?,
            caixa_hnt_g = ?,
            caixa_hnt_p = ?,
            caixa_chocolate = ?,
            caixa_bin = ?,
            pallets_pbr = ?,
            status = ?,
            usuario = ?,
            updated_at = ?
            WHERE id = ?
            ''', (
                dados.get('setor', ''),
                dados.get('data', ''),
                dados.get('caixa_hb_623', 0),
                dados.get('caixa_hb_618', 0),
                dados.get('caixa_hnt_g', 0),
                dados.get('caixa_hnt_p', 0),
                dados.get('caixa_chocolate', 0),
                dados.get('caixa_bin', 0),
                dados.get('pallets_pbr', 0),
                dados.get('status', 'pendente'),
                dados.get('usuario', ''),
                timestamp,
                id_loja
            ))
        else:
            # Inserir novo registro
            cursor.execute('''
            INSERT INTO contagem_lojas (
                loja,
                regional,
                setor,
                data,
                caixa_hb_623,
                caixa_hb_618,
                caixa_hnt_g,
                caixa_hnt_p,
                caixa_chocolate,
                caixa_bin,
                pallets_pbr,
                status,
                usuario,
                created_at,
                updated_at,
                cod_inventario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['loja'],
                dados.get('regional', ''),
                dados.get('setor', ''),
                dados.get('data', ''),
                dados.get('caixa_hb_623', 0),
                dados.get('caixa_hb_618', 0),
                dados.get('caixa_hnt_g', 0),
                dados.get('caixa_hnt_p', 0),
                dados.get('caixa_chocolate', 0),
                dados.get('caixa_bin', 0),
                dados.get('pallets_pbr', 0),
                dados.get('status', 'pendente'),
                dados.get('usuario', ''),
                timestamp,
                timestamp,
                cod_inventario
            ))
        
        conn.commit()
    
    def inserir_contagem_cd(self, dados, cod_inventario):
        """Insere ou atualiza dados de contagem do CD"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existe um registro para este setor neste inventário
        cursor.execute('''
        SELECT id FROM contagem_cd 
        WHERE setor = ? AND cod_inventario = ?
        ''', (dados['setor'], cod_inventario))
        
        resultado = cursor.fetchone()
        timestamp = datetime.datetime.now().isoformat()
        
        if resultado:
            # Atualizar registro existente
            id_cd = resultado['id']
            cursor.execute('''
            UPDATE contagem_cd SET
            data = ?,
            caixa_hb_623 = ?,
            caixa_hb_618 = ?,
            caixa_hnt_g = ?,
            caixa_hnt_p = ?,
            caixa_chocolate = ?,
            caixa_bin = ?,
            pallets_pbr = ?,
            status = ?,
            usuario = ?,
            updated_at = ?
            WHERE id = ?
            ''', (
                dados.get('data', ''),
                dados.get('caixa_hb_623', 0),
                dados.get('caixa_hb_618', 0),
                dados.get('caixa_hnt_g', 0),
                dados.get('caixa_hnt_p', 0),
                dados.get('caixa_chocolate', 0),
                dados.get('caixa_bin', 0),
                dados.get('pallets_pbr', 0),
                dados.get('status', 'pendente'),
                dados.get('usuario', ''),
                timestamp,
                id_cd
            ))
        else:
            # Inserir novo registro
            cursor.execute('''
            INSERT INTO contagem_cd (
                setor,
                data,
                caixa_hb_623,
                caixa_hb_618,
                caixa_hnt_g,
                caixa_hnt_p,
                caixa_chocolate,
                caixa_bin,
                pallets_pbr,
                status,
                usuario,
                created_at,
                updated_at,
                cod_inventario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['setor'],
                dados.get('data', ''),
                dados.get('caixa_hb_623', 0),
                dados.get('caixa_hb_618', 0),
                dados.get('caixa_hnt_g', 0),
                dados.get('caixa_hnt_p', 0),
                dados.get('caixa_chocolate', 0),
                dados.get('caixa_bin', 0),
                dados.get('pallets_pbr', 0),
                dados.get('status', 'pendente'),
                dados.get('usuario', ''),
                timestamp,
                timestamp,
                cod_inventario
            ))
        
        conn.commit()
    
    def inserir_dados_transito(self, dados, cod_inventario):
        """Insere dados de trânsito no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO dados_transito (
            setor,
            data,
            tipo_caixa,
            quantidade,
            usuario,
            created_at,
            updated_at,
            cod_inventario
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('setor', ''),
            dados.get('data', ''),
            dados['tipo_caixa'],
            dados.get('quantidade', 0),
            dados.get('usuario', ''),
            timestamp,
            timestamp,
            cod_inventario
        ))
        
        conn.commit()
    
    def inserir_dados_fornecedor(self, dados, cod_inventario):
        """Insere dados de fornecedor no banco"""
        conn = self.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO dados_fornecedor (
            tipo_fornecedor,
            tipo_caixa,
            quantidade,
            created_at,
            cod_inventario
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            dados['tipo_fornecedor'],
            dados['tipo_caixa'],
            dados.get('quantidade', 0),
            timestamp,
            cod_inventario
        ))
        
        conn.commit()
    
    def get_dados_inventario_atual(self, cod_inventario):
        """Retorna um resumo dos dados do inventário atual"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Dados de lojas
        cursor.execute('''
        SELECT COUNT(*) as total_lojas,
               SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as lojas_finalizadas,
               SUM(caixa_hb_623) as total_hb_623,
               SUM(caixa_hb_618) as total_hb_618,
               SUM(caixa_hnt_g) as total_hnt_g,
               SUM(caixa_hnt_p) as total_hnt_p,
               SUM(caixa_chocolate) as total_chocolate,
               SUM(caixa_bin) as total_bin,
               SUM(pallets_pbr) as total_pallets
        FROM contagem_lojas
        WHERE cod_inventario = ?
        ''', (cod_inventario,))
        
        dados_lojas = cursor.fetchone()
        
        # Dados de CD
        cursor.execute('''
        SELECT COUNT(*) as total_setores,
               SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as setores_finalizados,
               SUM(caixa_hb_623) as total_hb_623,
               SUM(caixa_hb_618) as total_hb_618,
               SUM(caixa_hnt_g) as total_hnt_g,
               SUM(caixa_hnt_p) as total_hnt_p,
               SUM(caixa_chocolate) as total_chocolate,
               SUM(caixa_bin) as total_bin,
               SUM(pallets_pbr) as total_pallets
        FROM contagem_cd
        WHERE cod_inventario = ?
        ''', (cod_inventario,))
        
        dados_cd = cursor.fetchone()
        
        # Dados de trânsito
        cursor.execute('''
        SELECT tipo_caixa, SUM(quantidade) as total
        FROM dados_transito
        WHERE cod_inventario = ?
        GROUP BY tipo_caixa
        ''', (cod_inventario,))
        
        dados_transito = cursor.fetchall()
        
        # Dados de fornecedor
        cursor.execute('''
        SELECT tipo_caixa, SUM(quantidade) as total
        FROM dados_fornecedor
        WHERE cod_inventario = ?
        GROUP BY tipo_caixa
        ''', (cod_inventario,))
        
        dados_fornecedor = cursor.fetchall()
        
        return {
            'dados_lojas': dict(dados_lojas) if dados_lojas else {},
            'dados_cd': dict(dados_cd) if dados_cd else {},
            'dados_transito': [dict(row) for row in dados_transito],
            'dados_fornecedor': [dict(row) for row in dados_fornecedor]
        }
    
    def get_lojas_por_regional(self, cod_inventario):
        """Retorna contagem de lojas agrupadas por regional"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT regional, 
               COUNT(*) as total_lojas,
               SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as lojas_finalizadas
        FROM contagem_lojas
        WHERE cod_inventario = ?
        GROUP BY regional
        ''', (cod_inventario,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_lojas_pendentes(self, cod_inventario):
        """Retorna lista de lojas pendentes agrupadas por regional"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT regional, loja
        FROM contagem_lojas
        WHERE cod_inventario = ? AND status != 'finalizado'
        ORDER BY regional, loja
        ''', (cod_inventario,))
        
        resultados = cursor.fetchall()
        
        # Agrupando lojas por regional
        lojas_por_regional = {}
        for row in resultados:
            regional = row['regional'] or 'Sem Regional'
            if regional not in lojas_por_regional:
                lojas_por_regional[regional] = []
            lojas_por_regional[regional].append(row['loja'])
        
        return lojas_por_regional
    

    def get_lojas_finalizadas(self, cod_inventario, regional=None):
        """Retorna uma lista de lojas finalizadas no inventário atual, opcionalmente filtradas por regional"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if regional and regional != 'Sem Regional':
                cursor.execute('''
                SELECT loja, regional
                FROM contagem_lojas
                WHERE cod_inventario = ? AND status = 'finalizado' AND regional = ?
                ''', (cod_inventario, regional))
            else:
                # Se for 'Sem Regional', precisamos considerar NULL ou vazio
                if regional == 'Sem Regional':
                    cursor.execute('''
                    SELECT loja, regional
                    FROM contagem_lojas
                    WHERE cod_inventario = ? AND status = 'finalizado' AND (regional IS NULL OR regional = '')
                    ''', (cod_inventario,))
                else:
                    # Se regional for None, retornar todas as lojas finalizadas
                    cursor.execute('''
                    SELECT loja, regional
                    FROM contagem_lojas
                    WHERE cod_inventario = ? AND status = 'finalizado'
                    ''', (cod_inventario,))
            
            resultados = cursor.fetchall()
            return [dict(row) for row in resultados]
        except Exception as e:
            print(f"Erro ao buscar lojas finalizadas: {e}")
            return []

def get_setores_finalizados(self, cod_inventario):
    """Retorna uma lista de setores finalizados no inventário atual"""
    conn = self.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT setor
        FROM contagem_cd
        WHERE cod_inventario = ? AND status = 'finalizado'
        ''', (cod_inventario,))
        
        resultados = cursor.fetchall()
        return [dict(row) for row in resultados]
    except Exception as e:
        print(f"Erro ao buscar setores finalizados: {e}")
        return []