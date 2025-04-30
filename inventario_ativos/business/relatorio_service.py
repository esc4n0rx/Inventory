# business/relatorio_service.py
import os
import datetime
from collections import defaultdict

class RelatorioService:
    def __init__(self, db_manager):
        """Inicializa o serviço de relatórios"""
        self.db_manager = db_manager
    
    def get_totais_por_tipo(self, cod_inventario):
        """Retorna os totais de cada tipo de caixa no inventário com separação por origem correta"""
        if not cod_inventario:
            print("Aviso: get_totais_por_tipo chamado com cod_inventario vazio")
            return self._get_totais_vazios()
            
        try:
            dados = self.db_manager.get_dados_inventario_atual(cod_inventario)
            if not dados:
                print(f"Aviso: Não foi possível obter dados para o inventário {cod_inventario}")
                return self._get_totais_vazios()
            
            tipos_caixa = [
                'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
                'chocolate', 'bin', 'pallets_pbr'
            ]
            
            resultado = {}
            
            # Inicializar todos os totais com zero para evitar valores None
            for prefixo in ['cd_sp_', 'cd_es_', 'cd_rj_', 'lojas_', 'transito_sp_', 'transito_es_', 'transito_rj_', 'fornecedor_', 'total_']:
                for tipo in tipos_caixa:
                    resultado[f'{prefixo}{tipo}'] = 0
                    
            # Obter conexão para consultas mais detalhadas
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # --- PROCESSAMENTO DAS LOJAS ---
            # Obter todas as lojas (excluindo CDs)
            cursor.execute('''
            SELECT loja, caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_lojas
            WHERE cod_inventario = ? AND loja NOT LIKE 'CD %'
            ''', (cod_inventario,))
            
            lojas = cursor.fetchall()
            
            # Somar por tipo de caixa
            for loja in lojas:
                resultado['lojas_hb_623'] += loja['caixa_hb_623'] or 0
                resultado['lojas_hb_618'] += loja['caixa_hb_618'] or 0
                resultado['lojas_hnt_g'] += loja['caixa_hnt_g'] or 0
                resultado['lojas_hnt_p'] += loja['caixa_hnt_p'] or 0
                resultado['lojas_chocolate'] += loja['caixa_chocolate'] or 0
                resultado['lojas_bin'] += loja['caixa_bin'] or 0
                resultado['lojas_pallets_pbr'] += loja['pallets_pbr'] or 0
            
            # --- PROCESSAMENTO DOS CDs a partir da tabela contagem_lojas (para CDs específicos) ---
            # CD SP
            cursor.execute('''
            SELECT loja, caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_lojas
            WHERE cod_inventario = ? AND loja = 'CD SP'
            ''', (cod_inventario,))
            
            cd_sp = cursor.fetchone()
            if cd_sp:
                resultado['cd_sp_hb_623'] += cd_sp['caixa_hb_623'] or 0
                resultado['cd_sp_hb_618'] += cd_sp['caixa_hb_618'] or 0
                resultado['cd_sp_hnt_g'] += cd_sp['caixa_hnt_g'] or 0
                resultado['cd_sp_hnt_p'] += cd_sp['caixa_hnt_p'] or 0
                resultado['cd_sp_chocolate'] += cd_sp['caixa_chocolate'] or 0
                resultado['cd_sp_bin'] += cd_sp['caixa_bin'] or 0
                resultado['cd_sp_pallets_pbr'] += cd_sp['pallets_pbr'] or 0
            
            # CD ES
            cursor.execute('''
            SELECT loja, caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_lojas
            WHERE cod_inventario = ? AND loja = 'CD ES'
            ''', (cod_inventario,))
            
            cd_es = cursor.fetchone()
            if cd_es:
                resultado['cd_es_hb_623'] += cd_es['caixa_hb_623'] or 0
                resultado['cd_es_hb_618'] += cd_es['caixa_hb_618'] or 0
                resultado['cd_es_hnt_g'] += cd_es['caixa_hnt_g'] or 0
                resultado['cd_es_hnt_p'] += cd_es['caixa_hnt_p'] or 0
                resultado['cd_es_chocolate'] += cd_es['caixa_chocolate'] or 0
                resultado['cd_es_bin'] += cd_es['caixa_bin'] or 0
                resultado['cd_es_pallets_pbr'] += cd_es['pallets_pbr'] or 0
            
            # --- PROCESSAMENTO DOS SETORES DO CD (tabela contagem_cd) ---
            # Somamos todos os setores como CD RJ
            cursor.execute('''
            SELECT setor, caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_cd
            WHERE cod_inventario = ?
            ''', (cod_inventario,))
            
            setores = cursor.fetchall()
            
            # Somar por tipo de caixa
            for setor in setores:
                resultado['cd_rj_hb_623'] += setor['caixa_hb_623'] or 0
                resultado['cd_rj_hb_618'] += setor['caixa_hb_618'] or 0
                resultado['cd_rj_hnt_g'] += setor['caixa_hnt_g'] or 0
                resultado['cd_rj_hnt_p'] += setor['caixa_hnt_p'] or 0
                resultado['cd_rj_chocolate'] += setor['caixa_chocolate'] or 0
                resultado['cd_rj_bin'] += setor['caixa_bin'] or 0
                resultado['cd_rj_pallets_pbr'] += setor['pallets_pbr'] or 0
            
            # --- PROCESSAMENTO DOS DADOS EM TRÂNSITO ---
            # Consultar dados de trânsito separados por CD
            cursor.execute('''
            SELECT setor, tipo_caixa, SUM(quantidade) as total
            FROM dados_transito
            WHERE cod_inventario = ?
            GROUP BY setor, tipo_caixa
            ''', (cod_inventario,))
            
            # Função auxiliar para normalizar os tipos de caixa
            def normalizar_tipo_caixa(tipo):
                # Remover prefixos como "CAIXA " ou "caixa_" e converter para minúsculas
                tipo = tipo.lower()
                if tipo.startswith('caixa_'):
                    tipo = tipo[6:]
                elif tipo.startswith('caixa '):
                    tipo = tipo[6:]
                
                # Mapeamento de nomes alternativos para os padrões
                mapeamento = {
                    'hb623': 'hb_623',
                    'hb618': 'hb_618',
                    'hntg': 'hnt_g',
                    'hntp': 'hnt_p',
                    'bin': 'bin',
                    'chocolate': 'chocolate',
                    'pallets': 'pallets_pbr',
                    'palletes': 'pallets_pbr',
                    'palletspbr': 'pallets_pbr',
                    'pallets_pbr': 'pallets_pbr',
                    'pbr': 'pallets_pbr'
                }
                
                # Remover underscores e espaços para correspondência mais flexível
                tipo_limpo = tipo.replace('_', '').replace(' ', '')
                
                # Verificar no mapeamento
                if tipo_limpo in mapeamento:
                    return mapeamento[tipo_limpo]
                
                # Verificar se é um dos tipos padrão
                for tipo_padrao in tipos_caixa:
                    if tipo_limpo == tipo_padrao.replace('_', ''):
                        return tipo_padrao
                
                # Se não encontrou correspondência, registrar e tratar como desconhecido
                print(f"Aviso: Tipo de caixa desconhecido: '{tipo}', considerando como 'bin'")
                return 'bin'  # Valor padrão para tipos desconhecidos
            
            # Processar resultados separando por origem
            for row in cursor.fetchall():
                setor = row['setor'] or ''
                tipo_caixa_original = row['tipo_caixa']
                quantidade = row['total'] or 0
                
                # Normalizar o tipo de caixa
                tipo_caixa = normalizar_tipo_caixa(tipo_caixa_original)
                
                # Registrar caso seja diferente para depuração
                if tipo_caixa != tipo_caixa_original:
                    print(f"Normalizando tipo de caixa: '{tipo_caixa_original}' -> '{tipo_caixa}'")
                
                # Mapear para as chaves específicas no resultado
                if 'SP' in setor:
                    resultado[f'transito_sp_{tipo_caixa}'] += quantidade
                elif 'ES' in setor:
                    resultado[f'transito_es_{tipo_caixa}'] += quantidade
                elif 'RJ' in setor:
                    resultado[f'transito_rj_{tipo_caixa}'] += quantidade
                else:
                    # Se não encaixar em nenhum CD específico, dividir igualmente entre os três
                    # Isso pode ser ajustado conforme a regra de negócio
                    resultado[f'transito_sp_{tipo_caixa}'] += quantidade / 3
                    resultado[f'transito_es_{tipo_caixa}'] += quantidade / 3
                    resultado[f'transito_rj_{tipo_caixa}'] += quantidade / 3
            
            # --- PROCESSAMENTO DOS DADOS DE FORNECEDOR ---
            # Obter totais dos fornecedores do banco
            cursor.execute('''
            SELECT tipo_caixa, SUM(quantidade) as total
            FROM dados_fornecedor
            WHERE cod_inventario = ?
            GROUP BY tipo_caixa
            ''', (cod_inventario,))
            
            for row in cursor.fetchall():
                tipo_caixa_original = row['tipo_caixa']
                # Usar a mesma função de normalização definida acima
                tipo_caixa = normalizar_tipo_caixa(tipo_caixa_original)
                
                # Registrar caso seja diferente para depuração
                if tipo_caixa != tipo_caixa_original:
                    print(f"Normalizando tipo de caixa (fornecedor): '{tipo_caixa_original}' -> '{tipo_caixa}'")
                
                resultado[f'fornecedor_{tipo_caixa}'] = row['total'] or 0
            
            # --- CALCULAR TOTAIS GERAIS ---
            # Calcular totais por tipo
            for tipo in tipos_caixa:
                total_tipo = (
                    resultado[f'lojas_{tipo}'] + 
                    resultado[f'cd_sp_{tipo}'] + 
                    resultado[f'cd_es_{tipo}'] + 
                    resultado[f'cd_rj_{tipo}'] + 
                    resultado[f'transito_sp_{tipo}'] + 
                    resultado[f'transito_es_{tipo}'] + 
                    resultado[f'transito_rj_{tipo}'] + 
                    resultado[f'fornecedor_{tipo}']
                )
                resultado[f'total_{tipo}'] = total_tipo
            
            # Calcular totais por origem
            resultado['total_lojas'] = sum(resultado[f'lojas_{tipo}'] for tipo in tipos_caixa)
            resultado['total_cd_sp'] = sum(resultado[f'cd_sp_{tipo}'] for tipo in tipos_caixa)
            resultado['total_cd_es'] = sum(resultado[f'cd_es_{tipo}'] for tipo in tipos_caixa)
            resultado['total_cd_rj'] = sum(resultado[f'cd_rj_{tipo}'] for tipo in tipos_caixa)
            resultado['total_transito_sp'] = sum(resultado[f'transito_sp_{tipo}'] for tipo in tipos_caixa)
            resultado['total_transito_es'] = sum(resultado[f'transito_es_{tipo}'] for tipo in tipos_caixa)
            resultado['total_transito_rj'] = sum(resultado[f'transito_rj_{tipo}'] for tipo in tipos_caixa)
            resultado['total_fornecedor'] = sum(resultado[f'fornecedor_{tipo}'] for tipo in tipos_caixa)
            
            # Total geral
            resultado['total_geral'] = (
                resultado['total_lojas'] + 
                resultado['total_cd_sp'] + 
                resultado['total_cd_es'] + 
                resultado['total_cd_rj'] + 
                resultado['total_transito_sp'] + 
                resultado['total_transito_es'] + 
                resultado['total_transito_rj'] + 
                resultado['total_fornecedor']
            )
            
            return resultado
            
        except Exception as e:
            import traceback
            print(f"Erro em get_totais_por_tipo: {e}")
            print(traceback.format_exc())
            return self._get_totais_vazios()
        

    def get_resumo_status(self, cod_inventario):
        """Retorna um resumo do status do inventário"""
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
        }

    def comparar_inventarios(self, cod_inventario_atual, cod_inventario_anterior):
        """Compara dois inventários e retorna as diferenças"""
        # Obter dados dos dois inventários
        dados_atual = self.get_totais_por_tipo(cod_inventario_atual)
        dados_anterior = self.get_totais_por_tipo(cod_inventario_anterior)
        
        tipos_caixa = [
            'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
            'chocolate', 'bin', 'pallets_pbr'
        ]
        
        # Calcular diferenças
        diferencas = {}
        
        # Diferenças por tipo
        for tipo in tipos_caixa:
            diferencas[f'diff_{tipo}'] = dados_atual[f'total_{tipo}'] - dados_anterior[f'total_{tipo}']
        
        # Diferenças por origem
        diferencas['diff_lojas'] = dados_atual['total_lojas'] - dados_anterior['total_lojas']
        
        # Calcular total de CDs somando os três CDs individuais
        cd_atual = dados_atual.get('total_cd_sp', 0) + dados_atual.get('total_cd_es', 0) + dados_atual.get('total_cd_rj', 0)
        cd_anterior = dados_anterior.get('total_cd_sp', 0) + dados_anterior.get('total_cd_es', 0) + dados_anterior.get('total_cd_rj', 0)
        diferencas['diff_cd'] = cd_atual - cd_anterior
        
        # Calcular total de trânsito somando os três trânsitos individuais
        transito_atual = dados_atual.get('total_transito_sp', 0) + dados_atual.get('total_transito_es', 0) + dados_atual.get('total_transito_rj', 0)
        transito_anterior = dados_anterior.get('total_transito_sp', 0) + dados_anterior.get('total_transito_es', 0) + dados_anterior.get('total_transito_rj', 0)
        diferencas['diff_transito'] = transito_atual - transito_anterior
        
        diferencas['diff_fornecedor'] = dados_atual['total_fornecedor'] - dados_anterior['total_fornecedor']

        
        # Diferença total
        diferencas['diff_total'] = dados_atual['total_geral'] - dados_anterior['total_geral']
        
        return {
            'atual': dados_atual,
            'anterior': dados_anterior,
            'diferencas': diferencas
        }
    
    def get_historico_inventarios(self, limite=10):
        """Retorna um histórico dos últimos inventários finalizados"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT im.cod_inventario, im.data_inicio, im.data_fim,
               COUNT(DISTINCT cl.loja) as total_lojas,
               COUNT(DISTINCT cd.setor) as total_setores
        FROM inventario_meta im
        LEFT JOIN contagem_lojas cl ON im.cod_inventario = cl.cod_inventario
        LEFT JOIN contagem_cd cd ON im.cod_inventario = cd.cod_inventario
        WHERE im.status = 'finalizado'
        GROUP BY im.cod_inventario
        ORDER BY im.data_fim DESC
        LIMIT ?
        ''', (limite,))
        
        inventarios = cursor.fetchall()
        
        resultados = []
        for inv in inventarios:
            cod_inventario = inv['cod_inventario']
            totais = self.get_totais_por_tipo(cod_inventario)
            
            # Formatar datas
            data_inicio = datetime.datetime.fromisoformat(inv['data_inicio']).strftime('%d/%m/%Y')
            data_fim = datetime.datetime.fromisoformat(inv['data_fim']).strftime('%d/%m/%Y')
            
            resultados.append({
                'cod_inventario': cod_inventario,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'total_lojas': inv['total_lojas'],
                'total_setores': inv['total_setores'],
                'total_geral': totais['total_geral']
            })
        
        return resultados
    
    def get_dados_dashboard(self, cod_inventario):
        """Retorna os dados para o dashboard com informações detalhadas de cada origem"""
        if not cod_inventario:
            print("Aviso: get_dados_dashboard chamado com cod_inventario vazio")
            return self._get_dados_dashboard_vazio()
            
        try:
            # Obter dados básicos
            totais = self.get_totais_por_tipo(cod_inventario)
            if not totais:
                print("Aviso: get_totais_por_tipo retornou None")
                return self._get_dados_dashboard_vazio()
                
            status = self.get_resumo_status(cod_inventario)
            
            # Obter inventário anterior para comparação (se houver)
            inventarios_anteriores = self.get_historico_inventarios(1)
            comparacao = None
            if inventarios_anteriores and inventarios_anteriores[0]['cod_inventario'] != cod_inventario:
                comparacao = self.comparar_inventarios(cod_inventario, inventarios_anteriores[0]['cod_inventario'])
            
            # Obter informações do inventário atual
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM inventario_meta WHERE cod_inventario = ?
            ''', (cod_inventario,))
            
            info_inventario = cursor.fetchone()
            
            # Extrair metadados do inventário
            meta = {}
            if info_inventario:
                data_inicio = datetime.datetime.fromisoformat(info_inventario['data_inicio'])
                data_inicio_str = data_inicio.strftime('%d/%m/%Y %H:%M')
                
                meta = {
                    'cod_inventario': info_inventario['cod_inventario'],
                    'data_inicio': data_inicio_str,
                    'status': info_inventario['status'],
                    'descricao': info_inventario['descricao'],
                    'duracao': None
                }
                
                # Calcular duração se o inventário estiver finalizado
                if info_inventario['data_fim']:
                    data_fim = datetime.datetime.fromisoformat(info_inventario['data_fim'])
                    duracao = data_fim - data_inicio
                    horas, resto = divmod(duracao.seconds, 3600)
                    minutos, _ = divmod(resto, 60)
                    
                    meta['duracao'] = f"{duracao.days} dias, {horas}h {minutos}m"
                    meta['data_fim'] = data_fim.strftime('%d/%m/%Y %H:%M')
            
            # Obter detalhes de dados de lojas, CDs, e trânsito para a interface de finalização
            
            # 1. Detalhes das lojas
            cursor.execute('''
            SELECT loja, regional, status,
                caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_lojas
            WHERE cod_inventario = ?
            ''', (cod_inventario,))
            
            lojas_detalhes = [dict(row) for row in cursor.fetchall()]
            
            # 2. Detalhes dos CDs (tabela contagem_cd)
            cursor.execute('''
            SELECT setor, status,
                caixa_hb_623, caixa_hb_618, caixa_hnt_g, caixa_hnt_p, 
                caixa_chocolate, caixa_bin, pallets_pbr
            FROM contagem_cd
            WHERE cod_inventario = ?
            ''', (cod_inventario,))
            
            cds_detalhes = [dict(row) for row in cursor.fetchall()]
            
            # 3. Detalhes de trânsito
            cursor.execute('''
            SELECT setor, tipo_caixa, SUM(quantidade) as total
            FROM dados_transito
            WHERE cod_inventario = ?
            GROUP BY setor, tipo_caixa
            ''', (cod_inventario,))
            
            transito_detalhes = [dict(row) for row in cursor.fetchall()]
            
            # 4. Detalhes de fornecedor
            cursor.execute('''
            SELECT tipo_fornecedor, tipo_caixa, SUM(quantidade) as total
            FROM dados_fornecedor
            WHERE cod_inventario = ?
            GROUP BY tipo_fornecedor, tipo_caixa
            ''', (cod_inventario,))
            
            fornecedor_detalhes = [dict(row) for row in cursor.fetchall()]
            
            return {
                'meta': meta,
                'totais': totais,
                'status': status,
                'comparacao': comparacao,
                'detalhes': {
                    'lojas': lojas_detalhes,
                    'cds': cds_detalhes,
                    'transito': transito_detalhes,
                    'fornecedor': fornecedor_detalhes
                }
            }
        except Exception as e:
            import traceback
            print(f"Erro em get_dados_dashboard: {e}")
            print(traceback.format_exc())
            return self._get_dados_dashboard_vazio()
    
    def _get_dados_dashboard_vazio(self):
        """Retorna uma estrutura de dados vazia mas válida para o dashboard"""
        # Criar uma estrutura mínima para evitar erros
        return {
            'meta': {
                'cod_inventario': "",
                'data_inicio': "",
                'status': "",
                'descricao': "",
                'duracao': None
            },
            'totais': {
                'total_lojas': 0,
                'total_cd_sp': 0,
                'total_cd_es': 0,
                'total_cd_rj': 0,
                'total_transito_sp': 0,
                'total_transito_es': 0,
                'total_transito_rj': 0,
                'total_fornecedor': 0,
                'total_geral': 0
            },
            'status': {
                'total_lojas': 0,
                'lojas_finalizadas': 0,
                'lojas_pendentes': 0,
                'porcentagem_lojas': 0,
                'total_setores': 0,
                'setores_finalizados': 0,
                'setores_pendentes': 0,
                'porcentagem_setores': 0,
                'resumo_regional': [],
                'setores_pendentes_lista': []
            },
            'comparacao': None,
            'detalhes': {
                'lojas': [],
                'cds': [],
                'transito': [],
                'fornecedor': []
            }
        }