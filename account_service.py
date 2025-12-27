import json
from datetime import datetime
from pathlib import Path

class AccountService:
    def __init__(self, storage_provider):
        self.storage = storage_provider
        self.accounts_file = self.storage.base_system / "accounts.json"

    def load_all_accounts(self) -> list:
        """Lê a base de contas do sistema."""
        if not self.accounts_file.exists():
            return []
        try:
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Erro ao carregar banco de contas: {e}")
            return []

    def save_account(self, accounts_list: list):
        """Persiste a lista de contas atualizada."""
        with open(self.accounts_file, "w", encoding="utf-8") as f:
            json.dump(accounts_list, f, indent=4)

    def update_references(self, user_id, sequence, file_hash):
        """Orquestra a atualização do mapa de arquivos (references.json)."""
        ref_path = self.storage.get_user_storage_path(user_id) / "references.json"
        
        # Estrutura base caso o arquivo não exista
        data = {"user": user_id, "sequence": 0, "files": [], "last_sync": ""}
        
        if ref_path.exists():
            try:
                with open(ref_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                pass

        # Atualiza dados de sincronização
        data["sequence"] = max(data["sequence"], sequence)
        data["last_sync"] = str(datetime.now())
        
        # Evita duplicar metadados do mesmo arquivo
        if not any(f["seq"] == sequence for f in data["files"]):
            data["files"].append({
                "seq": sequence,
                "hash": file_hash,
                "ts": int(datetime.now().timestamp())
            })

        with open(ref_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)