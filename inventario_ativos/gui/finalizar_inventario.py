# gui/finalizar_inventario.py
import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QFormLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFileDialog, QComboBox, QPushButton, QTabWidget, QSplitter, QFrame,
    QListWidget, QListWidgetItem, QSpinBox, QProgressBar, QScrollArea,
    QWidgetItem, QSizePolicy,QWidget
)
from PyQt5.QtCore import Qt, QMargins, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QIcon
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries, QLegend


class FinalizarInventarioDialog(QDialog):
    """Diálogo de finalização de inventário com agrupamentos e exportação"""
    def __init__(self, inventario_service, relatorio_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        self.relatorio_service = relatorio_service
        self.cod_inventario = inventario_service.inventario_atual
        
        # Configurar janela
        self.setWindowTitle("Finalizar Inventário")
        self.setMinimumSize(800, 600)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Resumo do Inventário para Finalização")
        titulo_font = titulo.font()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Subtítulo com o código do inventário
        subtitulo = QLabel(f"Código: {self.cod_inventario}")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)
        
        # Divisor visual
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Abas para diferentes visualizações
        self.tab_widget = QTabWidget()
        
        # Aba de resumo geral
        self.tab_resumo = QWidget()
        self.setup_tab_resumo()
        self.tab_widget.addTab(self.tab_resumo, "Resumo Geral")
        
        # Aba com detalhes por CD
        self.tab_cds = QWidget()
        self.setup_tab_cds()
        self.tab_widget.addTab(self.tab_cds, "Detalhes CDs")
        
        # Aba com detalhes de lojas
        self.tab_lojas = QWidget()
        self.setup_tab_lojas()
        self.tab_widget.addTab(self.tab_lojas, "Detalhes Lojas")
        
        # Aba de comparativo
        self.tab_comparativo = QWidget()
        self.setup_tab_comparativo()
        self.tab_widget.addTab(self.tab_comparativo, "Comparativo")
        
        layout.addWidget(self.tab_widget)
        
        # Área de botões
        btn_layout = QHBoxLayout()
        
        # Botão para exportar para Excel
        self.btn_exportar = QPushButton("Exportar para Excel")
        self.btn_exportar.setIcon(QIcon.fromTheme("document-save"))
        self.btn_exportar.clicked.connect(self.exportar_excel)
        btn_layout.addWidget(self.btn_exportar)
        
        btn_layout.addStretch()
        
        # Botão para realmente finalizar o inventário
        self.btn_finalizar = QPushButton("Finalizar Inventário")
        self.btn_finalizar.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        self.btn_finalizar.clicked.connect(self.finalizar)
        btn_layout.addWidget(self.btn_finalizar)
        
        # Botão para cancelar
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancelar)
        
        layout.addLayout(btn_layout)
        
        # Carregar os dados
        self.carregar_dados()
    
    def setup_tab_resumo(self):
        """Configura a aba de resumo geral"""
        layout = QVBoxLayout(self.tab_resumo)
        
        # Tabela de resumo por origem
        group_origem = QGroupBox("Totais por Origem")
        origem_layout = QVBoxLayout(group_origem)
        
        self.tabela_resumo_origem = QTableWidget(0, 9)
        self.tabela_resumo_origem.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela_resumo_origem.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_resumo_origem.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela_resumo_origem.verticalHeader().setVisible(False)
        origem_layout.addWidget(self.tabela_resumo_origem)
        
        layout.addWidget(group_origem)
        
        # Resumo agrupado por tipo de ativo
        group_tipo = QGroupBox("Resumo por Tipo de Ativo")
        tipo_layout = QVBoxLayout(group_tipo)
        
        # Sub-grupo: HB (623 e 618)
        group_hb = QGroupBox("HB (623 e 618)")
        hb_layout = QVBoxLayout(group_hb)
        
        self.tabela_hb = QTableWidget(0, 3)
        self.tabela_hb.setHorizontalHeaderLabels(["Origem", "Quantidade", "Porcentagem"])
        self.tabela_hb.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_hb.verticalHeader().setVisible(False)
        hb_layout.addWidget(self.tabela_hb)
        
        tipo_layout.addWidget(group_hb)
        
        # Sub-grupo: HNT (G e P)
        group_hnt = QGroupBox("HNT (G e P)")
        hnt_layout = QVBoxLayout(group_hnt)
        
        self.tabela_hnt = QTableWidget(0, 3)
        self.tabela_hnt.setHorizontalHeaderLabels(["Origem", "Quantidade", "Porcentagem"])
        self.tabela_hnt.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_hnt.verticalHeader().setVisible(False)
        hnt_layout.addWidget(self.tabela_hnt)
        
        tipo_layout.addWidget(group_hnt)
        
        # Sub-grupo: Outros
        group_outros = QGroupBox("Outros Ativos")
        outros_layout = QVBoxLayout(group_outros)
        
        self.tabela_outros = QTableWidget(0, 3)
        self.tabela_outros.setHorizontalHeaderLabels(["Tipo", "Quantidade", "Porcentagem"])
        self.tabela_outros.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_outros.verticalHeader().setVisible(False)
        outros_layout.addWidget(self.tabela_outros)
        
        tipo_layout.addWidget(group_outros)
        
        layout.addWidget(group_tipo)
    
    def setup_tab_cds(self):
        """Configura a aba de detalhes dos CDs"""
        layout = QVBoxLayout(self.tab_cds)
        
        # Abas para diferentes CDs
        self.tab_cd_widget = QTabWidget()
        
        # Aba para CD SP
        self.tab_cd_sp = QWidget()
        cd_sp_layout = QVBoxLayout(self.tab_cd_sp)
        
        # Tabela para CD SP
        self.tabela_cd_sp = QTableWidget(0, 9)
        self.tabela_cd_sp.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela_cd_sp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_cd_sp.verticalHeader().setVisible(False)
        cd_sp_layout.addWidget(self.tabela_cd_sp)
        
        self.tab_cd_widget.addTab(self.tab_cd_sp, "CD SP")
        
        # Aba para CD ES
        self.tab_cd_es = QWidget()
        cd_es_layout = QVBoxLayout(self.tab_cd_es)
        
        # Tabela para CD ES
        self.tabela_cd_es = QTableWidget(0, 9)
        self.tabela_cd_es.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela_cd_es.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_cd_es.verticalHeader().setVisible(False)
        cd_es_layout.addWidget(self.tabela_cd_es)
        
        self.tab_cd_widget.addTab(self.tab_cd_es, "CD ES")
        
        # Aba para CD RJ
        self.tab_cd_rj = QWidget()
        cd_rj_layout = QVBoxLayout(self.tab_cd_rj)
        
        # Tabela para CD RJ
        self.tabela_cd_rj = QTableWidget(0, 9)
        self.tabela_cd_rj.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela_cd_rj.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_cd_rj.verticalHeader().setVisible(False)
        cd_rj_layout.addWidget(self.tabela_cd_rj)
        
        self.tab_cd_widget.addTab(self.tab_cd_rj, "CD RJ")
        
        layout.addWidget(self.tab_cd_widget)
    
    def setup_tab_lojas(self):
        """Configura a aba de detalhes das lojas"""
        layout = QVBoxLayout(self.tab_lojas)
        
        # Caixa de pesquisa de loja
        search_layout = QHBoxLayout()
        search_label = QLabel("Buscar Loja:")
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Digite o nome da loja para filtrar...")
        self.txt_search.textChanged.connect(self.filtrar_lojas)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.txt_search)
        
        layout.addLayout(search_layout)
        
        # Tabela para mostrar lojas e ativos
        self.tabela_lojas = QTableWidget(0, 9)
        self.tabela_lojas.setHorizontalHeaderLabels([
            "Loja", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela_lojas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_lojas.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela_lojas.setSortingEnabled(True)
        layout.addWidget(self.tabela_lojas)
    
    def setup_tab_comparativo(self):
        """Configura a aba de comparativo com o último inventário"""
        layout = QVBoxLayout(self.tab_comparativo)
        
        # Informação de comparação
        info_label = QLabel("Comparativo com o último inventário finalizado")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Tabela de comparativo
        self.tabela_comparativo = QTableWidget(0, 10)
        self.tabela_comparativo.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total", "Diferença"
        ])
        self.tabela_comparativo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_comparativo.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela_comparativo)
        
        # Gráfico de comparativo
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(300)
        layout.addWidget(self.chart_view)
    
    def carregar_dados(self):
        """Carrega os dados nas tabelas"""
        try:
            # Obter dados do inventário
            dados = self.relatorio_service.get_dados_dashboard(self.cod_inventario)
            
            # Verificar se os totais estão presentes
            if 'totais' not in dados:
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Não foi possível obter os totais do inventário."
                )
                return
            
            # Imprimir os totais para depuração
            print("Totais recebidos:")
            for key, value in dados['totais'].items():
                if key.startswith('cd_sp_') or key.startswith('cd_es_') or key.startswith('cd_rj_') or key.startswith('transito_'):
                    print(f"{key}: {value}")
            
            # Carregar resumo por origem
            self._carregar_resumo_por_origem(dados['totais'])
            
            # Carregar resumo por tipo de ativo
            self._carregar_resumo_por_tipo(dados['totais'])
            
            # Carregar detalhes dos CDs
            self._carregar_detalhes_cds(dados)
            
            # Carregar detalhes das lojas
            self._carregar_detalhes_lojas(dados)
            
            # Carregar comparativo
            self._carregar_comparativo(dados)
            
        except Exception as e:
            import traceback
            print(f"Erro ao carregar dados: {e}")
            print(traceback.format_exc())
            QMessageBox.warning(
                self,
                "Erro",
                f"Ocorreu um erro ao carregar os dados: {str(e)}"
            )
    
    def _carregar_resumo_por_origem(self, totais):
        """Carrega a tabela de resumo por origem"""
        self.tabela_resumo_origem.setRowCount(0)
        
        # Lista de origens e seus respectivos dados
        origens = [
            {"nome": "CD SP", "prefixo": "cd_sp_"},
            {"nome": "CD ES", "prefixo": "cd_es_"},
            {"nome": "CD RJ", "prefixo": "cd_rj_"},
            {"nome": "Lojas", "prefixo": "lojas_"},
            {"nome": "Trânsito SP", "prefixo": "transito_sp_"},
            {"nome": "Trânsito ES", "prefixo": "transito_es_"},
            {"nome": "Trânsito RJ", "prefixo": "transito_rj_"},
            {"nome": "Fornecedor", "prefixo": "fornecedor_"},
            {"nome": "TOTAL", "prefixo": "total_"}
        ]
        
        # Lista de tipos de caixa
        tipos_caixa = [
            "hb_623", "hb_618", "hnt_g", "hnt_p", 
            "chocolate", "bin", "pallets_pbr"
        ]
        
        # Preencher tabela
        for i, origem in enumerate(origens):
            self.tabela_resumo_origem.insertRow(i)
            
            # Nome da origem
            nome_item = QTableWidgetItem(origem["nome"])
            if origem["nome"] == "TOTAL":
                fonte = nome_item.font()
                fonte.setBold(True)
                nome_item.setFont(fonte)
            self.tabela_resumo_origem.setItem(i, 0, nome_item)
            
            # Valores por tipo de caixa
            total_linha = 0
            for j, tipo in enumerate(tipos_caixa):
                chave = f"{origem['prefixo']}{tipo}"
                # Garantir que usamos um valor numérico (0 se não existir ou for None)
                valor = int(totais.get(chave, 0) or 0)
                total_linha += valor
                
                valor_item = QTableWidgetItem(str(valor))
                valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if origem["nome"] == "TOTAL":
                    fonte = valor_item.font()
                    fonte.setBold(True)
                    valor_item.setFont(fonte)
                
                self.tabela_resumo_origem.setItem(i, j + 1, valor_item)
            
            # Total da linha
            total_item = QTableWidgetItem(str(total_linha))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if origem["nome"] == "TOTAL":
                fonte = total_item.font()
                fonte.setBold(True)
                total_item.setFont(fonte)
            
            self.tabela_resumo_origem.setItem(i, 8, total_item)
    
    def _carregar_resumo_por_tipo(self, totais):
        """Carrega as tabelas de resumo por tipo de ativo"""
        # Calcular totais agrupados
        total_geral = totais.get('total_geral', 0) or 0
        
        # Calcular total HB (623 + 618)
        total_hb = (totais.get('total_hb_623', 0) or 0) + (totais.get('total_hb_618', 0) or 0)
        
        # Calcular total HNT (G + P)
        total_hnt = (totais.get('total_hnt_g', 0) or 0) + (totais.get('total_hnt_p', 0) or 0)
        
        # Calcular total Outros
        total_outros = (totais.get('total_chocolate', 0) or 0) + (totais.get('total_bin', 0) or 0) + (totais.get('total_pallets_pbr', 0) or 0)
        
        # Verificar que o total geral é não-zero para cálculos percentuais
        if total_geral == 0:
            total_geral = 1  # Evitar divisão por zero
        
        # Carregar tabela HB
        self.tabela_hb.setRowCount(0)
        
        # Adicionar linha para CD SP
        self._adicionar_linha_tipo(self.tabela_hb, "CD SP", 
                               (totais.get('cd_sp_hb_623', 0) or 0) + (totais.get('cd_sp_hb_618', 0) or 0),
                               total_hb)
        
        # Adicionar linha para CD ES
        # Adicionar linha para CD ES
        self._adicionar_linha_tipo(self.tabela_hb, "CD ES", 
                               (totais.get('cd_es_hb_623', 0) or 0) + (totais.get('cd_es_hb_618', 0) or 0),
                               total_hb)
        
        # Adicionar linha para CD RJ
        self._adicionar_linha_tipo(self.tabela_hb, "CD RJ", 
                               (totais.get('cd_rj_hb_623', 0) or 0) + (totais.get('cd_rj_hb_618', 0) or 0),
                               total_hb)
        
        # Adicionar linha para Lojas
        self._adicionar_linha_tipo(self.tabela_hb, "Lojas", 
                               (totais.get('lojas_hb_623', 0) or 0) + (totais.get('lojas_hb_618', 0) or 0),
                               total_hb)
        
        # Adicionar linha para Trânsito
        self._adicionar_linha_tipo(self.tabela_hb, "Trânsito", 
                               (totais.get('transito_sp_hb_623', 0) or 0) + (totais.get('transito_sp_hb_618', 0) or 0) +
                               (totais.get('transito_es_hb_623', 0) or 0) + (totais.get('transito_es_hb_618', 0) or 0) +
                               (totais.get('transito_rj_hb_623', 0) or 0) + (totais.get('transito_rj_hb_618', 0) or 0),
                               total_hb)
                               
        # Adicionar linha para Fornecedor
        self._adicionar_linha_tipo(self.tabela_hb, "Fornecedor", 
                               (totais.get('fornecedor_hb_623', 0) or 0) + (totais.get('fornecedor_hb_618', 0) or 0),
                               total_hb)
        
        # Adicionar linha para Total
        self._adicionar_linha_tipo(self.tabela_hb, "TOTAL", total_hb, total_hb, True)
        
        # Carregar tabela HNT
        self.tabela_hnt.setRowCount(0)
        
        # Adicionar linha para CD SP
        self._adicionar_linha_tipo(self.tabela_hnt, "CD SP", 
                               (totais.get('cd_sp_hnt_g', 0) or 0) + (totais.get('cd_sp_hnt_p', 0) or 0),
                               total_hnt)
        
        # Adicionar linha para CD ES
        self._adicionar_linha_tipo(self.tabela_hnt, "CD ES", 
                               (totais.get('cd_es_hnt_g', 0) or 0) + (totais.get('cd_es_hnt_p', 0) or 0),
                               total_hnt)
        
        # Adicionar linha para CD RJ
        self._adicionar_linha_tipo(self.tabela_hnt, "CD RJ", 
                               (totais.get('cd_rj_hnt_g', 0) or 0) + (totais.get('cd_rj_hnt_p', 0) or 0),
                               total_hnt)
        
        # Adicionar linha para Lojas
        self._adicionar_linha_tipo(self.tabela_hnt, "Lojas", 
                               (totais.get('lojas_hnt_g', 0) or 0) + (totais.get('lojas_hnt_p', 0) or 0),
                               total_hnt)
        
        # Adicionar linha para Trânsito
        self._adicionar_linha_tipo(self.tabela_hnt, "Trânsito", 
                               (totais.get('transito_sp_hnt_g', 0) or 0) + (totais.get('transito_sp_hnt_p', 0) or 0) +
                               (totais.get('transito_es_hnt_g', 0) or 0) + (totais.get('transito_es_hnt_p', 0) or 0) +
                               (totais.get('transito_rj_hnt_g', 0) or 0) + (totais.get('transito_rj_hnt_p', 0) or 0),
                               total_hnt)
                               
        # Adicionar linha para Fornecedor
        self._adicionar_linha_tipo(self.tabela_hnt, "Fornecedor", 
                               (totais.get('fornecedor_hnt_g', 0) or 0) + (totais.get('fornecedor_hnt_p', 0) or 0),
                               total_hnt)
        
        # Adicionar linha para Total
        self._adicionar_linha_tipo(self.tabela_hnt, "TOTAL", total_hnt, total_hnt, True)
        
        # Carregar tabela Outros
        self.tabela_outros.setRowCount(0)
        
        # Adicionar linha para Chocolate
        self._adicionar_linha_tipo(self.tabela_outros, "Chocolate", 
                               totais.get('total_chocolate', 0) or 0,
                               total_outros)
        
        # Adicionar linha para BIN
        self._adicionar_linha_tipo(self.tabela_outros, "BIN", 
                               totais.get('total_bin', 0) or 0,
                               total_outros)
        
        # Adicionar linha para Pallets PBR
        self._adicionar_linha_tipo(self.tabela_outros, "Pallets PBR", 
                               totais.get('total_pallets_pbr', 0) or 0,
                               total_outros)
        
        # Adicionar linha para Total
        self._adicionar_linha_tipo(self.tabela_outros, "TOTAL", total_outros, total_outros, True)
    
    def _adicionar_linha_tipo(self, tabela, nome, valor, total, negrito=False):
        """Adiciona uma linha nas tabelas de tipo"""
        row = tabela.rowCount()
        tabela.insertRow(row)
        
        # Nome
        item_nome = QTableWidgetItem(nome)
        if negrito:
            fonte = item_nome.font()
            fonte.setBold(True)
            item_nome.setFont(fonte)
        tabela.setItem(row, 0, item_nome)
        
        # Valor
        item_valor = QTableWidgetItem(str(valor))
        item_valor.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if negrito:
            fonte = item_valor.font()
            fonte.setBold(True)
            item_valor.setFont(fonte)
        tabela.setItem(row, 1, item_valor)
        
        # Percentual
        percentual = 0
        if total > 0:
            percentual = (valor / total) * 100
        
        item_percentual = QTableWidgetItem(f"{percentual:.1f}%")
        item_percentual.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if negrito:
            fonte = item_percentual.font()
            fonte.setBold(True)
            item_percentual.setFont(fonte)
        tabela.setItem(row, 2, item_percentual)
    
    def _carregar_detalhes_cds(self, dados):
        """Carrega os detalhes dos CDs nas tabelas correspondentes"""
        # Obter totais por tipo
        totais = dados['totais']
        detalhes = dados.get('detalhes', {})
        
        # Lista de tipos de caixa
        tipos_caixa = [
            "hb_623", "hb_618", "hnt_g", "hnt_p", 
            "chocolate", "bin", "pallets_pbr"
        ]
        
        # ----- CD SP -----
        self.tabela_cd_sp.setRowCount(0)
        
        # Linha para CD SP (Físico)
        valores_cd_sp = {tipo: totais.get(f'cd_sp_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_sp, "CD SP", valores_cd_sp)
        
        # Linha para Trânsito SP
        valores_transito_sp = {tipo: totais.get(f'transito_sp_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_sp, "Trânsito SP", valores_transito_sp)
        
        # Linha para Fornecedor SP
        # Dividimos os fornecedores igualmente entre os três CDs (SP, ES, RJ)
        valores_fornecedor_sp = {}
        for tipo in tipos_caixa:
            # Verificar se há informações detalhadas de fornecedor
            valor_fornecedor = 0
            for item in detalhes.get('fornecedor', []):
                if item['tipo_caixa'] == tipo and 'SP' in item.get('tipo_fornecedor', ''):
                    valor_fornecedor += item.get('total', 0)
            
            # Se não houver informação específica, dividir o total igualmente
            if valor_fornecedor == 0:
                valor_fornecedor = (totais.get(f'fornecedor_{tipo}', 0) or 0) / 3
                
            valores_fornecedor_sp[tipo] = valor_fornecedor
        
        self._adicionar_linha_origem(self.tabela_cd_sp, "Fornecedor SP", valores_fornecedor_sp)
        
        # Linha para Total
        self._adicionar_linha_total(self.tabela_cd_sp)
        
        # ----- CD ES -----
        self.tabela_cd_es.setRowCount(0)
        
        # Linha para CD ES (Físico)
        valores_cd_es = {tipo: totais.get(f'cd_es_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_es, "CD ES", valores_cd_es)
        
        # Linha para Trânsito ES
        valores_transito_es = {tipo: totais.get(f'transito_es_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_es, "Trânsito ES", valores_transito_es)
        
        # Linha para Fornecedor ES
        valores_fornecedor_es = {}
        for tipo in tipos_caixa:
            # Verificar se há informações detalhadas de fornecedor
            valor_fornecedor = 0
            for item in detalhes.get('fornecedor', []):
                if item['tipo_caixa'] == tipo and 'ES' in item.get('tipo_fornecedor', ''):
                    valor_fornecedor += item.get('total', 0)
            
            # Se não houver informação específica, dividir o total igualmente
            if valor_fornecedor == 0:
                valor_fornecedor = (totais.get(f'fornecedor_{tipo}', 0) or 0) / 3
                
            valores_fornecedor_es[tipo] = valor_fornecedor
        
        self._adicionar_linha_origem(self.tabela_cd_es, "Fornecedor ES", valores_fornecedor_es)
        
        # Linha para Total
        self._adicionar_linha_total(self.tabela_cd_es)
        
        # ----- CD RJ -----
        self.tabela_cd_rj.setRowCount(0)
        
        # Linha para CD RJ (Físico) - utilizando os dados da tabela contagem_cd
        valores_cd_rj = {tipo: totais.get(f'cd_rj_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_rj, "CD RJ", valores_cd_rj)
        
        # Linha para Trânsito RJ
        valores_transito_rj = {tipo: totais.get(f'transito_rj_{tipo}', 0) or 0 for tipo in tipos_caixa}
        self._adicionar_linha_origem(self.tabela_cd_rj, "Trânsito RJ", valores_transito_rj)
        
        # Linha para Fornecedor RJ
        valores_fornecedor_rj = {}
        for tipo in tipos_caixa:
            # Verificar se há informações detalhadas de fornecedor
            valor_fornecedor = 0
            for item in detalhes.get('fornecedor', []):
                if item['tipo_caixa'] == tipo and 'RJ' in item.get('tipo_fornecedor', ''):
                    valor_fornecedor += item.get('total', 0)
            
            # Se não houver informação específica, dividir o total igualmente
            if valor_fornecedor == 0:
                valor_fornecedor = (totais.get(f'fornecedor_{tipo}', 0) or 0) / 3
                
            valores_fornecedor_rj[tipo] = valor_fornecedor
        
        self._adicionar_linha_origem(self.tabela_cd_rj, "Fornecedor RJ", valores_fornecedor_rj)
        
        # Linha para Total
        self._adicionar_linha_total(self.tabela_cd_rj)
        
    def _adicionar_linha_origem(self, tabela, nome, valores_por_tipo):
        """Adiciona uma linha com valores por tipo para uma origem específica"""
        row = tabela.rowCount()
        tabela.insertRow(row)
        
        # Nome da origem
        item_nome = QTableWidgetItem(nome)
        tabela.setItem(row, 0, item_nome)
        
        # Valores por tipo de caixa
        tipos_caixa = [
            "hb_623", "hb_618", "hnt_g", "hnt_p", 
            "chocolate", "bin", "pallets_pbr"
        ]
        
        total_linha = 0
        for j, tipo in enumerate(tipos_caixa):
            valor = valores_por_tipo.get(tipo, 0)
            total_linha += valor
            
            valor_item = QTableWidgetItem(str(int(valor)))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            tabela.setItem(row, j + 1, valor_item)
        
        # Total da linha
        total_item = QTableWidgetItem(str(int(total_linha)))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tabela.setItem(row, 8, total_item)
    
    def _adicionar_linha_total(self, tabela):
        """Adiciona uma linha de total na tabela"""
        # Verificar se a tabela tem linhas
        if tabela.rowCount() == 0:
            return
        
        row = tabela.rowCount()
        tabela.insertRow(row)
        
        # Nome "TOTAL"
        item_nome = QTableWidgetItem("TOTAL")
        fonte = item_nome.font()
        fonte.setBold(True)
        item_nome.setFont(fonte)
        tabela.setItem(row, 0, item_nome)
        
        # Somar colunas
        for col in range(1, 9):
            total_col = 0
            for r in range(row):
                item = tabela.item(r, col)
                if item and item.text():
                    try:
                        total_col += int(float(item.text()))
                    except:
                        pass
            
            total_item = QTableWidgetItem(str(total_col))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fonte = total_item.font()
            fonte.setBold(True)
            total_item.setFont(fonte)
            tabela.setItem(row, col, total_item)
    
    def _carregar_detalhes_lojas(self, dados):
        """Carrega os detalhes das lojas na tabela"""
        # Limpar a tabela
        self.tabela_lojas.setRowCount(0)
        
        # Verificar se há detalhes disponíveis
        if 'detalhes' in dados and 'lojas' in dados['detalhes']:
            lojas = dados['detalhes']['lojas']
        else:
            # Fallback para consulta direta ao banco de dados
            conn = self.inventario_service.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Consultar os dados de todas as lojas no inventário atual (excluindo CDs)
            cursor.execute('''
            SELECT loja, caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr, status
            FROM contagem_lojas
            WHERE cod_inventario = ? AND loja NOT LIKE 'CD %'
            ORDER BY loja
            ''', (self.cod_inventario,))
            
            lojas = cursor.fetchall()
        
        # Adicionar cada loja à tabela
        for loja in lojas:
            if isinstance(loja, dict) and loja.get('loja', '').startswith('CD '):
                continue  # Ignorar os CDs na lista de lojas
                
            row = self.tabela_lojas.rowCount()
            self.tabela_lojas.insertRow(row)
            
            # Nome da loja (e status)
            if isinstance(loja, dict):
                nome_loja = loja.get('loja', '')
                status = loja.get('status', '')
            else:
                nome_loja = loja['loja']
                status = loja['status']
            
            item_nome = QTableWidgetItem(nome_loja)
            if status == 'finalizado':
                item_nome.setForeground(QColor(0, 128, 0))  # Verde para finalizado
                fonte = item_nome.font()
                fonte.setBold(True)
                item_nome = QTableWidgetItem(nome_loja)
            if status == 'finalizado':
                item_nome.setForeground(QColor(0, 128, 0))  # Verde para finalizado
                fonte = item_nome.font()
                fonte.setBold(True)
                item_nome.setFont(fonte)
            else:
                item_nome.setForeground(QColor(255, 0, 0))  # Vermelho para pendente
            
            self.tabela_lojas.setItem(row, 0, item_nome)
            
            # Valores por tipo
            tipos = ['caixa_hb_623', 'caixa_hb_618', 'caixa_hnt_g', 'caixa_hnt_p', 
                    'caixa_chocolate', 'caixa_bin', 'pallets_pbr']
            
            total_loja = 0
            for j, tipo in enumerate(tipos):
                # Verificar se estamos trabalhando com um dicionário (da API) ou um objeto Row (do banco)
                if isinstance(loja, dict):
                    # Para dicionários, usamos o nome curto do tipo
                    tipo_curto = tipo.replace('caixa_', '')
                    valor = loja.get(tipo, loja.get(tipo_curto, 0)) or 0
                else:
                    valor = loja[tipo] or 0
                
                total_loja += valor
                
                valor_item = QTableWidgetItem(str(valor))
                valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabela_lojas.setItem(row, j + 1, valor_item)
            
            # Total da loja
            total_item = QTableWidgetItem(str(total_loja))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_lojas.setItem(row, 8, total_item)
    
    def filtrar_lojas(self):
        """Filtra a tabela de lojas pelo texto digitado"""
        texto = self.txt_search.text().lower()
        
        for row in range(self.tabela_lojas.rowCount()):
            item = self.tabela_lojas.item(row, 0)
            if item:
                mostrar = texto in item.text().lower()
                self.tabela_lojas.setRowHidden(row, not mostrar)
    
    def _carregar_comparativo(self, dados):
        """Carrega o comparativo com o último inventário finalizado"""
        # Verificar se há comparação disponível
        if not dados.get('comparacao'):
            # Mostrar mensagem na tabela
            self.tabela_comparativo.setRowCount(1)
            msg_item = QTableWidgetItem("Não há inventário anterior para comparação")
            msg_item.setTextAlignment(Qt.AlignCenter)
            self.tabela_comparativo.setSpan(0, 0, 1, 10)
            self.tabela_comparativo.setItem(0, 0, msg_item)
            return
        
        # Limpar tabela
        self.tabela_comparativo.setRowCount(0)
        
        comparacao = dados['comparacao']
        atual = comparacao['atual']
        anterior = comparacao['anterior']
        diferencas = comparacao['diferencas']
        
        # Lista de origens para comparação
        origens = [
            {"nome": "CD SP", "prefixo_atual": "cd_sp_", "prefixo_anterior": "cd_sp_"},
            {"nome": "CD ES", "prefixo_atual": "cd_es_", "prefixo_anterior": "cd_es_"},
            {"nome": "CD RJ", "prefixo_atual": "cd_rj_", "prefixo_anterior": "cd_rj_"},
            {"nome": "Lojas", "prefixo_atual": "lojas_", "prefixo_anterior": "lojas_"},
            {"nome": "Trânsito", "prefixo_atual": "transito_", "prefixo_anterior": "transito_"},
            {"nome": "Fornecedor", "prefixo_atual": "fornecedor_", "prefixo_anterior": "fornecedor_"},
            {"nome": "TOTAL", "prefixo_atual": "total_", "prefixo_anterior": "total_"}
        ]
        
        # Lista de tipos de caixa
        tipos_caixa = [
            "hb_623", "hb_618", "hnt_g", "hnt_p", 
            "chocolate", "bin", "pallets_pbr"
        ]
        
        # Adicionar linha atual
        row = self.tabela_comparativo.rowCount()
        self.tabela_comparativo.insertRow(row)
        
        self.tabela_comparativo.setItem(row, 0, QTableWidgetItem("Inventário Atual"))
        
        # Valores por tipo
        total_atual = 0
        for j, tipo in enumerate(tipos_caixa):
            valor = atual.get(f'total_{tipo}', 0) or 0
            total_atual += valor
            
            valor_item = QTableWidgetItem(str(valor))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_comparativo.setItem(row, j + 1, valor_item)
        
        # Total atual
        total_item = QTableWidgetItem(str(total_atual))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabela_comparativo.setItem(row, 8, total_item)
        
        # Diferença (vazio para a primeira linha)
        self.tabela_comparativo.setItem(row, 9, QTableWidgetItem(""))
        
        # Adicionar linha anterior
        row = self.tabela_comparativo.rowCount()
        self.tabela_comparativo.insertRow(row)
        
        self.tabela_comparativo.setItem(row, 0, QTableWidgetItem("Inventário Anterior"))
        
        # Valores por tipo
        total_anterior = 0
        for j, tipo in enumerate(tipos_caixa):
            valor = anterior.get(f'total_{tipo}', 0) or 0
            total_anterior += valor
            
            valor_item = QTableWidgetItem(str(valor))
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_comparativo.setItem(row, j + 1, valor_item)
        
        # Total anterior
        total_item = QTableWidgetItem(str(total_anterior))
        total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabela_comparativo.setItem(row, 8, total_item)
        
        # Diferença (vazio para a segunda linha)
        self.tabela_comparativo.setItem(row, 9, QTableWidgetItem(""))
        
        # Adicionar linha de diferença
        row = self.tabela_comparativo.rowCount()
        self.tabela_comparativo.insertRow(row)
        
        diff_label = QTableWidgetItem("Diferença")
        fonte = diff_label.font()
        fonte.setBold(True)
        diff_label.setFont(fonte)
        self.tabela_comparativo.setItem(row, 0, diff_label)
        
        # Valores de diferença por tipo
        for j, tipo in enumerate(tipos_caixa):
            diff = diferencas.get(f'diff_{tipo}', 0) or 0
            
            diff_item = QTableWidgetItem(str(diff))
            diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fonte = diff_item.font()
            fonte.setBold(True)
            diff_item.setFont(fonte)
            
            # Definir cor baseada no valor
            if diff > 0:
                diff_item.setForeground(QColor(0, 128, 0))  # Verde para positivo
            elif diff < 0:
                diff_item.setForeground(QColor(255, 0, 0))  # Vermelho para negativo
            
            self.tabela_comparativo.setItem(row, j + 1, diff_item)
        
        # Diferença total
        diff_total = diferencas.get('diff_total', 0) or 0
        total_diff_item = QTableWidgetItem(str(diff_total))
        total_diff_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fonte = total_diff_item.font()
        fonte.setBold(True)
        total_diff_item.setFont(fonte)
        
        # Definir cor baseada no valor
        if diff_total > 0:
            total_diff_item.setForeground(QColor(0, 128, 0))  # Verde para positivo
        elif diff_total < 0:
            total_diff_item.setForeground(QColor(255, 0, 0))  # Vermelho para negativo
        
        self.tabela_comparativo.setItem(row, 8, total_diff_item)
        
        # Percentual de diferença
        perc_diff = 0
        if total_anterior > 0:
            perc_diff = (diff_total / total_anterior) * 100
        
        perc_item = QTableWidgetItem(f"{perc_diff:.1f}%")
        perc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fonte = perc_item.font()
        fonte.setBold(True)
        perc_item.setFont(fonte)
        
        # Definir cor baseada no valor
        if diff_total > 0:
            perc_item.setForeground(QColor(0, 128, 0))  # Verde para positivo
        elif diff_total < 0:
            perc_item.setForeground(QColor(255, 0, 0))  # Vermelho para negativo
        
        self.tabela_comparativo.setItem(row, 9, perc_item)
        
        # Criar gráfico de comparação
        self._criar_grafico_comparativo(atual, anterior)
    
    def _criar_grafico_comparativo(self, atual, anterior):
        """Cria um gráfico de barras para comparação entre inventários"""
        # Criar séries para o gráfico
        series = QBarSeries()
        
        # Criar conjunto de barras para cada inventário
        atual_set = QBarSet("Atual")
        anterior_set = QBarSet("Anterior")
        
        # Tipos de caixa para o gráfico
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
            atual_set.append(atual.get(f'total_{tipo}', 0) or 0)
            anterior_set.append(anterior.get(f'total_{tipo}', 0) or 0)
        
        # Adicionar conjuntos à série
        series.append(atual_set)
        series.append(anterior_set)
        
        # Criar gráfico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Comparação por Tipo de Caixa")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Criar eixos
        axis_x = QBarCategoryAxis()
        axis_x.append([nomes_tipos[tipo] for tipo in tipos_caixa])
        
        axis_y = QValueAxis()
        max_value = max(max(atual_set), max(anterior_set))
        axis_y.setRange(0, max_value * 1.1)  # 10% a mais que o valor máximo
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # Configurar legenda
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Atualizar view
        self.chart_view.setChart(chart)
    
    def exportar_excel(self):
        """Exporta os dados de finalização para um arquivo Excel"""
        # Solicitar local para salvar o arquivo
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Relatório de Finalização",
            f"relatorio_finalizacao_{self.cod_inventario}.xlsx",
            "Arquivos Excel (*.xlsx)"
        )
        
        if not caminho:
            return
        
        try:
            # Verificar se temos o módulo xlsxwriter
            import xlsxwriter
            
            # Criar workbook
            workbook = xlsxwriter.Workbook(caminho)
            
            # Formatos
            titulo_format = workbook.add_format({
                'bold': True,
                'font_size': 14,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            cabecalho_format = workbook.add_format({
                'bold': True,
                'bg_color': '#DDDDDD',
                'border': 1
            })
            
            negrito_format = workbook.add_format({
                'bold': True,
                'border': 1
            })
            
            normal_format = workbook.add_format({
                'border': 1
            })
            
            numero_format = workbook.add_format({
                'border': 1,
                'num_format': '#,##0'
            })
            
            verde_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'font_color': 'green'
            })
            
            vermelho_format = workbook.add_format({
                'bold': True,
                'border': 1,
                'font_color': 'red'
            })
            
            percentual_format = workbook.add_format({
                'border': 1,
                'num_format': '0.0%'
            })
            
            # Primeira planilha: Resumo Geral
            ws_resumo = workbook.add_worksheet("Resumo Geral")
            
            # Título
            ws_resumo.merge_range('A1:I1', f"Resumo do Inventário {self.cod_inventario}", titulo_format)
            ws_resumo.set_row(0, 30)  # Altura da linha de título
            
            # Cabeçalhos
            headers = ["Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
                       "Chocolate", "BIN", "Pallets PBR", "Total"]
            
            for col, header in enumerate(headers):
                ws_resumo.write(2, col, header, cabecalho_format)
            
            # Dados do resumo por origem
            # Dados do resumo por origem
            for row in range(self.tabela_resumo_origem.rowCount()):
                is_total = self.tabela_resumo_origem.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                for col in range(9):
                    item = self.tabela_resumo_origem.item(row, col)
                    if item:
                        if col == 0:  # Nome da origem
                            ws_resumo.write(row + 3, col, item.text(), formato)
                        else:  # Valores numéricos
                            try:
                                valor = int(item.text())
                                ws_resumo.write(row + 3, col, valor, formato)
                            except:
                                ws_resumo.write(row + 3, col, item.text(), formato)
            
            # Ajustar largura das colunas
            ws_resumo.set_column(0, 0, 15)  # Origem
            ws_resumo.set_column(1, 8, 12)  # Valores
            
            # Segunda planilha: Detalhes CDs
            ws_cds = workbook.add_worksheet("Detalhes CDs")
            
            # Título
            ws_cds.merge_range('A1:I1', "Detalhes por Centro de Distribuição", titulo_format)
            ws_cds.set_row(0, 30)  # Altura da linha de título
            
            # CD SP
            ws_cds.merge_range('A3:I3', "CD SP", cabecalho_format)
            
            # Cabeçalhos
            for col, header in enumerate(headers):
                ws_cds.write(4, col, header, cabecalho_format)
            
            # Dados do CD SP
            linha_excel = 5
            for row in range(self.tabela_cd_sp.rowCount()):
                is_total = self.tabela_cd_sp.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                for col in range(9):
                    item = self.tabela_cd_sp.item(row, col)
                    if item:
                        if col == 0:  # Nome da origem
                            ws_cds.write(linha_excel, col, item.text(), formato)
                        else:  # Valores numéricos
                            try:
                                valor = int(item.text())
                                ws_cds.write(linha_excel, col, valor, formato)
                            except:
                                ws_cds.write(linha_excel, col, item.text(), formato)
                
                linha_excel += 1
            
            # CD ES
            linha_excel += 2
            ws_cds.merge_range(f'A{linha_excel}:I{linha_excel}', "CD ES", cabecalho_format)
            linha_excel += 1
            
            # Cabeçalhos
            for col, header in enumerate(headers):
                ws_cds.write(linha_excel, col, header, cabecalho_format)
            linha_excel += 1
            
            # Dados do CD ES
            for row in range(self.tabela_cd_es.rowCount()):
                is_total = self.tabela_cd_es.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                for col in range(9):
                    item = self.tabela_cd_es.item(row, col)
                    if item:
                        if col == 0:  # Nome da origem
                            ws_cds.write(linha_excel, col, item.text(), formato)
                        else:  # Valores numéricos
                            try:
                                valor = int(item.text())
                                ws_cds.write(linha_excel, col, valor, formato)
                            except:
                                ws_cds.write(linha_excel, col, item.text(), formato)
                
                linha_excel += 1
            
            # CD RJ
            linha_excel += 2
            ws_cds.merge_range(f'A{linha_excel}:I{linha_excel}', "CD RJ", cabecalho_format)
            linha_excel += 1
            
            # Cabeçalhos
            for col, header in enumerate(headers):
                ws_cds.write(linha_excel, col, header, cabecalho_format)
            linha_excel += 1
            
            # Dados do CD RJ
            for row in range(self.tabela_cd_rj.rowCount()):
                is_total = self.tabela_cd_rj.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                for col in range(9):
                    item = self.tabela_cd_rj.item(row, col)
                    if item:
                        if col == 0:  # Nome da origem
                            ws_cds.write(linha_excel, col, item.text(), formato)
                        else:  # Valores numéricos
                            try:
                                valor = int(item.text())
                                ws_cds.write(linha_excel, col, valor, formato)
                            except:
                                ws_cds.write(linha_excel, col, item.text(), formato)
                
                linha_excel += 1
            
            # Ajustar largura das colunas
            ws_cds.set_column(0, 0, 15)  # Origem
            ws_cds.set_column(1, 8, 12)  # Valores
            
            # Terceira planilha: Detalhes Lojas
            ws_lojas = workbook.add_worksheet("Detalhes Lojas")
            
            # Título
            ws_lojas.merge_range('A1:I1', "Detalhes por Loja", titulo_format)
            ws_lojas.set_row(0, 30)  # Altura da linha de título
            
            # Cabeçalhos
            headers = ["Loja", "HB 623", "HB 618", "HNT G", "HNT P", 
                       "Chocolate", "BIN", "Pallets PBR", "Total"]
            
            for col, header in enumerate(headers):
                ws_lojas.write(2, col, header, cabecalho_format)
            
            # Dados das lojas
            for row in range(self.tabela_lojas.rowCount()):
                if self.tabela_lojas.isRowHidden(row):
                    continue  # Pular linhas filtradas
                
                for col in range(9):
                    item = self.tabela_lojas.item(row, col)
                    if item:
                        if col == 0:  # Nome da loja
                            # Verificar status pela cor
                            is_finalizado = item.foreground().color().green() > 0
                            formato = verde_format if is_finalizado else normal_format
                            ws_lojas.write(row + 3, col, item.text(), formato)
                        else:  # Valores numéricos
                            try:
                                valor = int(item.text())
                                ws_lojas.write(row + 3, col, valor, normal_format)
                            except:
                                ws_lojas.write(row + 3, col, item.text(), normal_format)
            
            # Ajustar largura das colunas
            ws_lojas.set_column(0, 0, 25)  # Loja
            ws_lojas.set_column(1, 8, 12)  # Valores
            
            # Quarta planilha: Resumo por tipo
            ws_tipo = workbook.add_worksheet("Resumo por Tipo")
            
            # Título
            ws_tipo.merge_range('A1:C1', "Resumo por Tipo de Ativo", titulo_format)
            ws_tipo.set_row(0, 30)  # Altura da linha de título
            
            # HB
            linha_excel = 3
            ws_tipo.merge_range(f'A{linha_excel}:C{linha_excel}', "HB (623 e 618)", cabecalho_format)
            linha_excel += 1
            
            ws_tipo.write(linha_excel, 0, "Origem", cabecalho_format)
            ws_tipo.write(linha_excel, 1, "Quantidade", cabecalho_format)
            ws_tipo.write(linha_excel, 2, "Porcentagem", cabecalho_format)
            linha_excel += 1
            
            # Dados HB
            for row in range(self.tabela_hb.rowCount()):
                is_total = self.tabela_hb.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                # Nome da origem
                ws_tipo.write(linha_excel, 0, self.tabela_hb.item(row, 0).text(), formato)
                
                # Quantidade
                try:
                    valor = int(self.tabela_hb.item(row, 1).text())
                    ws_tipo.write(linha_excel, 1, valor, formato)
                except:
                    ws_tipo.write(linha_excel, 1, self.tabela_hb.item(row, 1).text(), formato)
                
                # Porcentagem
                try:
                    # Converter "xx.x%" para float
                    perc_text = self.tabela_hb.item(row, 2).text().replace('%', '')
                    perc = float(perc_text) / 100.0
                    ws_tipo.write(linha_excel, 2, perc, percentual_format)
                except:
                    ws_tipo.write(linha_excel, 2, self.tabela_hb.item(row, 2).text(), formato)
                
                linha_excel += 1
            
            # HNT
            linha_excel += 2
            ws_tipo.merge_range(f'A{linha_excel}:C{linha_excel}', "HNT (G e P)", cabecalho_format)
            linha_excel += 1
            
            ws_tipo.write(linha_excel, 0, "Origem", cabecalho_format)
            ws_tipo.write(linha_excel, 1, "Quantidade", cabecalho_format)
            ws_tipo.write(linha_excel, 2, "Porcentagem", cabecalho_format)
            linha_excel += 1
            
            # Dados HNT
            for row in range(self.tabela_hnt.rowCount()):
                is_total = self.tabela_hnt.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                # Nome da origem
                ws_tipo.write(linha_excel, 0, self.tabela_hnt.item(row, 0).text(), formato)
                
                # Quantidade
                try:
                    valor = int(self.tabela_hnt.item(row, 1).text())
                    ws_tipo.write(linha_excel, 1, valor, formato)
                except:
                    ws_tipo.write(linha_excel, 1, self.tabela_hnt.item(row, 1).text(), formato)
                
                # Porcentagem
                try:
                    # Converter "xx.x%" para float
                    perc_text = self.tabela_hnt.item(row, 2).text().replace('%', '')
                    perc = float(perc_text) / 100.0
                    ws_tipo.write(linha_excel, 2, perc, percentual_format)
                except:
                    ws_tipo.write(linha_excel, 2, self.tabela_hnt.item(row, 2).text(), formato)
                
                linha_excel += 1
            
            # Outros
            linha_excel += 2
            ws_tipo.merge_range(f'A{linha_excel}:C{linha_excel}', "Outros Ativos", cabecalho_format)
            linha_excel += 1
            
            ws_tipo.write(linha_excel, 0, "Tipo", cabecalho_format)
            ws_tipo.write(linha_excel, 1, "Quantidade", cabecalho_format)
            ws_tipo.write(linha_excel, 2, "Porcentagem", cabecalho_format)
            linha_excel += 1
            
            # Dados Outros
            for row in range(self.tabela_outros.rowCount()):
                is_total = self.tabela_outros.item(row, 0).text() == "TOTAL"
                formato = negrito_format if is_total else normal_format
                
                # Nome do tipo
                ws_tipo.write(linha_excel, 0, self.tabela_outros.item(row, 0).text(), formato)
                
                # Quantidade
                try:
                    valor = int(self.tabela_outros.item(row, 1).text())
                    ws_tipo.write(linha_excel, 1, valor, formato)
                except:
                    ws_tipo.write(linha_excel, 1, self.tabela_outros.item(row, 1).text(), formato)
                
                # Porcentagem
                try:
                    # Converter "xx.x%" para float
                    perc_text = self.tabela_outros.item(row, 2).text().replace('%', '')
                    perc = float(perc_text) / 100.0
                    ws_tipo.write(linha_excel, 2, perc, percentual_format)
                except:
                    ws_tipo.write(linha_excel, 2, self.tabela_outros.item(row, 2).text(), formato)
                
                linha_excel += 1
            
            # Ajustar largura das colunas
            ws_tipo.set_column(0, 0, 15)  # Origem/Tipo
            ws_tipo.set_column(1, 1, 12)  # Quantidade
            ws_tipo.set_column(2, 2, 12)  # Porcentagem
            
            # Quinta planilha: Comparativo
            if self.tabela_comparativo.rowCount() > 1:  # Se houver dados de comparação
                ws_comp = workbook.add_worksheet("Comparativo")
                
                # Título
                ws_comp.merge_range('A1:J1', "Comparativo com Inventário Anterior", titulo_format)
                ws_comp.set_row(0, 30)  # Altura da linha de título
                
                # Cabeçalhos
                headers = ["Inventário", "HB 623", "HB 618", "HNT G", "HNT P", 
                        "Chocolate", "BIN", "Pallets PBR", "Total", "Diferença"]
                
                for col, header in enumerate(headers):
                    ws_comp.write(2, col, header, cabecalho_format)
                
                # Dados do comparativo
                for row in range(self.tabela_comparativo.rowCount()):
                    is_diff = row == 2  # A terceira linha é a diferença
                    formato = negrito_format if is_diff else normal_format
                    
                    for col in range(10):
                        item = self.tabela_comparativo.item(row, col)
                        if item:
                            if col == 0:  # Nome do inventário
                                ws_comp.write(row + 3, col, item.text(), formato)
                            else:  # Valores numéricos
                                if col == 9 and is_diff:  # Porcentagem na diferença
                                    try:
                                        # Converter "xx.x%" para float
                                        perc_text = item.text().replace('%', '')
                                        perc = float(perc_text) / 100.0
                                        
                                        # Verde para positivo, vermelho para negativo
                                        if perc > 0:
                                            ws_comp.write(row + 3, col, perc, workbook.add_format({
                                                'bold': True,
                                                'border': 1,
                                                'font_color': 'green',
                                                'num_format': '0.0%'
                                            }))
                                        elif perc < 0:
                                            ws_comp.write(row + 3, col, perc, workbook.add_format({
                                                'bold': True,
                                                'border': 1,
                                                'font_color': 'red',
                                                'num_format': '0.0%'
                                            }))
                                        else:
                                            ws_comp.write(row + 3, col, perc, percentual_format)
                                    except:
                                        ws_comp.write(row + 3, col, item.text(), formato)
                                else:  # Outros valores numéricos
                                    try:
                                        valor = int(item.text())
                                        
                                        # Verde para positivo, vermelho para negativo na linha de diferença
                                        if is_diff:
                                            if valor > 0:
                                                ws_comp.write(row + 3, col, valor, verde_format)
                                            elif valor < 0:
                                                ws_comp.write(row + 3, col, valor, vermelho_format)
                                            else:
                                                ws_comp.write(row + 3, col, valor, formato)
                                        else:
                                            ws_comp.write(row + 3, col, valor, formato)
                                    except:
                                        ws_comp.write(row + 3, col, item.text(), formato)
                
                # Ajustar largura das colunas
                ws_comp.set_column(0, 0, 15)  # Inventário
                ws_comp.set_column(1, 9, 12)  # Valores
            
            # Fechar o workbook
            workbook.close()
            
            QMessageBox.information(
                self,
                "Exportação Concluída",
                f"Relatório exportado com sucesso para:\n{caminho}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro na Exportação",
                f"Ocorreu um erro ao exportar o relatório: {str(e)}"
            )
    
    def finalizar(self):
        """Finaliza o inventário após revisão dos dados"""
        # Confirmar a finalização
        resp = QMessageBox.question(
            self,
            "Finalizar Inventário",
            "Tem certeza que deseja finalizar o inventário?\n"
            "Esta ação não pode ser desfeita e o inventário será marcado como concluído.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resp != QMessageBox.Yes:
            return
        
        # Finalizar o inventário
        resultado = self.inventario_service.finalizar_inventario_atual()
        
        if resultado:
            QMessageBox.information(
                self,
                "Inventário Finalizado",
                "O inventário foi finalizado com sucesso!"
            )
            self.accept()  # Fechar o diálogo com sucesso
        else:
            QMessageBox.warning(
                self,
                "Erro",
                "Ocorreu um erro ao finalizar o inventário. Por favor, tente novamente."
            )