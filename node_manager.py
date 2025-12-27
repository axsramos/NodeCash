import time
from datetime import datetime

class NodeManager:
    def __init__(self, config):
        self.config = config
        self.start_time = datetime.now()
        self.node_status = "STARTING"
        
        # Identidade do nó vinda do .env
        self.node_id = self.config.node_id
        self.host = self.config.node_host
        self.port = self.config.node_port

    def get_info(self):
        """Retorna as informações de saúde e identidade do nó."""
        return {
            "node_id": self.node_id,
            "status": self.node_status,
            "uptime": str(datetime.now() - self.start_time),
            "address": f"{self.host}:{self.port}",
            "timestamp": int(time.time())
        }

    def set_status(self, status: str):
        """Atualiza o estado atual do nó (ex: READY, SYNCING, BUSY)."""
        self.node_status = status
        print(f"[*] NodeManager: Status alterado para {status}")

    def is_healthy(self):
        """Verificação básica se o nó está operacional."""
        # Aqui você poderia adicionar lógicas de check de disco ou rede
        return True