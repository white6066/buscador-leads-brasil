import datetime
import requests

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
    
    print(f"Buscando empresas criadas entre {dois_dias_atras} e {hoje}...")
    empresas_coletadas = []
    
    # Lógica de varredura ou consumo da API pública escolhida
    for cnae in CNAES_ALVO:
        try:
            # Exemplo de consulta estruturada
            pass
        except Exception as e:
            print(f"Erro ao consultar CNAE {cnae}: {e}")
            
    return empresas_coletadas
