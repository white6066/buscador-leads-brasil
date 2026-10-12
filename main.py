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

# Dicionário de tradução para todos os CNAEs alvo
DICIONARIO_CNAES = {
    "4511101": "Comércio Varejista de Automóveis Novos",
    "4511102": "Comércio Varejista de Automóveis Usados",
    "4520001": "Manutenção e Reparação Mecânica de Veículos",
    "4530703": "Comércio Varejista de Peças para Veículos",
    "4637199": "Comércio Atacadista de Produtos Alimentícios",
    "4642701": "Comércio Atacadista de Vestuário e Acessórios",
    "4711302": "Supermercados",
    "4771701": "Comércio Varejista de Produtos Farmacêuticos",
    "4781400": "Comércio Varejista de Artigos do Vestuário",
    "6420300": "Holding de Instituições Financeiras",
    "6462000": "Holdings de Instituições Não-Financeiras",
    "6511101": "Seguro de Vida",
    "6612600": "Corretoras de Títulos e Câmbio",
    "6622300": "Corretores e Agentes de Seguros e Planos de Saúde",
    "6810201": "Compra e Venda de Imóveis Próprios",
    "6810202": "Aluguel de Imóveis Próprios",
    "6821801": "Corretagem na Compra e Venda de Imóveis",
    "6821802": "Administração de Imóveis por Contrato",
    "6822600": "Gestão e Administração da Propriedade Imobiliária",
    "6911701": "Serviços Advocatícios",
    "6920601": "Atividades de Contabilidade",
    "7020400": "Consultoria em Gestão Empresarial",
    "7111100": "Serviços de Arquitetura",
    "7112000": "Serviços de Engenharia",
    "7311400": "Agências de Publicidade",
    "7319002": "Promoção de Vendas",
    "7319003": "Marketing Direto",
    "7410202": "Design de Interiores",
    "7420001": "Atividades de Produção de Fotografias",
    "7500100": "Atividades Veterinárias",
    "7711000": "Locação de Automóveis sem Condutor",
    "7810800": "Seleção e Agenciamento de Mão-de-Obra",
    "7911200": "Agências de Viagens",
    "8011101": "Atividades de Vigilância e Segurança Privada",
    "8121400": "Limpeza em Prédios e Domicílios",
    "8130300": "Atividades Paisagísticas",
    "8211000": "Serviços Combinados de Escritório",
    "8230001": "Organização de Feiras, Congressos e Festas",
    "8511000": "Educação Infantil - Creche",
    "8512100": "Educação Infantil - Pré-escola",
    "8513900": "Ensino Fundamental",
    "8520100": "Ensino Médio",
    "8531700": "Educação Superior - Graduação",
    "8592901": "Ensino de Dança",
    "8592902": "Ensino de Artes Cênicas",
    "8593700": "Ensino de Idiomas",
    "8599603": "Cursos de Pilotagem",
    "8599604": "Treinamento em Informática",
    "8610101": "Atividades de Atendimento Hospitalar",
    "8630503": "Atividade Médica Ambulatorial Restrita a Consultas",
    "8630504": "Atividade Odontológica",
    "8640202": "Laboratórios de Análises Clínicas",
    "8650002": "Atividades de Nutrição",
    "8650003": "Atividades de Psicologia e Psicanálise",
    "8650004": "Atividades de Fisioterapia",
    "8650006": "Atividades de Fonoaudiologia",
    "8711501": "Clínicas e Residências Geriátricas",
    "8800600": "Serviços de Assistência Social sem Alojamento",
    "9511800": "Reparação e Manutenção de Computadores",
    "9512600": "Reparação de Equipamentos de Comunicação",
    "9602501": "Cabeleireiros, Manicure e Pedicure",
    "9602502": "Estética e Cuidados com a Beleza",
    "9609201": "Serviços de Cabeleireiro e Tratamentos de Beleza",
    "9609208": "Higiene e Embelezamento de Animais Domésticos",
}


def limpar_cnpj(cnpj):
  return "".join(filter(str.isdigit, str(cnpj)))


all_values = sheet.get_all_values()
linhas_com_conteudo = [
    row for row in all_values if any(str(cell).strip() for cell in row)
]

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

if not linhas_com_conteudo:
  sheet.clear()
  sheet.append_row(cabecalhos_desejados)
  existing_cnpjs = set()
else:
  existing_cnpjs = set(
      limpar_cnpj(row[0]) for row in linhas_com_conteudo[1:] if row and row[0]
  )

novas_empresas = obter_empresas_recentes()

if novas_empresas:
  linhas_para_adicionar = []
  for emp in novas_empresas:
    cnpj_raw = emp.get("cnpj", "")
    cnpj_limpo = limpar_cnpj(cnpj_raw)

    if cnpj_limpo and cnpj_limpo not in existing_cnpjs:
      cnae_codigo = str(emp.get("cnae", ""))
      segmento_descritivo = DICIONARIO_CNAES.get(cnae_codigo, cnae_codigo)

      linhas_para_adicionar.append([
          cnpj_raw,
          emp.get("razao_social", ""),
          emp.get("data_abertura", ""),
          segmento_descritivo,
          emp.get("uf", ""),
          emp.get("municipio", ""),
          emp.get("endereco", ""),
          emp.get("telefone", ""),
          emp.get("email", ""),
          emp.get("maps_link", ""),
      ])
      existing_cnpjs.add(cnpj_limpo)

  if linhas_para_adicionar:
    # Se a planilha estava apenas com lixo vazio, limpa e adiciona os cabeçalhos na primeira linha
    if not linhas_com_conteudo or len(linhas_com_conteudo) <= 1:
      sheet.clear()
      sheet.append_row(cabecalhos_desejados)

    sheet.append_rows(linhas_para_adicionar)
    print(
        f"Adicionadas {len(linhas_para_adicionar)} novas empresas organizadas"
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
