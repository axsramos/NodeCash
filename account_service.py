import json
from datetime import datetime
from pathlib import Path

class AccountService:
    def __init__(self, storage_provider, config):
        self.storage = storage_provider
        self.config = config
        self.accounts_file = self.storage.base_system / "accounts.json"

    def load_all_accounts(self) -> list:
        """Lê a base de contas ou cria a conta inicial baseada no .env."""
        if not self.accounts_file.exists():
            print("[*] Service: accounts.json não encontrado. Criando conta inicial...")
            return self._create_initial_account()
            
        try:
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if data else self._bootstrap_initial_account()
        except (json.JSONDecodeError, Exception) as e:
            print(f"[!] Erro ao ler accounts.json: {e}. Restaurando padrão...")
            return self._bootstrap_initial_account()
    
    def _bootstrap_initial_account(self) -> list:
        """Cria o registro inicial baseado nas variáveis do .env."""
        print(f"[*] Bootstrap: Gerando conta inicial para o usuário: {self.config.initial_user}")
        
        initial_acc = [{
            "user": self.config.initial_user,
            "name": self.config.initial_user_name,
            "profile": "admin",
            "repository": self.config.repository,
            "site": self.config.site,
            "status": "active"
        }]
        
        self.save_account(initial_acc)
        return initial_acc
    
    def _create_initial_account(self) -> list:
        """Gera a primeira conta a partir das variáveis de ambiente."""
        initial_acc = [{
            "user": self.config.initial_user,
            "name": self.config.initial_user_name,
            "profile": "admin",
            "repository": getattr(self.config, 'repository', ""),
            "site": getattr(self.config, 'site', "portalsiti.com.br"),
            "status": "active"
        }]
        
        # Já salva no disco para o arquivo passar a existir
        self.save_account(initial_acc)
        return initial_acc

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