import requests
import time

MAKE_WEBHOOK_URL = "https://hook.us2.make.com/nf6of83eo0v5se6qtdprvt65wy695wc8"

empresas_exemplo = [
    {
        "razao_social": "CENTRO DE ESTETICA BELEZA PURA LTDA",
        "nome_fantasia": "Beleza Pura Estética",
        "categoria": "Estética",
        "data_abertura": "15/03/2021",
        "cnpj": "14.256.789/0001-12",
        "endereco": "Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
        "telefone": "(11) 97777-8888",
        "email": "contato@belezapura.com",
        "google_maps": "https://www.google.com/maps/search/?api=1&query=Beleza+Pura+Estética+São+Paulo"
    },
    {
        "razao_social": "ACADEMIA FORCA TOTAL FITNESS LTDA",
        "nome_fantasia": "Força Total Fitness",
        "categoria": "Academia",
        "data_abertura": "10/08/2019",
        "cnpj": "28.999.111/0001-45",
        "endereco": "Rua das Palmeiras, 500 - Centro, Curitiba - PR",
        "telefone": "(41) 98888-2222",
        "email": "suporte@forcatotal.com",
        "google_maps": "https://www.google.com/maps/search/?api=1&query=Força+Total+Curitiba"
    },
    {
        "razao_social": "CLINICA ODONTOLOGICA SORRISO SAUDAVEL S/S",
        "nome_fantasia": "Sorriso Saudável Odontologia",
        "categoria": "Odonto",
        "data_abertura": "22/11/2023",
        "cnpj": "45.123.789/0001-90",
        "endereco": "Av. Brasil, 1500 - Centro, Lucas do Rio Verde - MT",
        "telefone": "(65) 99999-3333",
        "email": "atendimento@sorrisosaudavel.com",
        "google_maps": "https://www.google.com/maps/search/?api=1&query=Sorriso+Saudável+Lucas+do+Rio+Verde"
    }
]

print("A iniciar o envio de leads para o Make.com...")

for empresa in empresas_exemplo:
    try:
        response = requests.post(MAKE_WEBHOOK_URL, json=empresa)
        if response.status_code == 200:
            print(f"[SUCESSO] Empresa enviada: {empresa['nome_fantasia']}")
        else:
            print(f"[ERRO] Falha ao enviar {empresa['nome_fantasia']}: {response.status_code}")
    except Exception as e:
        print(f"[EXCEÇÃO] Erro de ligação: {e}")
    
    time.sleep(1)

print("Processo concluído!")
