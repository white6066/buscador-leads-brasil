import requests
import time

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

LEADS_REAIS_NACIONAL = [
    {"cnpj": "07594910000184", "categoria": "Academia"},
    {"cnpj": "31339301000109", "categoria": "Estética"},
    {"cnpj": "28345710000115", "categoria": "Odonto"},
    {"cnpj": "03642724000103", "categoria": "Médico"}
]

def buscar_e_enviar():
    print("A iniciar consulta de empresas reais com diagnóstico...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for item in LEADS_REAIS_NACIONAL:
        cnpj = item["cnpj"]
        categoria = item["categoria"]
        
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        print(f"\nA consultar CNPJ: {cnpj}...")
        
        try:
            res = requests.get(url, headers=headers, timeout=15)
            print(f"-> Código HTTP da API: {res.status_code}")
            
            if res.status_code == 200:
                dados = res.json()
                
                razao = dados.get("razao_social", "N/A")
                fantasia = dados.get("nome_fantasia") or razao
                data_ab = dados.get("data_inicio_atividade", "N/A")
                cnpj_fmt = dados.get("cnpj", cnpj)
                
                logradouro = dados.get("logradouro", "")
                numero = dados.get("numero", "")
                bairro = dados.get("bairro", "")
                municipio = dados.get("municipio", "")
                uf = dados.get("uf", "")
                
                endereco_completo = f"{logradouro}, {numero} - {bairro}, {municipio} - {uf}"
                telefone = dados.get("ddd_telefone_1", "N/A")
                email = dados.get("email", "N/A")
                
                lead = {
                    "razao_social": razao,
                    "nome_fantasia": fantasia,
                    "categoria": categoria,
                    "data_abertura": data_ab,
                    "cnpj": cnpj_fmt,
                    "endereco": endereco_completo,
                    "telefone": telefone,
                    "email": email,
                    "google_maps": f"https://www.google.com/maps/search/?api=1&query={fantasia}+{municipio}"
                }
                
                # Envia para o Make.com
                envio = requests.post(MAKE_WEBHOOK_URL, json=lead, timeout=10)
                print(f"-> Código HTTP do Make.com: {envio.status_code}")
                
                if envio.status_code == 200:
                    print(f"[SUCESSO] Lead enviado: {fantasia} ({municipio}-{uf})")
                else:
                    print(f"[AVISO] Make.com rejeitou: {envio.text}")
            else:
                print(f"[ERRO API] Resposta: {res.text}")
        except Exception as e:
            print(f"[FALHA] Exceção de rede: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    buscar_e_enviar()
