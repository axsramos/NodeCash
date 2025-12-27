import requests
import time
import threading
import json
from pathlib import Path

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
        while self.running:
            try:
                self.sync_with_peers()
            except Exception as e:
                print(f"[!] Erro crítico no loop de sincronização: {e}")
            
            time.sleep(self.config.sync_interval)

    def sync_with_peers(self):
        """Varre todos os peers conhecidos em busca de contas e atualizações."""
        targets = self.peer_mgr.get_all_targets()
        my_address = f"{self.config.node_host}:{self.config.node_port}"
        
        for target in targets:
            # Não sincroniza consigo mesmo
            if target == my_address:
                continue

            try:
                # 1. Busca a lista de contas do Peer (Descoberta)
                response = requests.get(f"http://{target}/accounts", timeout=5)
                if response.status_code != 200:
                    continue
                
                remote_accounts = response.json()
                for acc in remote_accounts:
                    # Persiste a conta no nó local (SC) se ela for nova
                    # Isso cria o accounts.json em data/system se necessário
                    self.account_mgr.add_account(acc)
                    
                    # 2. Verifica se o peer tem arquivos novos para este usuário
                    self._check_for_updates(target, acc['user'])

            except Exception:
                # Falhas de conexão são ignoradas; o PeerManager/GC lidam com peers mortos
                pass

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