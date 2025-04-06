# gui/relatorios.py
import sys
import os
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QComboBox,
    QSplitter, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries

class HistoricoInventariosWidget(QWidget):
    """Widget para exibir histórico de inventários"""
    def __init__(self, relatorio_service, parent=None):
        super().__init__(parent)
        self.relatorio_service = relatorio_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Histórico de Inventários")
        titulo_font = titulo.font()
        titulo_font.setPointSize(12)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabela de histórico
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Data Início", "Data Fim", "Total de Lojas", "Total de Ativos"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)
        self.tabela.selectionModel().selectionChanged.connect(self.selecionar_inventario)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_atualizar = QPushButton("Atualizar Histórico")
        self.btn_atualizar.clicked.connect(self.atualizar_dados)
        btn_layout.addWidget(self.btn_atualizar)
        
        btn_layout.addStretch()
        
        self.btn_comparar = QPushButton("Comparar Selecionado com Atual")
        self.btn_comparar.clicked.connect(self.comparar_com_atual)
        self.btn_comparar.setEnabled(False)
        btn_layout.addWidget(self.btn_comparar)
        
        self.btn_exportar = QPushButton("Exportar Relatório")
        self.btn_exportar.clicked.connect(self.exportar_relatorio)
        self.btn_exportar.setEnabled(False)
        btn_layout.addWidget(self.btn_exportar)
        
        layout.addLayout(btn_layout)
    
    def atualizar_dados(self):
        """Atualiza a tabela com o histórico de inventários"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Obter histórico de inventários
        historico = self.relatorio_service.get_historico_inventarios()
        
        # Preencher tabela
        for i, inv in enumerate(historico):
            self.tabela.insertRow(i)
            
            # Código
            self.tabela.setItem(i, 0, QTableWidgetItem(inv['cod_inventario']))
            
            # Data de início
            self.tabela.setItem(i, 1, QTableWidgetItem(inv['data_inicio']))
            
            # Data de fim
            self.tabela.setItem(i, 2, QTableWidgetItem(inv['data_fim']))
            
            # Total de lojas
            self.tabela.setItem(i, 3, QTableWidgetItem(str(inv['total_lojas'])))
            
            # Total de ativos
            self.tabela.setItem(i, 4, QTableWidgetItem(str(inv['total_geral'])))
    
    def selecionar_inventario(self):
        """Habilitar botões quando um inventário é selecionado"""
        indices = self.tabela.selectedIndexes()
        if indices:
            self.btn_comparar.setEnabled(True)
            self.btn_exportar.setEnabled(True)
        else:
            self.btn_comparar.setEnabled(False)
            self.btn_exportar.setEnabled(False)
    
    def get_inventario_selecionado(self):
        """Retorna o código do inventário selecionado"""
        indices = self.tabela.selectedIndexes()
        if not indices:
            return None
        
        linha = indices[0].row()
        return self.tabela.item(linha, 0).text()
    
    def comparar_com_atual(self):
        """Emite sinal para comparar o inventário selecionado com o atual"""
        cod_inventario = self.get_inventario_selecionado()
        if not cod_inventario:
            return
        
        # Chamar método do widget pai
        if hasattr(self.parent(), 'comparar_inventarios'):
            self.parent().comparar_inventarios(cod_inventario)
    
    def exportar_relatorio(self):
        """Exporta relatório do inventário selecionado"""
        cod_inventario = self.get_inventario_selecionado()
        if not cod_inventario:
            return
        
        # Perguntar onde salvar o relatório
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"relatorio_{cod_inventario}.csv",
            "Arquivos CSV (*.csv)"
        )
        
        if not caminho:
            return
        
        # Exportar relatório
        resultado = self.relatorio_service.db_manager.csv_manager.exportar_relatorio_inventario(
            cod_inventario,
            caminho
        )
        
        if resultado['status']:
            QMessageBox.information(
                self,
                "Relatório Exportado",
                f"Relatório exportado com sucesso para:\n{caminho}"
            )
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Erro ao exportar relatório: {resultado['message']}"
            )


class ComparacaoInventariosWidget(QWidget):
    """Widget para comparar dois inventários"""
    def __init__(self, relatorio_service, parent=None):
        super().__init__(parent)
        self.relatorio_service = relatorio_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Comparação de Inventários")
        titulo_font = titulo.font()
        titulo_font.setPointSize(12)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Área de seleção
        selecao_layout = QHBoxLayout()
        
        selecao_layout.addWidget(QLabel("Inventário 1:"))
        self.cb_inventario1 = QComboBox()
        self.cb_inventario1.setMinimumWidth(250)
        selecao_layout.addWidget(self.cb_inventario1)
        
        selecao_layout.addWidget(QLabel("Inventário 2:"))
        self.cb_inventario2 = QComboBox()
        self.cb_inventario2.setMinimumWidth(250)
        selecao_layout.addWidget(self.cb_inventario2)
        
        self.btn_comparar = QPushButton("Comparar")
        self.btn_comparar.clicked.connect(self.comparar_inventarios)
        selecao_layout.addWidget(self.btn_comparar)
        
        layout.addLayout(selecao_layout)
        
        # Splitter para dividir a área de visualização
        splitter = QSplitter(Qt.Vertical)
        
        # Tabela de comparação
        self.tabela = QTableWidget(0, 9)
        self.tabela.setHorizontalHeaderLabels([
            "Tipo", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        splitter.addWidget(self.tabela)
        
        # Gráfico de comparação
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)  # CORRIGIDO
        self.chart_view.setMinimumHeight(300)
        splitter.addWidget(self.chart_view)
        
        layout.addWidget(splitter)
    
    def atualizar_dados(self):
        """Atualiza os comboboxes com a lista de inventários"""
        # Salvar seleções atuais
        inv1_atual = self.cb_inventario1.currentText()
        inv2_atual = self.cb_inventario2.currentText()
        
        # Limpar comboboxes
        self.cb_inventario1.clear()
        self.cb_inventario2.clear()
        
        # Obter todos os inventários
        inventarios = self.relatorio_service.db_manager.get_todos_inventarios()
        
        # Preencher comboboxes
        for inv in inventarios:
            codigo = inv['cod_inventario']
            data_inicio = inv['data_inicio'].split('T')[0] if 'T' in inv['data_inicio'] else inv['data_inicio']
            status = "Em andamento" if inv['status'] == 'em_andamento' else "Finalizado"
            
            texto = f"{codigo} - {data_inicio} - {status}"
            self.cb_inventario1.addItem(texto, codigo)
            self.cb_inventario2.addItem(texto, codigo)
        
        # Restaurar seleções anteriores, se possível
        if inv1_atual:
            index = self.cb_inventario1.findText(inv1_atual)
            if index >= 0:
                self.cb_inventario1.setCurrentIndex(index)
        
        if inv2_atual:
            index = self.cb_inventario2.findText(inv2_atual)
            if index >= 0:
                self.cb_inventario2.setCurrentIndex(index)
    
    def comparar_inventarios(self):
        """Compara os dois inventários selecionados"""
        inv1 = self.cb_inventario1.currentData()
        inv2 = self.cb_inventario2.currentData()
        
        if not inv1 or not inv2:
            QMessageBox.warning(
                self,
                "Seleção Necessária",
                "Selecione dois inventários para comparação."
            )
            return
        
        if inv1 == inv2:
            QMessageBox.warning(
                self,
                "Inventários Idênticos",
                "Selecione inventários diferentes para comparação."
            )
            return
        
        # Realizar comparação
        resultado = self.relatorio_service.comparar_inventarios(inv1, inv2)
        
        # Atualizar tabela
        self.atualizar_tabela(resultado)
        
        # Atualizar gráfico
        self.atualizar_grafico(resultado)
    
    def atualizar_tabela(self, dados_comparacao):
        """Atualiza a tabela com os dados da comparação"""
        self.tabela.setRowCount(0)
        
        # Tipos de caixa
        tipos_caixa = [
            'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
            'chocolate', 'bin', 'pallets_pbr'
        ]
        
        # Adicionar linha para inventário 1
        self.tabela.insertRow(0)
        self.tabela.setItem(0, 0, QTableWidgetItem("Inventário 1"))
        
        # Valores por tipo de caixa
        total_inv1 = 0
        for j, tipo in enumerate(tipos_caixa):
            valor = dados_comparacao['atual'][f'total_{tipo}']
            total_inv1 += valor
            
            valor_item = QTableWidgetItem(str(valor))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(0, j + 1, valor_item)
        
        # Total da linha
        total_item = QTableWidgetItem(str(total_inv1))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabela.setItem(0, 8, total_item)
        
        # Adicionar linha para inventário 2
        self.tabela.insertRow(1)
        self.tabela.setItem(1, 0, QTableWidgetItem("Inventário 2"))
        
        # Valores por tipo de caixa
        total_inv2 = 0
        for j, tipo in enumerate(tipos_caixa):
            valor = dados_comparacao['anterior'][f'total_{tipo}']
            total_inv2 += valor
            
            valor_item = QTableWidgetItem(str(valor))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela.setItem(1, j + 1, valor_item)
        
        # Total da linha
        total_item = QTableWidgetItem(str(total_inv2))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabela.setItem(1, 8, total_item)
        
        # Adicionar linha para diferença
        self.tabela.insertRow(2)
        
        # Título com fonte em negrito
        titulo_diff = QTableWidgetItem("Diferença")
        fonte = titulo_diff.font()
        fonte.setBold(True)
        titulo_diff.setFont(fonte)
        self.tabela.setItem(2, 0, titulo_diff)
        
        # Valores por tipo de caixa
        for j, tipo in enumerate(tipos_caixa):
            diff = dados_comparacao['diferencas'][f'diff_{tipo}']
            
            valor_item = QTableWidgetItem(str(diff))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Estilizar célula (verde para positivo, vermelho para negativo)
            if diff > 0:
                valor_item.setForeground(QColor(0, 128, 0))  # Verde
            elif diff < 0:
                valor_item.setForeground(QColor(255, 0, 0))  # Vermelho
            
            fonte = valor_item.font()
            fonte.setBold(True)
            valor_item.setFont(fonte)
            
            self.tabela.setItem(2, j + 1, valor_item)
        
        # Diferença total
        diff_total = dados_comparacao['diferencas']['diff_total']
        total_item = QTableWidgetItem(str(diff_total))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Estilizar célula (verde para positivo, vermelho para negativo)
        if diff_total > 0:
            total_item.setForeground(QColor(0, 128, 0))  # Verde
        elif diff_total < 0:
            total_item.setForeground(QColor(255, 0, 0))  # Vermelho
        
        fonte = total_item.font()
        fonte.setBold(True)
        total_item.setFont(fonte)
        
        self.tabela.setItem(2, 8, total_item)
    
    def atualizar_grafico(self, dados_comparacao):
        """Atualiza o gráfico com os dados da comparação"""
        # Criar séries para o gráfico
        series = QBarSeries()
        
        # Criar conjunto de barras para cada inventário
        inv1_set = QBarSet("Inventário 1")
        inv2_set = QBarSet("Inventário 2")
        
        # Tipos de caixa para exibir no gráfico (com nomes mais amigáveis)
        tipos_caixa = [
            'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
            'chocolate', 'bin', 'pallets_pbr'
        ]
        
        nomes_tipos = {
            'hb_623': 'HB 623',
            'hb_618': 'HB 618',
            'hnt_g': 'HNT G',
            'hnt_p': 'HNT P',
            'chocolate': 'Chocolate',
            'bin': 'BIN',
            'pallets_pbr': 'Pallets PBR'
        }
        
        # Adicionar valores aos conjuntos
        for tipo in tipos_caixa:
            inv1_set.append(dados_comparacao['atual'][f'total_{tipo}'])
            inv2_set.append(dados_comparacao['anterior'][f'total_{tipo}'])
        
        # Adicionar conjuntos à série
        series.append(inv1_set)
        series.append(inv2_set)
        
        # Criar gráfico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Comparação por Tipo de Caixa")
        
        # Criar eixos
        axis_x = QBarCategoryAxis()
        axis_x.append([nomes_tipos[tipo] for tipo in tipos_caixa])
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(max(inv1_set), max(inv2_set)) * 1.1)  # 10% a mais que o valor máximo
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # Configurar legenda
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Atualizar view
        self.chart_view.setChart(chart)


class RelatoriosWidget(QWidget):
    """Widget principal para a aba de Relatórios"""
    def __init__(self, relatorio_service, inventario_service, parent=None):
        super().__init__(parent)
        self.relatorio_service = relatorio_service
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas de relatórios
        tab_widget = QTabWidget()
        
        # Aba de Histórico
        self.historico_widget = HistoricoInventariosWidget(relatorio_service)
        tab_widget.addTab(self.historico_widget, "Histórico de Inventários")
        
        # Aba de Comparação
        self.comparacao_widget = ComparacaoInventariosWidget(relatorio_service)
        tab_widget.addTab(self.comparacao_widget, "Comparação de Inventários")
        
        layout.addWidget(tab_widget)
    
    def atualizar_dados(self):
        """Atualiza todos os widgets de relatórios"""
        self.historico_widget.atualizar_dados()
        self.comparacao_widget.atualizar_dados()
    
    def comparar_inventarios(self, cod_inventario):
        """Compara o inventário atual com o inventário informado"""
        if not self.inventario_service.inventario_atual:
            QMessageBox.warning(
                self,
                "Inventário Atual Necessário",
                "Você precisa ter um inventário ativo para realizar a comparação."
            )
            return
        
        # Mudar para a aba de comparação
        self.parent().tab_widget.setCurrentIndex(
            self.parent().tab_widget.indexOf(self)
        )
        
        # Atualizar comboboxes
        idx1 = self.comparacao_widget.cb_inventario1.findData(self.inventario_service.inventario_atual)
        if idx1 >= 0:
            self.comparacao_widget.cb_inventario1.setCurrentIndex(idx1)
        
        idx2 = self.comparacao_widget.cb_inventario2.findData(cod_inventario)
        if idx2 >= 0:
            self.comparacao_widget.cb_inventario2.setCurrentIndex(idx2)
        
        # Realizar comparação
        self.comparacao_widget.comparar_inventarios()