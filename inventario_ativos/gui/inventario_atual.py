# gui/inventario_atual.py
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QSpinBox,QTabBar, QTabWidget,QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class TabelaResumoWidget(QWidget):
    """Widget para exibir a tabela de resumo do inventário"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Resumo do Inventário Atual")
        titulo_font = titulo.font()
        titulo_font.setPointSize(12)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabela de resumo
        self.tabela = QTableWidget(0, 9)
        self.tabela.setHorizontalHeaderLabels([
            "Origem", "HB 623", "HB 618", "HNT G", "HNT P", 
            "Chocolate", "BIN", "Pallets PBR", "Total"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
    
    def atualizar_dados(self, dados):
        """Atualiza a tabela com os dados de resumo"""
        self.tabela.setRowCount(0)
        
        # Lista de origens e seus respectivos dados
        origens = [
            {"nome": "Lojas", "prefixo": "lojas_"},
            {"nome": "CD", "prefixo": "cd_"},
            {"nome": "Trânsito", "prefixo": "transito_"},
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
            self.tabela.insertRow(i)
            
            # Nome da origem
            nome_item = QTableWidgetItem(origem["nome"])
            if origem["nome"] == "TOTAL":
                fonte = nome_item.font()
                fonte.setBold(True)
                nome_item.setFont(fonte)
            self.tabela.setItem(i, 0, nome_item)
            
            # Valores por tipo de caixa
            total_linha = 0
            for j, tipo in enumerate(tipos_caixa):
                chave = f"{origem['prefixo']}{tipo}"
                valor = dados.get(chave, 0) or 0
                total_linha += valor
                
                valor_item = QTableWidgetItem(str(valor))
                valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if origem["nome"] == "TOTAL":
                    fonte = valor_item.font()
                    fonte.setBold(True)
                    valor_item.setFont(fonte)
                
                self.tabela.setItem(i, j + 1, valor_item)
            
            # Total da linha
            total_item = QTableWidgetItem(str(total_linha))
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            if origem["nome"] == "TOTAL":
                fonte = total_item.font()
                fonte.setBold(True)
                total_item.setFont(fonte)
            
            self.tabela.setItem(i, 8, total_item)



class InventarioAtualWidget(QWidget):
    """Widget principal para a aba de Dados do Inventário Atual"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QHBoxLayout(self)
        
        # Coluna esquerda: Tabela de resumo
        self.tabela_resumo = TabelaResumoWidget()
        layout.addWidget(self.tabela_resumo, 3)  # Peso 3 para a tabela
        
        # Coluna direita: Formulário para adicionar dados
        self.formulario_widget = FormularioFornecedorWidget(inventario_service)
        layout.addWidget(self.formulario_widget, 2)  # Peso 2 para o formulário (aumentado para acomodar as novas abas)
    
    def atualizar_dados(self):
        """Atualiza os dados do widget"""
        if not self.inventario_service.inventario_atual:
            return
        
        # Obter resumo do inventário atual
        resumo = self.inventario_service.get_resumo_inventario_atual()
        
        # Obter totais por tipo
        totais = {}
        
        # Processar dados de lojas
        for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
            totais[f'lojas_{tipo}'] = resumo['dados_lojas'].get(f'total_{tipo}', 0) or 0
        
        # Processar dados de CD
        for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
            totais[f'cd_{tipo}'] = resumo['dados_cd'].get(f'total_{tipo}', 0) or 0
        
        # Processar dados de trânsito
        totais_transito = {item['tipo_caixa']: item['total'] for item in resumo['dados_transito']}
        for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
            totais[f'transito_{tipo}'] = totais_transito.get(tipo, 0) or 0
        
        # Processar dados de fornecedor
        totais_fornecedor = {item['tipo_caixa']: item['total'] for item in resumo['dados_fornecedor']}
        for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
            totais[f'fornecedor_{tipo}'] = totais_fornecedor.get(tipo, 0) or 0
        
        # Calcular totais por tipo
        for tipo in ['hb_623', 'hb_618', 'hnt_g', 'hnt_p', 'chocolate', 'bin', 'pallets_pbr']:
            totais[f'total_{tipo}'] = (
                totais[f'lojas_{tipo}'] + 
                totais[f'cd_{tipo}'] + 
                totais[f'transito_{tipo}'] + 
                totais[f'fornecedor_{tipo}']
            )
        
        # Atualizar tabela de resumo
        self.tabela_resumo.atualizar_dados(totais)
        
        # Atualizar lista de lojas no formulário (se necessário recarregar)
        if hasattr(self.formulario_widget, 'atualizar_lista_lojas'):
            self.formulario_widget.atualizar_lista_lojas()


class FormularioFornecedorWidget(QWidget):
    """Widget para adicionar diversos tipos de dados ao inventário"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas para diferentes tipos de entrada
        self.tab_widget = QTabWidget()
        
        # Tab para fornecedor (atual)
        self.tab_fornecedor = QWidget()
        self.setup_tab_fornecedor()
        self.tab_widget.addTab(self.tab_fornecedor, "Fornecedor")
        
        # Tab para contagem manual de lojas
        self.tab_loja = QWidget()
        self.setup_tab_loja()
        self.tab_widget.addTab(self.tab_loja, "Contagem Loja/CD")
        
        # Tab para trânsito
        self.tab_transito = QWidget()
        self.setup_tab_transito()
        self.tab_widget.addTab(self.tab_transito, "Trânsito")
        
        layout.addWidget(self.tab_widget)
    
    def setup_tab_fornecedor(self):
        """Configura a aba de fornecedor"""
        # Layout da aba
        form_layout = QFormLayout(self.tab_fornecedor)
        
        # Campos do formulário
        self.cb_fornecedor = QComboBox()
        self.cb_fornecedor.addItems(self.inventario_service.get_tipos_fornecedor())
        form_layout.addRow("Fornecedor:", self.cb_fornecedor)
        
        self.cb_tipo_caixa_fornecedor = QComboBox()
        self.atualizar_tipos_caixa(self.cb_tipo_caixa_fornecedor)
        form_layout.addRow("Tipo de Caixa:", self.cb_tipo_caixa_fornecedor)
        
        self.sp_quantidade_fornecedor = QSpinBox()
        self.sp_quantidade_fornecedor.setMinimum(0)
        self.sp_quantidade_fornecedor.setMaximum(999999)
        form_layout.addRow("Quantidade:", self.sp_quantidade_fornecedor)
        
        # Botão para adicionar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_adicionar_fornecedor = QPushButton("Adicionar")
        self.btn_adicionar_fornecedor.clicked.connect(self.adicionar_dados_fornecedor)
        btn_layout.addWidget(self.btn_adicionar_fornecedor)
        
        form_layout.addRow("", btn_layout)
    
    def setup_tab_loja(self):
        """Configura a aba de contagem manual de lojas e CDs"""
        # Layout da aba
        form_layout = QFormLayout(self.tab_loja)
        
        # Campo para selecionar a loja
        self.cb_loja = QComboBox()
        self.atualizar_lista_lojas()
        self.cb_loja.currentIndexChanged.connect(self.on_loja_changed)
        form_layout.addRow("Loja/CD:", self.cb_loja)
        
        self.cb_tipo_caixa_loja = QComboBox()
        self.atualizar_tipos_caixa(self.cb_tipo_caixa_loja)
        form_layout.addRow("Tipo de Caixa:", self.cb_tipo_caixa_loja)
        
        self.sp_quantidade_loja = QSpinBox()
        self.sp_quantidade_loja.setMinimum(0)
        self.sp_quantidade_loja.setMaximum(999999)
        form_layout.addRow("Quantidade:", self.sp_quantidade_loja)
        
        # Checkbox para finalizar a contagem
        self.chk_finalizar_loja = QCheckBox("Marcar como finalizado")
        form_layout.addRow("", self.chk_finalizar_loja)
        
        # Botão para adicionar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_adicionar_loja = QPushButton("Adicionar Contagem")
        self.btn_adicionar_loja.clicked.connect(self.adicionar_contagem_loja)
        btn_layout.addWidget(self.btn_adicionar_loja)
        
        form_layout.addRow("", btn_layout)
    
    def setup_tab_transito(self):
        """Configura a aba de trânsito"""
        # Layout da aba
        form_layout = QFormLayout(self.tab_transito)
        
        # Campo para selecionar o tipo de trânsito
        self.cb_tipo_transito = QComboBox()
        self.cb_tipo_transito.addItems(["Trânsito SP", "Trânsito ES", "Trânsito RJ"])
        form_layout.addRow("Tipo de Trânsito:", self.cb_tipo_transito)
        
        self.cb_tipo_caixa_transito = QComboBox()
        self.atualizar_tipos_caixa(self.cb_tipo_caixa_transito)
        form_layout.addRow("Tipo de Caixa:", self.cb_tipo_caixa_transito)
        
        self.sp_quantidade_transito = QSpinBox()
        self.sp_quantidade_transito.setMinimum(0)
        self.sp_quantidade_transito.setMaximum(999999)
        form_layout.addRow("Quantidade:", self.sp_quantidade_transito)
        
        # Botão para adicionar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_adicionar_transito = QPushButton("Adicionar em Trânsito")
        self.btn_adicionar_transito.clicked.connect(self.adicionar_dados_transito)
        btn_layout.addWidget(self.btn_adicionar_transito)
        
        form_layout.addRow("", btn_layout)
    
    def on_loja_changed(self, index):
        """Atualiza a interface quando a loja selecionada é alterada"""
        loja = self.cb_loja.currentData()
        # Verificar se é um CD
        is_cd = loja and ("CD SP" in loja or "CD ES" in loja)
        
        # Atualizar texto do botão e checkbox conforme o tipo
        if is_cd:
            self.btn_adicionar_loja.setText("Adicionar Contagem CD")
            self.chk_finalizar_loja.setText("Marcar CD como finalizado")
        else:
            self.btn_adicionar_loja.setText("Adicionar Contagem Loja")
            self.chk_finalizar_loja.setText("Marcar loja como finalizada")
    
    def atualizar_tipos_caixa(self, combobox):
        """Atualiza a lista de tipos de caixa no ComboBox especificado"""
        combobox.clear()
        
        # Nomes mais amigáveis para os tipos de caixa
        nomes_tipos = {
            "hb_623": "Caixa HB 623",
            "hb_618": "Caixa HB 618",
            "hnt_g": "Caixa HNT G",
            "hnt_p": "Caixa HNT P",
            "chocolate": "Caixa Chocolate",
            "bin": "Caixa BIN",
            "pallets_pbr": "Pallets PBR"
        }
        
        for tipo in self.inventario_service.get_tipo_caixas():
            combobox.addItem(nomes_tipos.get(tipo, tipo), tipo)
    
    def atualizar_lista_lojas(self):
        """Atualiza a lista de lojas disponíveis, destacando CDs"""
        self.cb_loja.clear()
        
        try:
            # Obter lista de lojas do CSV
            lojas = self.inventario_service.csv_manager.ler_lojas_csv(force_reload=True)
            
            # Listas separadas para CDs e lojas normais
            cds = []
            lojas_normais = []
            
            # Separar CDs das lojas normais
            for loja in lojas:
                nome_loja = loja.get('loja', '')
                regional = loja.get('regional', '')
                
                if nome_loja:
                    if regional == 'CENTRO_DISTRIBUICAO' or nome_loja.startswith('CD '):
                        cds.append((nome_loja, regional))
                    else:
                        lojas_normais.append((nome_loja, regional))
            
            # Adicionar CDs primeiro (no topo da lista)
            for nome, regional in cds:
                texto = f"🏢 {nome}"
                self.cb_loja.addItem(texto, nome)
            
            # Adicionar um separador se houver CDs e lojas normais
            if cds and lojas_normais:
                self.cb_loja.insertSeparator(len(cds))
            
            # Adicionar lojas normais
            for nome, regional in lojas_normais:
                texto = f"{nome}" if not regional else f"{nome} ({regional})"
                self.cb_loja.addItem(texto, nome)
            
        except Exception as e:
            print(f"Erro ao carregar lojas: {e}")
    
    def adicionar_dados_fornecedor(self):
        """Adiciona os dados de fornecedor ao inventário"""
        tipo_fornecedor = self.cb_fornecedor.currentText()
        tipo_caixa = self.cb_tipo_caixa_fornecedor.currentData()
        quantidade = self.sp_quantidade_fornecedor.value()
        
        if quantidade <= 0:
            QMessageBox.warning(
                self, 
                "Atenção", 
                "A quantidade deve ser maior que zero."
            )
            return
        
        resultado = self.inventario_service.adicionar_dados_fornecedor(
            tipo_fornecedor, 
            tipo_caixa, 
            quantidade
        )
        
        if resultado['status']:
            QMessageBox.information(
                self, 
                "Sucesso", 
                resultado['message']
            )
            
            # Limpar campos
            self.sp_quantidade_fornecedor.setValue(0)
            
            # Emitir sinal de dados atualizados
            if hasattr(self.parent(), 'atualizar_dados'):
                self.parent().atualizar_dados()
        else:
            QMessageBox.warning(
                self, 
                "Erro", 
                resultado['message']
            )
    
    def adicionar_contagem_loja(self):
        """Adiciona contagem manual para uma loja específica"""
        loja = self.cb_loja.currentData()  # Nome da loja armazenado como userData
        tipo_caixa = self.cb_tipo_caixa_loja.currentData()
        quantidade = self.sp_quantidade_loja.value()
        finalizar = self.chk_finalizar_loja.isChecked()
        
        if not loja:
            QMessageBox.warning(
                self, 
                "Atenção", 
                "Selecione uma loja ou CD válido."
            )
            return
        
        if quantidade <= 0:
            QMessageBox.warning(
                self, 
                "Atenção", 
                "A quantidade deve ser maior que zero."
            )
            return
        
        # Verificar se o inventário_service tem um método para esta funcionalidade
        # Se não, precisaremos implementá-lo
        resultado = self.inventario_service.adicionar_contagem_loja_manual(
            loja, 
            tipo_caixa, 
            quantidade,
            finalizar
        )
        
        if resultado['status']:
            QMessageBox.information(
                self, 
                "Sucesso", 
                resultado['message']
            )
            
            # Limpar campos
            self.sp_quantidade_loja.setValue(0)
            self.chk_finalizar_loja.setChecked(False)
            
            # Emitir sinal de dados atualizados
            if hasattr(self.parent(), 'atualizar_dados'):
                self.parent().atualizar_dados()
        else:
            QMessageBox.warning(
                self, 
                "Erro", 
                resultado['message']
            )
    
    def adicionar_dados_transito(self):
        """Adiciona dados de trânsito ao inventário"""
        tipo_transito = self.cb_tipo_transito.currentText()
        tipo_caixa = self.cb_tipo_caixa_transito.currentData()
        quantidade = self.sp_quantidade_transito.value()
        
        if quantidade <= 0:
            QMessageBox.warning(
                self, 
                "Atenção", 
                "A quantidade deve ser maior que zero."
            )
            return
        
        # Verificar se o inventário_service tem um método para esta funcionalidade
        # Se não, precisaremos implementá-lo
        resultado = self.inventario_service.adicionar_dados_transito_manual(
            tipo_transito,
            tipo_caixa, 
            quantidade
        )
        
        if resultado['status']:
            QMessageBox.information(
                self, 
                "Sucesso", 
                resultado['message']
            )
            
            # Limpar campos
            self.sp_quantidade_transito.setValue(0)
            
            # Emitir sinal de dados atualizados
            if hasattr(self.parent(), 'atualizar_dados'):
                self.parent().atualizar_dados()
        else:
            QMessageBox.warning(
                self, 
                "Erro", 
                resultado['message']
            )