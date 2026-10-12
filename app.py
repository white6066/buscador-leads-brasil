import streamlit as st
import pandas as pd
from gspread import service_account
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Painel de Prospecção & Inteligência Commercial",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central de Leads & Novas Empresas")
st.markdown("Filtre as empresas recém-criadas, pesquise presença digital e gerencie a geração de Landing Pages.")

# 1. Conexão e carregamento de dados (Google Sheets)
@st.cache_data(ttl=300)
def load_data():
    # Substitua pelo caminho da sua credencial ou URL da planilha pública/Service Account
    url = "https://docs.google.com/spreadsheets/d/11FwBk_p5VK7OxR8LiPeTFZ_HuX1opMrZrX2fCxcX8pQ/export?format=csv"
    df = pd.read_csv(url)
    
    # Tratamento inicial de colunas
    df.columns = ["CNPJ", "Razao_Social", "Data_Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Status", "Link_Maps"]
    df["Data_Abertura"] = pd.to_datetime(df["Data_Abertura"], errors="coerce")
    df["Status"] = df["Status"].fillna("Pendente")
    return df

df = load_data()

# 2. Barra Lateral - Filtros Dinâmicos
st.sidebar.header("🎯 Filtros de Prospecção")

# Filtro por Segmento (CNAE)
segmentos = ["Todos"] + sorted(list(df["Segmento"].dropna().unique()))
seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

# Filtro por UF / Cidade
ufs = ["Todos"] + sorted(list(df["UF"].dropna().unique()))
uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

if uf_selecionada != "Todos":
    cidades = ["Todas"] + sorted(list(df[df["UF"] == uf_selecionada]["Cidade"].dropna().unique()))
else:
    cidades = ["Todas"] + sorted(list(df["Cidade"].dropna().unique()))
cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

# Filtro por Status do Lead
status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

# Aplicar Filtros
df_filtered = df.copy()

if seg_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Segmento"] == seg_selecionado]

if uf_selecionada != "Todos":
    df_filtered = df_filtered[df_filtered["UF"] == uf_selecionada]

if cidade_selecionada != "Todas":
    df_filtered = df_filtered[df_filtered["Cidade"] == cidade_selecionada]

if status_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Status"] == status_selecionado]

# 3. Métricas Principais
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Leads Exibidos", len(df_filtered))
col2.metric("Pendentes", len(df_filtered[df_filtered["Status"] == "Pendente"]))
col3.metric("LPs Geradas", len(df_filtered[df_filtered["Status"] == "LP Gerada"]))
col4.metric("Vendas Fechadas", len(df_filtered[df_filtered["Status"] == "Finalizado Positivo"]))

st.divider()

# 4. Exibição em Cards Detalhados de Leads
st.subheader("📋 Lista de Empresas")

for idx, row in df_filtered.iterrows():
    with st.expander(f"🏢 **{row['Razao_Social']}** — {row['Segmento']} ({row['Cidade']}/{row['UF']})"):
        c1, c2, c3 = st.columns([2, 2, 1.5])
        
        with c1:
            st.markdown(f"**CNPJ:** {row['CNPJ']}")
            st.markdown(f"**Data de Abertura:** {row['Data_Abertura'].strftime('%d/%m/%Y') if pd.notnull(row['Data_Abertura']) else 'N/A'}")
            st.markdown(f"**Endereço:** {row['Endereco']}")
            st.markdown(f"**Telefone/WhatsApp:** {row['Telefone']}")
            
        with c2:
            st.markdown(f"**Status Atual:** `{row['Status']}`")
            
            # Formatação de busca no Google / Instagram
            nome_busca = row['Razao_Social'].replace(' ', '+')
            cidade_busca = f"{row['Cidade']}+{row['UF']}".replace(' ', '+')
            
            url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
            url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
            
            st.markdown(f"📍 [Ver no Google Maps]({row['Link_Maps']})")
            st.markdown(f"🔍 [Pesquisar Empresa no Google]({url_google})")
            st.markdown(f"📸 [Buscar Instagram da Empresa]({url_instagram})")

        with c3:
            st.markdown("### Ações")
             novo_status = st.selectbox(
                "Atualizar Status:",
                ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"],
                index=["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"].index(row['Status']) if row['Status'] in ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"] else 0,
                key=f"status_{idx}"
            )
            
            if st.button("🚀 Gerar Landing Page Customizada", key=f"btn_lp_{idx}"):
                st.info(f"Disparando automação para gerar LP para {row['Razao_Social']}...")
                # Aqui entra o código de gatilho para automação de geração da LP
