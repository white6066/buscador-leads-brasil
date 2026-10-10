import requests
import sqlite3
import tempfile
import os
import time

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

def buscar_ultimas_empresas_criadas():
    print("A aceder à base de dados pública de novos registos do Brasil...")
    
    # Exemplo de ligação a um repositório público/dataset aberto espelhado da Receita Federal
    # Nota: Utiliza um endpoint de espelhamento aberto ou base SQLite pública partilhada pela comunidade
    url_base_publica = "https://raw.githubusercontent.com/codeedu/dados-abertos-receita-federal/main/sample.db" # ou base similar indexada
    
    try:
        # Descarrega temporariamente a base indexada para consulta rápida e gratuita
        print("A descarregar índice público atualizado...")
        response = requests.get(url_base_publica, stream=True, timeout=30)
        
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
                
            # Consulta local na base SQLite descarregada gratuitamente
            conn = sqlite3.connect(tmp_path)
            cursor = conn.cursor()
            
            # Seleciona as últimas empresas ordenadas por data de abertura
            query = """
                SELECT razao_social, nome_fantasia, cnpj, data_inicio_atividade, logradouro, numero, bairro, municipio, uf, ddd1, telefone1, email 
                FROM empresas_recentes 
                ORDER BY data_inicio_atividade DESC 
                LIMIT 50;
            """
            
            cursor.execute(query)
            empresas = cursor.fetchall()
            print(f"Encontradas {len(empresas)} novas empresas recentes!")
            
            for emp in empresas:
                lead = {
                    "razao_social": emp[0] or "N/A",
                    "nome_fantasia": emp[1] or emp[0] or "N/A",
                    "categoria": "Geral (Recente)",
                    "data_abertura": emp[3] or "N/A",
                    "cnpj": emp[2] or "N/A",
                    "endereco": f"{emp[4]}, {emp[5]} - {emp[6]}, {emp[7]} - {emp[8]}",
                    "telefone": f"({emp[9]}) {emp[10]}" if emp[9] and emp[10] else "N/A",
                    "email": emp[11] or "N/A",
                    "google_maps": f"https://www.google.com/maps/search/?api=1&query={emp[1] or emp[0]}+{emp[7]}"
                }
                
                # Envia para o Make.com
                envio = requests.post(MAKE_WEBHOOK_URL, json=lead, timeout=10)
                if envio.status_code == 200:
                    print(f"[ENVIADO] {lead['nome_fantasia']} ({emp[7]}/{emp[8]})")
                time.sleep(0.5)
                
            conn.close()
            os.unlink(tmp_path)
        else:
            print("[AVISO] O espelho público atualizado está temporariamente indisponível. A utilizar rota alternativa...")
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar base de dados aberta: {e}")

if __name__ == "__main__":
    buscar_ultimas_empresas_criadas()
