# gui/main_window.py
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QPushButton, QMessageBox, QDialog, 
    QLineEdit, QFormLayout, QListWidget, QDialogButtonBox, QComboBox,
    QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

from database.database_manager import DatabaseManager
from business.inventario_service import InventarioService
from business.relatorio_service import RelatorioService

from gui.dashboard import DashboardWidget
from gui.inventario_atual import InventarioAtualWidget
from gui.status_atual import StatusAtualWidget
from gui.atualizacao import AtualizacaoWidget
from gui.configuracoes import ConfiguracoesWidget
from gui.relatorios import RelatoriosWidget

class NovoInventarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Inventário")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.descricao_edit = QLineEdit()
        self.descricao_edit.setPlaceholderText("Opcional")
        
        layout.addRow("Descrição:", self.descricao_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
    
    def get_descricao(self):
        return self.descricao_edit.text()


class SelecionarInventarioDialog(QDialog):
    def __init__(self, inventarios, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selecionar Inventário")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        # Lista de inventários
        self.list_widget = QListWidget()
        for inv in inventarios:
            status = "Em andamento" if inv['status'] == 'em_andamento' else "Finalizado"
            self.list_widget.addItem(
                f"{inv['cod_inventario']} - {inv['data_inicio'][:10]} - {status}"
            )
        
        layout.addWidget(QLabel("Selecione um inventário para continuar:"))
        layout.addWidget(self.list_widget)
        
        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def get_inventario_selecionado(self):
        item = self.list_widget.currentItem()
        if item:
            # Extrair o código do inventário (primeiro elemento antes do primeiro hífen)
            return item.text().split(' - ')[0]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Inventário Rotativo de Ativos")
        self.setMinimumSize(1024, 768)
        
        # Inicializa os serviços
        self.db_manager = DatabaseManager()
        self.inventario_service = InventarioService(self.db_manager)
        self.relatorio_service = RelatorioService(self.db_manager)
        
        # Configurar interface
        self.setup_ui()
        
        # Verificar se há um inventário em andamento
        self.verificar_inventario_em_andamento()
    
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área de cabeçalho
        header_layout = QHBoxLayout()
        
        self.lbl_inventario_atual = QLabel("Nenhum inventário selecionado")
        header_layout.addWidget(self.lbl_inventario_atual)
        
        header_layout.addStretch()
        
        self.btn_novo_inventario = QPushButton("Novo Inventário")
        self.btn_novo_inventario.clicked.connect(self.criar_novo_inventario)
        header_layout.addWidget(self.btn_novo_inventario)
        
        self.btn_carregar_inventario = QPushButton("Carregar Inventário")
        self.btn_carregar_inventario.clicked.connect(self.carregar_inventario)
        header_layout.addWidget(self.btn_carregar_inventario)
        
        self.btn_finalizar_inventario = QPushButton("Finalizar Inventário")
        self.btn_finalizar_inventario.clicked.connect(self.finalizar_inventario)
        self.btn_finalizar_inventario.setEnabled(False)
        header_layout.addWidget(self.btn_finalizar_inventario)
        
        main_layout.addLayout(header_layout)
        
        # Criar abas
        self.tab_widget = QTabWidget()
        
        # Inicializar widgets das abas
        self.dashboard_widget = DashboardWidget(self.relatorio_service)
        self.inventario_atual_widget = InventarioAtualWidget(self.inventario_service)
        self.status_atual_widget = StatusAtualWidget(self.relatorio_service)
        self.atualizacao_widget = AtualizacaoWidget(self.inventario_service)
        self.configuracoes_widget = ConfiguracoesWidget(self.inventario_service)
        self.relatorios_widget = RelatoriosWidget(self.relatorio_service, self.inventario_service)
        
        # Adicionar abas ao widget de abas
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        self.tab_widget.addTab(self.inventario_atual_widget, "Dados do Inventário")
        self.tab_widget.addTab(self.status_atual_widget, "Status Atual")
        self.tab_widget.addTab(self.atualizacao_widget, "Atualização")
        self.tab_widget.addTab(self.configuracoes_widget, "Configurações")
        self.tab_widget.addTab(self.relatorios_widget, "Relatórios")
        
        main_layout.addWidget(self.tab_widget)
        
        # Área de rodapé
        footer_layout = QHBoxLayout()
        self.lbl_status = QLabel("Pronto")
        footer_layout.addWidget(self.lbl_status)
        
        main_layout.addLayout(footer_layout)
        
        # Desabilitar todas as abas no início
        self.toggle_tabs_enabled(False)
    
    def toggle_tabs_enabled(self, enabled):
        """Habilita ou desabilita todas as abas"""
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enabled)
    
    def atualizar_interface(self):
        """Atualiza a interface após a seleção de um inventário"""
        if self.inventario_service.inventario_atual:
            # Atualizar label de inventário atual
            self.lbl_inventario_atual.setText(f"Inventário Atual: {self.inventario_service.inventario_atual}")
            self.btn_finalizar_inventario.setEnabled(True)
            
            # Habilitar abas
            self.toggle_tabs_enabled(True)
            
            # Atualizar todas as abas
            self.dashboard_widget.atualizar_dados(self.inventario_service.inventario_atual)
            self.inventario_atual_widget.atualizar_dados()
            self.status_atual_widget.atualizar_dados(self.inventario_service.inventario_atual)
            self.atualizacao_widget.atualizar_dados()
            self.relatorios_widget.atualizar_dados()
            
            # Exibir mensagem de status
            self.lbl_status.setText(f"Inventário {self.inventario_service.inventario_atual} carregado com sucesso")
        else:
            # Resetar interface
            self.lbl_inventario_atual.setText("Nenhum inventário selecionado")
            self.btn_finalizar_inventario.setEnabled(False)
            self.toggle_tabs_enabled(False)
            self.lbl_status.setText("Pronto")
    
    def verificar_inventario_em_andamento(self):
        """Verifica se há um inventário em andamento e pergunta se deseja carregá-lo"""
        inventarios = self.inventario_service.get_inventarios_ativos()
        if not inventarios:
            return
        
        # Perguntar ao usuário se deseja carregar o inventário em andamento mais recente
        resp = QMessageBox.question(
            self, 
            "Inventário em Andamento", 
            f"Existe um inventário em andamento ({inventarios[0]['cod_inventario']}). Deseja carregá-lo?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resp == QMessageBox.Yes:
            self.inventario_service.carregar_inventario_existente(inventarios[0]['cod_inventario'])
            self.atualizar_interface()
    
    def criar_novo_inventario(self):
        """Cria um novo inventário"""
        dialog = NovoInventarioDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            descricao = dialog.get_descricao()
            
            # Se já houver um inventário em andamento, perguntar se deseja finalizar
            if self.inventario_service.inventario_atual:
                resp = QMessageBox.question(
                    self, 
                    "Finalizar Inventário Atual", 
                    "Já existe um inventário em andamento. Deseja finalizá-lo antes de criar um novo?",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if resp == QMessageBox.Cancel:
                    return
                elif resp == QMessageBox.Yes:
                    self.inventario_service.finalizar_inventario_atual()
            
            # Criar novo inventário
            novo_codigo = self.inventario_service.iniciar_novo_inventario(descricao)
            
            QMessageBox.information(
                self, 
                "Novo Inventário", 
                f"Inventário criado com sucesso!\nCódigo: {novo_codigo}"
            )
            
            self.atualizar_interface()
    
    def carregar_inventario(self):
        """Carrega um inventário existente"""
        inventarios = self.inventario_service.get_inventarios_disponiveis()
        if not inventarios:
            QMessageBox.information(
                self, 
                "Sem Inventários", 
                "Não há inventários disponíveis para carregar."
            )
            return
        
        dialog = SelecionarInventarioDialog(inventarios, self)
        if dialog.exec_() == QDialog.Accepted:
            codigo = dialog.get_inventario_selecionado()
            if codigo:
                if self.inventario_service.carregar_inventario_existente(codigo):
                    self.atualizar_interface()
                else:
                    QMessageBox.warning(
                        self, 
                        "Erro", 
                        "Não foi possível carregar o inventário selecionado."
                    )
    
    def finalizar_inventario(self):
        """Finaliza o inventário atual com os novos requisitos de finalização"""
        if not self.inventario_service.inventario_atual:
            return
        
        # Verificar se há algum pendente antes de finalizar
        pendentes = self._verificar_pendentes()
        if pendentes and len(pendentes) > 0:
            # Mostrar diálogo de confirmação com os pendentes
            resp = QMessageBox.question(
                self, 
                "Itens Pendentes", 
                f"Existem {len(pendentes)} itens pendentes no inventário. Deseja continuar com a finalização?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if resp != QMessageBox.Yes:
                return
        
        # Criar e exibir o diálogo de finalização
        try:
            # Garantir que o módulo esteja importado
            from gui.finalizar_inventario import FinalizarInventarioDialog
            
            dialog = FinalizarInventarioDialog(
                self.inventario_service,
                self.relatorio_service,
                self
            )
            
            if dialog.exec_() == QDialog.Accepted:
                # O inventário foi finalizado com sucesso
                QMessageBox.information(
                    self, 
                    "Inventário Finalizado", 
                    "O inventário foi finalizado com sucesso!"
                )
                
                # Resetar interface
                self.inventario_service.inventario_atual = None
                self.atualizar_interface()
        except Exception as e:
            import traceback
            print(f"Erro ao mostrar diálogo de finalização: {e}")
            print(traceback.format_exc())
            QMessageBox.warning(
                self, 
                "Erro", 
                f"Ocorreu um erro ao finalizar o inventário: {str(e)}"
            )

    def _verificar_pendentes(self):
        """Verifica se há itens pendentes no inventário atual"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Verificar lojas pendentes
            cursor.execute('''
            SELECT loja FROM contagem_lojas
            WHERE cod_inventario = ? AND status != 'finalizado'
            ''', (self.inventario_service.inventario_atual,))
            
            lojas_pendentes = [row['loja'] for row in cursor.fetchall()]
            
            # Verificar setores pendentes
            cursor.execute('''
            SELECT setor FROM contagem_cd
            WHERE cod_inventario = ? AND status != 'finalizado'
            ''', (self.inventario_service.inventario_atual,))
            
            setores_pendentes = [row['setor'] for row in cursor.fetchall()]
            
            return lojas_pendentes + setores_pendentes
        except Exception as e:
            print(f"Erro ao verificar pendentes: {e}")
            return []