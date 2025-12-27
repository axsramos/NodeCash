import hashlib
from pathlib import Path

class StorageProvider:
    def __init__(self, config):
        self.config = config
        # Definição dos caminhos base
        self.base_storage = Path("data/storage")
        self.base_system = Path("data/system")
        self.base_inbound = Path("data/inbound")
        
        # Garante a existência da infraestrutura física
        self._ensure_base_dirs()

    def _ensure_base_dirs(self):
        """Cria as pastas fundamentais se não existirem."""
        for path in [self.base_storage, self.base_system, self.base_inbound]:
            path.mkdir(parents=True, exist_ok=True)

    def get_user_folder_name(self, user_id: str) -> str:
        """Resolve o nome da pasta baseado na preferência de privacidade (Hash)."""
        if hasattr(self.config, 'use_plain_names') and self.config.use_plain_names:
            return user_id
        return hashlib.sha256(user_id.encode()).hexdigest()

    def get_user_storage_path(self, user_id: str) -> Path:
        """Retorna o caminho da pasta de arquivos finais do usuário."""
        path = self.base_storage / self.get_user_folder_name(user_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_user_inbound_path(self, user_id: str) -> Path:
        """Retorna o caminho da pasta onde o usuário 'solta' arquivos novos."""
        path = self.base_inbound / self.get_user_folder_name(user_id)
        path.mkdir(parents=True, exist_ok=True)
        return path