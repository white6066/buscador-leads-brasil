import requests
import time
from datetime import datetime, timedelta

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

# CNAEs Alvo (Estética, Academia, Odonto, Médico)
SETORES_ALVO = [
    {"cnae": "9602502", "categoria": "Estética"},
    {"cnae": "9313100", "categoria": "Academia"},
    {"cnae": "8630504", "categoria": "Odonto"},
    {"cnae": "8630503", "categoria": "Médico"}
]

def buscar_cnpjs_recentes():
    # Define o período de corte (últimos dias para garantir captura de novos registos)
    hoje = datetime.now()
    ontem = hoje - timedelta(days=3)
    data_limite = ontem.strftime("%Y-%m-%d")
    
    print(f"--- A iniciar busca pública de empresas abertas desde {data_limite} ---")

    # Estados alvo (focando em Mato Grosso e regiões principais)
    estados = ["MT", "SP", "PR"]

    for uf in estados:
        for setor in SETORES_ALVO:
            cnae = setor["cnae"]
            categoria = setor["categoria"]
            
            url = f"https://minhareceita.org/?uf={uf}&cnae={cnae}"
            print(f"A pesquisar em {uf} - {categoria} (CNAE {cnae})...")
            
            try:
                response = requests.get(url, timeout=20)
                if response.status_code == 200:
                    dados = response.json()
                    
                    empresas = dados if isinstance(dados, list) else dados.get("resultado", [])
                    if not empresas and isinstance(dados, dict) and "cnpj" in dados:
                        empresas = [dados]
                        
                    print(f"   -> Encontradas {len(empresas)} empresas no total para {uf}.")
                    
                    for emp in empresas:
                        data_abertura = emp.get("data_inicio_atividade") or emp.get("data_abertura", "")
                        
                        # Filtra por data recente
                        if data_abertura >= data_limite:
                            lead = {
                                "razao_social": emp.get("razao_social", "N/A"),
                                "nome_fantasia": emp.get("nome_fantasia") or emp.get("razao_social", "N/A"),
                                "categoria": categoria,
                                "data_abertura": data_abertura,
                                "cnpj": emp.get("cnpj", "N/A"),
                                "endereco": f"{emp.get('logradouro', '')}, {emp.get('numero', '')} - {emp.get('bairro', '')}, {emp.get('municipio', '')} - {emp.get('uf', uf)}",
                                "telefone": emp.get("ddd_telefone_1", "N/A"),
                                "email": emp.get("email", "N/A"),
                                "google_maps": f"https://www.google.com/maps/search/?api=1&query={emp.get('nome_fantasia', emp.get('razao_social'))}+{emp.get('municipio', '')}"
                            }
                            
                            # Envia para o Make.com
                            envio = requests.post(MAKE_WEBHOOK_URL, json=lead)
                            if envio.status_code == 200:
                                print(f"   [ENVIADO] {lead['nome_fantasia']} ({lead['cnpj']})")
                            time.sleep(0.5)
                else:
                    print(f"   [AVISO] Sem resultados para {uf} - {categoria}")
            except Exception as e:
                print(f"   [ERRO] Falha na consulta: {e}")
                
            time.sleep(1)

if __name__ == "__main__":
    buscar_cnpjs_recentes()
