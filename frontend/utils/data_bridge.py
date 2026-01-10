import json
import os
import pandas as pd
import random
from datetime import datetime, timedelta

JSON_PATH = os.path.join('data', 'system', 'status.json')

def load_data():
    """Lê o arquivo JSON da raiz"""
    try:
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r') as f:
                return json.load(f)
        return None
    except Exception:
        return None
    
def get_node_status(node_name):
    data = load_data()
    if data and node_name in data['nodes']:
        node = data['nodes'][node_name]
        return {
            "id": node_name,
            "status": node['status'],
            "uptime": "99.9%", # Valor fixo por enquanto
            "peers": node['peers'],
            "latencia": f"{node['latencia']}ms",
            "last_ping": data['last_update']
        }
    return {"status": "Offline", "latencia": "0ms", "peers": 0, "last_ping": "--"}

def get_network_history():
    """
    Gera um histórico de tráfego para os gráficos.
    """
    last_7_days = [(datetime.now() - timedelta(days=i)).strftime("%d/%m") for i in range(7)]
    last_7_days.reverse()
    
    data = {
        "Dia": last_7_days,
        "Node BR": [random.randint(100, 150) for _ in range(7)],
        "Node SC": [random.randint(80, 120) for _ in range(7)],
        "Node SP": [random.randint(150, 250) for _ in range(7)]
    }
    return pd.DataFrame(data)

def get_financial_summary():
    """
    Simula o rendimento (Cash) acumulado.
    """
    return {
        "total_brl": 1450.50,
        "daily_yield": 42.15,
        "estimated_monthly": 1260.00
    }