import json
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PeerManager:
    def __init__(self, config, peers_file="data/system/peers.json"):
        self.config = config
        self.peers_file = Path(peers_file)
        self.peers = {} 
        self.expire_time = 3600  
        
        self.peers_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_peers()

    def _load_peers(self):
        """Carrega a lista de IPs do disco."""
        if self.peers_file.exists():
            try:
                with open(self.peers_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.peers = {peer: time.time() for peer in data}
                    else:
                        self.peers = data
                print(f"[*] {len(self.peers)} peers carregados.")
            except Exception as e:
                print(f"[!] Erro ao carregar peers.json: {e}")
                self.peers = {}
        else:
            seeds = self.config.seeds if hasattr(self.config, 'seeds') else []
            self.peers = {peer: time.time() for peer in seeds}
            self._save_peers()

    def _save_peers(self):
        """Salva a lista no disco."""
        try:
            with open(self.peers_file, "w", encoding="utf-8") as f:
                json.dump(self.peers, f, indent=4)
        except Exception as e:
            print(f"[!] Erro ao salvar peers.json: {e}")

    def get_all_targets(self):
        return list(self.peers.keys())

    def get_active_peers(self):
        """Retorna a lista de endereços dos peers ativos (Necessário para o Dashboard)."""
        return list(self.peers.keys())

    def get_peers_count(self):
        """Retorna a quantidade total de peers (Necessário para o Dashboard)."""
        return len(self.peers)

    def add_peer_by_address(self, peer_address):
        if not peer_address or ":" not in peer_address:
            return False
            
        is_new = peer_address not in self.peers
        self.peers[peer_address] = time.time() 
        
        if is_new:
            self._save_peers()
            print(f"[*] Novo peer descoberto: {peer_address}")
        return True

    def run_garbage_collector(self):
        now = time.time()
        seeds = getattr(self.config, 'seeds', [])
        to_remove = [
            addr for addr, last_seen in self.peers.items() 
            if (now - last_seen > self.expire_time) and (addr not in seeds)
        ]
        
        if to_remove:
            for addr in to_remove:
                del self.peers[addr]
                print(f"[-] GC: Peer dinâmico removido: {addr}", flush=True)
            self._save_peers()
            return True
        return False
    