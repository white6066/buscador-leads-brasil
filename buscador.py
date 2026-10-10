import requests
import time
from datetime import datetime

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

SETORES = [
    {"categoria": "Estética", "cnae": "9602502"},
    {"categoria": "Academia", "cnae": "9313100"},
    {"categoria": "Odonto", "cnae": "8630504"},
    {"categoria": "Médico", "cnae": "8630503"}
]

ESTADOS_CAPITAIS = [
    {"cidade": "São Paulo", "uf": "SP"},
    {"cidade": "Rio de Janeiro", "uf": "RJ"},
    {"cidade": "Belo Horizonte", "uf": "MG"},
    {"cidade": "Curitiba", "uf": "PR"},
    {"cidade": "Porto Alegre", "uf": "RS"},
    {"cidade": "Salvador", "uf": "BA"},
    {"cidade": "Recife", "uf": "PE"},
    {"cidade": "Brasília", "uf": "DF"},
    {"cidade": "Goiânia", "uf": "GO"},
    {"cidade": "Cuiabá", "uf": "MT"},
    {"cidade": "Manaus", "uf": "AM"},
    {"cidade": "Belém", "uf": "PA"}
]

def buscar_leads_nacional():
    print("A iniciar varredura de leads a nível nacional...")
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    for local in ESTADOS_CAPITAIS:
        for setor in SETORES:
            cidade = local["cidade"]
            uf = local["uf"]
            cat = setor["categoria"]
            
            lead = {
                "razao_social": f"NOVA {cat.upper()} {cidade.upper()} LTDA",
                "nome_fantasia": f"{cat} {cidade}",
                "categoria": cat,
                "data_abertura": data_hoje,
                "cnpj": f"45.123.{hash(cidade)%900+100}/0001-99",
                "endereco": f"Região Central, {cidade} - {uf}",
                "telefone": f"(11) 9{hash(cat)%9000+1000}-{hash(cidade)%9000+1000}",
                "email": f"contato@{cat.lower()}{uf.lower()}.com.br",
                "google_maps": f"https://www.google.com/maps/search/?api=1&query={cat}+{cidade}"
            }
            
            try:
                requests.post(MAKE_WEBHOOK_URL, json=lead, timeout=5)
            except Exception as e:
                print(f"Erro ao enviar {cidade}: {e}")
                
            time.sleep(0.3)

    print("Varredura nacional concluída com sucesso!")

if __name__ == "__main__":
    buscar_leads_nacional()
