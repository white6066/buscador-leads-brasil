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
    hoje = datetime.date.today()
    dois_dias_atras = hoje - datetime.timedelta(days=2)
    
    print(f"A procurar empresas criadas entre {dois_dias_atras} e {hoje} para os CNAEs configurados...")
    empresas_coletadas = []
    
    # Exemplo de consulta estruturada por CNAE utilizando endpoints públicos gratuitos
    for cnae in CNAES_ALVO:
        try:
            # Podes integrar aqui a chamada à API pública de consulta (ex: Minha Receita ou BrasilAPI)
            # url = f"https://minhareceita.org/cnae/{cnae}" (ou endpoint equivalente)
            response = requests.get(f"https://minhareceita.org/", timeout=5)
            
            # Nota: Como as APIs públicas de CNPJ funcionam habitualmente por consulta de CNPJ específico,
            # podes adaptar a listagem conforme a base de dados pública que preferires utilizar no projeto.
            
        except Exception as e:
            print(f"Erro ao consultar CNAE {cnae}: {e}")
            
    return empresas_coletadas
