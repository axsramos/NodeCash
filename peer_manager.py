import json
import time
from pathlib import Path

class PeerManager:
    def __init__(self, config, peers_file="data/system/peers.json"):
        self.config = config
        self.peers_file = Path(peers_file)
        # Mudamos para dict para armazenar o timestamp: { "ip:port": last_seen }
        self.peers = {} 
        self.expire_time = 3600  # 1 hora para expiração (ajustável)
        
        self.peers_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_peers()

    def _load_peers(self):
        """Carrega a lista de IPs do disco."""
        if self.peers_file.exists():
            try:
                with open(self.peers_file, "r", encoding="utf-8") as f:
                    # Carrega e garante que temos um dicionário com timestamps
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
        """Retorna apenas os endereços (keys do dict)."""
        return list(self.peers.keys())

    def add_peer_by_address(self, peer_address):
        """Implementação pendente: Adiciona ou atualiza o timestamp do peer."""
        if not peer_address or ":" not in peer_address:
            return False
            
        is_new = peer_address not in self.peers
        self.peers[peer_address] = time.time() # Atualiza o 'last_seen'
        
        if is_new:
            self._save_peers()
            print(f"[*] Novo peer descoberto: {peer_address}")
        return True

    def run_garbage_collector(self):
        """Remove vizinhos inativos, exceto os peers 'seeds' de confiança."""
        now = time.time()
        seeds = getattr(self.config, 'seeds', [])
        
        # Condição: o peer deve estar inativo E não pode ser um seed
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