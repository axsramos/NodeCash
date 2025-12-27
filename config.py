import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Carrega as variáveis do arquivo .env
        load_dotenv()
        
        # --- IDENTIDADE DO NÓ ---
        # Nome único do nó (ex: NODECASH-BR ou NODECASH-SC)
        self.node_id = os.getenv("NODE_ID", "NODE-DEFAULT")
        
        # --- CONFIGURAÇÕES DE REDE ---
        self.node_host = os.getenv("NODE_HOST", "127.0.0.1")
        try:
            self.node_port = int(os.getenv("NODE_PORT", 3000))
        except (TypeError, ValueError):
            self.node_port = 3000

        # --- REGRAS DE ARMAZENAMENTO ---
        # Define se usa o nome real do usuário ou Hash SHA-256 nas pastas
        self.use_plain_names = os.getenv("USE_PLAIN_USER_NAMES", "False").lower() == "true"
        
        # --- INTERVALOS DE TEMPO (EM SEGUNDOS) ---
        self.sync_interval = int(os.getenv("SYNC_INTERVAL", 30))
        self.gc_interval = int(os.getenv("GC_INTERVAL", 60))
        
        # --- DESCOBERTA DE PEERS ---
        # Lista de IPs vizinhos separados por vírgula no .env
        seeds_raw = os.getenv("SEEDS", "")
        self.seeds = [s.strip() for s in seeds_raw.split(",")] if seeds_raw else []

        # --- DEBUG ---
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

    def __repr__(self):
        return f"<Config Node:{self.node_id} Port:{self.node_port}>"