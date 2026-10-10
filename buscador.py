import os
import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials

# 1. Sua lista de CNAEs alvo
CNAES_ALVO = [
    "8630504", "8623300", "3250706", "8640205",  # Saúde / Odonto / Diagnóstico
    "9313100", "8591100", "8592901",             # Esportes / Condicionamento / Dança
    "8230002", "8230001", "5620102", "7739003",  # Eventos / Festas / Buffet / Estruturas
    "9602501", "9602502",                      # Beleza / Cabeleireiro / Estética
    "8630501", "8690901", "8630502"              # Medicina / Práticas Integrativas
]

# 2. Definir janela dos últimos dias
hoje = datetime.date.today()
dois_dias_atras = hoje - datetime.timedelta(days=2)

print(f"Executando busca para a janela: {dois_dias_atras} até {hoje}")

# 3. Autenticação no Google Sheets usando Segredos do GitHub (para segurança)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Lê as credenciais JSON guardadas nas variáveis de ambiente do GitHub
service_account_info = os.environ.get("GOOGLE_CREDENTIALS")

if service_account_info:
    import json
    creds_dict = json.loads(service_account_info)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
else:
    # Para testes locais no seu computador
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

client = gspread.authorize(creds)

# Abre a planilha pelo nome
NOME_PLANILHA = "Novas Empresas - Segmentos Alvo"
try:
    spreadsheet = client.open(NOME_PLANILHA)
    sheet = spreadsheet.sheet1
except Exception:
    spreadsheet = client.create(NOME_PLANILHA)
    sheet = spreadsheet.sheet1
    sheet.append_row(["CNPJ", "Razão Social", "Data Abertura", "CNAE", "UF", "Município", "Telefone", "E-mail"])

# 4. Lógica de consulta pública
# Aqui o script consome o serviço público da Receita / Minha Receita
def consultar_empresas():
    resultados = []
    # O script percorre a base pública e aplica os filtros
    # (Exemplo simplificado de estrutura)
    return resultados

empresas = consultar_empresas()

# 5. Adiciona os dados na planilha
for emp in empresas:
    sheet.append_row([
        emp.get("cnpj"),
        emp.get("razao_social"),
        emp.get("data_abertura"),
        emp.get("cnae"),
        emp.get("uf"),
        emp.get("municipio"),
        emp.get("telefone"),
        emp.get("email")
    ])

print("Execução finalizada com sucesso!")
