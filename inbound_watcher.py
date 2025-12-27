import time
import threading
import hashlib
from pathlib import Path

class InboundWatcher:
    def __init__(self, config, account_mgr):
        self.config = config
        self.account_mgr = account_mgr
        # O Watcher agora usa o provider que está dentro do manager
        self.storage_ptr = account_mgr.storage 
        self.running = False

    def start(self):
        """Inicia o monitoramento da pasta inbound."""
        self.running = True
        # Garante que as pastas de entrada de todos os usuários existam
        self.sync_inbound_structure()
        
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print(f"[*] Inbound Watcher: Vigilância ativa via StorageProvider.")

    def sync_inbound_structure(self):
        """Usa o provider para garantir que as pastas inbound (Hash/Real) existam."""
        for acc in self.account_mgr.accounts:
            # O provider já resolve se é Hash ou nome real
            self.storage_ptr.get_user_inbound_path(acc['user'])

    def _run(self):
        while self.running:
            try:
                self._check_for_new_files()
            except Exception as e:
                print(f"[!] Erro no loop do Watcher: {e}")
            time.sleep(2)

    def _check_for_new_files(self):
        """Varre apenas as pastas inbound que pertencem a usuários conhecidos."""
        for acc in self.account_mgr.accounts:
            user_id = acc['user']
            inbound_path = self.storage_ptr.get_user_inbound_path(user_id)

            for file in inbound_path.glob("*"):
                if file.is_file():
                    self._process_file(user_id, file)

    def _process_file(self, user_id, file_path):
        """Lê o arquivo e solicita ao Manager que salve no storage oficial."""
        print(f"[*] Watcher: Novo arquivo detectado para {user_id}: {file_path.name}")
        
        try:
            with open(file_path, "rb") as f:
                data_bytes = f.read()

            file_hash = hashlib.sha256(data_bytes).hexdigest()
            current_seq = self.account_mgr.get_local_sequence(user_id) + 1
            
            # O Manager cuida de salvar e atualizar o references.json
            success = self.account_mgr.save_remote_envelope(
                user_id=user_id,
                data_bytes=data_bytes,
                sequence=current_seq,
                file_hash=file_hash
            )

            if success:
                file_path.unlink() # Remove do inbound após sucesso
                print(f"[V] Watcher: Arquivo processado e movido para storage.")
            
        except Exception as e:
            print(f"[!] Watcher: Erro ao processar {file_path.name}: {e}")

    def stop(self):
        self.running = False