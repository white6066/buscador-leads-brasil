import asyncio
import datetime
import urllib.parse
import aiohttp

# --- DICIONÁRIO COMPLETO DE CONVERSÃO DE CNAES ---
CNAE_DESCRIPTIONS = {
    # Automotivo e Peças
    "4511101": "Comércio a varejo de veículos automotores novos",
    "4511102": "Comércio a varejo de veículos automotores usados",
    "4520001": "Manutenção e reparação mecânica de veículos",
    "4520007": "Lanternagem ou funilaria e pintura de veículos",
    "4520008": "Lavagem, lubrificação e polimento de veículos",
    "4530703": "Comércio a varejo de peças e acessórios para veículos",
    
    # Comércio Especializado e Varejo
    "4637199": "Comércio atacadista especializado em outros produtos alimentícios",
    "4642701": "Comércio atacadista de artigos de vestuário e acessórios",
    "4711302": "Comércio varejista em supermercados",
    "4771701": "Comércio varejista de produtos farmacêuticos",
    "4781400": "Comércio varejista de artigos do vestuário e acessórios",
    "4789004": "Comércio varejista de animais vivos e artigos para pets",

    # Financeiro, Seguros e Holdings
    "6420300": "Holdings de instituições não financeiras",
    "6462000": "Holdings de instituições financeiras",
    "6511101": "Seguros de vida",
    "6612600": "Atividades de intermediação em operações financeira",
    "6622300": "Corretores e agentes de seguros, de previdência complementar e de saúde",

    # Imobiliário
    "6810201": "Compra e venda de imóveis próprios",
    "6810202": "Aluguel de imóveis próprios",
    "6821801": "Corretagem na compra e venda e avaliação de imóveis",
    "6821802": "Corretagem no aluguel de imóveis",
    "6822600": "Gestão e administração da propriedade imobiliária",

    # Serviços Profissionais, Jurídicos, Contábeis e Consultoria
    "6911701": "Serviços advocatícios",
    "6920601": "Atividades de contabilidade",
    "7020400": "Consultoria em gestão empresarial",
    "7111100": "Serviços de arquitetura",
    "7112000": "Serviços de engenharia",
    "7311400": "Agências de publicidade",
    "7319002": "Promoção de vendas",
    "7319003": "Marketing direto",
    "7319004": "Consultoria em publicidade e marketing",
    "7410202": "Design de interiores",
    "7420001": "Atividades de produção de fotografias",
    "7500100": "Atividades veterinárias",

    # Outros Serviços Administrativos e Apoio
    "7711000": "Locação de automóveis sem condutor",
    "7810800": "Seleção e agenciamento de mão-de-obra",
    "7911200": "Agências de viagens",
    "8011101": "Atividades de vigilância e segurança privada",
    "8121400": "Limpeza em prédios e em domicílios",
    "8130300": "Atividades paisagísticas",
    "8211000": "Serviços combinados de escritório e apoio administrativo",
    "8230001": "Serviços de organização de feiras, congressos e exposições",

    # Educação
    "8511000": "Educação infantil - creche",
    "8512100": "Educação infantil - pré-escola",
    "8513900": "Ensino fundamental",
    "8520100": "Ensino médio",
    "8531700": "Educação superior - graduação",
    "8592901": "Ensino de dança",
    "8592902": "Ensino de artes cênicas, exceto dança",
    "8593700": "Ensino de idiomas",
    "8599603": "Treinamento em informática",
    "8599604": "Treinamento em desenvolvimento profissional e gerencial",
    "8599699": "Outras atividades de ensino não especificadas",

    # Saúde e Bem-Estar
    "8610101": "Atividades de atendimento hospitalar",
    "8630501": "Atividade médica ambulatorial com procedimentos cirúrgicos",
    "8630502": "Atividade médica ambulatorial com exames complementares",
    "8630503": "Atividade médica ambulatorial restrita a consultas",
    "8630504": "Atividade odontológica",
    "8640202": "Laboratórios clínicos",
    "8650002": "Atividades de profissionais da nutrição",
    "8650003": "Atividades de psicologia e psicanálise",
    "8650004": "Atividades de fisioterapia",
    "8650006": "Atividades de fonoaudiologia",
    "8690901": "Atividades de práticas integrativas e complementares em saúde",
    "8711501": "Clinicas e residências geriátricas",
    "8800600": "Serviços de assistência social sem alojamento",

    # Tecnologia e Manutenção de Equipamentos
    "9511800": "Reparação e manutenção de computadores e de equipamentos periféricos",
    "9512600": "Reparação e manutenção de equipamentos de comunicação",

    # Beleza, Estética e Outros Serviços Pessoais
    "9602501": "Cabeleireiros, manicure e pedicure",
    "9602502": "Atividades de estética e outros serviços de cuidados com a beleza",
    "9609201": "Clichês, fotolagos e serviços de pré-impressão",
    "9609208": "Serviços de pigmentação de pele (tatuagem e piercing)"
}

CNAES_ALVO = list(CNAE_DESCRIPTIONS.keys())

UFS_ALVO = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
    "SP", "SE", "TO",
]

def obter_descricao_cnae(cnae_str):
    """Converte o código CNAE puro na sua descrição legível correspondente."""
    clean_code = "".join(filter(str.isdigit, str(cnae_str)))
    return CNAE_DESCRIPTIONS.get(clean_code, f"CNAE {cnae_str}")


async def buscar_uf_cnae(session, uf, cnae_codigo, limite_data, sem):
  url = f"https://minhareceita.org/?uf={uf}&cnae={cnae_codigo}"
  async with sem:
    try:
      async with session.get(url, timeout=15) as response:
        if response.status == 200:
          dados_json = await response.json()
          lista_empresas = dados_json.get("data", [])
          resultados = []

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

                  # Transcreve automaticamente o CNAE para a descrição legível
                  segmento_transcrito = obter_descricao_cnae(cnae_codigo)

                  resultados.append({
                      "cnpj": dados.get("cnpj", ""),
                      "razao_social": razao_social,
                      "data_abertura": data_abertura_str,
                      "cnae": segmento_transcrito, # Já exporta transcrito
                      "uf": uf_emp,
                      "municipio": municipio,
                      "endereco": endereco_completo,
                      "telefone": telefone,
                      "email": email_empresa,
                      "maps_link": maps_link,
                  })
              except Exception:
                pass
          return resultados
    except Exception:
      pass
    return []


async def main_async():
  print(
      f"A iniciar busca nacional em paralelo para {len(CNAES_ALVO)} CNAEs e"
      f" {len(UFS_ALVO)} UFs..."
  )
  hoje = datetime.date.today()
  limite_data = hoje - datetime.timedelta(days=60)

  sem = asyncio.Semaphore(25)

  async with aiohttp.ClientSession() as session:
    tarefas = []
    for uf in UFS_ALVO:
      for cnae_codigo in CNAES_ALVO:
        tarefas.append(buscar_uf_cnae(session, uf, cnae_codigo, limite_data, sem))

    respostas = await asyncio.gather(*tarefas)

    empresas_coletadas = []
    cnpjs_vistos = set()
    for lista in respostas:
      for emp in lista:
        if emp["cnpj"] not in cnpjs_vistos:
          cnpjs_vistos.add(emp["cnpj"])
          empresas_coletadas.append(emp)

    print(
        f"Total de empresas únicas recolhidas e transcritas com sucesso:"
        f" {len(empresas_coletadas)}"
    )
    return empresas_coletadas


def obter_empresas_recentes():
  return asyncio.run(main_async())
