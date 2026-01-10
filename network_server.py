import json
import logging
from flask import Flask, jsonify, send_file, request # Importamos o 'request'
from pathlib import Path

logger = logging.getLogger(__name__)

class NetworkServer:
    def __init__(self, config, account_mgr, peer_mgr, node_mgr):
        self.config = config
        self.account_mgr = account_mgr
        self.peer_mgr = peer_mgr
        self.node_mgr = node_mgr
        
        self.app = Flask(__name__)

        # --- NOVA ROTA: HANDSHAKE (Peer Discovery) ---

        @self.app.route('/handshake', methods=['POST'])
        def handshake():
            """
            Permite que um novo nó se apresente ao servidor.
            O BR agora registra o SC em sua lista de peers.
            """
            try:
                data = request.get_json()
                sender_ip = request.remote_addr
                
                # 1. Registra o nó que ligou (SC)
                new_address = f"{sender_ip}:{data.get('port')}"
                self.peer_mgr.add_peer_by_address(new_address)
                
                # 2. Registra os amigos do nó que ligou (SP e outros)
                other_peers = data.get('known_peers', [])
                for peer in other_peers:
                    # Evita que o nó adicione a si mesmo na própria agenda
                    if peer != f"{self.config.node_host}:{self.config.node_port}":
                        self.peer_mgr.add_peer_by_address(peer)
                    
                if not data or 'port' not in data:
                    return jsonify({"error": "Porta de escuta não informada"}), 400
                
                # Captura o IP de origem e a porta informada pelo vizinho
                peer_ip = request.remote_addr
                peer_port = data['port']
                peer_address = f"{peer_ip}:{peer_port}"
                
                print(f"[DEBUG] Recebi handshake de: {request.remote_addr}")
                
                # O Node BR adiciona o Node SC na 'agenda' (peers.json)
                self.peer_mgr.add_peer_by_address(peer_address)
                
                return jsonify({
                    "status": "accepted",
                    "node_id": self.config.node_id,
                    "message": f"Bem-vindo à rede NodeCash, {peer_address}!"
                }), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # --- ROTAS EXISTENTES ---

        @self.app.route('/accounts', methods=['GET'])
        def get_accounts():
            try:
                return jsonify(self.account_mgr.accounts), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            return jsonify({
                "node_id": self.config.node_id,
                "version": "1.0.0",
                "accounts_count": len(self.account_mgr.accounts)
            }), 200

        # ... (mantive as rotas de download e references omitidas para brevidade)

    def start(self):
        print(f"[*] Network Server ativo em http://{self.config.node_host}:{self.config.node_port}")
        self.app.run(
            host=self.config.node_host, 
            port=self.config.node_port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )