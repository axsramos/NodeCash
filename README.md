# NODECASH P2P
> Core Architecture em Python  

<img src="https://img.shields.io/badge/license-MIT-green"><img/>
<img src="https://img.shields.io/badge/version-1.2.0-blue"><img/>
<img src="https://img.shields.io/badge/biuld-2601030930-orange"><img/>

Ver mais em [Changelog](./docs/v1.2.0/whatsnew.md)

Este projeto implementa um sistema de rede Peer-to-Peer (P2P) focado na sincronização resiliente de arquivos entre nós distribuídos. Desenvolvido em Python, o sistema utiliza uma arquitetura em camadas para garantir escalabilidade e fácil manutenção.

## 🚀 Funcionalidades Atuais
**Sincronização Proativa:** Clientes de rede que buscam atualizações em vizinhos (Peers) automaticamente.

**Servidor de Dados Reativo:** Cada nó expõe uma API (Flask) para entrega de envelopes de dados e mapas de referência.

**Monitoramento Inbound:** Um sentinela (InboundWatcher) que processa arquivos novos e os converte em envelopes .dat.gz.

**Garbage Collection:** Gestão automática de armazenamento para limpeza de arquivos órfãos ou obsoletos.

**Arquitetura em Camadas:** Separação clara entre infraestrutura de armazenamento (StorageProvider), lógica de negócio (AccountService) e orquestração (Managers).

## Estrutura de pastas
```
/node
├── data/
│   ├── inbound/          <-- Entrada de arquivos (Bolachas)
│   │   └── [user_hash]/
│   ├── storage/          <-- Repositório oficial (.dat.gz)
│   │   └── [user_hash]/
│   │       └── references.json  <-- Mapa de integridade
│   └── system/           <-- Configurações de rede
│       ├── accounts.json        <-- Usuários autorizados
│       └── peers.json           <-- Lista de vizinhos (Vizinhos)
├── config.py             <-- Leitura do .env e constantes
├── storage_provider.py   <-- Especialista em caminhos e disco
├── account_service.py    <-- Regras de negócio e lógica JSON
├── account_manager.py    <-- Orquestrador de contas
├── node_manager.py       <-- Identidade e status do nó
├── peer_manager.py       <-- Gestão de IPs da rede
├── network_server.py     <-- API Flask (Reativo)
├── network_client.py     <-- Sincronizador (Proativo)
├── inbound_watcher.py    <-- Monitor de arquivos novos
├── garbage_collector.py  <-- Limpeza automática
├── main.py               <-- Ponto de entrada (Injeção de Dependência)
└── .env                  <-- Variáveis de ambiente
```

## 🔑 Configuração de Contas (Acesso Manual)

Nesta versão, a autorização de usuários é feita através do arquivo accounts.json. Para que o nó reconheça um usuário e inicie o monitoramento de arquivos, siga os passos abaixo:

Navegue até a pasta node/data/system/ (a pasta será criada automaticamente na primeira execução).

Crie ou edite o arquivo accounts.json.

Adicione o objeto do usuário seguindo o esquema abaixo:
```json
[
    {
        "user": "axsramos",
        "name": "Alex Sandro Ramos",
        "profile": "admin",
        "repository": "https://github.com/axsramos",
        "site": "portalsiti.com.br",
        "status": "active"
    }
]
```
**Nota:** O campo user é a chave principal. É a partir dele que o StorageProvider gerará os nomes das pastas (diretos ou em Hash) para armazenar os arquivos e referências.

### 🔑 Auto-Provisionamento (Bootstrap)
Nesta versão, o nó realiza a configuração inicial de forma automática. Não é necessário criar arquivos JSON manualmente. O sistema utiliza as variáveis do arquivo `.env` para realizar o bootstrap da conta administrativa e da estrutura de pastas:

- **INITIAL_USER**: ID do usuário administrativo.
- **INITIAL_USER_NAME**: Nome completo para o perfil.
- **INITIAL_REPOSITORY**: Link para o repositório do usuário.
- **INITIAL_SITE**: Site de referência.

Ao iniciar o `main.py` pela primeira vez, o `AccountService` deteta a ausência do banco de dados e provisiona a conta inicial imediatamente.


## 🛠️ Tecnologias Utilizadas
Python 3.x

* Flask (Servidor Web/API)

* Requests (Comunicação entre nós)

* Python-dotenv (Gestão de ambiente)

* Pathlib (Manipulação robusta de sistemas de arquivos)

## 🏗️ Arquitetura do Sistema
O sistema foi projetado seguindo os princípios de Injeção de Dependência e Responsabilidade Única (SOLID).

**Camada de Infraestrutura:** O StorageProvider centraliza todas as decisões sobre caminhos de arquivos e privacidade (suportando nomes reais ou Hashes SHA-256 para as pastas).

**Camada de Serviço:** O AccountService gerencia a integridade do references.json, garantindo que o histórico de sincronização seja mantido mesmo após reinicializações.

**Camada de Gestão:** AccountManager e PeerManager coordenam a memória e a persistência dos dados da rede.

## ⛓️ Futuro e Blockchain
Embora esta versão foque na robustez da comunicação P2P e na integridade dos arquivos, a arquitetura já foi preparada para a implementação de um DLP (Distributed Ledger Protocol). O sistema de sequenciamento e hashing de arquivos atual serve como base para o futuro encadeamento de blocos (Blockchain).

## 💻 Como Rodar
Configure o seu arquivo .env com as informações do nó (Porta, ID e Seeds).

**Instale as dependências:** pip install flask requests python-dotenv.

Execute python main.py.

