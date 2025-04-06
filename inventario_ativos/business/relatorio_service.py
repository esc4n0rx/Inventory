# business/relatorio_service.py
import os
import datetime
from collections import defaultdict

class RelatorioService:
    def __init__(self, db_manager):
        """Inicializa o serviço de relatórios"""
        self.db_manager = db_manager
    
    def get_totais_por_tipo(self, cod_inventario):
        """Retorna os totais de cada tipo de caixa no inventário"""
        dados = self.db_manager.get_dados_inventario_atual(cod_inventario)
        
        tipos_caixa = [
            'hb_623', 'hb_618', 'hnt_g', 'hnt_p', 
            'chocolate', 'bin', 'pallets_pbr'
        ]
        
        resultado = {}
        
        # Totais de lojas
        for tipo in tipos_caixa:
            resultado[f'lojas_{tipo}'] = dados['dados_lojas'].get(f'total_{tipo}', 0) or 0
        
        # Totais de CD
        for tipo in tipos_caixa:
            resultado[f'cd_{tipo}'] = dados['dados_cd'].get(f'total_{tipo}', 0) or 0
        
        # Totais de trânsito
        transito_dict = {item['tipo_caixa']: item['total'] for item in dados['dados_transito']}
        for tipo in tipos_caixa:
            resultado[f'transito_{tipo}'] = transito_dict.get(tipo, 0) or 0
        
        # Totais de fornecedor
        fornecedor_dict = {item['tipo_caixa']: item['total'] for item in dados['dados_fornecedor']}
        for tipo in tipos_caixa:
            resultado[f'fornecedor_{tipo}'] = fornecedor_dict.get(tipo, 0) or 0
        
        # Calcular totais gerais por tipo
        for tipo in tipos_caixa:
            total = (
                resultado[f'lojas_{tipo}'] + 
                resultado[f'cd_{tipo}'] + 
                resultado[f'transito_{tipo}'] + 
                resultado[f'fornecedor_{tipo}']
            )
            resultado[f'total_{tipo}'] = total
        
        # Calcular totais por origem
        resultado['total_lojas'] = sum(resultado[f'lojas_{tipo}'] for tipo in tipos_caixa)
        resultado['total_cd'] = sum(resultado[f'cd_{tipo}'] for tipo in tipos_caixa)
        resultado['total_transito'] = sum(resultado[f'transito_{tipo}'] for tipo in tipos_caixa)
        resultado['total_fornecedor'] = sum(resultado[f'fornecedor_{tipo}'] for tipo in tipos_caixa)
        
        # Total geral
        resultado['total_geral'] = (
            resultado['total_lojas'] + 
            resultado['total_cd'] + 
            resultado['total_transito'] + 
            resultado['total_fornecedor']
        )
        
        return resultado
    

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
        diferencas['diff_cd'] = dados_atual['total_cd'] - dados_anterior['total_cd']
        diferencas['diff_transito'] = dados_atual['total_transito'] - dados_anterior['total_transito']
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
        """Retorna os dados para o dashboard"""
        # Obter dados básicos
        totais = self.get_totais_por_tipo(cod_inventario)
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
        
        return {
            'meta': meta,
            'totais': totais,
            'status': status,
            'comparacao': comparacao
        }