# 📢 What's New! (Recentes Atualizações)
[v1.1.0] - 2025-12-29  
**Foco:** Autonomia e Infraestrutura "Zero-Setup"

## 🚀 Novas Funcionalidades
**Auto-Provisionamento (Bootstrap):** O Nó agora é capaz de se auto-inicializar. Se o accounts.json não existir, o sistema utiliza as variáveis do .env para criar a conta administrativa automaticamente.

**Gestão Dinâmica de Bolachas (Files):** Refatoração do InboundWatcher para identificar e processar arquivos em tempo real, movendo-os para o storage oficial com hash de integridade.

**StorageProvider & AccountService:** Implementação de camadas de infraestrutura e serviço para desacoplar a lógica de disco da lógica de rede.

## 🛠️ Melhorias Técnicas
**Injeção de Dependência:** O main.py foi totalmente reestruturado para injetar provedores de storage e serviços, facilitando testes unitários e manutenção.

**Segurança de Paths:** Implementação de suporte a caminhos ofuscados via SHA-256 para pastas de usuários, configurável via .env.

**Git Flow Limpo:** Otimização do .gitignore para garantir que dados de teste e ambiente local não poluam o repositório público.

## 🐛 Correções (Bug Fixes)
Corrigido erro de AttributeError no NetworkServer ao tentar acessar caminhos de storage inexistentes.

Ajustada a concorrência entre o GarbageCollector e o InboundWatcher para evitar conflitos de acesso a arquivos.