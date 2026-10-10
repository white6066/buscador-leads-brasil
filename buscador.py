import requests
import time
from datetime import datetime, timedelta

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

# CNAEs Alvo
# 9602-5/02: Estética / Beleza
# 9313-1/00: Academias / Fitness
# 8630-5/04: Odontologia
# 8630-5/03: Consultórios Médicos
SETORES_ALVO = [
    {"cnae": "9602502", "categoria": "Estética"},
    {"cnae": "9313100", "categoria": "Academia"},
    {"cnae": "8630504", "categoria": "Odonto"},
    {"cnae": "8630503", "categoria": "Médico"}
]

def buscar_cnpjs_ultimas_24h():
    # Calcula a data de ontem (últimas 24 horas)
    hoje = datetime.now()
    ontem = hoje - timedelta(days=1)
    
    data_inicio_filtro = ontem.strftime("%Y-%m-%d")
    data_fim_filtro = hoje.strftime("%Y-%m-%d")
    
    print(f"--- A buscar CNPJs abertos entre {data_inicio_filtro} e {data_fim_filtro} ---")

    for setor in SETORES_ALVO:
        cnae = setor["cnae"]
        categoria = setor["categoria"]
        
        print(f"\n[+] A pesquisar novos registos para: {categoria} (CNAE {cnae})...")
        
        payload = {
            "cnae_fiscal": cnae,
            "data_inicio_atividade_gte": data_inicio_filtro,
            "data_inicio_atividade_lte": data_fim_filtro,
            "limite": 50
        }
        
        try:
            response = requests.post("https://api.casadosdados.com.br/v2/public/cnpj/search", json=payload, timeout=15)
            
            if response.status_code == 200:
                empresas = response.json().get("data", {}).get("cnpj", [])
                print(f"   -> {len(empresas)} novas empresas encontradas nas últimas 24h!")
                
                for emp in empresas:
                    lead = {
                        "razao_social": emp.get("razao_social", "N/A"),
                        "nome_fantasia": emp.get("nome_fantasia") or emp.get("razao_social"),
                        "categoria": categoria,
                        "data_abertura": emp.get("data_inicio_atividade", data_inicio_filtro),
                        "cnpj": emp.get("cnpj", "N/A"),
                        "endereco": f"{emp.get('logradouro', '')}, {emp.get('numero', '')} - {emp.get('bairro', '')}, {emp.get('municipio', '')} - {emp.get('uf', '')}",
                        "telefone": emp.get("telefone1", "N/A"),
                        "email": emp.get("email", "N/A"),
                        "google_maps": f"https://www.google.com/maps/search/?api=1&query={emp.get('nome_fantasia', emp.get('razao_social'))}+{emp.get('municipio')}"
                    }
                    
                    envio = requests.post(MAKE_WEBHOOK_URL, json=lead)
                    if envio.status_code == 200:
                        print(f"   [ENVIADO] {lead['nome_fantasia']} ({lead['cnpj']})")
                    
                    time.sleep(1)
            else:
                print(f"   [AVISO] Nenhuma nova empresa encontrada hoje para {categoria} ou limite atingido.")
                
        except Exception as e:
            print(f"   [ERRO] Falha ao consultar setor {categoria}: {e}")
            
    print("\n--- Varredura das últimas 24 horas concluída! ---")

if __name__ == "__main__":
    buscar_cnpjs_ultimas_24h()
