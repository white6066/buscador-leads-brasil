import datetime
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

# Todos os estados do Brasil e o Distrito Federal usando as siglas oficiais
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
  print("A pesquisar novas empresas em todo o território nacional...")
  empresas_coletadas = []

  # Define o período recente (empresas abertas nos últimos 60 dias)
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

                # Filtra apenas empresas recentes (últimos 60 dias)
                if data_abertura >= limite_data:
                  cnae_fiscal = str(dados.get("cnae_fiscal", ""))
                  empresa = {
                      "cnpj": dados.get("cnpj", ""),
                      "razao_social": dados.get("razao_social", ""),
                      "data_abertura": data_abertura_str,
                      "cnae": cnae_fiscal,
                      "uf": dados.get("uf", ""),
                      "municipio": dados.get("municipio", ""),
                      "telefone": dados.get("ddd_telefone_1", ""),
                      "email": dados.get("email", "") or "",
                  }

                  # Evita duplicados
                  if not any(
                      e["cnpj"] == empresa["cnpj"] for e in empresas_coletadas
                  ):
                    empresas_coletadas.append(empresa)
              except Exception:
                pass
      except Exception:
        pass  # Ignora timeouts pontuais de estados específicos para manter o fluxo robusto

  print(f"Total de novas empresas nacionais recolhidas: {len(empresas_coletadas)}")
  return empresas_coletadas
