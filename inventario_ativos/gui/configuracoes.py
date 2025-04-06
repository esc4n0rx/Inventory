# gui/configuracoes.py
import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QGroupBox, QFormLayout,
    QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BancoDadosWidget(QWidget):
    """Widget para configurações e manutenção do banco de dados"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Grupo para informações do banco
        grupo_info = QGroupBox("Informações do Banco de Dados")
        info_layout = QFormLayout(grupo_info)
        
        # Caminho do banco
        self.lbl_caminho = QLabel(self.inventario_service.db_manager.db_file)
        info_layout.addRow("Caminho:", self.lbl_caminho)
        
        # Total de inventários
        self.lbl_total_inventarios = QLabel("Carregando...")
        info_layout.addRow("Total de Inventários:", self.lbl_total_inventarios)
        
        layout.addWidget(grupo_info)
        
        # Grupo para manutenção
        grupo_manutencao = QGroupBox("Manutenção do Banco de Dados")
        manutencao_layout = QVBoxLayout(grupo_manutencao)
        
        # Botão para backup
        btn_backup = QPushButton("Realizar Backup")
        btn_backup.clicked.connect(self.realizar_backup)
        manutencao_layout.addWidget(btn_backup)
        
        # Aviso sobre backup
        lbl_aviso = QLabel(
            "O backup irá criar uma cópia do arquivo de banco de dados.\n"
            "Recomenda-se fazer backups regularmente."
        )
        lbl_aviso.setWordWrap(True)
        manutencao_layout.addWidget(lbl_aviso)
        
        layout.addWidget(grupo_manutencao)
        
        # Adicionar espaçador
        layout.addStretch()
    
    def atualizar_dados(self):
        """Atualiza as informações do widget"""
        # Atualizar caminho do banco
        self.lbl_caminho.setText(self.inventario_service.db_manager.db_file)
        
        # Contar inventários
        inventarios = self.inventario_service.get_inventarios_disponiveis()
        self.lbl_total_inventarios.setText(str(len(inventarios)))
    
    def realizar_backup(self):
        """Realiza backup do banco de dados"""
        try:
            # Obter caminho para o backup
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Backup",
                f"{os.path.splitext(self.inventario_service.db_manager.db_file)[0]}_backup.db",
                "Arquivos SQLite (*.db);;Todos os Arquivos (*)"
            )
            
            if not caminho:
                return
            
            # Fechar conexão com o banco para permitir cópia
            self.inventario_service.db_manager.close_connection()
            
            # Copiar arquivo
            import shutil
            shutil.copy2(
                self.inventario_service.db_manager.db_file,
                caminho
            )
            
            QMessageBox.information(
                self,
                "Backup Realizado",
                f"Backup realizado com sucesso!\nCaminho: {caminho}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Erro ao realizar backup: {str(e)}"
            )
        finally:
            # Reabrir conexão
            self.inventario_service.db_manager.get_connection()


class InventariosTableWidget(QWidget):
    """Widget para exibir e gerenciar inventários"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Tabela de inventários
        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Data Início", "Data Fim", "Status", "Descrição"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        btn_layout = QHBoxLayout()
        
        self.btn_atualizar = QPushButton("Atualizar Lista")
        self.btn_atualizar.clicked.connect(self.atualizar_dados)
        btn_layout.addWidget(self.btn_atualizar)
        
        btn_layout.addStretch()
        
        self.btn_exportar = QPushButton("Exportar Relatório")
        self.btn_exportar.clicked.connect(self.exportar_relatorio)
        btn_layout.addWidget(self.btn_exportar)
        
        layout.addLayout(btn_layout)
    
    def atualizar_dados(self):
        """Atualiza a tabela com a lista de inventários"""
        # Limpar tabela
        self.tabela.setRowCount(0)
        
        # Obter todos os inventários
        inventarios = self.inventario_service.get_inventarios_disponiveis()
        
        # Preencher tabela
        for i, inv in enumerate(inventarios):
            self.tabela.insertRow(i)
            
            # Código
            self.tabela.setItem(i, 0, QTableWidgetItem(inv['cod_inventario']))
            
            # Data de início
            data_inicio = inv['data_inicio'].split('T')[0] if 'T' in inv['data_inicio'] else inv['data_inicio']
            self.tabela.setItem(i, 1, QTableWidgetItem(data_inicio))
            
            # Data de fim
            data_fim = "-"
            if inv['data_fim']:
                data_fim = inv['data_fim'].split('T')[0] if 'T' in inv['data_fim'] else inv['data_fim']
            self.tabela.setItem(i, 2, QTableWidgetItem(data_fim))
            
            # Status
            status = "Em andamento" if inv['status'] == 'em_andamento' else "Finalizado"
            self.tabela.setItem(i, 3, QTableWidgetItem(status))
            
            # Descrição
            self.tabela.setItem(i, 4, QTableWidgetItem(inv['descricao'] or ""))
    
    def exportar_relatorio(self):
        """Exporta relatório do inventário selecionado"""
        # Verificar se há linha selecionada
        indices = self.tabela.selectedIndexes()
        if not indices:
            QMessageBox.warning(
                self,
                "Seleção Necessária",
                "Selecione um inventário na tabela para exportar seu relatório."
            )
            return
        
        # Obter código do inventário selecionado
        linha = indices[0].row()
        cod_inventario = self.tabela.item(linha, 0).text()
        
        # Verificar se o inventário está finalizado
        status = self.tabela.item(linha, 3).text()
        
        # Perguntar onde salvar o relatório
        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"relatorio_{cod_inventario}.csv",
            "Arquivos CSV (*.csv)"
        )
        
        if not caminho:
            return
        
        # Se o inventário selecionado é o atual, usar o método do inventário atual
        if cod_inventario == self.inventario_service.inventario_atual:
            resultado = self.inventario_service.exportar_relatorio_atual(caminho)
        else:
            # Caso contrário, criar um serviço temporário
            resultado = self.inventario_service.csv_manager.exportar_relatorio_inventario(
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


class ConfiguracoesWidget(QWidget):
    """Widget principal para a aba de Configurações"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Abas de configuração
        tab_widget = QTabWidget()
        
        # Aba de Banco de Dados
        self.banco_widget = BancoDadosWidget(inventario_service)
        tab_widget.addTab(self.banco_widget, "Banco de Dados")
        
        # Aba de Inventários
        self.inventarios_widget = InventariosTableWidget(inventario_service)
        tab_widget.addTab(self.inventarios_widget, "Inventários")
        
        # Nova aba de Manutenção
        self.manutencao_widget = ManutencaoWidget(inventario_service)
        tab_widget.addTab(self.manutencao_widget, "Manutenção")
        
        layout.addWidget(tab_widget)
    
    def atualizar_dados(self):
        """Atualiza todos os widgets de configuração"""
        self.banco_widget.atualizar_dados()
        self.inventarios_widget.atualizar_dados()


class ManutencaoWidget(QWidget):
    """Widget para integrar as funções de manutenção do sistema"""
    def __init__(self, inventario_service, parent=None):
        super().__init__(parent)
        self.inventario_service = inventario_service
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Grupo para opções de manutenção
        grupo_manutencao = QGroupBox("Operações de Manutenção")
        operacoes_layout = QVBoxLayout(grupo_manutencao)
        
        # Descrição
        lbl_descricao = QLabel(
            "Esta seção permite executar operações de manutenção no sistema. "
            "Selecione a operação desejada e clique em 'Executar'."
        )
        lbl_descricao.setWordWrap(True)
        operacoes_layout.addWidget(lbl_descricao)
        
        # Combobox para escolher a operação
        self.cb_operacao = QComboBox()
        self.cb_operacao.addItems([
            "Mostrar informações do banco de dados",
            "Listar lojas e setores dos CSVs",
            "Criar lojas e setores pendentes (do CSV)",
            "Atualizar status de todos registros para 'finalizado'",
            "Corrigir cálculo de totais"
        ])
        operacoes_layout.addWidget(self.cb_operacao)
        
        # Botão para executar
        btn_executar = QPushButton("Executar Operação")
        btn_executar.clicked.connect(self.executar_operacao)
        operacoes_layout.addWidget(btn_executar)
        
        layout.addWidget(grupo_manutencao)
        
        # Área de log para mostrar resultados
        grupo_log = QGroupBox("Log de Operações")
        log_layout = QVBoxLayout(grupo_log)
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMinimumHeight(300)
        log_layout.addWidget(self.txt_log)
        
        # Botões para o log
        log_btn_layout = QHBoxLayout()
        
        btn_limpar_log = QPushButton("Limpar Log")
        btn_limpar_log.clicked.connect(self.limpar_log)
        log_btn_layout.addWidget(btn_limpar_log)
        
        log_layout.addLayout(log_btn_layout)
        
        layout.addWidget(grupo_log)
    
    def executar_operacao(self):
        """Executa a operação selecionada"""
        # Verificar se o usuário realmente deseja executar a operação
        resposta = QMessageBox.question(
            self,
            "Confirmar Operação",
            f"Deseja realmente executar a operação: '{self.cb_operacao.currentText()}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta != QMessageBox.Yes:
            return
        
        # Importar módulos necessários diretamente em vez do script
        try:
            from database.database_manager import DatabaseManager
            from import_export.csv_manager import CSVManager
            import datetime
            import shutil
            import os
            import re
            
            # Obter instâncias dos gerenciadores
            db_manager = DatabaseManager()
            csv_manager = CSVManager(db_manager)
            
            # Executar a operação correspondente
            operacao_indice = self.cb_operacao.currentIndex()
            
            if operacao_indice == 0:
                # Mostrar informações do banco de dados
                self.mostrar_info_banco(db_manager)
            elif operacao_indice == 1:
                # Listar lojas e setores dos CSVs
                self.listar_csv(csv_manager)
            elif operacao_indice == 2:
                # Criar lojas e setores pendentes (do CSV)
                self.criar_lojas_setores(db_manager, csv_manager)
            elif operacao_indice == 3:
                # Atualizar status para 'finalizado'
                self.atualizar_status(db_manager)
            elif operacao_indice == 4:
                # Corrigir cálculo de totais
                self.corrigir_totais()
                
        except Exception as e:
            self.adicionar_log(f"Erro ao executar operação: {str(e)}")
            import traceback
            self.adicionar_log(traceback.format_exc())
    
    def mostrar_info_banco(self, db_manager):
        """Mostra informações do banco de dados"""
        self.adicionar_log("INFORMAÇÕES DO BANCO DE DADOS\n" + "="*50)
        
        # Obter informações básicas
        self.adicionar_log(f"Arquivo de banco de dados: {db_manager.db_file}")
        
        # Obter inventários
        inventarios = db_manager.get_todos_inventarios()
        self.adicionar_log(f"\nTotal de inventários: {len(inventarios)}")
        
        # Mostrar detalhes de cada inventário
        for i, inv in enumerate(inventarios):
            self.adicionar_log(f"\nInventário {i+1}:")
            self.adicionar_log(f"  Código: {inv['cod_inventario']}")
            self.adicionar_log(f"  Status: {inv['status']}")
            self.adicionar_log(f"  Data de início: {inv['data_inicio'][:19]}")
            
            # Contar registros
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            # Contar lojas
            cursor.execute('''
            SELECT COUNT(*) as total_lojas,
                   SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as lojas_finalizadas
            FROM contagem_lojas
            WHERE cod_inventario = ?
            ''', (inv['cod_inventario'],))
            
            lojas = cursor.fetchone()
            total_lojas = lojas['total_lojas'] if lojas and 'total_lojas' in lojas else 0
            lojas_finalizadas = lojas['lojas_finalizadas'] if lojas and 'lojas_finalizadas' in lojas else 0
            
            # Contar setores
            cursor.execute('''
            SELECT COUNT(*) as total_setores,
                   SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as setores_finalizados
            FROM contagem_cd
            WHERE cod_inventario = ?
            ''', (inv['cod_inventario'],))
            
            setores = cursor.fetchone()
            total_setores = setores['total_setores'] if setores and 'total_setores' in setores else 0
            setores_finalizados = setores['setores_finalizados'] if setores and 'setores_finalizados' in setores else 0
            
            self.adicionar_log(f"  Lojas: {total_lojas} total, {lojas_finalizadas} finalizadas")
            self.adicionar_log(f"  Setores do CD: {total_setores} total, {setores_finalizados} finalizados")
    
    def listar_csv(self, csv_manager):
        """Lista lojas e setores dos CSVs"""
        self.adicionar_log("LOJAS E SETORES DOS ARQUIVOS CSV\n" + "="*50)
        
        # Listar caminhos
        self.adicionar_log(f"CSV de lojas: {csv_manager.csv_lojas_path}")
        self.adicionar_log(f"CSV de setores: {csv_manager.csv_setores_path}")
        
        # Ler CSVs
        lojas = csv_manager.ler_lojas_csv(force_reload=True)
        setores = csv_manager.ler_setores_csv(force_reload=True)
        
        # Mostrar lojas
        self.adicionar_log(f"\nLojas no CSV: {len(lojas)}")
        if lojas:
            self.adicionar_log("\nPrimeiras 10 lojas:")
            for i, loja in enumerate(lojas[:10]):
                self.adicionar_log(f"  {i+1}. {loja.get('loja', '???')} - Regional: {loja.get('regional', '???')}")
        
        # Mostrar setores
        self.adicionar_log(f"\nSetores no CSV: {len(setores)}")
        if setores:
            self.adicionar_log("\nPrimeiros 10 setores:")
            for i, setor in enumerate(setores[:10]):
                self.adicionar_log(f"  {i+1}. {setor.get('setor', '???')} - {setor.get('descricao', '???')}")
    
    def criar_lojas_setores(self, db_manager, csv_manager):
        """Cria registros para lojas e setores pendentes"""
        self.adicionar_log("CRIAR LOJAS E SETORES PENDENTES\n" + "="*50)
        
        # Listar inventários ativos
        inventarios_ativos = db_manager.get_inventarios_ativos()
        
        if not inventarios_ativos:
            self.adicionar_log("❌ Não há inventários ativos. Crie um novo inventário no sistema principal.")
            return
        
        # Mostrar diálogo de seleção de inventário
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Inventário")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Selecione o inventário:"))
        
        combo = QComboBox()
        for inv in inventarios_ativos:
            combo.addItem(f"{inv['cod_inventario']} - {inv['data_inicio'][:10]}", inv['cod_inventario'])
        
        layout.addWidget(combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Executar diálogo
        if dialog.exec_() != QDialog.Accepted:
            self.adicionar_log("Operação cancelada.")
            return
        
        # Processar inventário selecionado
        cod_inventario = combo.currentData()
        
        self.adicionar_log(f"\nProcessando inventário: {cod_inventario}")
        
        # Ler CSVs
        lojas_csv = csv_manager.ler_lojas_csv(force_reload=True)
        setores_csv = csv_manager.ler_setores_csv(force_reload=True)
        
        # Obter lojas e setores atuais no banco
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT loja FROM contagem_lojas WHERE cod_inventario = ?', (cod_inventario,))
        lojas_banco = [row['loja'] for row in cursor.fetchall()]
        
        cursor.execute('SELECT setor FROM contagem_cd WHERE cod_inventario = ?', (cod_inventario,))
        setores_banco = [row['setor'] for row in cursor.fetchall()]
        
        # Calcular lojas e setores faltantes
        lojas_faltantes = [loja.get('loja') for loja in lojas_csv if loja.get('loja') not in lojas_banco]
        setores_faltantes = [setor.get('setor') for setor in setores_csv if setor.get('setor') not in setores_banco]
        
        self.adicionar_log(f"\nLojas no CSV: {len(lojas_csv)}")
        self.adicionar_log(f"Lojas no banco: {len(lojas_banco)}")
        self.adicionar_log(f"Lojas faltantes: {len(lojas_faltantes)}")
        
        self.adicionar_log(f"\nSetores no CSV: {len(setores_csv)}")
        self.adicionar_log(f"Setores no banco: {len(setores_banco)}")
        self.adicionar_log(f"Setores faltantes: {len(setores_faltantes)}")
        
        if not lojas_faltantes and not setores_faltantes:
            self.adicionar_log("\n✅ Não há lojas ou setores faltantes para criar.")
            return
        
        # Confirmar criação
        resposta = QMessageBox.question(
            self,
            "Criar Registros",
            f"Deseja criar {len(lojas_faltantes)} lojas e {len(setores_faltantes)} setores faltantes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta != QMessageBox.Yes:
            self.adicionar_log("Operação cancelada.")
            return
        
        # Criar registros faltantes
        timestamp = datetime.datetime.now().isoformat()
        lojas_criadas = 0
        setores_criados = 0
        
        # Mapear regionais por loja
        regionais = {loja.get('loja'): loja.get('regional', '') for loja in lojas_csv if loja.get('loja')}
        
        # Criar lojas faltantes
        for loja in lojas_faltantes:
            if not loja:
                continue
            
            regional = regionais.get(loja, '')
            
            try:
                cursor.execute('''
                INSERT INTO contagem_lojas (
                    loja, regional, setor, data, status, 
                    caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                    caixa_chocolate, caixa_bin, pallets_pbr,
                    usuario, created_at, updated_at, cod_inventario
                ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?, ?, ?)
                ''', (
                    loja, regional, 'Geral', timestamp, 'pendente', 
                    'sistema', timestamp, timestamp, cod_inventario
                ))
                lojas_criadas += 1
            except Exception as e:
                self.adicionar_log(f"Erro ao criar loja {loja}: {str(e)}")
        
        # Criar setores faltantes
        for setor in setores_faltantes:
            if not setor:
                continue
            
            try:
                cursor.execute('''
                INSERT INTO contagem_cd (
                    setor, data, status, 
                    caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                    caixa_chocolate, caixa_bin, pallets_pbr,
                    usuario, created_at, updated_at, cod_inventario
                ) VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, 0, ?, ?, ?, ?)
                ''', (
                    setor, timestamp, 'pendente', 
                    'sistema', timestamp, timestamp, cod_inventario
                ))
                setores_criados += 1
            except Exception as e:
                self.adicionar_log(f"Erro ao criar setor {setor}: {str(e)}")
        
        conn.commit()
        
        self.adicionar_log(f"\n✅ Operação concluída. Criados {lojas_criadas} lojas e {setores_criados} setores.")
    
    def atualizar_status(self, db_manager):
        """Atualiza o status de todos os registros para 'finalizado'"""
        self.adicionar_log("ATUALIZAR STATUS PARA 'FINALIZADO'\n" + "="*50)
        
        # Listar inventários ativos
        inventarios_ativos = db_manager.get_inventarios_ativos()
        
        if not inventarios_ativos:
            self.adicionar_log("❌ Não há inventários ativos. Crie um novo inventário no sistema principal.")
            return
        
        # Mostrar diálogo de seleção de inventário
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Inventário")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Selecione o inventário:"))
        
        combo = QComboBox()
        for inv in inventarios_ativos:
            combo.addItem(f"{inv['cod_inventario']} - {inv['data_inicio'][:10]}", inv['cod_inventario'])
        
        layout.addWidget(combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Executar diálogo
        if dialog.exec_() != QDialog.Accepted:
            self.adicionar_log("Operação cancelada.")
            return
        
        # Processar inventário selecionado
        cod_inventario = combo.currentData()
        
        self.adicionar_log(f"\nProcessando inventário: {cod_inventario}")
        
        # Obter contagens atuais
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as finalizados
        FROM contagem_lojas
        WHERE cod_inventario = ?
        ''', (cod_inventario,))
        
        lojas = cursor.fetchone()
        total_lojas = lojas['total'] if lojas and 'total' in lojas else 0
        lojas_finalizadas = lojas['finalizados'] if lojas and 'finalizados' in lojas else 0
        
        cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status = 'finalizado' THEN 1 ELSE 0 END) as finalizados
        FROM contagem_cd
        WHERE cod_inventario = ?
        ''', (cod_inventario,))
        
        setores = cursor.fetchone()
        total_setores = setores['total'] if setores and 'total' in setores else 0
        setores_finalizados = setores['finalizados'] if setores and 'finalizados' in setores else 0
        
        self.adicionar_log(f"\nLojas: {lojas_finalizadas} de {total_lojas} finalizadas")
        self.adicionar_log(f"Setores: {setores_finalizados} de {total_setores} finalizados")
        
        # Confirmar atualização
        resposta = QMessageBox.question(
            self,
            "Atualizar Status",
            f"Deseja marcar TODOS os registros como 'finalizado'?\n\n"
            f"Isso irá atualizar {total_lojas - lojas_finalizadas} lojas e {total_setores - setores_finalizados} setores.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta != QMessageBox.Yes:
            self.adicionar_log("Operação cancelada.")
            return
        
        # Atualizar status
        try:
            # Atualizar lojas
            cursor.execute('''
            UPDATE contagem_lojas
            SET status = 'finalizado'
            WHERE cod_inventario = ? AND status != 'finalizado'
            ''', (cod_inventario,))
            
            lojas_atualizadas = cursor.rowcount
            
            # Atualizar setores
            cursor.execute('''
            UPDATE contagem_cd
            SET status = 'finalizado'
            WHERE cod_inventario = ? AND status != 'finalizado'
            ''', (cod_inventario,))
            
            setores_atualizados = cursor.rowcount
            
            conn.commit()
            
            self.adicionar_log(f"\n✅ Operação concluída. {lojas_atualizadas} lojas e {setores_atualizados} setores marcados como 'finalizado'.")
        except Exception as e:
            self.adicionar_log(f"\n❌ Erro ao atualizar status: {str(e)}")
    
    def corrigir_totais(self):
        """Corrige o cálculo de totais para o dashboard"""
        import os
        import shutil
        import re
        
        self.adicionar_log("CORRIGIR CÁLCULO DE TOTAIS\n" + "="*50)
        
        self.adicionar_log("Esta função atualiza o sistema para usar os totais dos CSVs para calcular corretamente o progresso.")
        
        # Confirmar correção
        resposta = QMessageBox.question(
            self,
            "Corrigir Totais",
            "Esta operação modificará o arquivo relatorio_service.py para corrigir o cálculo de totais.\n\n"
            "Um backup do arquivo original será criado antes da modificação.\n\n"
            "Deseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if resposta != QMessageBox.Yes:
            self.adicionar_log("Operação cancelada.")
            return
        
        # Caminho do arquivo relatorio_service.py
        arquivo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "business", "relatorio_service.py")
        
        if not os.path.exists(arquivo_path):
            self.adicionar_log(f"\n❌ Arquivo não encontrado: {arquivo_path}")
            return
        
        # Backup do arquivo original
        backup_path = f"{arquivo_path}.bak"
        try:
            shutil.copy2(arquivo_path, backup_path)
            self.adicionar_log(f"✅ Backup criado: {backup_path}")
        except Exception as e:
            self.adicionar_log(f"❌ Erro ao criar backup: {str(e)}")
            return
        
        # Ler o código original
        with open(arquivo_path, 'r', encoding='utf-8') as file:
            codigo_original = file.read()
        
        # Verificar se a correção já foi aplicada
        if "total_lojas_csv =" in codigo_original:
            self.adicionar_log("⚠️ Parece que a correção já foi aplicada anteriormente.")
            resposta = QMessageBox.question(
                self,
                "Aplicar Novamente",
                "Parece que a correção já foi aplicada anteriormente.\n\nDeseja aplicar novamente?",
                QMessageBox.Yes | QMessageBox.No
            )
            if resposta != QMessageBox.Yes:
                self.adicionar_log("Operação cancelada.")
                return
        
        # Aplicar a correção
        try:
            # Código corrigido (igual ao do script original)
            codigo_corrigido = """    def get_resumo_status(self, cod_inventario):
        \"\"\"Retorna um resumo do status do inventário\"\"\"
        # Obter dados do banco
        dados = self.db_manager.get_dados_inventario_atual(cod_inventario)
        
        # Tentar obter referência ao CSV manager
        csv_manager = None
        try:
            from import_export.csv_manager import CSVManager
            csv_manager = CSVManager(self.db_manager)
            print("CSV Manager criado com sucesso")
        except Exception as e:
            print(f"Aviso: Não foi possível criar CSVManager: {e}")
        
        # Dados de lojas e setores do CSV
        total_lojas_csv = 0
        total_setores_csv = 0
        lojas_csv = []
        setores_csv = []
        
        # Obter total de lojas do CSV
        if csv_manager:
            try:
                lojas_csv = csv_manager.ler_lojas_csv(force_reload=True)
                total_lojas_csv = len(lojas_csv)
                
                setores_csv = csv_manager.ler_setores_csv(force_reload=True)
                total_setores_csv = len(setores_csv)
                
                print(f"Total de lojas no CSV: {total_lojas_csv}")
                print(f"Total de setores no CSV: {total_setores_csv}")
            except Exception as e:
                print(f"Erro ao ler CSV: {e}")
        
        # Dados de lojas do banco
        lojas_cadastradas = dados['dados_lojas'].get('total_lojas', 0) or 0
        lojas_finalizadas = dados['dados_lojas'].get('lojas_finalizadas', 0) or 0
        
        # Dados de setores do banco
        setores_cadastrados = dados['dados_cd'].get('total_setores', 0) or 0
        setores_finalizados = dados['dados_cd'].get('setores_finalizados', 0) or 0
        
        # CORREÇÃO: Definir total correto de lojas e setores, 
        # sempre dando prioridade para os valores do CSV (que tem a lista completa)
        total_lojas = total_lojas_csv if total_lojas_csv > 0 else lojas_cadastradas
        total_setores = total_setores_csv if total_setores_csv > 0 else setores_cadastrados
        
        # Obter lojas por regional do banco
        lojas_por_regional = self.db_manager.get_lojas_por_regional(cod_inventario)
        lojas_pendentes = self.db_manager.get_lojas_pendentes(cod_inventario)
        
        # Calcular porcentagens usando o total correto
        porcentagem_lojas = 0
        if total_lojas > 0:  # Evitar divisão por zero
            porcentagem_lojas = (lojas_finalizadas / total_lojas) * 100
        
        porcentagem_setores = 0
        if total_setores > 0:  # Evitar divisão por zero
            porcentagem_setores = (setores_finalizados / total_setores) * 100
        
        # Formatar resumo por regional usando dados do CSV e banco
        resumo_regional = []
        
        # Se temos acesso ao CSV, criar um mapeamento mais preciso de lojas por regional
        if csv_manager and total_lojas_csv > 0:
            # Agrupar lojas por regional no CSV
            regionais_csv = {}
            try:
                for loja in lojas_csv:
                    regional = loja.get('regional', 'Sem Regional')
                    if not regional:
                        regional = 'Sem Regional'
                    
                    if regional not in regionais_csv:
                        regionais_csv[regional] = []
                    
                    regionais_csv[regional].append(loja.get('loja', ''))
                
                # Mapa de lojas finalizadas para verificação rápida
                lojas_finalizadas_map = {}
                try:
                    cursor = self.db_manager.get_connection().cursor()
                    cursor.execute('''
                    SELECT loja FROM contagem_lojas
                    WHERE cod_inventario = ? AND status = 'finalizado'
                    ''', (cod_inventario,))
                    for row in cursor.fetchall():
                        lojas_finalizadas_map[row['loja']] = True
                except Exception as e:
                    print(f"Erro ao obter lojas finalizadas: {e}")
                
                # Para cada regional no CSV, extrair informações
                for regional, lojas in regionais_csv.items():
                    total_lojas_regional = len(lojas)
                    lojas_finalizadas_regional = 0
                    lojas_pendentes_regional = []
                    
                    # Contar manualmente as lojas finalizadas desta regional
                    for loja_nome in lojas:
                        if loja_nome in lojas_finalizadas_map:
                            lojas_finalizadas_regional += 1
                        else:
                            # Se não está nas finalizadas, é pendente
                            lojas_pendentes_regional.append(loja_nome)
                    
                    # Calcular porcentagem
                    porcentagem_regional = 0
                    if total_lojas_regional > 0:
                        porcentagem_regional = (lojas_finalizadas_regional / total_lojas_regional) * 100
                    
                    # Adicionar ao resumo
                    resumo_regional.append({
                        'regional': regional,
                        'total_lojas': total_lojas_regional,
                        'lojas_finalizadas': lojas_finalizadas_regional,
                        'porcentagem': porcentagem_regional,
                        'lojas_pendentes': lojas_pendentes_regional
                    })
            except Exception as e:
                print(f"Erro ao processar regionais do CSV: {e}")
                
                # Fallback ao processamento tradicional
                for regional in lojas_por_regional:
                    resumo_regional.append({
                        'regional': regional['regional'] or 'Sem Regional',
                        'total_lojas': regional['total_lojas'],
                        'lojas_finalizadas': regional['lojas_finalizadas'],
                        'porcentagem': (regional['lojas_finalizadas'] / regional['total_lojas'] * 100) if regional['total_lojas'] > 0 else 0,
                        'lojas_pendentes': lojas_pendentes.get(regional['regional'], [])
                    })
        else:
            # Processamento tradicional com dados apenas do banco
            for regional in lojas_por_regional:
                resumo_regional.append({
                    'regional': regional['regional'] or 'Sem Regional',
                    'total_lojas': regional['total_lojas'],
                    'lojas_finalizadas': regional['lojas_finalizadas'],
                    'porcentagem': (regional['lojas_finalizadas'] / regional['total_lojas'] * 100) if regional['total_lojas'] > 0 else 0,
                    'lojas_pendentes': lojas_pendentes.get(regional['regional'], [])
                })
        
        return resumo_regional

        })
        
        # Ordenar regionais por porcentagem de conclusão
        resumo_regional.sort(key=lambda x: x['porcentagem'], reverse=True)
        
        # Criar lista de setores pendentes comparando CSV com o banco
        setores_pendentes = []
        if csv_manager and total_setores_csv > 0:
            # Mapa de setores finalizados para verificação rápida
            setores_finalizados_map = {}
            try:
                cursor = self.db_manager.get_connection().cursor()
                cursor.execute('''
                SELECT setor FROM contagem_cd
                WHERE cod_inventario = ? AND status = 'finalizado'
                ''', (cod_inventario,))
                for row in cursor.fetchall():
                    setores_finalizados_map[row['setor']] = True
            except Exception as e:
                print(f"Erro ao obter setores finalizados: {e}")
            
            # Identificar setores pendentes comparando com o CSV
            for setor in setores_csv:
                setor_nome = setor.get('setor', '')
                if setor_nome and setor_nome not in setores_finalizados_map:
                    setores_pendentes.append({
                        'setor': setor_nome,
                        'descricao': setor.get('descricao', '')
                    })
        
        return {
            'total_lojas': total_lojas,
            'lojas_finalizadas': lojas_finalizadas,
            'lojas_pendentes': total_lojas - lojas_finalizadas,
            'porcentagem_lojas': porcentagem_lojas,
            'total_setores': total_setores,
            'setores_finalizados': setores_finalizados,
            'setores_pendentes': total_setores - setores_finalizados,
            'porcentagem_setores': porcentagem_setores,
            'resumo_regional': resumo_regional,
            'setores_pendentes_lista': setores_pendentes
        }"""
            
            # Substituir o método na arquivo original
            padrao = r'def get_resumo_status\(self, cod_inventario\):.*?return \{.*?\}'
            codigo_modificado = re.sub(padrao, codigo_corrigido, codigo_original, flags=re.DOTALL)
            
            # Escrever o arquivo modificado
            with open(arquivo_path, 'w', encoding='utf-8') as file:
                file.write(codigo_modificado)
            
            self.adicionar_log("\n✅ Correção aplicada com sucesso!")
            self.adicionar_log(f"O arquivo original foi salvo como: {backup_path}")
        except Exception as e:
            self.adicionar_log(f"\n❌ Erro ao aplicar correção: {str(e)}")
            import traceback
            self.adicionar_log(traceback.format_exc())

    def adicionar_log(self, texto):
        """Adiciona texto ao log"""
        # Obter texto atual
        texto_atual = self.txt_log.toPlainText()
        
        # Adicionar timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Adicionar nova entrada ao início ou anexar ao final
        if not texto_atual:
            novo_texto = f"[{timestamp}]\n{texto}"
        else:
            novo_texto = f"{texto_atual}\n[{timestamp}]\n{texto}"
        
        # Atualizar o texto
        self.txt_log.setPlainText(novo_texto)
        
        # Rolar para o final
        self.txt_log.verticalScrollBar().setValue(self.txt_log.verticalScrollBar().maximum())
    
    def limpar_log(self):
        """Limpa o log"""
        self.txt_log.clear()