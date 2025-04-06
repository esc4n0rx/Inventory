# gui/status_atual.py
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QTableWidget, QTableWidgetItem, 
    QHeaderView, QGroupBox, QScrollArea, QTreeWidget,
    QTreeWidgetItem, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor

class StatusProgressWidget(QWidget):
    """Widget para exibir progresso geral do inventário"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Progresso de lojas
        loja_group = QGroupBox("Progresso de Lojas")
        loja_layout = QVBoxLayout(loja_group)
        
        self.lbl_lojas = QLabel("0 de 0 lojas finalizadas")
        self.lbl_lojas.setAlignment(Qt.AlignCenter)
        loja_layout.addWidget(self.lbl_lojas)
        
        self.progress_lojas = QProgressBar()
        self.progress_lojas.setMinimum(0)
        self.progress_lojas.setMaximum(100)
        loja_layout.addWidget(self.progress_lojas)
        
        layout.addWidget(loja_group)
        
        # Progresso de setores do CD
        cd_group = QGroupBox("Progresso de Setores do CD")
        cd_layout = QVBoxLayout(cd_group)
        
        self.lbl_cd = QLabel("0 de 0 setores finalizados")
        self.lbl_cd.setAlignment(Qt.AlignCenter)
        cd_layout.addWidget(self.lbl_cd)
        
        self.progress_cd = QProgressBar()
        self.progress_cd.setMinimum(0)
        self.progress_cd.setMaximum(100)
        cd_layout.addWidget(self.progress_cd)
        
        layout.addWidget(cd_group)
        
        # Adicionar espaçador para empurrar os widgets para cima
        layout.addStretch()
    
    def atualizar_dados(self, dados_status):
        """Atualiza os widgets de progresso com os dados atuais"""
        # Progresso de lojas
        lojas_finalizadas = dados_status['lojas_finalizadas']
        total_lojas = dados_status['total_lojas']
        porcentagem_lojas = dados_status['porcentagem_lojas']
        
        self.lbl_lojas.setText(f"{lojas_finalizadas} de {total_lojas} lojas finalizadas")
        self.progress_lojas.setValue(int(porcentagem_lojas))
        
        # Progresso de setores do CD
        setores_finalizados = dados_status['setores_finalizados']
        total_setores = dados_status['total_setores']
        porcentagem_setores = dados_status['porcentagem_setores']
        
        self.lbl_cd.setText(f"{setores_finalizados} de {total_setores} setores finalizados")
        self.progress_cd.setValue(int(porcentagem_setores))


class RegionalTreeWidget(QWidget):
    """Widget para exibir árvore de lojas por regional"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Lojas por Regional")
        titulo_font = titulo.font()
        titulo_font.setPointSize(12)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Árvore de regionais
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Regional / Loja", "Status"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.tree)
    
    def atualizar_dados(self, resumo_regional, lojas_pendentes):
        """Atualiza a árvore com os dados de regionais e lojas"""
        self.tree.clear()
        
        # Adicionar regionais e suas lojas
        for regional in resumo_regional:
            # Criar item da regional
            regional_nome = regional['regional']
            porcentagem = regional['porcentagem']
            regional_item = QTreeWidgetItem([
                regional_nome,
                f"{regional['lojas_finalizadas']} de {regional['total_lojas']} ({porcentagem:.1f}%)"
            ])
            
            # Configurar fonte em negrito para o item da regional
            font = regional_item.font(0)
            font.setBold(True)
            regional_item.setFont(0, font)
            regional_item.setFont(1, font)
            
            self.tree.addTopLevelItem(regional_item)
            
            # Adicionar lojas desta regional
            lojas_desta_regional = lojas_pendentes.get(regional_nome, [])
            
            # Primeiro adicionar lojas finalizadas (que não estão na lista de pendentes)
            total_lojas = regional['total_lojas']
            lojas_finalizadas = regional['lojas_finalizadas']
            
            # Se houver lojas finalizadas, adicionar um item especial
            if lojas_finalizadas > 0:
                finalizadas_item = QTreeWidgetItem([
                    f"Lojas Finalizadas",
                    f"{lojas_finalizadas} lojas"
                ])
                finalizadas_item.setForeground(0, QColor(0, 128, 0))  # Verde
                finalizadas_item.setForeground(1, QColor(0, 128, 0))  # Verde
                regional_item.addChild(finalizadas_item)
            
            # Adicionar lojas pendentes
            if lojas_desta_regional:
                pendentes_item = QTreeWidgetItem([
                    f"Lojas Pendentes",
                    f"{len(lojas_desta_regional)} lojas"
                ])
                pendentes_item.setForeground(0, QColor(200, 0, 0))  # Vermelho
                pendentes_item.setForeground(1, QColor(200, 0, 0))  # Vermelho
                regional_item.addChild(pendentes_item)
                
                # Adicionar cada loja pendente
                for loja in lojas_desta_regional:
                    loja_item = QTreeWidgetItem([loja, "Pendente"])
                    loja_item.setForeground(1, QColor(200, 0, 0))  # Vermelho
                    pendentes_item.addChild(loja_item)
        
        # Expandir todos os itens
        self.tree.expandAll()


class StatusAtualWidget(QWidget):
    """Widget principal para a aba de Status Atual"""
    def __init__(self, relatorio_service, parent=None):
        super().__init__(parent)
        self.relatorio_service = relatorio_service
        
        # Layout principal
        layout = QHBoxLayout(self)
        
        # Splitter para dividir a tela
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel de progresso
        self.progress_widget = StatusProgressWidget()
        splitter.addWidget(self.progress_widget)
        
        # Árvore de regionais e lojas
        self.regional_tree = RegionalTreeWidget()
        splitter.addWidget(self.regional_tree)
        
        # Definir proporções do splitter
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
    
    def atualizar_dados(self, cod_inventario):
        """Atualiza todos os componentes com os dados atuais"""
        # Obter dados de status
        dados_status = self.relatorio_service.get_resumo_status(cod_inventario)
        
        # Atualizar widgets de progresso
        self.progress_widget.atualizar_dados(dados_status)
        
        # Atualizar árvore de regionais
        lojas_pendentes = {}
        for regional in dados_status['resumo_regional']:
            if regional['lojas_pendentes']:
                lojas_pendentes[regional['regional']] = regional['lojas_pendentes']
        
        self.regional_tree.atualizar_dados(dados_status['resumo_regional'], lojas_pendentes)