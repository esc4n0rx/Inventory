# utils/config.py
import os
import configparser

CONFIG_FILE = 'config.ini'

class Config:
    """Classe para gerenciar configurações do sistema"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.carregar_config()
    
    def carregar_config(self):
        """Carrega as configurações do arquivo ou cria configurações padrão"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
        else:
            self.criar_config_padrao()
    
    def criar_config_padrao(self):
        """Cria um arquivo de configuração padrão"""
        # Seção de banco de dados
        self.config['Database'] = {
            'file': 'inventario.db'
        }
        
        # Seção de caminhos de arquivos
        self.config['Files'] = {
            'lojas_path': 'data/lojas.csv',
            'setores_path': 'data/setores.csv',
            'contagem_lojas_path': 'data/contagem_lojas.csv',
            'contagem_cd_path': 'data/contagem_cd.csv',
            'dados_transito_path': 'data/dados_transito.csv'
        }
        
        # Seção de usuário
        self.config['User'] = {
            'last_inventory': '',
            'default_export_path': 'relatorios/'
        }
        
        # Salvar configurações
        self.salvar_config()
    
    def salvar_config(self):
        """Salva as configurações no arquivo"""
        with open(CONFIG_FILE, 'w') as configfile:
            self.config.write(configfile)
    
    def get_database_file(self):
        """Retorna o caminho do arquivo de banco de dados"""
        return self.config.get('Database', 'file', fallback='inventario.db')
    
    def get_csv_paths(self):
        """Retorna os caminhos dos arquivos CSV"""
        return {
            'lojas_path': self.config.get('Files', 'lojas_path', fallback='data/lojas.csv'),
            'setores_path': self.config.get('Files', 'setores_path', fallback='data/setores.csv'),
            'contagem_lojas_path': self.config.get('Files', 'contagem_lojas_path', fallback='data/contagem_lojas.csv'),
            'contagem_cd_path': self.config.get('Files', 'contagem_cd_path', fallback='data/contagem_cd.csv'),
            'dados_transito_path': self.config.get('Files', 'dados_transito_path', fallback='data/dados_transito.csv')
        }
    
    def set_csv_paths(self, paths):
        """Define os caminhos dos arquivos CSV"""
        if 'lojas_path' in paths:
            self.config.set('Files', 'lojas_path', paths['lojas_path'])
        if 'setores_path' in paths:
            self.config.set('Files', 'setores_path', paths['setores_path'])
        if 'contagem_lojas_path' in paths:
            self.config.set('Files', 'contagem_lojas_path', paths['contagem_lojas_path'])
        if 'contagem_cd_path' in paths:
            self.config.set('Files', 'contagem_cd_path', paths['contagem_cd_path'])
        if 'dados_transito_path' in paths:
            self.config.set('Files', 'dados_transito_path', paths['dados_transito_path'])
        
        self.salvar_config()
    
    def set_last_inventory(self, cod_inventario):
        """Define o último inventário utilizado"""
        self.config.set('User', 'last_inventory', cod_inventario)
        self.salvar_config()
    
    def get_last_inventory(self):
        """Retorna o último inventário utilizado"""
        return self.config.get('User', 'last_inventory', fallback='')
    
    def get_default_export_path(self):
        """Retorna o caminho padrão para exportação de relatórios"""
        return self.config.get('User', 'default_export_path', fallback='relatorios/')
    
    def set_default_export_path(self, path):
        """Define o caminho padrão para exportação de relatórios"""
        self.config.set('User', 'default_export_path', path)
        self.salvar_config()