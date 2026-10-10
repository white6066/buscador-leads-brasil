import requests
import time

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

# Lista de CNPJs reais e ativos no Brasil nos setores alvo (consultados via API Pública da Receita Federal)
CNPJS_REAIS_BRASIL = [
    {"categoria": "Academia", "cnpj": "07594910000184"},  # Ex: Unidade de Condicionamento Físico
    {"categoria": "Estética", "cnpj": "31339301000109"},  # Ex: Clínica de Estética e Beleza
    {"categoria": "Odonto", "cnpj": "28345710000115"},    # Ex: Centro Odontológico
    {"categoria": "Médico", "cnpj": "03642724000103"}     # Ex: Clínica Médica Ambulatorial
]

def buscar_dados_reais_nacionais():
    print("A consultar dados oficiais e reais da Receita Federal...")
    
    for item in CNPJS_REAIS_BRASIL:
        cnpj_limpo = item["cnpj"]
        categoria_alvo = item["categoria"]
        
        url = f"https://publica.cnpj.ws/cnpj/{cnpj_limpo}"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                dados = response.json()
                
                razao_social = dados.get("razao_social", "N/A")
                estabelecimento = dados.get("estabelecimento", {})
                nome_fantasia = estabelecimento.get("nome_fantasia") or razao_social
                data_abertura = estabelecimento.get("data_inicio_atividade", "N/A")
                
                logradouro = estabelecimento.get("logradouro", "")
                numero = estabelecimento.get("numero", "")
                bairro = estabelecimento.get("bairro", "")
                cidade = estabelecimento.get("cidade", {}).get("nome", "")
                uf = estabelecimento.get("estado", {}).get("sigla", "")
                endereco = f"{logradouro}, {numero} - {bairro}, {cidade} - {uf}"
                
                ddd = estabelecimento.get("ddd1", "")
                telefone = estabelecimento.get("telefone1", "")
                tel_completo = f"({ddd}) {telefone}" if ddd and telefone else "N/A"
                email = estabelecimento.get("email", "N/A")
                
                # Monta o CNPJ formatado corretamente
                cnpj_formatado = f"{dados.get('cnpj_raiz', '')}/{estabelecimento.get('cnpj_ordem', '')}-{estabelecimento.get('cnpj_dv', '')}"
                
                lead = {
                    "razao_social": razao_social,
                    "nome_fantasia": nome_fantasia,
                    "categoria": categoria_alvo,
                    "data_abertura": data_abertura,
                    "cnpj": cnpj_formatado,
                    "endereco": endereco,
                    "telefone": tel_completo,
                    "email": email,
                    "google_maps": f"https://www.google.com/maps/search/?api=1&query={nome_fantasia}+{cidade}"
                }
                
                # Envia os dados reais para o Make.com
                envio = requests.post(MAKE_WEBHOOK_URL, json=lead, timeout=10)
                if envio.status_code == 200:
                    print(f"[SUCESSO] Lead real enviado: {nome_fantasia} ({cidade}/{uf})")
            else:
                print(f"[AVISO] Não foi possível consultar o CNPJ {cnpj_limpo}")
        except Exception as e:
            print(f"[ERRO] Falha na requisição: {e}")
            
        time.sleep(2) # Respeita o limite de requisições da API pública

if __name__ == "__main__":
    buscar_dados_reais_nacionais()
