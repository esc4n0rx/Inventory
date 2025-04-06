# Sistema de Inventário Rotativo de Ativos (Nova)

## Introdução
O Sistema de Inventário Rotativo de Ativos (Nova) é uma aplicação desenvolvida para auxiliar na gestão e acompanhamento de inventários de ativos, oferecendo uma interface gráfica intuitiva e funcionalidades robustas para gerenciar relatórios e dados de inventário.

## Estrutura do Projeto
```
data
- inventario_ativos
- inventario_ativos\business
- inventario_ativos\data
- inventario_ativos\database
- inventario_ativos\gui
- inventario_ativos\import_export
- inventario_ativos\relatorios
- inventario_ativos\utils
- relatorios
```

## Componentes Principais
- `data`: Dados ou exemplos utilizados pelo sistema.
- `inventario_ativos`: Componente principal do sistema, contendo funcionalidades de negócios, banco de dados, interface gráfica, importação/exportação e geração de relatórios.
- `relatorios`: Pasta para armazenamento de relatórios gerados pelo sistema.

## Instalação
### Pré-requisitos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)

### Passos para Instalação
1. **Clone o Repositório**: 
   ```
   git clone https://github.com/seu-repositorio/nova.git
   cd nova
   ```

2. **Instale as Dependências**:
   ```
   pip install -r requirements.txt
   ```

## Configuração
### Arquivo de Configuração
O sistema utiliza um arquivo de configuração para gerenciar parâmetros como o caminho do arquivo de banco de dados. O arquivo `config.ini` está localizado na pasta `utils/` e pode ser modificado conforme a necessidade do usuário.

### Exemplo de Configuração
```ini
[DATABASE]
file = data/database.db
```

## Uso
### Iniciando a Aplicação
Para iniciar a aplicação, execute o seguinte comando na raiz do projeto:
```
python inventario_ativos/main.py
```

### Funcionalidades Principais
- **Iniciar Novo Inventário**: Cria um novo inventário com uma descrição específica.
- **Carregar Inventário Existente**: Permite carregar inventários previamente criados.
- **Gerar Relatórios**: Gera relatórios detalhados baseados nos dados do inventário.
- **Interface Gráfica**: Interface amigável para interação com o sistema.

### Exemplos de Uso
- **Iniciar um Novo Inventário**
  ```python
  from inventario_ativos.business.inventario_service import InventarioService

  service = InventarioService()
  novo_inventario = service.iniciar_novo_inventario("Inventário de itens de 2023")
  ```

- **Gerar Totais por Tipo de Caixa**
  ```python
  from inventario_ativos.database.database_manager import DatabaseManager
  from inventario_ativos.business.relatorio_service import RelatorioService

  db_manager = DatabaseManager()
  relatorio_service = RelatorioService(db_manager)
  totais = relatorio_service.get_totais_por_tipo(1)
  print(totais)
  ```

## Testes
O sistema utiliza testes unitários para garantir a qualidade do código. Os testes podem ser executados utilizando o `pytest`.

### Executando os Testes
```
pip install pytest
pytest tests/
```

## Contribuição
Contribuições são sempre bem-vindas! Para contribuir com o projeto:
1. Faça um fork do repositório.
2. Crie sua feature branch (`git checkout -b feature/nome-da-feature`).
3. Adicione suas mudanças (`git add .`).
4. Commit suas mudanças (`git commit -m "Adiciona nome-da-feature"`).
5. Faça o push da branch (`git push origin feature/nome-da-feature`).
6. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato
Para mais informações ou suporte, entre em contato através dos canais abaixo:
- E-mail: suporte@novainventario.com
- GitHub: [seu-repositorio/nova](https://github.com/seu-repositorio/nova)

---

Este README fornece uma visão geral abrangente do Sistema de Inventário Rotativo de Ativos, incluindo instruções para instalação, configuração, uso e contribuição, além de detalhes técnicos importantes.