class AccountManager:
    def __init__(self, config, storage_provider, account_service):
        self.config = config
        self.storage = storage_provider  # Especialista em pastas
        self.service = account_service   # Especialista em regras de negócio
        
        # Carrega as contas usando o serviço
        self.accounts = self.service.load_all_accounts()
        print(f"[*] AccountManager: {len(self.accounts)} contas inicializadas via Service.")

    def get_user_folder_name(self, user_id: str):
        # Apenas repassa a responsabilidade para o provedor de storage
        return self.storage.get_user_folder_name(user_id)

    def add_account(self, account_data):
        """Usa o serviço para validar e salvar uma nova conta."""
        if any(acc['user'] == account_data['user'] for acc in self.accounts):
            return False
            
        self.accounts.append(account_data)
        self.service.save_account(self.accounts)
        print(f"[*] Conta '{account_data['user']}' persistida com sucesso.")
        return True

    def get_local_sequence(self, user_id: str):
        """Busca a sequência no storage através do caminho resolvido pelo provider."""
        ref_path = self.storage.get_user_storage_path(user_id) / "references.json"
        if ref_path.exists():
            import json
            try:
                with open(ref_path, "r") as f:
                    return json.load(f).get("sequence", 0)
            except: pass
        return 0

    def save_remote_envelope(self, user_id, data_bytes, sequence, file_hash):
        """Coordena o salvamento do arquivo e a atualização do mapa de referências."""
        user_dir = self.storage.get_user_storage_path(user_id)
        filename = f"{str(sequence).zfill(4)}.dat.gz"
        file_path = user_dir / filename
        
        try:
            with open(file_path, "wb") as f:
                f.write(data_bytes)
            
            # Delega a atualização do JSON de referência para o serviço
            self.service.update_references(user_id, sequence, file_hash)
            return True
        except Exception as e:
            print(f"[!] Erro ao salvar envelope: {e}")
            return False