import json
import os
from buscador import obter_empresas_recentes
from google.oauth2.service_account import Credentials
import gspread

# Configuração de credenciais e escopos (Sheets + Drive)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
service_account_info = os.environ.get("GOOGLE_CREDENTIALS")

if service_account_info:
  creds_dict = json.loads(service_account_info)
  creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
else:
  creds = Credentials.from_service_account_file(
      "credentials.json", scopes=SCOPES
  )

client = gspread.authorize(creds)

# Abre a planilha existente
NOME_PLANILHA = "Novas Empresas - Segmentos Alvo"
spreadsheet = client.open(NOME_PLANILHA)
sheet = spreadsheet.sheet1

# Obtém todos os dados atuais da planilha para verificar duplicados
all_values = sheet.get_all_values()

# Se a planilha estiver vazia, adiciona o cabeçalho
if not all_values:
  sheet.append_row([
      "CNPJ",
      "Razão Social",
      "Data Abertura",
      "CNAE",
      "UF",
      "Município",
      "Telefone",
      "E-mail",
  ])
  existing_cnpjs = set()
else:
  # Recolhe todos os CNPJs já registados na coluna A (ignorando o cabeçalho)
  existing_cnpjs = set(row[0] for row in all_values[1:] if row)

novas_empresas = obter_empresas_recentes()

if novas_empresas:
  linhas_para_adicionar = []
  for emp in novas_empresas:
    cnpj_atual = emp.get("cnpj", "")

    # Verifica se o CNPJ é válido e se AINDA NÃO existe na planilha
    if cnpj_atual and cnpj_atual not in existing_cnpjs:
      linhas_para_adicionar.append([
          cnpj_atual,
          emp.get("razao_social", ""),
          emp.get("data_abertura", ""),
          emp.get("cnae", ""),
          emp.get("uf", ""),
          emp.get("municipio", ""),
          emp.get("telefone", ""),
          emp.get("email", ""),
      ])
      # Adiciona ao conjunto local para evitar duplicados na mesma execução
      existing_cnpjs.add(cnpj_atual)

  if linhas_para_adicionar:
    sheet.append_rows(linhas_para_adicionar)
    print(
        f"Adicionadas {len(linhas_para_adicionar)} novas empresas inéditas à"
        " planilha!"
    )
  else:
    print(
        "Nenhuma empresa nova encontrada. Todas as encontradas já constavam na"
        " planilha."
    )
else:
  print("Nenhuma empresa encontrada nesta execução.")

print("Processo concluído com sucesso!")
