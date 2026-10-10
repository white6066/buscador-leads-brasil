import datetime


def obter_empresas_recentes():
  hoje = datetime.date.today()
  dois_dias_atras = hoje - datetime.timedelta(days=2)

  print(
      f"Buscando empresas criadas entre {dois_dias_atras} e {hoje} para os"
      " segmentos alvo..."
  )

  # Dados de exemplo (simulando empresas recém-abertas encontradas nos CNAEs alvo)
  empresas_coletadas = [
      {
          "cnpj": "12.345.678/0001-99",
          "razao_social": "Clinica Exemplo de Saude LTDA",
          "data_abertura": str(hoje - datetime.timedelta(days=1)),
          "cnae": "8630504",
          "uf": "SP",
          "municipio": "Sao Paulo",
          "telefone": "(11) 99999-8888",
          "email": "contato@clinicaexemplo.com",
      },
      {
          "cnpj": "98.765.432/0001-11",
          "razao_social": "Espaco Beleza e Estetica LTDA",
          "data_abertura": str(hoje - datetime.timedelta(days=1)),
          "cnae": "9602501",
          "uf": "RJ",
          "municipio": "Rio de Janeiro",
          "telefone": "(21) 98888-7777",
          "email": "contato@belezaestetica.com",
      },
  ]

  return empresas_coletadas
