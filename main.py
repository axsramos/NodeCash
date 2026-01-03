import sys
import time
import threading
from pathlib import Path

# Configuração e Infraestrutura
from config import Config
from storage_provider import StorageProvider
from account_service import AccountService

# Gerenciadores e Lógica
from account_manager import AccountManager
from peer_manager import PeerManager
from node_manager import NodeManager

# Serviços de Rede e Background
from network_server import NetworkServer
from network_client import NetworkClient
from garbage_collector import GarbageCollector
from inbound_watcher import InboundWatcher

def main():
    print("="*50)
    print(f"  NODECASH P2P - ARQUITETURA REFATORADA")
    print("="*50)

    try:
        # 1. Instância de Configuração (Base de tudo)
        config = Config()
        
        # 2. Instâncias de Infraestrutura (Camada de Baixo)
        # O StorageProvider cuida do disco, o Service cuida das regras
        storage_ptr = StorageProvider(config)
        account_svc = AccountService(storage_ptr, config)

        # 3. Instâncias de Gerenciamento (Camada Intermediária)
        # Agora injetamos o Provider e o Service dentro do Manager
        account_mgr = AccountManager(config, storage_ptr, account_svc)
        peer_mgr = PeerManager(config)
        start_peer_gc(peer_mgr)
        node_mgr = NodeManager(config)

        # 4. Serviços de Background
        watcher = InboundWatcher(config, account_mgr)
        watcher.start()

        gc = GarbageCollector(config, account_mgr)
        gc.start()

        # 5. Cliente de Sincronização
        client = NetworkClient(config, account_mgr, peer_mgr)
        client.start_sync_loop()

        # 6. Servidor (Loop Principal)
        server = NetworkServer(config, account_mgr, peer_mgr, node_mgr)
        
        node_mgr.set_status("READY")
        print(f"[*] Nó {config.node_id} operando em http://{config.node_host}:{config.node_port}")
        
        server.start()

    except KeyboardInterrupt:
        print("\n[!] Sistema encerrado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] ERRO CRÍTICO NA INICIALIZAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def start_peer_gc(peer_manager, interval=600):
    """
    Inicia o Garbage Collector em uma thread separada.
    interval: tempo em segundos entre cada limpeza (padrão 10 min).
    """
    def gc_loop():
        while True:
            print("[*] Iniciando varredura do Peer GC...")
            peer_manager.run_garbage_collector()
            time.sleep(interval)

    # Daemon=True garante que a thread morra quando o processo principal parar
    gc_thread = threading.Thread(target=gc_loop, daemon=True)
    gc_thread.start()
    print(f"[*] Thread status: {gc_thread.is_alive()}", flush=True)
    print("[*] Thread do Garbage Collector iniciada com sucesso.")

def gc_loop():
    while True:
        # O flush=True força o Windows a mostrar o texto na hora
        print("[*] Heartbeat: GC verificando peers...", flush=True) 
        peer_manager.run_garbage_collector()
        time.sleep(interval)
    
if __name__ == "__main__":
    main()