import datetime
import requests

# Os teus 16 CNAEs alvo
CNAES_ALVO = [
    "8630504", "8623300", "3250706", "8640205",  # Saúde / Odonto / Diagnóstico
    "9313100", "8591100", "8592901",             # Esportes / Condicionamento / Dança
    "8230002", "8230001", "5620102", "7739003",  # Eventos / Festas / Buffet / Estruturas
    "9602501", "9602502",                      # Beleza / Cabeleireiro / Estética
    "8630501", "8690901", "8630502"              # Medicina / Práticas Integrativas
]

def obter_empresas_recentes():
    print("A consultar a API e a filtrar pelos CNAEs alvo...")
    empresas_coletadas = []
    
    # Lista de CNPJs para monitorização/teste. 
    # Podes adicionar novos CNPJs descobertos a esta lista para o robô os processar.
    cnpjs_para_testar = [
        "33000167000101", # Exemplo antigo (será ignorado por não estar nos CNAEs alvo)
        "00000000000191", # Exemplo antigo (será ignorado)
        # Adiciona aqui novos CNPJs que pretendes validar e enviar para a planilha
    ]
    
    for cnpj in cnpjs_para_testar:
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                cnae_fiscal = str(dados.get("cnae_fiscal", ""))
                
                # FILTRO PRINCIPAL: Só aceita se o CNAE estiver nos 16 CNAEs alvo
                if cnae_fiscal in CNAES_ALVO:
                    empresa = {
                        "cnpj": dados.get("cnpj", ""),
                        "razao_social": dados.get("razao_social", ""),
                        "data_abertura": dados.get("data_inicio_atividade", ""),
                        "cnae": cnae_fiscal,
                        "uf": dados.get("uf", ""),
                        "municipio": dados.get("municipio", ""),
                        "telefone": dados.get("ddd_telefone_1", ""),
                        "email": dados.get("email", "") or ""
                    }
                    empresas_coletadas.append(empresa)
                else:
                    print(f"CNPJ {cnpj} ignorado (CNAE {cnae_fiscal} não faz parte dos alvos).")
                    
        except Exception as e:
            print(f"Erro ao consultar o CNPJ {cnpj}: {e}")
            
    print(f"Total de empresas válidas recolhidas: {len(empresas_coletadas)}")
    return empresas_coletadas
