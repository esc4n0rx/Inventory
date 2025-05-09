# import_export/csv_manager.py - Versão corrigida
import csv
import os
import datetime
from utils.config import Config

class CSVManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Carregar caminhos de arquivos da configuração
        config = Config()
        csv_paths = config.get_csv_paths()
        
        self.csv_lojas_path = csv_paths['lojas_path']
        self.csv_setores_path = csv_paths['setores_path']
        self.csv_contagem_lojas_path = csv_paths['contagem_lojas_path']
        self.csv_contagem_cd_path = csv_paths['contagem_cd_path']
        self.csv_dados_transito_path = csv_paths['dados_transito_path']
        
        # Manter cache dos dados carregados
        self.cached_lojas = None
        self.cached_setores = None
        self.last_load_time = {
            'lojas': 0,
            'setores': 0,
            'contagem_lojas': 0,
            'contagem_cd': 0,
            'dados_transito': 0
        }
    
    def set_csv_paths(self, lojas_path=None, setores_path=None, 
                     contagem_lojas_path=None, contagem_cd_path=None, 
                     dados_transito_path=None):
        """Define os caminhos para os arquivos CSV"""
        if lojas_path:
            self.csv_lojas_path = lojas_path
            self.cached_lojas = None  # Resetar cache
        if setores_path:
            self.csv_setores_path = setores_path
            self.cached_setores = None  # Resetar cache
        if contagem_lojas_path:
            self.csv_contagem_lojas_path = contagem_lojas_path
        if contagem_cd_path:
            self.csv_contagem_cd_path = contagem_cd_path
        if dados_transito_path:
            self.csv_dados_transito_path = dados_transito_path
    
    def _garantir_diretorios(self):
        """Garante que os diretórios para os CSVs existam"""
        diretórios = [
            os.path.dirname(self.csv_lojas_path),
            os.path.dirname(self.csv_setores_path),
            os.path.dirname(self.csv_contagem_lojas_path),
            os.path.dirname(self.csv_contagem_cd_path),
            os.path.dirname(self.csv_dados_transito_path)
        ]
        
        for dir in diretórios:
            if dir and not os.path.exists(dir):
                os.makedirs(dir)
    
    def _arquivo_modificado(self, filepath, tipo):
        """Verifica se um arquivo foi modificado desde a última vez que foi carregado"""
        if not os.path.exists(filepath):
            return False
        
        mtime = os.path.getmtime(filepath)
        return mtime > self.last_load_time[tipo]
    
    def ler_lojas_csv(self, force_reload=False):
        """Lê o arquivo CSV de lojas e retorna uma lista de dicionários"""
        # Usar cache se disponível e não forçar recarga
        if self.cached_lojas and not force_reload and not self._arquivo_modificado(self.csv_lojas_path, 'lojas'):
            return self.cached_lojas
        
        if not os.path.exists(self.csv_lojas_path):
            self.cached_lojas = []
            return []
        
        lojas = []
        try:
            with open(self.csv_lojas_path, mode='r', encoding='utf-8-sig') as file:  # Changed to utf-8-sig
                reader = csv.DictReader(file)
                for row in reader:
                    # Garantir que loja e regional existam e não sejam vazios
                    loja = row.get('loja', '').strip()
                    if not loja:
                        continue
                    
                    # Adicionar loja ao resultado
                    lojas.append({
                        'loja': loja,
                        'regional': row.get('regional', '').strip()
                    })
            
            # Atualizar cache e tempo de carregamento
            self.cached_lojas = lojas
            self.last_load_time['lojas'] = os.path.getmtime(self.csv_lojas_path)
            return lojas
        except Exception as e:
            print(f"Erro ao ler arquivo CSV de lojas: {e}")
            return []
    
    def ler_setores_csv(self, force_reload=False):
        """Lê o arquivo CSV de setores e retorna uma lista de dicionários"""
        # Usar cache se disponível e não forçar recarga
        if self.cached_setores and not force_reload and not self._arquivo_modificado(self.csv_setores_path, 'setores'):
            return self.cached_setores
        
        if not os.path.exists(self.csv_setores_path):
            self.cached_setores = []
            return []
        
        setores = []
        try:
            with open(self.csv_setores_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Garantir que setor exista e não seja vazio
                    setor = row.get('setor', '').strip()
                    if not setor:
                        continue
                    
                    # Adicionar setor ao resultado
                    setores.append({
                        'setor': setor,
                        'descricao': row.get('descricao', '').strip()
                    })
            
            # Atualizar cache e tempo de carregamento
            self.cached_setores = setores
            self.last_load_time['setores'] = os.path.getmtime(self.csv_setores_path)
            return setores
        except Exception as e:
            print(f"Erro ao ler arquivo CSV de setores: {e}")
            return []
    
    # CORREÇÃO PARA IMPORTAR_CONTAGEM_LOJAS no CSV_MANAGER

    def importar_contagem_lojas(self, cod_inventario, usuario="sistema", force_reload=False):
        """Importa dados do CSV de contagem de lojas para o banco de dados"""
        if not os.path.exists(self.csv_contagem_lojas_path):
            return {'status': False, 'message': 'Arquivo CSV de contagem de lojas não encontrado.'}
        
        # Verificar se o arquivo foi modificado
        if not force_reload and not self._arquivo_modificado(self.csv_contagem_lojas_path, 'contagem_lojas'):
            return {'status': True, 'message': 'Arquivo não modificado desde a última importação. Nenhuma atualização necessária.', 'modified': False}
        
        try:
            imported_count = 0
            
            # Obter mapeamento de lojas para regionais do CSV de lojas
            lojas_regionais = {}
            lojas_csv = self.ler_lojas_csv(force_reload=True)
            for loja in lojas_csv:
                nome_loja = loja.get('loja', '').strip()
                regional = loja.get('regional', '').strip()
                if nome_loja:
                    lojas_regionais[nome_loja] = regional
            
            with open(self.csv_contagem_lojas_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # AJUSTE: Verificar onde está o nome da loja
                    # Estratégia 1: Usar a coluna "loja" se preenchida
                    loja = row.get('loja', '').strip() 
                    
                    # Estratégia 2: Se "loja" vazia mas "setor" preenchido, usar "setor" como nome da loja
                    if not loja and row.get('setor', '').strip():
                        loja = row.get('setor', '').strip()
                    
                    # Estratégia 3: Se ambos estiverem vazios mas tiver ID, criar nome baseado no ID
                    if not loja and 'id' in row:
                        loja = f"Loja ID:{row['id']}"
                    
                    # Obter regional do CSV de referência de lojas
                    regional = row.get('regional', '').strip()
                    if not regional and loja in lojas_regionais:
                        regional = lojas_regionais[loja]
                    
                    # Montar dados da loja
                    dados_loja = {
                        'loja': loja,
                        'regional': regional,
                        'setor': 'Geral',  # Padronizar como "Geral" já que "setor" está sendo usado como nome da loja
                        'data': row.get('data', datetime.datetime.now().strftime('%Y-%m-%d')),
                        'caixa_hb_623': int(row.get('caixa_hb_623', 0) or 0),
                        'caixa_hb_618': int(row.get('caixa_hb_618', 0) or 0),
                        'caixa_hnt_g': int(row.get('caixa_hnt_g', 0) or 0),
                        'caixa_hnt_p': int(row.get('caixa_hnt_p', 0) or 0),
                        'caixa_chocolate': int(row.get('caixa_chocolate', 0) or 0),
                        'caixa_bin': int(row.get('caixa_bin', 0) or 0),
                        'pallets_pbr': int(row.get('pallets_pbr', 0) or 0),
                        'status': row.get('status', 'finalizado').strip().lower(),  # Default para 'finalizado'
                        'usuario': row.get('usuario', usuario)
                    }
                    
                    # Validar dados mínimos
                    if not dados_loja['loja']:
                        continue
                    
                    # Inserir no banco de dados
                    self.db_manager.inserir_contagem_loja(dados_loja, cod_inventario)
                    imported_count += 1
            
            # Atualizar tempo de carregamento
            self.last_load_time['contagem_lojas'] = os.path.getmtime(self.csv_contagem_lojas_path)
            
            return {
                'status': True, 
                'message': f'Importação concluída com sucesso. {imported_count} registros importados.',
                'modified': True,
                'count': imported_count
            }
            
        except Exception as e:
            return {'status': False, 'message': f'Erro ao importar dados: {str(e)}'}
    
    def importar_contagem_cd(self, cod_inventario, usuario="sistema", force_reload=False):
        """Importa dados do CSV de contagem do CD para o banco de dados"""
        if not os.path.exists(self.csv_contagem_cd_path):
            return {'status': False, 'message': 'Arquivo CSV de contagem do CD não encontrado.'}
        
        # Verificar se o arquivo foi modificado
        if not force_reload and not self._arquivo_modificado(self.csv_contagem_cd_path, 'contagem_cd'):
            return {'status': True, 'message': 'Arquivo não modificado desde a última importação. Nenhuma atualização necessária.', 'modified': False}
        
        try:
            imported_count = 0
            
            # Obter lista de setores do CSV de setores (para validação)
            setores_ref = {setor['setor']: setor['descricao'] for setor in self.ler_setores_csv(force_reload=True)}
            
            with open(self.csv_contagem_cd_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Processando os dados do CSV
                    setor = row.get('setor', '').strip()
                    
                    # Se setor não existir mas tiver ID, pode ser um registro válido
                    if not setor and 'id' in row:
                        setor = f"Setor ID:{row['id']}"
                    
                    # Verificar se o setor está na lista de referência (mas não impedir importação)
                    setor_valido = setor in setores_ref
                    
                    dados_cd = {
                        'setor': setor,
                        'data': row.get('data', datetime.datetime.now().strftime('%Y-%m-%d')),
                        'caixa_hb_623': int(row.get('caixa_hb_623', 0) or 0),
                        'caixa_hb_618': int(row.get('caixa_hb_618', 0) or 0),
                        'caixa_hnt_g': int(row.get('caixa_hnt_g', 0) or 0),
                        'caixa_hnt_p': int(row.get('caixa_hnt_p', 0) or 0),
                        'caixa_chocolate': int(row.get('caixa_chocolate', 0) or 0),
                        'caixa_bin': int(row.get('caixa_bin', 0) or 0),
                        'pallets_pbr': int(row.get('pallets_pbr', 0) or 0),
                        'status': row.get('status', 'finalizado').strip().lower(),  # Default para 'finalizado'
                        'usuario': row.get('usuario', usuario)
                    }
                    
                    # Validar dados mínimos
                    if not dados_cd['setor']:
                        continue
                    
                    # Inserir no banco de dados
                    self.db_manager.inserir_contagem_cd(dados_cd, cod_inventario)
                    imported_count += 1
            
            # Atualizar tempo de carregamento
            self.last_load_time['contagem_cd'] = os.path.getmtime(self.csv_contagem_cd_path)
            
            return {
                'status': True, 
                'message': f'Importação concluída com sucesso. {imported_count} registros importados.',
                'modified': True,
                'count': imported_count
            }
            
        except Exception as e:
            return {'status': False, 'message': f'Erro ao importar dados: {str(e)}'}
    
    def importar_dados_transito(self, cod_inventario, usuario="sistema", force_reload=False):
        """Importa dados do CSV de trânsito para o banco de dados"""
        if not os.path.exists(self.csv_dados_transito_path):
            return {'status': False, 'message': 'Arquivo CSV de dados em trânsito não encontrado.'}
        
        # Verificar se o arquivo foi modificado
        if not force_reload and not self._arquivo_modificado(self.csv_dados_transito_path, 'dados_transito'):
            return {'status': True, 'message': 'Arquivo não modificado desde a última importação. Nenhuma atualização necessária.', 'modified': False}
        
        try:
            imported_count = 0
            with open(self.csv_dados_transito_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Processando os dados do CSV
                    dados_transito = {
                        'setor': row.get('setor', '').strip(),
                        'data': row.get('data', datetime.datetime.now().strftime('%Y-%m-%d')),
                        'tipo_caixa': row.get('tipo_caixa', '').strip(),
                        'quantidade': int(row.get('quantidade', 0) or 0),
                        'usuario': row.get('usuario', usuario)
                    }
                    
                    # Validar dados mínimos
                    if not dados_transito['tipo_caixa']:
                        continue
                    
                    # Inserir no banco de dados
                    self.db_manager.inserir_dados_transito(dados_transito, cod_inventario)
                    imported_count += 1
            
            # Atualizar tempo de carregamento
            self.last_load_time['dados_transito'] = os.path.getmtime(self.csv_dados_transito_path)
            
            return {
                'status': True, 
                'message': f'Importação concluída com sucesso. {imported_count} registros importados.',
                'modified': True,
                'count': imported_count
            }
            
        except Exception as e:
            return {'status': False, 'message': f'Erro ao importar dados: {str(e)}'}
    
    def exportar_relatorio_inventario(self, cod_inventario, output_path):
        """Exporta dados do inventário para um CSV de relatório"""
        self._garantir_diretorios()
        
        try:
            # Obter dados do inventário
            dados = self.db_manager.get_dados_inventario_atual(cod_inventario)
            
            # Preparar cabeçalhos e linhas para o CSV
            headers = [
                'Origem', 'caixa_hb_623', 'caixa_hb_618', 'caixa_hnt_g', 'caixa_hnt_p', 
                'caixa_chocolate', 'caixa_bin', 'pallets_pbr', 'Total'
            ]
            
            rows = []
            
            # Linha para Lojas
            lojas_row = ['Lojas']
            total_lojas = 0
            for col in headers[1:-1]:  # Excluir 'Origem' e 'Total'
                valor = dados['dados_lojas'].get(f'total_{col[6:]}', 0) or 0
                lojas_row.append(valor)
                total_lojas += valor
            lojas_row.append(total_lojas)
            rows.append(lojas_row)
            
            # Linha para CD
            cd_row = ['CD']
            total_cd = 0
            for col in headers[1:-1]:  # Excluir 'Origem' e 'Total'
                valor = dados['dados_cd'].get(f'total_{col[6:]}', 0) or 0
                cd_row.append(valor)
                total_cd += valor
            cd_row.append(total_cd)
            rows.append(cd_row)
            
            # Linha para Trânsito
            transito_row = ['Trânsito']
            
            # Inicializar com zeros
            valores_transito = {f'caixa_{tipo}': 0 for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']}
            
            # Preencher com os dados disponíveis
            for item in dados['dados_transito']:
                tipo_caixa = item['tipo_caixa']
                coluna = f'caixa_{tipo_caixa}'
                if coluna in valores_transito:
                    valores_transito[coluna] = item['total']
            
            total_transito = 0
            for col in headers[1:-1]:  # Excluir 'Origem' e 'Total'
                valor = valores_transito.get(col, 0) or 0
                transito_row.append(valor)
                total_transito += valor
            transito_row.append(total_transito)
            rows.append(transito_row)
            
            # Linha para Fornecedor
            fornecedor_row = ['Fornecedor']
            
            # Inicializar com zeros
            valores_fornecedor = {f'caixa_{tipo}': 0 for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']}
            
            # Preencher com os dados disponíveis
            for item in dados['dados_fornecedor']:
                tipo_caixa = item['tipo_caixa']
                coluna = f'caixa_{tipo_caixa}'
                if coluna in valores_fornecedor:
                    valores_fornecedor[coluna] = item['total']
            
            total_fornecedor = 0
            for col in headers[1:-1]:  # Excluir 'Origem' e 'Total'
                valor = valores_fornecedor.get(col, 0) or 0
                fornecedor_row.append(valor)
                total_fornecedor += valor
            fornecedor_row.append(total_fornecedor)
            rows.append(fornecedor_row)
            
            # Linha para Totais
            total_row = ['TOTAL']
            total_geral = 0
            for i in range(len(headers[1:-1])):
                col_total = sum(row[i+1] for row in rows)
                total_row.append(col_total)
                total_geral += col_total
            total_row.append(total_geral)
            rows.append(total_row)
            
            # Escrever no arquivo CSV
            with open(output_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
                
            return {
                'status': True,
                'message': f'Relatório exportado com sucesso para {output_path}',
                'path': output_path
            }
            
        except Exception as e:
            return {'status': False, 'message': f'Erro ao exportar relatório: {str(e)}'}
    
    def criar_csv_padrao(self):
        """Cria arquivos CSV padrão se eles não existirem"""
        self._garantir_diretorios()
        
        # Criar CSV de lojas padrão
        if not os.path.exists(self.csv_lojas_path):
            with open(self.csv_lojas_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['loja', 'regional'])
                # Adicionar algumas lojas de exemplo
                writer.writerow(['Loja 001', 'Norte'])
                writer.writerow(['Loja 002', 'Sul'])
                writer.writerow(['Loja 003', 'Leste'])
                writer.writerow(['Loja 004', 'Oeste'])
                writer.writerow(['Loja 005', 'Centro'])
        
        # Criar CSV de setores padrão
        if not os.path.exists(self.csv_setores_path):
            with open(self.csv_setores_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['setor', 'descricao'])
                # Adicionar alguns setores de exemplo
                writer.writerow(['Setor A', 'Recebimento'])
                writer.writerow(['Setor B', 'Expedição'])
                writer.writerow(['Setor C', 'Estoque'])
                writer.writerow(['Setor D', 'Picking'])
        
        # Criar template para CSV de contagem de lojas
        if not os.path.exists(self.csv_contagem_lojas_path):
            with open(self.csv_contagem_lojas_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['loja', 'regional', 'setor', 'data', 'caixa_hb_623', 'caixa_hb_618', 
                                'caixa_hnt_g', 'caixa_hnt_p', 'caixa_chocolate', 'caixa_bin', 
                                'pallets_pbr', 'status', 'usuario'])
        
        # Criar template para CSV de contagem de CD
        if not os.path.exists(self.csv_contagem_cd_path):
            with open(self.csv_contagem_cd_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['setor', 'data', 'caixa_hb_623', 'caixa_hb_618', 
                                'caixa_hnt_g', 'caixa_hnt_p', 'caixa_chocolate', 'caixa_bin', 
                                'pallets_pbr', 'status', 'usuario'])
        
        # Criar template para CSV de dados em trânsito
        if not os.path.exists(self.csv_dados_transito_path):
            with open(self.csv_dados_transito_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['setor', 'data', 'tipo_caixa', 'quantidade', 'usuario'])