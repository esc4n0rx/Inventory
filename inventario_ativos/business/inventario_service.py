# business/inventario_service.py
import os
import datetime
from database.database_manager import DatabaseManager
from import_export.csv_manager import CSVManager

class InventarioService:
    def __init__(self, db_manager=None, csv_manager=None):
        """Inicializa o serviço de inventário"""
        self.db_manager = db_manager or DatabaseManager()
        self.csv_manager = csv_manager or CSVManager(self.db_manager)
        self.inventario_atual = None
    
    def iniciar_novo_inventario(self, descricao=""):
        """Inicia um novo inventário no sistema"""
        self.inventario_atual = self.db_manager.iniciar_novo_inventario(descricao)
        return self.inventario_atual
    
    def carregar_inventario_existente(self, cod_inventario):
        """Carrega um inventário existente"""
        # Verificar se o inventário existe
        inventarios = self.db_manager.get_todos_inventarios()
        for inv in inventarios:
            if inv['cod_inventario'] == cod_inventario:
                self.inventario_atual = cod_inventario
                return True
        return False
    
    def get_inventarios_disponiveis(self):
        """Retorna a lista de inventários disponíveis"""
        return self.db_manager.get_todos_inventarios()
    
    def get_inventarios_ativos(self):
        """Retorna a lista de inventários ativos"""
        return self.db_manager.get_inventarios_ativos()
    
    def finalizar_inventario_atual(self):
        """Finaliza o inventário atual"""
        if self.inventario_atual:
            self.db_manager.finalizar_inventario(self.inventario_atual)
            return True
        return False
    
    def get_resumo_inventario_atual(self):
        """Retorna um resumo do inventário atual"""
        if not self.inventario_atual:
            return None
        
        return self.db_manager.get_dados_inventario_atual(self.inventario_atual)
    
    def get_lojas_por_regional(self):
        """Retorna contagem de lojas agrupadas por regional"""
        if not self.inventario_atual:
            return []
        
        return self.db_manager.get_lojas_por_regional(self.inventario_atual)
    
    def get_lojas_pendentes(self):
        """Retorna lista de lojas pendentes agrupadas por regional"""
        if not self.inventario_atual:
            return {}
        
        return self.db_manager.get_lojas_pendentes(self.inventario_atual)
    
    def importar_dados_csv(self, usuario="sistema"):
        """Importa todos os dados dos CSVs para o inventário atual"""
        if not self.inventario_atual:
            return {
                'status': False, 
                'message': 'Nenhum inventário ativo. Inicie um novo inventário ou carregue um existente.'
            }
        
        resultados = {
            'contagem_lojas': self.csv_manager.importar_contagem_lojas(self.inventario_atual, usuario),
            'contagem_cd': self.csv_manager.importar_contagem_cd(self.inventario_atual, usuario),
            'dados_transito': self.csv_manager.importar_dados_transito(self.inventario_atual, usuario)
        }
        
        # Verificar se ocorreu algum erro
        erros = [r['message'] for k, r in resultados.items() if not r['status']]
        
        if erros:
            return {
                'status': False,
                'message': f'Ocorreram erros durante a importação: {", ".join(erros)}',
                'resultados': resultados
            }
        
        return {
            'status': True,
            'message': 'Todos os dados foram importados com sucesso.',
            'resultados': resultados
        }
    
    def adicionar_dados_fornecedor(self, tipo_fornecedor, tipo_caixa, quantidade):
        """Adiciona dados de fornecedor ao inventário atual"""
        if not self.inventario_atual:
            return {
                'status': False, 
                'message': 'Nenhum inventário ativo. Inicie um novo inventário ou carregue um existente.'
            }
        
        try:
            dados = {
                'tipo_fornecedor': tipo_fornecedor,
                'tipo_caixa': tipo_caixa,
                'quantidade': int(quantidade)
            }
            
            self.db_manager.inserir_dados_fornecedor(dados, self.inventario_atual)
            
            return {
                'status': True,
                'message': 'Dados do fornecedor adicionados com sucesso.'
            }
        except Exception as e:
            return {
                'status': False,
                'message': f'Erro ao adicionar dados do fornecedor: {str(e)}'
            }
    
    def exportar_relatorio_atual(self, output_path=None):
        """Exporta relatório do inventário atual"""
        if not self.inventario_atual:
            return {
                'status': False, 
                'message': 'Nenhum inventário ativo. Inicie um novo inventário ou carregue um existente.'
            }
        
        if not output_path:
            # Criar nome de arquivo baseado na data e código do inventário
            data_atual = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'relatorios/relatorio_{self.inventario_atual}_{data_atual}.csv'
        
        # Certificar-se de que o diretório de relatórios existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        return self.csv_manager.exportar_relatorio_inventario(self.inventario_atual, output_path)
    
    def get_tipo_caixas(self):
        """Retorna os tipos de caixas disponíveis no sistema"""
        return [
            'hb_623',
            'hb_618',
            'hnt_g',
            'hnt_p',
            'chocolate',
            'bin',
            'pallets_pbr'
        ]
    
    def get_tipos_fornecedor(self):
        """Retorna os tipos de fornecedores disponíveis no sistema"""
        return [
            'FORNECEDOR RJ',
            'FORNECEDOR SP',
            'FORNECEDOR ES',
            'Outro'
        ]
    
    def configurar_caminhos_csv(self, lojas_path=None, setores_path=None, 
                              contagem_lojas_path=None, contagem_cd_path=None, 
                              dados_transito_path=None):
        """Configura os caminhos para os arquivos CSV"""
        self.csv_manager.set_csv_paths(
            lojas_path, 
            setores_path, 
            contagem_lojas_path, 
            contagem_cd_path, 
            dados_transito_path
        )
        
        return {
            'status': True,
            'message': 'Caminhos configurados com sucesso.'
        }
    
    def criar_csv_padrao(self):
        """Cria arquivos CSV padrão se eles não existirem"""
        self.csv_manager.criar_csv_padrao()
        return {
            'status': True,
            'message': 'Arquivos CSV padrão criados com sucesso.'
        }
    

    def importar_dados_csv_silencioso(self, usuario="sistema"):
        """Importa todos os dados dos CSVs para o inventário atual de forma silenciosa (sem confirmações)"""
        if not self.inventario_atual:
            return {
                'status': False, 
                'message': 'Nenhum inventário ativo.',
                'modified': False
            }
        
        resultados = {
            'contagem_lojas': self.csv_manager.importar_contagem_lojas(self.inventario_atual, usuario),
            'contagem_cd': self.csv_manager.importar_contagem_cd(self.inventario_atual, usuario),
            'dados_transito': self.csv_manager.importar_dados_transito(self.inventario_atual, usuario)
        }
        
        # Verificar se algum arquivo foi modificado
        arquivos_modificados = any(r.get('modified', False) for _, r in resultados.items() if r['status'])
        
        # Verificar se ocorreu algum erro
        erros = [r['message'] for k, r in resultados.items() if not r['status']]
        
        if erros:
            return {
                'status': False,
                'message': f'Erros durante a importação: {", ".join(erros)}',
                'resultados': resultados,
                'modified': arquivos_modificados
            }
        
        # Contar registros importados
        total_importado = sum(r.get('count', 0) for _, r in resultados.items() if r['status'] and r.get('modified', False))
        
        if arquivos_modificados:
            mensagem = f'{total_importado} registros atualizados.'
        else:
            mensagem = 'Nenhuma atualização necessária.'
        
        return {
            'status': True,
            'message': mensagem,
            'resultados': resultados,
            'modified': arquivos_modificados,
            'count': total_importado
        }
    

    # Adicione este método ao InventarioService

def atualizar_totais_lojas_setores(self):
    """Atualiza o total de lojas e setores baseado nos CSVs"""
    if not self.inventario_atual:
        return {
            'status': False, 
            'message': 'Nenhum inventário ativo.'
        }
    
    try:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Lê os CSVs de lojas e setores
        lojas_csv = self.csv_manager.ler_lojas_csv(force_reload=True)
        setores_csv = self.csv_manager.ler_setores_csv(force_reload=True)
        
        # Obtém todas as lojas do banco
        cursor.execute('''
        SELECT loja FROM contagem_lojas
        WHERE cod_inventario = ?
        ''', (self.inventario_atual,))
        
        lojas_banco = [row['loja'] for row in cursor.fetchall()]
        
        # Obtém todos os setores do banco
        cursor.execute('''
        SELECT setor FROM contagem_cd
        WHERE cod_inventario = ?
        ''', (self.inventario_atual,))
        
        setores_banco = [row['setor'] for row in cursor.fetchall()]
        
        # Conta quantas lojas faltam ser inseridas
        lojas_ausentes = []
        for loja in lojas_csv:
            nome_loja = loja.get('loja', '').strip()
            if nome_loja and nome_loja not in lojas_banco:
                lojas_ausentes.append(nome_loja)
        
        # Conta quantos setores faltam ser inseridos
        setores_ausentes = []
        for setor in setores_csv:
            nome_setor = setor.get('setor', '').strip()
            if nome_setor and nome_setor not in setores_banco:
                setores_ausentes.append(nome_setor)
        
        return {
            'status': True,
            'lojas_total': len(lojas_csv),
            'lojas_preenchidas': len(lojas_banco),
            'lojas_ausentes': len(lojas_ausentes),
            'setores_total': len(setores_csv),
            'setores_preenchidos': len(setores_banco),
            'setores_ausentes': len(setores_ausentes)
        }
    
    except Exception as e:
        return {
            'status': False,
            'message': f'Erro ao atualizar totais: {str(e)}'
        }
        


    # Adicione este método ao InventarioService

def criar_lojas_setores_faltantes(self):
    """Cria registros vazios para todas as lojas e setores que estão no CSV mas não no banco"""
    if not self.inventario_atual:
        return {
            'status': False, 
            'message': 'Nenhum inventário ativo.'
        }
    
    try:
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Lê os CSVs de lojas e setores
        lojas_csv = self.csv_manager.ler_lojas_csv(force_reload=True)
        setores_csv = self.csv_manager.ler_setores_csv(force_reload=True)
        
        # Obtém todas as lojas do banco
        cursor.execute('''
        SELECT loja FROM contagem_lojas
        WHERE cod_inventario = ?
        ''', (self.inventario_atual,))
        
        lojas_banco = [row['loja'] for row in cursor.fetchall()]
        
        # Obtém todos os setores do banco
        cursor.execute('''
        SELECT setor FROM contagem_cd
        WHERE cod_inventario = ?
        ''', (self.inventario_atual,))
        
        setores_banco = [row['setor'] for row in cursor.fetchall()]
        
        # Timestamp atual
        timestamp = datetime.datetime.now().isoformat()
        
        # Cria registros para lojas ausentes
        lojas_criadas = 0
        for loja in lojas_csv:
            nome_loja = loja.get('loja', '').strip()
            regional = loja.get('regional', '').strip()
            
            if nome_loja and nome_loja not in lojas_banco:
                cursor.execute('''
                INSERT INTO contagem_lojas (
                    loja, regional, setor, data, status, 
                    caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                    caixa_chocolate, caixa_bin, pallets_pbr,
                    usuario, created_at, updated_at, cod_inventario
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?, ?, ?)
                ''', (
                    nome_loja, regional, 'Geral', timestamp, 'pendente', 
                    'sistema', timestamp, timestamp, self.inventario_atual
                ))
                lojas_criadas += 1
        
        # Cria registros para setores ausentes
        setores_criados = 0
        for setor in setores_csv:
            nome_setor = setor.get('setor', '').strip()
            
            if nome_setor and nome_setor not in setores_banco:
                cursor.execute('''
                INSERT INTO contagem_cd (
                    setor, data, status, 
                    caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                    caixa_chocolate, caixa_bin, pallets_pbr,
                    usuario, created_at, updated_at, cod_inventario
                ) VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?, ?, ?)
                ''', (
                    nome_setor, timestamp, 'pendente', 
                    'sistema', timestamp, timestamp, self.inventario_atual
                ))
                setores_criados += 1
        
        conn.commit()
        
        return {
            'status': True,
            'message': f'Criados {lojas_criadas} lojas e {setores_criados} setores ausentes',
            'lojas_criadas': lojas_criadas,
            'setores_criados': setores_criados
        }
    
    except Exception as e:
        return {
            'status': False,
            'message': f'Erro ao criar lojas/setores faltantes: {str(e)}'
        }