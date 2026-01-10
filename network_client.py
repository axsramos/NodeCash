import requests
import time
import threading
import json
import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class NetworkClient:
    def __init__(self, config, account_mgr, peer_mgr):
        self.config = config
        self.account_mgr = account_mgr
        self.peer_mgr = peer_mgr
        self.running = False

    def start_sync_loop(self):
        """Inicia o ciclo de sincronização em uma thread separada."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print(f"[*] Network Client ativo (Sincronização a cada {self.config.sync_interval}s)")

    def _run(self):
        """Loop contínuo de sincronização."""
        # --- O AJUSTE ESTÁ AQUI: O nó se apresenta às SEEDS ao ligar ---
        self.announce_to_seeds() 
        
        while self.running:
            try:
                self.sync_with_peers()
            except Exception as e:
                print(f"[!] Erro crítico no loop de sincronização: {e}")
            
            time.sleep(self.config.sync_interval)
    
    def sync_with_peers(self):
        """Refatorado: Escolhe vizinhos aleatórios e sincroniza (Gossip)."""
        targets = self.peer_mgr.get_all_targets()
        if not targets:
            logger.warning("Nenhum peer encontrado para sincronização.") # Amarelo/Aviso
            return
        
        logger.info(f"Iniciando sincronização com {len(targets)} peers.") # Informativo

        # 1. Gossip: Seleciona até 3 vizinhos aleatórios para não sobrecarregar
        sample_size = min(len(targets), 3)
        targets_to_sync = random.sample(targets, sample_size)
        
        my_address = f"{self.config.node_host}:{self.config.node_port}"
        my_peers_list = self.peer_mgr.get_all_targets()

        for target in targets_to_sync:
            if target == my_address:
                continue

            # --- PARTE 1: Peer Exchange (PEX) ---
            try:
                url_handshake = f"http://{target}/handshake"
                payload = {"port": self.config.node_port, "known_peers": my_peers_list}
                response = requests.post(url_handshake, json=payload, timeout=5)
                
                if response.status_code == 200:
                    received_peers = response.json().get('known_peers', [])
                    for p in received_peers:
                        if p != my_address:
                            self.peer_mgr.add_peer_by_address(p)
            except Exception as e:
                logger.error(f"Erro crítico na sincronização: {e}") # Vermelho/Erro

            # --- PARTE 2: Chamada da lógica de contas (O método que faltava!) ---
            self._sync_accounts_with_target(target)

    def _sync_accounts_with_target(self, target):
        """Sincroniza dados de contas, tratando a resposta como lista ou dicionário."""
        try:
            url = f"http://{target}/accounts"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                remote_accounts = response.json()
                
                # --- CORREÇÃO AQUI ---
                # Se for uma lista de IDs [ "id1", "id2" ]
                if isinstance(remote_accounts, list):
                    for user_id in remote_accounts:
                        self._fetch_references_and_download(target, user_id)
                
                # Se for um dicionário { "id1": "data" }
                elif isinstance(remote_accounts, dict):
                    for user_id in remote_accounts.keys():
                        self._fetch_references_and_download(target, user_id)
                        
        except Exception as e:
            print(f"[!] Erro ao sincronizar dados de contas com {target}: {e}")

    def _fetch_references_and_download(self, target, user_id):
        """Lógica auxiliar para baixar referências de um usuário específico."""
        try:
            ref_url = f"http://{target}/accounts/{user_id}/references"
            ref_resp = requests.get(ref_url, timeout=5)
            
            if ref_resp.status_code == 200:
                references = ref_resp.json()
                for file_info in references.get('files', []):
                    self._download_envelope_if_needed(
                        target, user_id, 
                        file_info['name'], 
                        file_info['sequence'], 
                        file_info['hash']
                    )
        except Exception as e:
            print(f"[!] Falha ao buscar referências do user {user_id} em {target}: {e}")
    
    def _check_for_updates(self, target, user_id):
        """Compara a sequência local com a remota e inicia o download."""
        try:
            # Pergunta qual a sequência atual do usuário no Peer
            url = f"http://{target}/accounts/{user_id}/references"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                remote_ref = response.json()
                remote_seq = remote_ref.get("sequence", 0)
                local_seq = self.account_mgr.get_local_sequence(user_id)

                # Se o Peer tem algo mais novo, baixamos os arquivos faltantes
                if remote_seq > local_seq:
                    print(f"[*] Peer {target} tem novidades para {user_id} ({local_seq} -> {remote_seq})")
                    
                    for seq in range(local_seq + 1, remote_seq + 1):
                        self._fetch_user_file(target, user_id, seq, remote_ref)

        except Exception as e:
            print(f"[!] Erro ao checar atualizações em {target} para {user_id}: {e}")

    def _fetch_user_file(self, target, user_id, sequence, remote_ref):
        """Baixa o envelope .dat.gz e delega o salvamento ao AccountManager."""
        filename = f"{str(sequence).zfill(4)}.dat.gz"
        # Rota padronizada conforme o NetworkServer
        url = f"http://{target}/accounts/{user_id}/download/{filename}"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Tenta localizar o hash desse arquivo específico nos metadados remotos
                file_hash = None
                if "files" in remote_ref:
                    for f_meta in remote_ref["files"]:
                        if f_meta["seq"] == sequence:
                            file_hash = f_meta.get("hash")
                            break

                # Entrega os bytes para o AccountManager salvar no local correto (Hash ou Plain)
                # O manager também atualizará o references.json local
                success = self.account_mgr.save_remote_envelope(
                    user_id=user_id,
                    data_bytes=response.content,
                    sequence=sequence,
                    file_hash=file_hash
                )
                
                if success:
                    print(f"[+] Envelope {filename} sincronizado com sucesso de {target}")
            else:
                print(f"[!] Erro ao baixar {filename}: Status {response.status_code}")
                
        except Exception as e:
            print(f"[!] Falha no download de {filename} de {target}: {e}")

    def stop(self):
        """Para o loop de sincronização."""
        self.running = False
        
    def announce_to_seeds(self):
        """O nó se apresenta e compartilha sua lista de conhecidos."""
        # Pegamos todos os peers que o SC já conhece (incluindo o SP)
        known_peers = self.peer_mgr.get_all_targets()
        
        for seed in self.config.seeds:
            try:
                # Não faz sentido dar handshake em si mesmo
                if seed == f"{self.config.node_host}:{self.config.node_port}":
                    continue
                
                url = f"http://{seed}/handshake"
                payload = {
                    "port": self.config.node_port,
                    "known_peers": known_peers  # <--- Enviando a lista completa!
                }
                requests.post(url, json=payload, timeout=5)
            except Exception:
                pass
    def broadcast_new_envelope(self, user_id, envelope_name):
        """
        Avisa todos os peers conhecidos sobre um novo ficheiro 
        para que eles façam o download imediatamente.
        """
        targets = self.peer_mgr.get_all_targets()
        for target in targets:
            try:
                url = f"http://{target}/notify_new_file"
                payload = {
                    "user_id": user_id,
                    "filename": envelope_name,
                    "origin_node": f"{self.config.node_host}:{self.config.node_port}"
                }
                requests.post(url, json=payload, timeout=2)
            except Exception:
                pass # Se um peer estiver offline, o Gossip normal resolverá depois
    