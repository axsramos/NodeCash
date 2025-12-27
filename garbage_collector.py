import time
import shutil
import threading
from pathlib import Path
from datetime import datetime, timedelta

class GarbageCollector:
    def __init__(self, config, account_mgr):
        self.config = config
        self.account_mgr = account_mgr
        self.storage_ptr = account_mgr.storage  # Uso do novo Provider
        self.running = False

    def start(self):
        """Inicia o ciclo de limpeza em background."""
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()
        print(f"[*] Garbage Collector: Ativo e integrado ao StorageProvider.")

    def _run(self):
        while self.running:
            try:
                self.cleanup_orphan_folders()
                self.cleanup_old_inbound_files()
            except Exception as e:
                print(f"[!] Erro no Garbage Collector: {e}")
            
            time.sleep(self.config.gc_interval)

    def cleanup_orphan_folders(self):
        """Remove pastas no storage que não constam na lista oficial de contas."""
        base_storage = self.storage_ptr.base_storage
        if not base_storage.exists():
            return

        # Mapeia quais são os nomes de pasta válidos hoje (Hash ou Real)
        valid_folder_names = [
            self.storage_ptr.get_user_folder_name(acc['user']) 
            for acc in self.account_mgr.accounts
        ]

        for folder in base_storage.iterdir():
            if folder.is_dir() and folder.name not in valid_folder_names:
                print(f"[*] GC: Removendo pasta órfã: {folder.name}")
                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    print(f"[!] GC: Erro ao remover {folder.name}: {e}")

    def cleanup_old_inbound_files(self):
        """Limpa arquivos que ficaram 'presos' no inbound por mais de 24h."""
        base_inbound = self.storage_ptr.base_inbound
        if not base_inbound.exists():
            return

        threshold = datetime.now() - timedelta(hours=24)

        for user_folder in base_inbound.iterdir():
            if user_folder.is_dir():
                for file in user_folder.glob("*"):
                    file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if file_mtime < threshold:
                        print(f"[*] GC: Removendo arquivo antigo no inbound: {file.name}")
                        file.unlink()

    def stop(self):
        self.running = False