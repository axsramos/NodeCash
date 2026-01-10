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
        """
        Guarda o ficheiro recebido na pasta correta: data/storage/{user_id}/
        """
        try:
            # O ERRO ESTAVA AQUI: A variável precisa ser definida primeiro
            target_dir = self.storage.get_user_storage_path(user_id)
            
            # Agora podemos usar 'target_dir' com segurança
            target_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{sequence}_{file_hash}.env"
            file_path = target_dir / filename
            
            with open(file_path, "wb") as f:
                f.write(data_bytes)
                
            print(f"[+] Arquivo salvo com sucesso: {file_path}")
            return True
        except Exception as e:
            # Se target_dir não foi definido antes do erro, o print abaixo falharia.
            # Por isso usamos uma mensagem genérica ou capturamos o erro corretamente.
            print(f"[!] Erro ao gravar envelope no disco: {e}")
            return False