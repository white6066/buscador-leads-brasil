import os
import json
import gspread
from google.oauth2.service_account import Credentials
from buscador import obter_empresas_recentes

# Configuração de credenciais via variáveis de ambiente do GitHub
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service_account_info = os.environ.get("GOOGLE_CREDENTIALS")

if service_account_info:
    creds_dict = json.loads(service_account_info)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
else:
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

client = gspread.authorize(creds)

NOME_PLANILHA = "Novas Empresas - Segmentos Alvo"
try:
    spreadsheet = client.open(NOME_PLANILHA)
    sheet = spreadsheet.sheet1
except Exception:
    spreadsheet = client.create(NOME_PLANILHA)
    sheet = spreadsheet.sheet1
    sheet.append_row(["CNPJ", "Razão Social", "Data Abertura", "CNAE", "UF", "Município", "Telefone", "E-mail"])

novas_empresas = obter_empresas_recentes()

for emp in novas_empresas:
    sheet.append_row([
        emp.get("cnpj", ""),
        emp.get("razao_social", ""),
        emp.get("data_abertura", ""),
        emp.get("cnae", ""),
        emp.get("uf", ""),
        emp.get("municipio", ""),
        emp.get("telefone", ""),
        emp.get("email", "")
    ])

print("Processo concluído com sucesso!")
