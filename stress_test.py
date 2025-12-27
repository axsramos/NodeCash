import os
import time
import random
from pathlib import Path
from config import Config
from storage_provider import StorageProvider

def run_stress_test(num_files=50):
    print(f"[*] Iniciando Teste de Estresse: Gerando {num_files} arquivos...")
    
    config = Config()
    storage = StorageProvider(config)
    
    # Vamos simular o usuário 'axsramos'
    user_id = "axsramos"
    inbound_path = storage.get_user_inbound_path(user_id)
    
    print(f"[*] Alvo: {inbound_path}")

    for i in range(1, num_files + 1):
        filename = f"test_file_{i}.txt"
        file_path = inbound_path / filename
        
        # Gera conteúdo aleatório para simular dados reais
        content = f"Data: {time.time()} - Random ID: {random.randint(1000, 9999)}"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        if i % 10 == 0:
            print(f"[>] {i} arquivos gerados...")
        
        # Pequeno delay para não travar o SO, mas rápido o suficiente para o Watcher
        time.sleep(0.1)

    print(f"\n[V] Teste concluído! Agora observe os logs do seu Nó P2P.")

if __name__ == "__main__":
    run_stress_test(100) # Vamos de 100 arquivos logo de cara!