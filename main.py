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

# Dicionário para traduzir o código do CNAE para a descrição amigável na planilha
DICIONARIO_CNAES = {
    "8630504": "Atividade Odontológica",
    "8623300": "Atividade Médica Ambulatorial",
    "3250706": "Fabricação de Aparelhos Ortopédicos/Médicos",
    "8640205": "Serviços de Diagnóstico por Imagem",
    "9313100": "Condicionamento Físico (Academia)",
    "8591100": "Ensino de Esportes",
    "8592901": "Ensino de Dança",
    "8230002": "Casas de Festas e Eventos",
    "8230001": "Organização de Feiras e Congressos",
    "5620102": "Serviços de Bufê / Catering",
    "7739003": "Aluguel de Estruturas para Eventos",
    "9602501": "Cabeleireiros, Manicure e Pedicure",
    "9602502": "Estética e Cuidados com a Beleza",
    "8630501": "Atividade Médica com Cirurgia",
    "8690901": "Práticas Integrativas em Saúde",
    "8630502": "Atividade Médica com Exames",
}


def limpar_cnpj(cnpj):
  return "".join(filter(str.isdigit, str(cnpj)))


all_values = sheet.get_all_values()

# Cabeçalho com a coluna "Segmento"
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
      # Traduz o código CNAE para a descrição escrita
      cnae_codigo = str(emp.get("cnae", ""))
      segmento_descritivo = DICIONARIO_CNAES.get(cnae_codigo, cnae_codigo)

      linhas_para_adicionar.append([
          cnpj_raw,
          emp.get("razao_social", ""),
          emp.get("data_abertura", ""),
          segmento_descritivo,  # Aqui já vai escrito o significado
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
        f"Adicionadas {len(linhas_para_adicionar)} novas empresas com o"
        " segmento descritivo à planilha!"
    )
  else:
    print(
        "Nenhuma empresa nova encontrada. Todas as encontradas já constavam na"
        " planilha."
    )
else:
  print("Nenhuma empresa encontrada nesta execução.")

print("Processo concluído com sucesso!")
