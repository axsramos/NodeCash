import json
from pathlib import Path

class PeerManager:
    def __init__(self, config, peers_file="data/system/peers.json"):
        self.config = config
        self.peers_file = Path(peers_file)
        self.peers = []
        
        # Garante que a pasta system exista
        self.peers_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_peers()

    def _load_peers(self):
        """Carrega a lista de IPs dos vizinhos do disco."""
        if self.peers_file.exists():
            try:
                with open(self.peers_file, "r", encoding="utf-8") as f:
                    self.peers = json.load(f)
                print(f"[*] {len(self.peers)} peers carregados da lista de confiança.")
            except Exception as e:
                print(f"[!] Erro ao carregar peers.json: {e}")
                self.peers = []
        else:
            # Se não existir, inicia com os seeds do .env
            self.peers = self.config.seeds if hasattr(self.config, 'seeds') else []
            self._save_peers()

    def _save_peers(self):
        """Salva a lista atualizada de peers no disco."""
        try:
            with open(self.peers_file, "w", encoding="utf-8") as f:
                json.dump(self.peers, f, indent=4)
        except Exception as e:
            print(f"[!] Erro ao salvar peers.json: {e}")

    def get_all_targets(self):
        """Retorna a lista de endereços (host:port) para o NetworkClient."""
        return self.peers

    def add_peer(self, peer_address):
        """Adiciona um novo vizinho à rede se ele ainda não existir."""
        if peer_address not in self.peers:
            self.peers.append(peer_address)
            self._save_peers()
            print(f"[*] Novo peer adicionado: {peer_address}")
            return True
        return False

    def remove_peer(self, peer_address):
        """Remove um vizinho que está offline (chamado pelo GC ou Client)."""
        if peer_address in self.peers:
            self.peers.remove(peer_address)
            self._save_peers()
            print(f"[-] Peer removido por inatividade: {peer_address}")
            return True
        return False