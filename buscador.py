import datetime
import urllib.parse
import requests

# Os teus 16 CNAEs alvo
CNAES_ALVO = [
    "8630504",
    "8623300",
    "3250706",
    "8640205",  # Saúde / Odonto / Diagnóstico
    "9313100",
    "8591100",
    "8592901",  # Esportes / Condicionamento / Dança
    "8230002",
    "8230001",
    "5620102",
    "7739003",  # Eventos / Festas / Buffet / Estruturas
    "9602501",
    "9602502",  # Beleza / Cabeleireiro / Estética
    "8630501",
    "8690901",
    "8630502",  # Medicina / Práticas Integrativas
]

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
  print("A pesquisar novas empresas com endereço, email e link do Maps...")
  empresas_coletadas = []

  hoje = datetime.date.today()
  limite_data = hoje - datetime.timedelta(days=60)

  for uf in UFS_ALVO:
    for cnae in CNAES_ALVO:
      try:
        url = f"https://minhareceita.org/?cnae={cnae}&uf={uf}"
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
                  cnae_fiscal = str(dados.get("cnae_fiscal", ""))
                  razao_social = dados.get("razao_social", "")
                  municipio = dados.get("municipio", "")
                  uf_emp = dados.get("uf", "")

                  # Montar endereço completo
                  logradouro = dados.get("logradouro", "")
                  numero = dados.get("numero", "")
                  bairro = dados.get("bairro", "")
                  cep = dados.get("cep", "")
                  endereco_completo = (
                      f"{logradouro}, {numero} - {bairro}, {municipio} -"
                      f" {uf_emp} (CEP: {cep})"
                  ).strip(" ,-")

                  # Gerar link direto do Google Maps para facilitar a localização
                  query_maps = f"{razao_social} {municipio} {uf_emp}"
                  maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query_maps)}"

                  empresa = {
                      "cnpj": dados.get("cnpj", ""),
                      "razao_social": razao_social,
                      "data_abertura": data_abertura_str,
                      "cnae": cnae_fiscal,
                      "uf": uf_emp,
                      "municipio": municipio,
                      "endereco": endereco_completo,
                      "telefone": dados.get("ddd_telefone_1", ""),
                      "email": dados.get("email", "") or "",
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
      f"Total de novas empresas recolhidas com dados completos:"
      f" {len(empresas_coletadas)}"
  )
  return empresas_coletadas
