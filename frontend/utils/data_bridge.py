import pandas as pd
import random
from datetime import datetime, timedelta

def get_node_status(node_name):
    """
    Retorna métricas realistas baseadas na localização do Node.
    """
    # Lógica de diferenciação por região
    config = {
        "BR": {"latency_range": (15, 25), "peer_range": (40, 60), "uptime": "99.99%"},
        "SC": {"latency_range": (10, 18), "peer_range": (20, 35), "uptime": "99.95%"},
        "SP": {"latency_range": (5, 12),  "peer_range": (50, 80), "uptime": "99.90%"}
    }
    
    node_cfg = config.get(node_name, config["BR"])
    
    return {
        "id": node_name,
        "status": "Online" if node_name != "SP" else "Warning", # SP com alerta para teste
        "uptime": node_cfg["uptime"],
        "peers": random.randint(*node_cfg["peer_range"]),
        "latencia": f"{random.randint(*node_cfg["latency_range"])}ms",
        "last_ping": datetime.now().strftime("%H:%M:%S")
    }

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