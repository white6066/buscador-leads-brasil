import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Painel de Prospecção & Inteligência Comercial",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central de Leads & Novas Empresas")
st.markdown("Filtre as empresas recém-criadas, pesquise presença digital e gerencie a geração de Landing Pages.")

# Carregamento de dados oficial sincronizado
@st.cache_data
def get_leads_data():
    data = [
        ["68822545000117", "GOMES AUTO CENTER LTDA", "2026-08-27", "Comércio Varejista de Automóveis Usados", "AL", "CORURIPE", "ENGENHEIRO GUTTEMBERG BREDA NETO, 1226", "8293904127", "https://www.google.com/maps/search/?api=1&query=GOMES%20AUTO%20CENTER%20LTDA%20CORURIPE%20AL"],
        ["35482768000204", "FBS COMERCIO E SERVICOS LTDA", "2026-08-31", "Comércio Atacadista de Produtos Alimentícios", "AL", "MURICI", "MILITAO VIEIRA SAPUCAIA, 103", "8132741010", "https://www.google.com/maps/search/?api=1&query=FBS%20COMERCIO%20E%20SERVICOS%20LTDA%20MURICI%20AL"],
        ["68806510000194", "LILY PRESENTES LTDA", "2026-08-26", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DA ALEGRIA, 258", "8293885886", "https://www.google.com/maps/search/?api=1&query=LILY%20PRESENTES%20LTDA%20MACEIO%20AL"],
        ["29342202000527", "IBRAFISIO INSTITUTO BRASILIENSE DE FISIOTERAPIA LTDA", "2026-08-26", "Atividades de Nutrição", "DF", "BRASILIA", "03 AREA RESERVADA, 01 - SOBRADINHO", "6196938090", "https://www.google.com/maps/search/?api=1&query=IBRAFISIO%20INSTITUTO%20BRASILIENSE%20DE%20FISIOTERAPIA%20LTDA%20BRASILIA%20DF"],
        ["68582009000191", "CLAUDIA TATIANA PEREIRA CORREA LTDA", "2026-08-14", "Atividades de Fonoaudiologia", "DF", "BRASILIA", "5, SN - NORTE (AGUAS CLARAS)", "6198539541", "https://www.google.com/maps/search/?api=1&query=CLAUDIA%20TATIANA%20PEREIRA%20CORREA%20LTDA%20BRASILIA%20DF"],
        ["42611727005203", "GREAT WALL MOTOR BRASIL LTDA", "2026-08-25", "Comércio Varejista de Automóveis Novos", "ES", "CARIACICA", "AFRICA DO SUL, S/N", "1181185538", "https://www.google.com/maps/search/?api=1&query=GREAT%20WALL%20MOTOR%20BRASIL%20LTDA%20CARIACICA%20ES"],
        ["68835584000159", "COMEXCAR COMERCIAL LTDA", "2026-08-26", "Comércio Varejista de Automóveis Novos", "ES", "VILA VELHA", "DARLY SANTOS, S/N", "2835428200", "https://www.google.com/maps/search/?api=1&query=COMEXCAR%20COMERCIAL%20LTDA%20VILA%20VELHA%20ES"],
        ["68852604000108", "COLUNAS PRODUCAO DE EVENTOS LTDA", "2026-08-28", "Design de Interiores", "MT", "TANGARA DA SERRA", "16-A, 1186 - JARDIM GOIAS", "6599871087", "https://www.google.com/maps/search/?api=1&query=COLUNAS%20PRODUCAO%20DE%20EVENTOS%20LTDA%20TANGARA%20DA%20SERRA%20MT"],
        ["68957151000176", "JEAN SALIBA DE SOUZA LTDA", "2026-08-29", "Design de Interiores", "MT", "NOVA MUTUM", "DAS HELICONIAS, 653N", "6599455068", "https://www.google.com/maps/search/?api=1&query=JEAN%20SALIBA%20DE%20SOUZA%20LTDA%20NOVA%20MUTUM%20MT"],
        ["68984744000121", "DESIGN BOUSH LTDA", "2026-09-05", "Design de Interiores", "MT", "VARZEA GRANDE", "GOIAS, 525 - CENTRO SUL", "6593576018", "https://www.google.com/maps/search/?api=1&query=DESIGN%20BOUSH%20LTDA%20VARZEA%20GRANDE%20MT"],
        ["68653103000194", "JOAO PAULO CAMPOS RIBEIRO LTDA", "2026-08-18", "Atividades Veterinárias", "MT", "CUIABA", "DAS PLAMEIRA, 252 - JD IMPERIAL", "6581295485", "https://www.google.com/maps/search/?api=1&query=JOAO%20PAULO%20CAMPOS%20RIBEIRO%20LTDA%20CUIABA%20MT"],
        ["68770664000173", "ESTACAO PET LTDA", "2026-08-19", "Atividades Veterinárias", "MT", "CUIABA", "VINTE E UM, 16 - PEDRA 90", "6592979320", "https://www.google.com/maps/search/?api=1&query=ESTACAO%20PET%20LTDA%20CUIABA%20MT"],
        ["68795916000119", "CENTRO EDUCACIONAL INVEST LTDA", "2026-08-24", "Ensino Fundamental", "MT", "CUIABA", "FERNANDO CORREA DA COSTA, 5022", "6536615124", "https://www.google.com/maps/search/?api=1&query=CENTRO%20EDUCACIONAL%20INVEST%20LTDA%20CUIABA%20MT"]
    ]
    df = pd.DataFrame(data, columns=["CNPJ", "Razao Social", "Data Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Maps"])
    df["Status"] = "Pendente"
    return df

df = get_leads_data()

# 2. Barra Lateral - Filtros Dinâmicos
st.sidebar.header("🎯 Filtros de Prospecção")

segmentos = ["Todos"] + sorted(list(df["Segmento"].dropna().unique()))
seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

ufs = ["Todos"] + sorted(list(df["UF"].dropna().unique()))
uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

if uf_selecionada != "Todos":
    cidades = ["Todas"] + sorted(list(df[df["UF"] == uf_selecionada]["Cidade"].dropna().unique()))
else:
    cidades = ["Todas"] + sorted(list(df["Cidade"].dropna().unique()))
cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

# Aplicar Filtros
df_filtered = df.copy()
if seg_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Segmento"] == seg_selecionado]
if uf_selecionada != "Todos":
    df_filtered = df_filtered[df_filtered["UF"] == uf_selecionada]
if cidade_selecionada != "Todos":
    df_filtered = df_filtered[df_filtered["Cidade"] == cidade_selecionada]
if status_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Status"] == status_selecionado]

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Leads Exibidos", len(df_filtered))
col2.metric("Pendentes", len(df_filtered[df_filtered["Status"] == "Pendente"]))
col3.metric("LPs Geradas", len(df_filtered[df_filtered["Status"] == "LP Gerada"]))
col4.metric("Vendas Fechadas", len(df_filtered[df_filtered["Status"] == "Finalizado Positivo"]))

st.divider()

# Exibição detalhada de cada lead
st.subheader("📋 Lista de Empresas")

if df_filtered.empty:
    st.info("Nenhum lead encontrado com os filtros selecionados.")
else:
    for idx, row in df_filtered.iterrows():
        razao = row["Razao Social"]
        segmento = row["Segmento"]
        cidade = row["Cidade"]
        uf = row["UF"]
        
        with st.expander(f"🏢 **{razao}** — {segmento} ({cidade}/{uf})"):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            
            with c1:
                st.markdown(f"**CNPJ:** {row['CNPJ']}")
                st.markdown(f"**Data de Abertura:** {row['Data Abertura']}")
                st.markdown(f"**Endereço:** {row['Endereco']}")
                tel = row['Telefone'] if row['Telefone'] != "" else "Não informado"
                st.markdown(f"**Telefone/WhatsApp:** {tel}")
                
            with c2:
                st.markdown(f"**Status Atual:** `{row['Status']}`")
                
                nome_busca = razao.replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
                url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
                
                if row["Maps"]:
                    st.markdown(f"📍 [Ver no Google Maps]({row['Maps']})")
                st.markdown(f"🔍 [Pesquisar Empresa no Google]({url_google})")
                st.markdown(f"📸 [Buscar Instagram da Empresa]({url_instagram})")

            with c3:
                st.markdown("### Ações")
                novo_status = st.selectbox(
                    "Atualizar Status:",
                    ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"],
                    index=0,
                    key=f"status_{idx}"
                )
                df.at[idx, "Status"] = novo_status
                
                if st.button("🚀 Gerar Landing Page", key=f"btn_lp_{idx}"):
                    st.success(f"LP gerada com sucesso para {razao}!")
