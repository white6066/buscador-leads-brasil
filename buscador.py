import datetime
import urllib.parse
import requests

# Os teus 16 CNAEs alvo com as respetivas descrições comerciais
CNAES_MAP = {
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

UFS_ALVO = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]


def obter_empresas_recentes():
  print("A pesquisar novas empresas com descrição dos CNAEs...")
  empresas_coletadas = []

  hoje = datetime.date.today()
  limite_data = hoje - datetime.timedelta(days=60)

  for uf in UFS_ALVO:
    for cnae_codigo in CNAES_MAP.keys():
      try:
        url = f"https://minhareceita.org/?cnae={cnae_codigo}&uf={uf}"
        response = requests.get(url, timeout=12)

        if response.status_code == 200:
          dados_json = response.json()
          lista_empresas = dados_json.get("data", [])

          for dados in lista_empresas:
            data_abertura_str = dados.get("data_inicio_atividade", "")
            if data_abertura_str:
              try:
                data_abertura = datetime.datetime.strptime(
                    data_abertura_str, "%Y-%m-%d"
                ).date()

                if data_abertura >= limite_data:
                  telefone = dados.get("ddd_telefone_1", "") or ""
                  if not telefone:
                    continue  # Descarta se não tiver telefone

                  cnae_fiscal = str(dados.get("cnae_fiscal", ""))
                  razao_social = dados.get("razao_social", "")
                  municipio = dados.get("municipio", "")
                  uf_emp = dados.get("uf", "")

                  # Endereço completo
                  logradouro = dados.get("logradouro", "")
                  numero = dados.get("numero", "")
                  bairro = dados.get("bairro", "")
                  cep = dados.get("cep", "")
                  endereco_completo = (
                      f"{logradouro}, {numero} - {bairro}, {municipio} -"
                      f" {uf_emp} (CEP: {cep})"
                  ).strip(" ,-")

                  # Link do Google Maps
                  query_maps = f"{razao_social} {municipio} {uf_emp}"
                  maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query_maps)}"

                  email_empresa = (
                      dados.get("email")
                      or dados.get("email_contato")
                      or dados.get("correio_eletronico")
                      or ""
                  )

                  # Pega a descrição amigável do dicionário
                  cnae_descricao = CNAES_MAP.get(
                      cnae_fiscal, "Outros Segmentos"
                  )

                  empresa = {
                      "cnpj": dados.get("cnpj", ""),
                      "razao_social": razao_social,
                      "data_abertura": data_abertura_str,
                      "cnae": cnae_descricao,  # Agora guarda a descrição em vez do número
                      "uf": uf_emp,
                      "municipio": municipio,
                      "endereco": endereco_completo,
                      "telefone": telefone,
                      "email": email_empresa,
                      "maps_link": maps_link,
                  }

                  if not any(
                      e["cnpj"] == empresa["cnpj"] for e in empresas_coletadas
                  ):
                    empresas_coletadas.append(empresa)
              except Exception:
                pass
      except Exception:
        pass

  print(
      f"Total de empresas qualificadas com descrições encontradas:"
      f" {len(empresas_coletadas)}"
  )
  return empresas_coletadas
