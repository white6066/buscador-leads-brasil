import requests
import sqlite3
import tempfile
import os
import time
from datetime import datetime, timedelta

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

def buscar_empresas_ultimos_30_dias():
    # Calcula exatamente a data de há 30 dias atrás até hoje
    data_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    print(f"A procurar empresas criadas desde {data_limite} (últimos 30 dias)...")
    
    # Base de dados pública indexada com os dados abertos da Receita Federal
    url_base_publica = "https://raw.githubusercontent.com/codeedu/dados-abertos-receita-federal/main/sample.db"
    
    try:
        print("A descarregar índice público atualizado...")
        response = requests.get(url_base_publica, stream=True, timeout=30)
        
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
                
            # Ligação à base SQLite descarregada temporariamente
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            
            # Query com filtro temporal estrito para os últimos 30 dias e limite de 400 empresas
            query = """
                SELECT razao_social, nome_fantasia, cnpj, data_inicio_atividade, logradouro, numero, bairro, municipio, uf, ddd1, telefone1, email 
                FROM empresas_recentes 
                WHERE data_inicio_atividade >= ?
                ORDER BY data_inicio_atividade DESC 
                LIMIT 400;
            """
            
            cursor.execute(query, (data_limite,))
            empresas = cursor.fetchall()
            print(f"Encontradas {len(empresas)} empresas criadas nos últimos 30 dias!")
            
            for emp in empresas:
                lead = {
                    "razao_social": emp[0] or "N/A",
                    "nome_fantasia": emp[1] or emp[0] or "N/A",
                    "categoria": "Recente (30 dias)",
                    "data_abertura": emp[3] or "N/A",
                    "cnpj": emp[2] or "N/A",
                    "endereco": f"{emp[4]}, {emp[5]} - {emp[6]}, {emp[7]} - {emp[8]}",
                    "telefone": f"({emp[9]}) {emp[10]}" if emp[9] and emp[10] else "N/A",
                    "email": emp[11] or "N/A",
                    "google_maps": f"https://www.google.com/maps/search/?api=1&query={emp[1] or emp[0]}+{emp[7]}"
                }
                
                # Envia os dados filtrados diretamente para o Make.com / Google Sheets
                envio = requests.post(MAKE_WEBHOOK_URL, json=lead, timeout=10)
                if envio.status_code == 200:
                    print(f"[ENVIADO] {lead['nome_fantasia']} ({emp[7]}/{emp[8]}) - Abertura: {emp[3]}")
                time.sleep(0.3)
                
            conn.close()
            os.unlink(tmp_path)
        else:
            print("[AVISO] O índice público está temporariamente indisponível.")
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar base de dados: {e}")

if __name__ == "__main__":
    buscar_empresas_ultimos_30_dias()
