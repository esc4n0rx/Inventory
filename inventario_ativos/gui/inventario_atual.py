# gui/inventario_atual.py
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QSpinBox
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


class FormularioFornecedorWidget(QWidget):
    """Widget para adicionar dados de fornecedor"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Grupo para o formulário
        grupo = QGroupBox("Adicionar Dados de Fornecedor")
        form_layout = QFormLayout(grupo)
        
        # Campos do formulário
        self.cb_fornecedor = QComboBox()
        self.cb_fornecedor.addItems(self.inventario_service.get_tipos_fornecedor())
        form_layout.addRow("Fornecedor:", self.cb_fornecedor)
        
        self.cb_tipo_caixa = QComboBox()
        self.atualizar_tipos_caixa()
        form_layout.addRow("Tipo de Caixa:", self.cb_tipo_caixa)
        
        self.sp_quantidade = QSpinBox()
        self.sp_quantidade.setMinimum(0)
        self.sp_quantidade.setMaximum(999999)
        form_layout.addRow("Quantidade:", self.sp_quantidade)
        
        # Botão para adicionar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_adicionar.clicked.connect(self.adicionar_dados)
        btn_layout.addWidget(self.btn_adicionar)
        
        form_layout.addRow("", btn_layout)
        
        layout.addWidget(grupo)
        layout.addStretch()
    
    def atualizar_tipos_caixa(self):
        """Atualiza a lista de tipos de caixa"""
        self.cb_tipo_caixa.clear()
        
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
            self.cb_tipo_caixa.addItem(nomes_tipos.get(tipo, tipo), tipo)
    
    def adicionar_dados(self):
        """Adiciona os dados de fornecedor ao inventário"""
        tipo_fornecedor = self.cb_fornecedor.currentText()
        tipo_caixa = self.cb_tipo_caixa.currentData()
        quantidade = self.sp_quantidade.value()
        
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
            self.sp_quantidade.setValue(0)
            
            # Emitir sinal de dados atualizados
            if hasattr(self.parent(), 'atualizar_dados'):
                self.parent().atualizar_dados()
        else:
            QMessageBox.warning(
                self, 
                "Erro", 
                resultado['message']
            )


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
        
        # Coluna direita: Formulário para adicionar dados de fornecedor
        self.formulario_fornecedor = FormularioFornecedorWidget(inventario_service)
        layout.addWidget(self.formulario_fornecedor, 1)  # Peso 1 para o formulário
    
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