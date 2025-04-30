# gui/dashboard.py
import sys
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries, QLegend
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QGridLayout, QSizePolicy, QScrollArea,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries

class InfoCard(QFrame):
    """Widget tipo cartão para exibir informações importantes"""
    def __init__(self, title, value, subtitle="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setMinimumHeight(120)
        
        # Configurar layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignLeft)
        title_font = title_label.font()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        
        # Valor
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        value_font = value_label.font()
        value_font.setPointSize(24)
        value_font.setBold(True)
        value_label.setFont(value_font)
        
        # Subtítulo
        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

class RegionalProgressWidget(QWidget):
    """Widget para exibir progresso por regional"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduzir margens
        
        # Título
        title = QLabel("Progresso por Regional")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(30)  # Limitar altura do título
        layout.addWidget(title)
        
        # Tabela de progresso
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Regional", "Concluídas", "Total", "Progresso"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Ajustes na tabela para otimizar espaço
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)  # Cores alternadas para melhor visualização
        self.table.horizontalHeader().setDefaultSectionSize(80)  # Tamanho padrão
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Apenas o nome da regional estica
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)  # Fixar largura
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)  # Fixar largura
        self.table.setStyleSheet("QTableWidget { gridline-color: lightgray; }")
        
        layout.addWidget(self.table)
    
    def atualizar_dados(self, dados_regionais):
        """Atualiza a tabela com os dados de progresso por regional"""
        self.table.setRowCount(0)
        
        # Verificar se temos dados_regionais válidos
        if not dados_regionais:
            print("Aviso: dados_regionais está vazio")
            return
            
        # Separar CDs e regionais normais
        regionais_normais = []
        regionais_cd = []
        
        for regional in dados_regionais:
            # Verificar se temos um dicionário válido
            if not isinstance(regional, dict):
                print(f"Aviso: elemento não é um dicionário: {regional}")
                continue
                
            regional_name = regional.get('regional', '')
            if not regional_name:
                print(f"Aviso: regional sem nome: {regional}")
                continue
                
            # Verificar dados mínimos necessários
            if 'total_lojas' not in regional or 'lojas_finalizadas' not in regional:
                print(f"Aviso: regional com dados incompletos: {regional}")
                continue
                
            if regional_name == 'CENTRO_DISTRIBUICAO':
                regionais_cd.append(regional)
            else:
                regionais_normais.append(regional)
        
        # Adicionar CDs primeiro
        row_index = 0
        for regional in regionais_cd:
            self._adicionar_linha_regional(regional, row_index, True)
            row_index += 1
        
        # Adicionar regionais normais
        for regional in regionais_normais:
            self._adicionar_linha_regional(regional, row_index, False)
            row_index += 1

    def _adicionar_linha_regional(self, regional, row_index, is_cd):
        """Adiciona uma linha na tabela para a regional ou CD"""
        try:
            self.table.insertRow(row_index)
            
            # Regional - Nome mais visível com estilo específico
            regional_name = regional.get('regional', '')
            item_regional = QTableWidgetItem(
                f"🏢 {regional_name}" if is_cd else regional_name
            )
            
            font = item_regional.font()
            font.setBold(True)
            item_regional.setFont(font)
            
            # Destacar CDs com cor diferente
            if is_cd:
                item_regional.setForeground(QColor(41, 128, 185))  # Azul mais brilhante para CDs
            
            self.table.setItem(row_index, 0, item_regional)
            
            # Lojas concluídas
            lojas_finalizadas = regional.get('lojas_finalizadas', 0)
            item_concluidas = QTableWidgetItem(str(lojas_finalizadas))
            if is_cd:
                item_concluidas.setForeground(QColor(41, 128, 185))
            self.table.setItem(row_index, 1, item_concluidas)
            
            # Total de lojas
            total_lojas = regional.get('total_lojas', 0)
            item_total = QTableWidgetItem(str(total_lojas))
            if is_cd:
                item_total.setForeground(QColor(41, 128, 185))
            self.table.setItem(row_index, 2, item_total)
            
            # Calcular porcentagem
            porcentagem = 0
            if 'porcentagem' in regional:
                porcentagem = regional['porcentagem']
            elif total_lojas > 0:
                porcentagem = (lojas_finalizadas / total_lojas) * 100
            
            # Barra de progresso com texto mais visível
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setValue(int(porcentagem))
            progress_bar.setFormat("%v%")  # Mostrar valor com percentual
            progress_bar.setAlignment(Qt.AlignCenter)
            
            # Alterar cor da barra de progresso baseado no percentual e tipo
            stylesheet = ""
            if is_cd:
                # Paleta especial para CDs
                if porcentagem < 30:
                    stylesheet = "QProgressBar::chunk { background-color: #3498db; }"  # Azul claro
                elif porcentagem < 70:
                    stylesheet = "QProgressBar::chunk { background-color: #2980b9; }"  # Azul médio
                else:
                    stylesheet = "QProgressBar::chunk { background-color: #1c6ea4; }"  # Azul escuro
            else:
                # Paleta normal para lojas
                if porcentagem < 30:
                    stylesheet = "QProgressBar::chunk { background-color: #FF6666; }"  # Vermelho claro
                elif porcentagem < 70:
                    stylesheet = "QProgressBar::chunk { background-color: #FFCC66; }"  # Amarelo
                else:
                    stylesheet = "QProgressBar::chunk { background-color: #66CC66; }"  # Verde claro
            
            progress_bar.setStyleSheet(stylesheet)
            self.table.setCellWidget(row_index, 3, progress_bar)
            
        except Exception as e:
            print(f"Erro ao adicionar linha regional: {e}")

class LojasPendentesWidget(QWidget):
    """Widget para exibir lojas pendentes por regional"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduzir margens
        layout.setSpacing(5)  # Reduzir espaçamento
        
        # Título
        title = QLabel("Lojas Pendentes")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(30)  # Limitar altura do título
        layout.addWidget(title)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remover bordas
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)  # Remover margens
        self.scroll_layout.setSpacing(2)  # Espaçamento mínimo entre grupos
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
    
    def atualizar_dados(self, lojas_pendentes):
        """Atualiza a lista de lojas pendentes por regional"""
        # Limpar layout atual
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Adicionar novas regionais e suas lojas pendentes
        for regional, lojas in lojas_pendentes.items():
            if not lojas:  # Pular regionais sem lojas pendentes
                continue
            
            # Verificar se é a regional especial para CDs
            is_cd_regional = regional == 'CENTRO_DISTRIBUICAO'
            
            # Criar grupo para a regional com estilo compacto
            group_title = "CENTROS DE DISTRIBUIÇÃO" if is_cd_regional else regional
            count_suffix = f" ({len(lojas)})"
            
            group = QGroupBox(f"{group_title}{count_suffix}")
            
            # Estilo especial para CDs
            if is_cd_regional:
                group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border: 1px solid #2980b9;
                        background-color: #ecf0f1;
                        border-radius: 3px;
                        margin-top: 5px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 3px;
                        color: #2980b9;
                    }
                """)
            else:
                group.setStyleSheet("""
                    QGroupBox {
                        font-weight: bold;
                        border: 1px solid #CCCCCC;
                        border-radius: 3px;
                        margin-top: 5px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 3px;
                    }
                """)
            
            # Layout mais compacto para o grupo
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(5, 10, 5, 5)  # Margens reduzidas
            group_layout.setSpacing(0)  # Sem espaçamento entre itens
            
            # Adicionar lista de lojas em formato compacto
            for loja in lojas:
                # Ícone especial para CDs
                prefix = "🏢 " if "CD " in loja else ""
                
                loja_label = QLabel(f"{prefix}{loja}")
                
                # Estilo especial para CDs
                if "CD " in loja:
                    loja_label.setStyleSheet("font-weight: bold; color: #2980b9; padding: 1px 3px;")
                else:
                    loja_label.setStyleSheet("padding: 1px 3px;")  # Padding mínimo
                    
                group_layout.addWidget(loja_label)
            
            self.scroll_layout.addWidget(group)
        
        # Adicionar espaçador para alinhar tudo ao topo
        self.scroll_layout.addStretch()

class ComparacaoInventarioWidget(QWidget):
    """Widget para exibir gráfico de comparação entre inventários"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduzir margens
        layout.setSpacing(5)  # Reduzir espaçamento
        
        # Título
        title = QLabel("Comparação com Inventário Anterior")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(30)  # Limitar altura do título
        layout.addWidget(title)
        
        # Área para o gráfico
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(180)  # Altura mínima reduzida
        layout.addWidget(self.chart_view)
    
    def atualizar_dados(self, dados_comparacao):
        """Atualiza o gráfico com dados de comparação entre inventários"""
        if not dados_comparacao:
            # Exibir mensagem de que não há dados para comparação
            chart = QChart()
            chart.setTitle("Sem dados para comparação")
            chart.setTitleFont(QFont("Arial", 10, QFont.Bold))
            self.chart_view.setChart(chart)
            return
        
        # Criar séries para o gráfico
        series = QBarSeries()
        
        # Criar conjunto de barras para cada origem
        atual_set = QBarSet("Atual")
        anterior_set = QBarSet("Anterior")
        
        # Definir cores para os conjuntos
        atual_set.setColor(QColor(52, 152, 219))  # Azul
        anterior_set.setColor(QColor(149, 165, 166))  # Cinza
        
        # Tipos de caixa para exibir no gráfico - usar abreviações para economizar espaço
        tipos_caixa = [
            'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
            'chocolate', 'bin', 'pallets_pbr'
        ]
        
        # Mapeamento para nomes mais curtos
        nomes_curtos = {
            'hb_623': 'HB623',
            'hb_618': 'HB618',
            'hnt_g': 'HNTG',
            'hnt_p': 'HNTP',
            'chocolate': 'Choc',
            'bin': 'BIN',
            'pallets_pbr': 'PBR'
        }
        
        # Adicionar valores aos conjuntos
        for tipo in tipos_caixa:
            atual_set.append(dados_comparacao['atual'][f'total_{tipo}'])
            anterior_set.append(dados_comparacao['anterior'][f'total_{tipo}'])
        
        # Adicionar conjuntos à série
        series.append(atual_set)
        series.append(anterior_set)
        
        # Criar gráfico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Comparação por Tipo de Caixa")
        chart.setTitleFont(QFont("Arial", 10, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Remover margens do gráfico
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setBackgroundRoundness(0)
        
        # Criar eixos - usar nomes abreviados
        axis_x = QBarCategoryAxis()
        axis_x.append([nomes_curtos[tipo] for tipo in tipos_caixa])
        axis_x.setLabelsFont(QFont("Arial", 8))
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(max(atual_set), max(anterior_set)) * 1.1)  # 10% a mais que o valor máximo
        axis_y.setLabelFormat("%d")  # Sem decimais
        axis_y.setLabelsFont(QFont("Arial", 8))
        axis_y.setTickCount(5)  # Reduzir número de ticks
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        # Configurar legenda - mais compacta
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Arial", 8))
        
        # Atualizar view
        self.chart_view.setChart(chart)

class DistribuicaoWidget(QWidget):
    """Widget para exibir gráfico de distribuição de caixas por origem"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduzir margens
        layout.setSpacing(5)  # Reduzir espaçamento
        
        # Título
        title = QLabel("Distribuição por Origem")
        title_font = title.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setMaximumHeight(30)  # Limitar altura do título
        layout.addWidget(title)
        
        # Área para o gráfico
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(180)  # Altura mínima reduzida
        layout.addWidget(self.chart_view)
    
    def atualizar_dados(self, totais):
        """Atualiza o gráfico com dados de distribuição por origem"""
        # Verificar se temos dados válidos
        if not totais:
            print("Aviso: Dados inválidos para o gráfico de distribuição")
            return
            
        # Criar série para o gráfico de pizza
        series = QPieSeries()
        
        # Adicionar fatias para cada origem
        # Calcular o total dos CDs somando os 3 CDs
        total_cd = (totais.get('total_cd_sp', 0) or 0) + (totais.get('total_cd_es', 0) or 0) + (totais.get('total_cd_rj', 0) or 0)
        
        # Se não temos total de CDs, verificar se existe um total_cd geral
        if total_cd == 0 and 'total_cd' in totais:
            total_cd = totais['total_cd']
        
        # Modificado para separar os dados de trânsito por origem
        origens = {
            'Lojas': totais.get('total_lojas', 0) or 0,
            'CDs': total_cd,
            'Trânsito SP': totais.get('total_transito_sp', 0) or 0,
            'Trânsito ES': totais.get('total_transito_es', 0) or 0,
            'Trânsito RJ': totais.get('total_transito_rj', 0) or 0,
            'Fornecedor': totais.get('total_fornecedor', 0) or 0
        }
        
        # Remover origens com valor zero
        origens = {k: v for k, v in origens.items() if v > 0}
        
        # Se não há valores positivos, mostrar mensagem
        if not origens:
            # Criar gráfico vazio com mensagem
            chart = QChart()
            chart.setTitle("Sem dados de distribuição")
            self.chart_view.setChart(chart)
            return
            
        # Calcular porcentagens
        total_geral = totais.get('total_geral', 0) or 0
        if total_geral == 0:
            # Se total_geral não está disponível, calculamos a partir das origens
            total_geral = sum(origens.values())
        
        # Se ainda for zero, definir como 1 para evitar divisão por zero
        if total_geral == 0:
            total_geral = 1
        
        # Cores personalizadas para cada origem
        cores = {
            'Lojas': QColor(52, 152, 219),      # Azul
            'CDs': QColor(46, 204, 113),         # Verde
            'Trânsito SP': QColor(155, 89, 182),   # Roxo
            'Trânsito ES': QColor(142, 68, 173),   # Roxo mais escuro
            'Trânsito RJ': QColor(175, 122, 197),  # Roxo mais claro
            'Fornecedor': QColor(241, 196, 15)  # Amarelo
        }
        
        for origem, valor in origens.items():
            porcentagem = (valor / total_geral) * 100
            # Formatar texto para ser mais compacto (eliminando decimais se for 0)
            texto = f"{origem} ({porcentagem:.1f}%)" if porcentagem % 1 != 0 else f"{origem} ({int(porcentagem)}%)"
            slice = series.append(texto, valor)
            
            # Definir cores personalizadas
            if origem in cores:
                slice.setColor(cores[origem])
                
            # Apenas mostrar labels para origens com valores significativos (> 5%)
            slice.setLabelVisible(porcentagem > 5)
            
            # Destacar a fatia maior
            if valor == max(origens.values()):
                slice.setExploded(True)
                slice.setExplodeDistanceFactor(0.08)
        
        # Criar gráfico
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Distribuição de Ativos por Origem")
        chart.setTitleFont(QFont("Arial", 10, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Remover margens do gráfico
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.setBackgroundRoundness(0)
        
        # Configurar legenda - mais compacta
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setFont(QFont("Arial", 8))
        chart.legend().setMarkerShape(QLegend.MarkerShapeCircle)
        
        # Atualizar view
        self.chart_view.setChart(chart)

class DashboardWidget(QWidget):
    """Widget principal do dashboard"""
    def __init__(self, relatorio_service, parent=None):
        super().__init__(parent)
        self.relatorio_service = relatorio_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Reduzir espaçamento entre elementos
        
        # Linha 1: Cards de informação
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)  # Reduzir espaçamento entre cards
        
        self.card_lojas = InfoCard("Lojas Contadas", "0", "de 0")
        cards_layout.addWidget(self.card_lojas)
        
        self.card_cd = InfoCard("Setores do CD", "0", "de 0")
        cards_layout.addWidget(self.card_cd)
        
        self.card_total = InfoCard("Total de Ativos", "0", "")
        cards_layout.addWidget(self.card_total)
        
        layout.addLayout(cards_layout)
        
        # Linha 2: Gráficos e tabelas
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)  # Reduzir espaçamento entre colunas
        
        # Coluna esquerda: Progresso por regional e distribuição
        left_column = QVBoxLayout()
        left_column.setSpacing(10)  # Reduzir espaçamento entre widgets
        
        # Widget de progresso regional com altura maior
        self.regional_progress = RegionalProgressWidget()
        self.regional_progress.setMinimumHeight(250)  # Aumentar altura mínima
        left_column.addWidget(self.regional_progress, 3)  # Aumentar peso vertical para 3
        
        # Gráfico de distribuição mais compacto
        self.distribuicao_widget = DistribuicaoWidget()
        left_column.addWidget(self.distribuicao_widget, 2)  # Reduzir peso vertical para 2
        
        charts_layout.addLayout(left_column, 3)  # Aumentar proporção da coluna esquerda (3:2)
        
        # Coluna direita: Lojas pendentes e comparação
        right_column = QVBoxLayout()
        right_column.setSpacing(10)  # Reduzir espaçamento entre widgets
        
        # Widget de lojas pendentes com altura maior
        self.lojas_pendentes = LojasPendentesWidget()
        self.lojas_pendentes.setMinimumHeight(250)  # Aumentar altura mínima
        right_column.addWidget(self.lojas_pendentes, 3)  # Aumentar peso vertical para 3
        
        # Gráfico de comparação mais compacto
        self.comparacao_widget = ComparacaoInventarioWidget()
        right_column.addWidget(self.comparacao_widget, 2)  # Reduzir peso vertical para 2
        
        charts_layout.addLayout(right_column, 2)  # Diminuir proporção da coluna direita (3:2)
        
        layout.addLayout(charts_layout)
    
    def atualizar_cards(self, dados):
        """Atualiza os cards de informação com os dados do inventário"""
        # Verificar se os dados são válidos
        if not dados or 'status' not in dados:
            print("Aviso: Dados inválidos para atualizar_cards")
            return
            
        # Card de lojas
        total_lojas = dados['status'].get('total_lojas', 0)
        lojas_finalizadas = dados['status'].get('lojas_finalizadas', 0)
        
        self.card_lojas.findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText("Lojas Contadas")
        valor_lojas = self.card_lojas.findChildren(QLabel)[1]
        valor_lojas.setText(str(lojas_finalizadas))
        
        subtitulo_lojas = self.card_lojas.findChildren(QLabel)[2]
        porcentagem_lojas = dados['status'].get('porcentagem_lojas', 0)
        subtitulo_lojas.setText(f"de {total_lojas} ({porcentagem_lojas:.1f}%)")
        
        # Card de setores do CD
        total_setores = dados['status'].get('total_setores', 0)
        setores_finalizados = dados['status'].get('setores_finalizados', 0)
        
        self.card_cd.findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText("Setores do CD")
        valor_cd = self.card_cd.findChildren(QLabel)[1]
        valor_cd.setText(str(setores_finalizados))
        
        subtitulo_cd = self.card_cd.findChildren(QLabel)[2]
        porcentagem_setores = dados['status'].get('porcentagem_setores', 0)
        subtitulo_cd.setText(f"de {total_setores} ({porcentagem_setores:.1f}%)")
        
        # Card de total de ativos
        self.card_total.findChild(QLabel, "", Qt.FindDirectChildrenOnly).setText("Total de Ativos")
        valor_total = self.card_total.findChildren(QLabel)[1]
        
        # Usar total_geral do dicionário de totais, se existir
        total_geral = 0
        if 'totais' in dados and dados['totais']:
            total_geral = dados['totais'].get('total_geral', 0)
        valor_total.setText(str(total_geral))
        
        subtitulo_total = self.card_total.findChildren(QLabel)[2]
        subtitulo_total.setText("unidades")
    
    def atualizar_dados(self, cod_inventario):
        """Atualiza todos os componentes do dashboard com os dados do inventário"""
        if not cod_inventario:
            print("Aviso: atualizar_dados chamado com cod_inventario vazio")
            return
            
        try:
            # Obter dados do dashboard
            dados = self.relatorio_service.get_dados_dashboard(cod_inventario)
            
            # Verificar se os dados são válidos
            if not dados:
                print("Aviso: get_dados_dashboard retornou None")
                return
                
            # Processar os dados de trânsito para separar por origem
            # Adicionar totais separados para cada origem de trânsito
            totais = dados.get('totais', {})
            
            # Verificar se os totais são válidos
            if not totais:
                print("Aviso: Dicionário de totais vazio")
                # Tente obter os totais diretamente
                totais = self.relatorio_service.get_totais_por_tipo(cod_inventario)
                if not totais:
                    print("Aviso: Não foi possível obter totais")
                    return
                dados['totais'] = totais
            
            # Inicializar valores mínimos necessários no dicionário de totais para evitar KeyError
            for chave in ['total_lojas', 'total_geral', 'total_fornecedor',
                        'total_transito_sp', 'total_transito_es', 'total_transito_rj',
                        'total_cd_sp', 'total_cd_es', 'total_cd_rj']:
                if chave not in totais:
                    totais[chave] = 0
            
            # Obter detalhes de trânsito por tipo (se disponíveis)
            # Calcular totais de trânsito por origem específica se necessário
            if 'detalhes' in dados and 'transito' in dados['detalhes']:
                for item in dados['detalhes']['transito']:
                    setor = item.get('setor', '').upper()
                    tipo = item.get('tipo_caixa', '')
                    quantidade = item.get('total', 0)
                    
                    # Normalizar o tipo
                    if tipo and tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
                        if 'SP' in setor:
                            totais[f'transito_sp_{tipo}'] = quantidade
                        elif 'ES' in setor:
                            totais[f'transito_es_{tipo}'] = quantidade
                        elif 'RJ' in setor:
                            totais[f'transito_rj_{tipo}'] = quantidade
            
            # Atualizar cards
            self.atualizar_cards(dados)
            
            # Atualizar progresso por regional
            self.regional_progress.atualizar_dados(dados['status'].get('resumo_regional', []))
            
            # Atualizar lojas pendentes
            lojas_pendentes = {}
            for regional in dados['status'].get('resumo_regional', []):
                if regional.get('lojas_pendentes'):
                    # Agrupar CDs em uma categoria especial
                    if regional.get('regional') == 'CENTRO_DISTRIBUICAO':
                        lojas_pendentes['CENTRO_DISTRIBUICAO'] = regional['lojas_pendentes']
                    else:
                        lojas_pendentes[regional.get('regional', '')] = regional['lojas_pendentes']
            
            self.lojas_pendentes.atualizar_dados(lojas_pendentes)
            
            # Atualizar gráfico de comparação
            self.comparacao_widget.atualizar_dados(dados.get('comparacao'))
            
            # Atualizar gráfico de distribuição com os dados processados
            self.distribuicao_widget.atualizar_dados(totais)
            
        except Exception as e:
            import traceback
            print(f"Erro ao atualizar dados do dashboard: {e}")
            print(traceback.format_exc())