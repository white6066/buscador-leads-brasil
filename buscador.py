import asyncio
import datetime
import urllib.parse
import aiohttp

# --- DICIONÁRIO HIPER-ABRANGENTE (ÁREAS DE ALTA RENTABILIDADE E VOLUME) ---
CNAE_DESCRIPTIONS = {
    # --- GRUPO 1: TECNOLOGIA, SOFTWARE, WEB, DESIGN E MARKETING ---
    "6201501": "Desenvolvimento de programas de computador sob encomenda",
    "6202300": "Licenciamento e customização de programas de computador",
    "6203100": "Desenvolvimento e licenciamento de programas de computador customizáveis",
    "6204000": "Consultoria em tecnologia da informação",
    "6209100": "Suporte técnico, manutenção e outros serviços em tecnologia da informação",
    "6311900": "Tratamento de dados, servidores e serviços de hospedagem na internet",
    "6319400": "Portais, provedores de conteúdo e outros serviços de informação na internet",
    "7311400": "Agências de publicidade",
    "7319002": "Promoção de vendas",
    "7319003": "Marketing direto",
    "7319004": "Consultoria em publicidade e marketing",
    "7410201": "Atividades de design de produto",
    "7410202": "Design de interiores",
    "7410203": "Design de moda",
    "7490104": "Atividades de intermediação e agenciamento de serviços e negócios em geral",

    # --- GRUPO 2: TRANSPORTE, LOGÍSTICA, ENTREGAS E MUDANÇAS ---
    "4930201": "Transporte rodoviário de carga, exceto produtos perigosos, municipal",
    "4930202": "Transporte rodoviário de carga, intermunicipal, interestadual e internacional",
    "4930203": "Transporte rodoviário de mudança",
    "5250803": "Organização logística do transporte de carga",
    "5320201": "Serviços de malote nacional",
    "5320202": "Serviços de entrega rápida (Motoboy e delivery urbano)",
    "7711000": "Locação de automóveis sem condutor",
    "4923002": "Serviço de transporte de passageiros - locação de veículos com motorista",

    # --- GRUPO 3: COMÉRCIO VAREJISTA, LOJAS E MODA ---
    "4711301": "Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - hipermercados",
    "4711302": "Comércio varejista em supermercados",
    "4712100": "Comércio varejista de mercadorias em geral (Minimercados, mercearias e armazéns)",
    "4751201": "Comércio varejista especializado de equipamentos e suprimentos de informática",
    "4753900": "Comércio varejista especializado de eletrodomésticos e equipamentos de áudio e vídeo",
    "4754701": "Comércio varejista de móveis",
    "4755502": "Comércio varejista de artigos de armarinho",
    "4763602": "Comércio varejista de artigos esporte e lazer",
    "4771701": "Comércio varejista de produtos farmacêuticos, sem manipulação",
    "4772500": "Comércio varejista de cosméticos, produtos de perfumaria e higiene pessoal",
    "4774100": "Comércio varejista de artigos de ótica",
    "4781400": "Comércio varejista de artigos do vestuário e acessórios",
    "4782201": "Comércio varejista de calçados",
    "4782202": "Comércio varejista de artigos de viagem",
    "4789001": "Comércio varejista de peças e acessórios novos para veículos automotores",
    "4789004": "Comércio varejista de animais vivos e artigos e alimentos para animais de estimação (Pet shop)",
    "4789099": "Comércio varejista de outros produtos não especificados anteriormente",

    # --- GRUPO 4: ALIMENTAÇÃO, BARES, RESTAURANTES E PADARIAS ---
    "5611201": "Restaurantes e similares",
    "5611202": "Bares e outros estabelecimentos especializados em servir bebidas",
    "5611203": "Lanchonetes, casas de chá, de sucos e similares",
    "5612100": "Serviços ambulantes de alimentação",
    "5620101": "Fornecimento de alimentos preparados preponderantemente para empresas",
    "5620102": "Serviços de catering, bufê e outros serviços de comida preparada",
    "4721102": "Padaria e confeitaria com predominância de revenda",
    "4722901": "Comércio varejista de carnes - açougues",
    "4729699": "Comércio varejista de produtos alimentícios em geral ou especializado em produtos naturais",

    # --- GRUPO 5: CONSTRUÇÃO, MATERIAIS, REFORMAS E INSTALAÇÕES ---
    "4120400": "Construção de edifícios",
    "4313400": "Obras de terraplanagem",
    "4321500": "Instalação e manutenção elétrica",
    "4322301": "Instalações hidráulicas, sanitárias e de gás",
    "4322302": "Instalação e manutenção de sistemas de ar condicionado, ventilação e aquecimento",
    "4330401": "Impermeabilização em obras de engenharia civil",
    "4330402": "Instalação de portas, janelas, tetos, divisórias e armários embutidos",
    "4330403": "Obras de acabamento em gesso e estuque",
    "4330404": "Serviços de pintura em geral",
    "4330405": "Aplicação de revestimentos e de resinas em pisos e paredes",
    "4330499": "Outras obras de acabamento da construção",
    "4399103": "Obras de alvenaria",
    "4399199": "Serviços especializados para construção não especificados anteriormente",
    "4744001": "Comércio varejista de ferragens e ferramentas",
    "4744003": "Comércio varejista de materiais hidráulicos",
    "4744005": "Comércio varejista de materiais de construção não especificados anteriormente",
    "4744099": "Comércio varejista de materiais de construção em geral",

    # --- GRUPO 6: SAÚDE, CLÍNICAS, ODONTOLOGIA E BEM-ESTAR ---
    "8610101": "Atividades de atendimento hospitalar, exceptuando unidades de pronto-socorro",
    "8630501": "Atividade médica ambulatorial com recursos para procedimentos cirúrgicos",
    "8630502": "Atividade médica ambulatorial com recursos para exames complementares",
    "8630503": "Atividade médica ambulatorial restrita a consultas",
    "8630504": "Atividade odontológica",
    "8640201": "Laboratórios de anatomia patológica e citológica",
    "8640202": "Laboratórios clínicos",
    "8640206": "Serviços de ressonância magnética",
    "8640207": "Serviços de diagnóstico por imagem com uso de radiação ionizante, tomografia",
    "8650001": "Atividades de enfermagem",
    "8650002": "Atividades de profissionais da nutrição",
    "8650003": "Atividades de psicologia e psicanálise",
    "8650004": "Atividades de fisioterapia",
    "8650005": "Atividades de terapia ocupacional",
    "8650006": "Atividades de fonoaudiologia",
    "8690901": "Atividades de práticas integrativas e complementares em saúde humana",
    "8711501": "Clinicas e residências geriátricas",
    "8800600": "Serviços de assistência social sem alojamento",

    # --- GRUPO 7: SERVIÇOS PROFISSIONAIS, JURÍDICOS, CONTÁBEIS E IMOBILIÁRIOS ---
    "6420300": "Holdings de instituições não financeiras",
    "6462000": "Holdings de instituições financeiras",
    "6810201": "Compra e venda de imóveis próprios",
    "6810202": "Aluguel de imóveis próprios",
    "6821801": "Corretagem na compra e venda e avaliação de imóveis",
    "6821802": "Corretagem no aluguel de imóveis",
    "6822600": "Gestão e administração da propriedade imobiliária",
    "6911701": "Serviços advocatícios",
    "6920601": "Atividades de contabilidade",
    "6920602": "Atividades de consultoria e auditoria contábil e tributária",
    "7020400": "Atividades de consultoria em gestão empresarial",
    "7111100": "Serviços de arquitetura",
    "7112000": "Serviços de engenharia",
    "7420001": "Atividades de produção de fotografias",
    "7490199": "Outras atividades profissionais, científicas e técnicas não especificadas",
    "7500100": "Atividades veterinárias",

    # --- GRUPO 8: BELEZA, ESTÉTICA, BARBEARIAS E FITNESS ---
    "9313100": "Atividades de condicionamento físico (Academias e Estúdios de musculação/crossfit)",
    "9602501": "Cabeleireiros, manicure e pedicure",
    "9602502": "Atividades de estética e outros serviços de cuidados com a beleza",
    "9609206": "Serviços de tatuagem e colocação de piercing",
    "9609208": "Serviços de pigmentação de pele e estética corporal",

    # --- GRUPO 9: AUTOMOTIVO, OFICINAS, ESTÉTICA E PEÇAS ---
    "4511101": "Comércio a varejo de veículos automotores novos",
    "4511102": "Comércio a varejo de veículos automotores usados",
    "4520001": "Serviços de manutenção e reparação mecânica de veículos automotores",
    "4520003": "Serviços de manutenção e reparação elétrica de veículos automotores",
    "4520007": "Serviços de lanternagem ou funilaria e pintura de veículos automotores",
    "4520008": "Serviços de lavagem, lubrificação e polimento de veículos automotores",
    "4530703": "Comércio a varejo de peças e acessórios novos para veículos automotores",

    # --- GRUPO 10: EDUCAÇÃO, CURSOS E TREINAMENTOS ---
    "8512100": "Educação infantil - pré-escola",
    "8513900": "Ensino fundamental",
    "8520100": "Ensino médio",
    "8531700": "Educação superior - graduação",
    "8592901": "Ensino de dança",
    "8592999": "Ensino de arte e cultura não especificado anteriormente",
    "8593700": "Ensino de idiomas",
    "8599603": "Treinamento em informática",
    "8599604": "Treinamento em desenvolvimento profissional e gerencial",
    "8599699": "Outras atividades de ensino não especificadas anteriormente",

    # --- GRUPO 11: ENERGIA SOLAR, SUSTENTABILIDADE E ELÉTRICA AVANÇADA (ALTA RENTABILIDADE) ---
    "3511501": "Geração de energia elétrica",
    "3513300": "Comércio atacadista de energia elétrica",
    "3530100": "Produção e distribuição de vapor, água quente e ar condicionado",
    "4321500": "Instalação e manutenção elétrica (inclui sistemas de energia solar fotovoltaica)",

    # --- GRUPO 12: SEGURANÇA ELETRÔNICA, MONITORAMENTO E CFTV ---
    "8011101": "Atividades de vigilância e segurança privada",
    "8020001": "Atividades de monitoramento de sistemas de segurança eletrônica",
    "8030700": "Atividades de investigação particular",

    # --- GRUPO 13: DEDETIZAÇÃO, CONTROLE DE PRAGAS E LIMPEZA ESPECIALIZADA ---
    "8121400": "Limpeza em prédios e em domicílios",
    "8122200": "Imunização e controle de pragas urbanas (Dedetização)",
    "8129000": "Atividades de limpeza não especificadas anteriormente",

    # --- GRUPO 14: ALUGUEL E LOCAÇÃO DE MÁQUINAS, EQUIPAMENTOS E ANDAIMES (B2B) ---
    "7732201": "Aluguel de máquinas e equipamentos para construção sem operador",
    "7739299": "Aluguel de outras máquinas e equipamentos comerciais e industriais não especificados",
    "7729202": "Aluguel de móveis, utensílios e aparelhos de uso doméstico e pessoal",

    # --- GRUPO 15: GESTÃO AMBIENTAL, RESÍDUOS E ENGENHARIA CONSULTIVA ---
    "3811400": "Coleta de resíduos não perigosos",
    "3812200": "Coleta de resíduos perigosos",
    "3821100": "Tratamento e disposição de resíduos não perigosos",
    "7112000": "Serviços de engenharia e projetos técnicos"
}

# Lista 100% isolada gerada automaticamente a partir das chaves do dicionário expandido
CNAES_ALVO = list(CNAE_DESCRIPTIONS.keys())

UFS_ALVO = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", 
    "SP", "SE", "TO",
]


def obter_descricao_cnae(cnae_str):
  """Verifica se o CNAE existe no dicionário e devolve a descrição transcrita."""
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

                  # Transcrição automática do CNAE para texto legível
                  segmento_transcrito = obter_descricao_cnae(cnae_codigo)

                  resultados.append({
                      "cnpj": dados.get("cnpj", ""),
                      "razao_social": razao_social,
                      "data_abertura": data_abertura_str,
                      "cnae": segmento_transcrito,
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
      f"A iniciar busca nacional massiva e rentável para {len(CNAES_ALVO)} CNAEs isolados e"
      f" {len(UFS_ALVO)} UFs..."
  )
  hoje = datetime.date.today()
  
  # Janela de 90 dias mantida para capturar o maior volume de novos negócios
  limite_data = hoje - datetime.timedelta(days=90)

  sem = asyncio.Semaphore(30)

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
