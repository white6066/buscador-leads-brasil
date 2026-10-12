import datetime
import urllib.parse
import requests

# Lista completa com todos os 64 CNAEs alvo
CNAES_ALVO = [
    "4511101",
    "4511102",
    "4520001",
    "4530703",
    "4637199",
    "4642701",
    "4711302",
    "4771701",
    "4781400",
    "6420300",
    "6462000",
    "6511101",
    "6612600",
    "6622300",
    "6810201",
    "6810202",
    "6821801",
    "6821802",
    "6822600",
    "6911701",
    "6920601",
    "7020400",
    "7111100",
    "7112000",
    "7311400",
    "7319002",
    "7319003",
    "7410202",
    "7420001",
    "7500100",
    "7711000",
    "7810800",
    "7911200",
    "8011101",
    "8121400",
    "8130300",
    "8211000",
    "8230001",
    "8511000",
    "8512100",
    "8513900",
    "8520100",
    "8531700",
    "8592901",
    "8592902",
    "8593700",
    "8599603",
    "8599604",
    "8610101",
    "8630503",
    "8630504",
    "8640202",
    "8650002",
    "8650003",
    "8650004",
    "8650006",
    "8711501",
    "8800600",
    "9511800",
    "9512600",
    "9602501",
    "9602502",
    "9609201",
    "9609208",
]


def obter_empresas_recentes():
  print("A pesquisar novas empresas (busca nacional otimizada)...")
  empresas_coletadas = []

  hoje = datetime.date.today()
  limite_data = hoje - datetime.timedelta(days=60)

  for cnae_codigo in CNAES_ALVO:
    try:
      # Busca nacional direta pelo CNAE (elimina o loop de estados e evita bloqueios)
      url = f"https://minhareceita.org/?cnae={cnae_codigo}"
      response = requests.get(url, timeout=15)

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
                telefone = (
                    dados.get("ddd_telefone_1", "")
                    or dados.get("telefone")
                    or ""
                )
                razao_social = dados.get("razao_social", "")
                municipio = dados.get("municipio", "")
                uf_emp = dados.get("uf", "")

                logradouro = dados.get("logradouro", "")
                numero = dados.get("numero", "")
                bairro = dados.get("bairro", "")
                cep = dados.get("cep", "")
                endereco_completo = (
                    f"{logradouro}, {numero} - {bairro}, {municipio} -"
                    f" {uf_emp} (CEP: {cep})"
                ).strip(" ,-")

                query_maps = f"{razao_social} {municipio} {uf_emp}"
                maps_link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query_maps)}"

                email_empresa = (
                    dados.get("email")
                    or dados.get("email_contato")
                    or dados.get("correio_eletronico")
                    or ""
                )

                empresa = {
                    "cnpj": dados.get("cnpj", ""),
                    "razao_social": razao_social,
                    "data_abertura": data_abertura_str,
                    "cnae": cnae_codigo,
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
      f"Total de empresas recolhidas com sucesso: {len(empresas_coletadas)}"
  )
  return empresas_coletadas
