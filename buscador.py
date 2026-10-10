import datetime
import requests

# Os teus CNAEs alvo para referência e filtragem
CNAES_ALVO = [
    "8630504", "8623300", "3250706", "8640205",  # Saúde / Odonto / Diagnóstico
    "9313100", "8591100", "8592901",             # Esportes / Condicionamento / Dança
    "8230002", "8230001", "5620102", "7739003",  # Eventos / Festas / Buffet / Estruturas
    "9602501", "9602502",                      # Beleza / Cabeleireiro / Estética
    "8630501", "8690901", "8630502"              # Medicina / Práticas Integrativas
]

def obter_empresas_recentes():
    print("A iniciar a busca de empresas através da API pública...")
    empresas_coletadas = []
    
    # Exemplo de consulta a um CNPJ ativo na BrasilAPI (podes adicionar mais CNPJs à lista para teste real)
    # Nota: Para consultar por CNAE em escala sem custos de APIs comerciais, 
    # podes expandir esta lista com CNPJs reais descobertos ou usar endpoints públicos abertos.
    cnpjs_exemplo = ["33000167000101", "00000000000191"] 
    
    for cnpj in cnpjs_exemplo:
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                
                # Extrai os dados principais de forma segura
                empresa = {
                    "cnpj": dados.get("cnpj", ""),
                    "razao_social": dados.get("razao_social", ""),
                    "data_abertura": dados.get("data_inicio_atividade", ""),
                    "cnae": str(dados.get("cnae_fiscal", "")),
                    "uf": dados.get("uf", ""),
                    "municipio": dados.get("municipio", ""),
                    "telefone": dados.get("ddd_telefone_1", ""),
                    "email": dados.get("email", "") or ""
                }
                
                empresas_coletadas.append(empresa)
        except Exception as e:
            print(f"Erro ao consultar o CNPJ {cnpj}: {e}")
            
    print(f"Total de empresas recolhidas com sucesso: {len(empresas_coletadas)}")
    return empresas_coletadas
