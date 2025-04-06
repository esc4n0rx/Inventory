# gui/atualizacao.py
import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QFormLayout, QLineEdit,
    QFileDialog, QTextEdit, QMessageBox, QCheckBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
import time

class CaminhosArquivosWidget(QWidget):
    """Widget para configurar caminhos de arquivos"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Grupo para configuração de caminhos
        grupo = QGroupBox("Caminhos dos Arquivos CSV")
        form_layout = QFormLayout(grupo)
        
        # Caminho do arquivo de lojas
        self.txt_lojas = QLineEdit()
        self.txt_lojas.setText(self.inventario_service.csv_manager.csv_lojas_path)
        btn_lojas = QPushButton("...")
        btn_lojas.setMaximumWidth(30)
        btn_lojas.clicked.connect(lambda: self.selecionar_arquivo("lojas"))
        
        lojas_layout = QHBoxLayout()
        lojas_layout.addWidget(self.txt_lojas)
        lojas_layout.addWidget(btn_lojas)
        form_layout.addRow("Arquivo de Lojas:", lojas_layout)
        
        # Caminho do arquivo de setores
        self.txt_setores = QLineEdit()
        self.txt_setores.setText(self.inventario_service.csv_manager.csv_setores_path)
        btn_setores = QPushButton("...")
        btn_setores.setMaximumWidth(30)
        btn_setores.clicked.connect(lambda: self.selecionar_arquivo("setores"))
        
        setores_layout = QHBoxLayout()
        setores_layout.addWidget(self.txt_setores)
        setores_layout.addWidget(btn_setores)
        form_layout.addRow("Arquivo de Setores:", setores_layout)
        
        # Caminho do arquivo de contagem de lojas
        self.txt_contagem_lojas = QLineEdit()
        self.txt_contagem_lojas.setText(self.inventario_service.csv_manager.csv_contagem_lojas_path)
        btn_contagem_lojas = QPushButton("...")
        btn_contagem_lojas.setMaximumWidth(30)
        btn_contagem_lojas.clicked.connect(lambda: self.selecionar_arquivo("contagem_lojas"))
        
        contagem_lojas_layout = QHBoxLayout()
        contagem_lojas_layout.addWidget(self.txt_contagem_lojas)
        contagem_lojas_layout.addWidget(btn_contagem_lojas)
        form_layout.addRow("Contagem de Lojas:", contagem_lojas_layout)
        
        # Caminho do arquivo de contagem de CD
        self.txt_contagem_cd = QLineEdit()
        self.txt_contagem_cd.setText(self.inventario_service.csv_manager.csv_contagem_cd_path)
        btn_contagem_cd = QPushButton("...")
        btn_contagem_cd.setMaximumWidth(30)
        btn_contagem_cd.clicked.connect(lambda: self.selecionar_arquivo("contagem_cd"))
        
        contagem_cd_layout = QHBoxLayout()
        contagem_cd_layout.addWidget(self.txt_contagem_cd)
        contagem_cd_layout.addWidget(btn_contagem_cd)
        form_layout.addRow("Contagem de CD:", contagem_cd_layout)
        
        # Caminho do arquivo de dados em trânsito
        self.txt_dados_transito = QLineEdit()
        self.txt_dados_transito.setText(self.inventario_service.csv_manager.csv_dados_transito_path)
        btn_dados_transito = QPushButton("...")
        btn_dados_transito.setMaximumWidth(30)
        btn_dados_transito.clicked.connect(lambda: self.selecionar_arquivo("dados_transito"))
        
        dados_transito_layout = QHBoxLayout()
        dados_transito_layout.addWidget(self.txt_dados_transito)
        dados_transito_layout.addWidget(btn_dados_transito)
        form_layout.addRow("Dados em Trânsito:", dados_transito_layout)
        
        # Botão para salvar configurações
        btn_salvar = QPushButton("Salvar Configurações")
        btn_salvar.clicked.connect(self.salvar_configuracoes)
        form_layout.addRow("", btn_salvar)
        
        layout.addWidget(grupo)
    
    def selecionar_arquivo(self, tipo):
        """Abre diálogo para selecionar arquivo"""
        opcoes = QFileDialog.Options()
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            f"Selecionar Arquivo {tipo.capitalize()}",
            "",
            "Arquivos CSV (*.csv);;Todos os Arquivos (*)",
            options=opcoes
        )
        
        if arquivo:
            if tipo == "lojas":
                self.txt_lojas.setText(arquivo)
            elif tipo == "setores":
                self.txt_setores.setText(arquivo)
            elif tipo == "contagem_lojas":
                self.txt_contagem_lojas.setText(arquivo)
            elif tipo == "contagem_cd":
                self.txt_contagem_cd.setText(arquivo)
            elif tipo == "dados_transito":
                self.txt_dados_transito.setText(arquivo)
    
    def salvar_configuracoes(self):
        """Salva as configurações de caminhos"""
        resultado = self.inventario_service.configurar_caminhos_csv(
            self.txt_lojas.text(),
            self.txt_setores.text(),
            self.txt_contagem_lojas.text(),
            self.txt_contagem_cd.text(),
            self.txt_dados_transito.text()
        )
        
        if resultado['status']:
            QMessageBox.information(
                self,
                "Sucesso",
                "Configurações salvas com sucesso!"
            )
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Erro ao salvar configurações: {resultado['message']}"
            )


class AtualizacaoWidget(QWidget):
    """Widget principal para a aba de Atualização"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QHBoxLayout(self)
        
        # Coluna esquerda: Configuração de caminhos
        self.caminhos_widget = CaminhosArquivosWidget(inventario_service)
        layout.addWidget(self.caminhos_widget)
        
        # Coluna direita: Importação de dados
        self.importacao_widget = ImportacaoDadosWidget(inventario_service)
        layout.addWidget(self.importacao_widget)
        
        # Configurar atualização automática
        self.timer_atualizacao = QTimer(self)
        self.timer_atualizacao.timeout.connect(self.verificar_arquivos_modificados)
        
        # Inicialmente desligado, será ligado quando o widget for mostrado
        self.atualizar_timer()
    
    def showEvent(self, event):
        """Evento chamado quando o widget é mostrado"""
        super().showEvent(event)
        # Ativar timer quando widget for exibido
        self.atualizar_timer()
    
    def hideEvent(self, event):
        """Evento chamado quando o widget é escondido"""
        super().hideEvent(event)
        # Parar timer quando widget for escondido
        self.timer_atualizacao.stop()
    
    def atualizar_timer(self):
        """Atualiza o timer baseado na configuração de atualização automática"""
        if self.importacao_widget.chk_auto_atualizar.isChecked():
            intervalo = self.importacao_widget.sp_intervalo.value() * 1000  # converter para milissegundos
            self.timer_atualizacao.start(intervalo)
        else:
            self.timer_atualizacao.stop()
    
    def verificar_arquivos_modificados(self):
        """Verifica se os arquivos CSV foram modificados e importa se necessário"""
        if not self.inventario_service.inventario_atual:
            # Se não houver inventário ativo, não fazer nada
            return
        
        try:
            # Forçar verificação de modificações nos arquivos
            resultado = self.inventario_service.importar_dados_csv_silencioso()
            
            # Se algum arquivo foi modificado, atualizar a interface
            if resultado.get('modified', False):
                # Emitir sinal de dados atualizados
                if hasattr(self.parent(), 'atualizar_dados'):
                    self.parent().atualizar_dados()
                
                # Atualizar o log
                self.importacao_widget.adicionar_log(
                    f"✅ Atualização automática: {resultado.get('message', 'Arquivos atualizados')}"
                )
        except Exception as e:
            # Em caso de erro, apenas registrar no log, sem mostrar mensagens de erro
            self.importacao_widget.adicionar_log(f"❌ Erro na atualização automática: {str(e)}")
    
    def atualizar_dados(self):
        """Atualiza os widgets com as configurações atuais"""
        # Atualizar campos de texto com os caminhos atuais
        self.caminhos_widget.txt_lojas.setText(self.inventario_service.csv_manager.csv_lojas_path)
        self.caminhos_widget.txt_setores.setText(self.inventario_service.csv_manager.csv_setores_path)
        self.caminhos_widget.txt_contagem_lojas.setText(self.inventario_service.csv_manager.csv_contagem_lojas_path)
        self.caminhos_widget.txt_contagem_cd.setText(self.inventario_service.csv_manager.csv_contagem_cd_path)
        self.caminhos_widget.txt_dados_transito.setText(self.inventario_service.csv_manager.csv_dados_transito_path)


# Modificar a classe ImportacaoDadosWidget para incluir opções de atualização automática:
class ImportacaoDadosWidget(QWidget):
    """Widget para importação de dados CSV"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Grupo para importação
        grupo = QGroupBox("Importação de Dados")
        importacao_layout = QVBoxLayout(grupo)
        
        # Botão para atualizar dados
        self.btn_atualizar = QPushButton("Atualizar Dados dos CSVs")
        self.btn_atualizar.setMinimumHeight(50)
        self.btn_atualizar.clicked.connect(self.importar_dados)
        importacao_layout.addWidget(self.btn_atualizar)
        
        # Opções de atualização automática
        auto_layout = QHBoxLayout()
        
        self.chk_auto_atualizar = QCheckBox("Atualização Automática")
        self.chk_auto_atualizar.setChecked(True)
        self.chk_auto_atualizar.stateChanged.connect(self.toggle_auto_atualizacao)
        auto_layout.addWidget(self.chk_auto_atualizar)
        
        auto_layout.addWidget(QLabel("Intervalo (segundos):"))
        
        self.sp_intervalo = QSpinBox()
        self.sp_intervalo.setMinimum(5)  # Mínimo de 5 segundos
        self.sp_intervalo.setMaximum(300)  # Máximo de 5 minutos
        self.sp_intervalo.setValue(30)  # Padrão de 30 segundos
        self.sp_intervalo.valueChanged.connect(self.atualizar_intervalo)
        auto_layout.addWidget(self.sp_intervalo)
        
        importacao_layout.addLayout(auto_layout)
        
        # Informações sobre a importação
        importacao_layout.addWidget(QLabel("Ao clicar em 'Atualizar Dados', o sistema irá:"))
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setPlainText(
            "1. Ler os arquivos CSV configurados\n"
            "2. Importar os dados para o banco de dados\n"
            "3. Vincular os dados ao inventário atual\n"
            "4. Manter os dados antigos caso não sejam sobrescritos"
        )
        importacao_layout.addWidget(info_text)
        
        # Log de importação
        importacao_layout.addWidget(QLabel("Log de Importação:"))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlainText("Nenhuma importação realizada.")
        importacao_layout.addWidget(self.log_text)
        
        layout.addWidget(grupo)
        
        # Grupo para criar CSVs padrão
        grupo_padrao = QGroupBox("Criar Arquivos CSV Padrão")
        padrao_layout = QVBoxLayout(grupo_padrao)
        
        info_padrao = QLabel(
            "Caso não possua os arquivos CSV necessários, você pode criar "
            "versões padrão destes arquivos nos caminhos configurados."
        )
        info_padrao.setWordWrap(True)
        padrao_layout.addWidget(info_padrao)
        
        btn_criar_padrao = QPushButton("Criar CSVs Padrão")
        btn_criar_padrao.clicked.connect(self.criar_csv_padrao)
        padrao_layout.addWidget(btn_criar_padrao)
        
        layout.addWidget(grupo_padrao)
    
    def toggle_auto_atualizacao(self, state):
        """Ativa ou desativa a atualização automática"""
        # Notificar o widget pai para atualizar o timer
        if hasattr(self.parent(), 'atualizar_timer'):
            self.parent().atualizar_timer()
    
    def atualizar_intervalo(self, value):
        """Atualiza o intervalo de atualização automática"""
        # Notificar o widget pai para atualizar o timer
        if hasattr(self.parent(), 'atualizar_timer'):
            self.parent().atualizar_timer()
    
    def importar_dados(self):
        """Importa dados dos arquivos CSV"""
        if not self.inventario_service.inventario_atual:
            QMessageBox.warning(
                self,
                "Erro",
                "Nenhum inventário ativo. Inicie um novo inventário ou carregue um existente."
            )
            return
        
        # Confirmar com o usuário
        resp = QMessageBox.question(
            self,
            "Importar Dados",
            "Tem certeza que deseja importar os dados dos arquivos CSV?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resp != QMessageBox.Yes:
            return
        
        # Importar dados
        resultado = self.inventario_service.importar_dados_csv()
        
        # Atualizar log
        self.atualizar_log(resultado)
        
        # Exibir mensagem
        if resultado['status']:
            QMessageBox.information(
                self,
                "Sucesso",
                "Dados importados com sucesso!"
            )
            
            # Emitir sinal de dados atualizados
            if hasattr(self.parent().parent(), 'atualizar_dados'):
                self.parent().parent().atualizar_dados()
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Erro ao importar dados: {resultado['message']}"
            )
    
    def atualizar_log(self, resultado):
        """Atualiza o log com o resultado da importação"""
        log = "=== Resultado da Importação ===\n"
        log += f"Status: {'Sucesso' if resultado['status'] else 'Erro'}\n"
        log += f"Mensagem: {resultado['message']}\n\n"
        
        # Adicionar detalhes de cada tipo de importação
        if 'resultados' in resultado:
            log += "=== Detalhes ===\n"
            
            # Contagem de lojas
            res_lojas = resultado['resultados']['contagem_lojas']
            log += f"Contagem de Lojas: {'Sucesso' if res_lojas['status'] else 'Erro'}\n"
            log += f"  {res_lojas['message']}\n"
            
            # Contagem de CD
            res_cd = resultado['resultados']['contagem_cd']
            log += f"Contagem de CD: {'Sucesso' if res_cd['status'] else 'Erro'}\n"
            log += f"  {res_cd['message']}\n"
            
            # Dados em trânsito
            res_transito = resultado['resultados']['dados_transito']
            log += f"Dados em Trânsito: {'Sucesso' if res_transito['status'] else 'Erro'}\n"
            log += f"  {res_transito['message']}\n"
        
        self.log_text.setPlainText(log)
    
    def adicionar_log(self, mensagem):
        """Adiciona uma mensagem ao log"""
        texto_atual = self.log_text.toPlainText()
        timestamp = time.strftime('%H:%M:%S')
        nova_mensagem = f"[{timestamp}] {mensagem}"
        
        # Adicionar nova mensagem no início
        novo_texto = nova_mensagem + "\n" + texto_atual
        
        # Limitar o tamanho do log (opcional)
        linhas = novo_texto.splitlines()
        if len(linhas) > 100:  # Manter apenas as 100 linhas mais recentes
            novo_texto = "\n".join(linhas[:100])
        
        self.log_text.setPlainText(novo_texto)
    
    def criar_csv_padrao(self):
        """Cria arquivos CSV padrão"""
        # Confirmar com o usuário
        resp = QMessageBox.question(
            self,
            "Criar CSVs Padrão",
            "Isso irá criar arquivos CSV padrão nos caminhos configurados.\n"
            "Arquivos existentes não serão sobrescritos.\n\n"
            "Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resp != QMessageBox.Yes:
            return
        
        # Criar arquivos
        resultado = self.inventario_service.criar_csv_padrao()
        
        if resultado['status']:
            QMessageBox.information(
                self,
                "Sucesso",
                "Arquivos CSV padrão criados com sucesso!"
            )
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Erro ao criar arquivos CSV padrão: {resultado['message']}"
            )