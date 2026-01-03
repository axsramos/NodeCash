# 📢 What's New! (Recentes Atualizações)
[v1.2.0] - 2026-01-03  
**Foco:** Resiliência de Rede e Autogestão de Vizinhos.

## 🚀 Novas Funcionalidades

## 📝 Resumo de Alterações (v0.2.0 - Proposta)
[Added]
**Sistema de Garbage Collection (GC):** Implementação da função run_garbage_collector para limpar automaticamente peers inativos com base em um tempo de expiração (expire_time).

**Função add_peer_by_address:** Adicionada lógica para descoberta e registro de novos nós na rede com validação básica de formato.

**Background Processing:** Implementação de suporte a Threads para que o GC rode de forma não-bloqueante no servidor.

**Proteção de Seed Nodes:** Adicionada condição de segurança que impede que os nós "seeds" (âncoras) sejam removidos pelo GC, evitando o isolamento do nó.

[Changed]
**Estrutura de Dados de Peers:** A lista simples de endereços foi convertida para um dicionário { "ip:port": timestamp }. Isso permite o rastreamento do "último sinal de vida" (Liveness) de cada vizinho.

**Persistência em Disco:** O método _save_peers agora persiste os timestamps no arquivo peers.json.