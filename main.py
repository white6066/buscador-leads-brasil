import json
import os
from buscador import obter_empresas_recentes
from google.oauth2.service_account import Credentials
import gspread

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

NOME_PLANILHA = "Novas Empresas - Segmentos Alvo"
spreadsheet = client.open(NOME_PLANILHA)
sheet = spreadsheet.sheet1


def limpar_cnpj(cnpj):
  return "".join(filter(str.isdigit, str(cnpj)))


all_values = sheet.get_all_values()

# Cabeçalho atualizado com "Segmento" no lugar de "CNAE"
cabecalhos_desejados = [
    "CNPJ",
    "Razão Social",
    "Data Abertura",
    "Segmento",
    "UF",
    "Município",
    "Endereço",
    "Telefone",
    "E-mail",
    "Google Maps",
]

if not all_values:
  sheet.append_row(cabecalhos_desejados)
  existing_cnpjs = set()
else:
  existing_cnpjs = set(
      limpar_cnpj(row[0]) for row in all_values[1:] if row and row[0]
  )

novas_empresas = obter_empresas_recentes()

if novas_empresas:
  linhas_para_adicionar = []
  for emp in novas_empresas:
    cnpj_raw = emp.get("cnpj", "")
    cnpj_limpo = limpar_cnpj(cnpj_raw)

    if cnpj_limpo and cnpj_limpo not in existing_cnpjs:
      linhas_para_adicionar.append([
          cnpj_raw,
          emp.get("razao_social", ""),
          emp.get("data_abertura", ""),
          emp.get("cnae", ""),  # Aqui entra a descrição amigável
          emp.get("uf", ""),
          emp.get("municipio", ""),
          emp.get("endereco", ""),
          emp.get("telefone", ""),
          emp.get("email", ""),
          emp.get("maps_link", ""),
      ])
      existing_cnpjs.add(cnpj_limpo)

  if linhas_para_adicionar:
    sheet.append_rows(linhas_para_adicionar)
    print(
        f"Adicionadas {len(linhas_para_adicionar)} novas empresas com descrições"
        " à planilha!"
    )
  else:
    print(
        "Nenhuma empresa nova encontrada. Todas as encontradas já constavam na"
        " planilha."
    )
else:
  print("Nenhuma empresa encontrada nesta execução.")

print("Processo concluído com sucesso!")
