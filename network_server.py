import json
from flask import Flask, jsonify, send_file
from pathlib import Path

class NetworkServer:
    def __init__(self, config, account_mgr, peer_mgr, node_mgr):
        self.config = config
        self.account_mgr = account_mgr
        self.peer_mgr = peer_mgr
        self.node_mgr = node_mgr
        
        self.app = Flask(__name__)

        # --- DEFINIÇÃO DAS ROTAS (DENTRO DO ESCOPO DA CLASSE) ---

        @self.app.route('/accounts', methods=['GET'])
        def get_accounts():
            """Retorna a lista de contas autorizadas neste nó."""
            try:
                return jsonify(self.account_mgr.accounts), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/accounts/<user_id>/references', methods=['GET'])
        def get_user_references(user_id):
            """Busca o references.json usando o StorageProvider via AccountManager."""
            # Agora pedimos o caminho correto para o StorageProvider que está dentro do Manager
            folder_path = self.account_mgr.storage.get_user_storage_path(user_id)
            ref_path = folder_path / "references.json"
            
            if ref_path.exists():
                try:
                    with open(ref_path, "r", encoding="utf-8") as f:
                        return jsonify(json.load(f)), 200
                except Exception as e:
                    return jsonify({"error": f"Erro ao ler referências: {e}"}), 500
            
            return jsonify({"user": user_id, "sequence": 0, "files": []}), 200

        @self.app.route('/accounts/<user_id>/download/<filename>', methods=['GET'])
        def download_envelope(user_id, filename):
            """Entrega o arquivo usando o caminho resolvido pelo StorageProvider."""
            folder_path = self.account_mgr.storage.get_user_storage_path(user_id)
            file_path = folder_path / filename
            
            if file_path.exists():
                return send_file(file_path, as_attachment=True)
            
            return jsonify({"error": "Arquivo não encontrado"}), 404

        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Retorna o status básico do nó para o PeerManager."""
            return jsonify({
                "node_id": self.config.node_id,
                "version": "1.0.0",
                "accounts_count": len(self.account_mgr.accounts)
            }), 200

    def start(self):
        """Inicia o servidor Flask no host e porta configurados."""
        print(f"[*] Network Server ativo em http://{self.config.node_host}:{self.config.node_port}")
        # threaded=True permite lidar com múltiplas requisições de sincronização
        self.app.run(
            host=self.config.node_host, 
            port=self.config.node_port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )