import time
import threading
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InboundWatcher:
    def __init__(self, config, account_mgr, network_client):
        """
        Consolidado com suporte a Broadcast em tempo real.
        """
        self.config = config
        self.account_mgr = account_mgr
        self.network_client = network_client
        # O Watcher utiliza o provider injetado no manager
        self.storage_ptr = account_mgr.storage 
        self.running = False

    def start(self):
        """Inicia o monitoramento da pasta inbound em segundo plano."""
        self.running = True
        # Garante a estrutura de pastas antes de começar
        self.sync_inbound_structure()
        
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print(f"[*] Inbound Watcher: Vigilância ativa via StorageProvider.")

    def sync_inbound_structure(self):
        """Garante que as pastas inbound existam para todas as contas."""
        for acc in self.account_mgr.accounts:
            user_id = acc['user'] if isinstance(acc, dict) else acc
            self.storage_ptr.get_user_inbound_path(user_id)

    def _run(self):
        """Loop de verificação periódica."""
        while self.running:
            try:
                self._check_for_new_files()
            except Exception as e:
                print(f"[!] Erro no loop do Watcher: {e}")
            time.sleep(2)

    def _check_for_new_files(self):
        """Varre as pastas inbound de cada conta cadastrada."""
        for acc in self.account_mgr.accounts:
            user_id = acc['user'] if isinstance(acc, dict) else acc
            inbound_path = self.storage_ptr.get_user_inbound_path(user_id)
            
            if inbound_path.exists():
                for file_path in inbound_path.iterdir():
                    if file_path.is_file():
                        self._process_file(user_id, file_path)

    def _process_file(self, user_id, file_path):
        """Processa a bolacha (arquivo), move para o storage e notifica a rede."""
        filename = file_path.name
        print(f"[*] Watcher: Novo arquivo detectado para {user_id}: {filename}")
        
        try:
            with open(file_path, "rb") as f:
                data_bytes = f.read()

            file_hash = hashlib.sha256(data_bytes).hexdigest()
            # Define a próxima sequência para o novo envelope
            current_seq = self.account_mgr.get_local_sequence(user_id) + 1
            
            # O Manager salva o arquivo e atualiza o references.json
            success = self.account_mgr.save_remote_envelope(
                user_id=user_id,
                data_bytes=data_bytes,
                sequence=current_seq,
                file_hash=file_hash
            )

            if success:
                file_path.unlink() # Remove da pasta inbound após o sucesso
                print(f"[V] Watcher: Arquivo {filename} processado e movido para storage.")
                
                # --- GATILHO DE BROADCAST (Sincronia Instantânea) ---
                print(f"[*] Notificando rede sobre novo envelope: {filename}")
                self.network_client.broadcast_new_envelope(user_id, filename)
            
        except Exception as e:
            print(f"[!] Watcher: Erro ao processar {filename}: {e}")