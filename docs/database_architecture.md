# Arquitetura de Banco de Dados - Netmap v2

Este documento detalha como os dados são estruturados, armazenados e acessados no projeto.

## 1. Visão Geral

O Netmap v2 utiliza o **PostgreSQL 16** com a extensão **PostGIS 3.4** para gerenciar dados espaciais (coordenadas no mapa). A persistência é garantida através de Volumes Docker, isolando os dados do ciclo de vida dos containers.

-   **Database Engine**: PostgreSQL 16 + PostGIS
-   **ORM (Object Relational Mapper)**: SQLAlchemy (Python)
-   **Gerenciador de Migração**: `Base.metadata.create_all` (Inicialização automática)
-   **Volume de Dados**: `postgres_data` (Mapeado para `/var/lib/postgresql/data` no container)

## 2. Estrutura de Tabelas

### A. Tabela `floors` (Andares/Backgrounds)
Armazena as informações das plantas baixas inseridas no sistema.

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Identificador único. |
| `name` | String | Nome do andar (ex: "Térreo"). |
| `level_order` | Integer | Ordem de exibição na lista (1, 2, 3...). |
| `image_path` | String | Caminho relativo da imagem (`/static/assets/floors/...`). |
| `width` | Float | Largura original da imagem em pixels. |
| `height` | Float | Altura original da imagem em pixels. |

*Código de Definição*: `app/models/floor.py`

### B. Tabela `network_nodes` (Itens/Marcadores)
Armazena os itens posicionados sobre os andares (Computadores, Pontos, etc).

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Identificador único. |
| `name` | String | Nome do item (ex: "RJ-PC01"). |
| `type` | String | Tipo: `Computador`, `Ponto`, `Ramal`, `Equipamento`. |
| `point_number` | String | Número do ponto de rede (ex: "160"). |
| `floor_id` | Integer (FK) | Vínculo com a tabela `floors`. |
| `geom` | Geometry(POINT) | Coordenada espacial X/Y (PostGIS Geometry). |

*Código de Definição*: `app/models/node.py`

## 3. Fluxo de Persistência

1.  **API Request**: O usuário envia um dado (Ex: `POST /api/nodes`).
2.  **Pydantic**: O FastAPI valida o formato dos dados.
3.  **SQLAlchemy Session**: O código (`app/api/nodes.py`) abre uma transação.
4.  **SQL Execution**: O driver converte o objeto Python em comando SQL (`INSERT INTO...`).
5.  **Commit**: O dado é gravado no arquivo de banco de dados dentro do volume Docker.

## 4. Onde os dados ficam fisicamente?

Como estamos usando Docker, os dados não ficam soltos numa pasta visível do Windows. Eles residem em um **Volume Docker** chamado `postgres_data`.

Para inspecionar onde o Docker guarda isso no Windows (WSL2):
```bash
docker volume inspect netmapv2_postgres_data
```

Isso garante que mesmo se você deletar o container `netmap-db`, os dados permanecem salvos, a menos que você delete explicitamente o volume (`docker volume rm`).

## 5. Conexão Externa (OCS Inventory)

O sistema também consulta (apenas leitura) um banco externo MySQL via Túnel SSH.
- **Configuração**: Definida em `app/database.py` e `.env`.
- **Tabela Consultada**: `hardware` (MySQL).
- **Dados lidos**: `NAME`, `OSNAME`, `IPADDR`.
