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

# 1. Carregamento de dados da planilha via link público do Google Sheets (gviz)
@st.cache_data(ttl=300)
def load_data():
    sheet_id = "11FwBk_p5VK7OxR8LiPeTFZ_HuX1opMrZrX2fCxcX8pQ"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(url)
    if "Status" not in df.columns:
        df["Status"] = "Pendente"
    df["Status"] = df["Status"].fillna("Pendente")
    return df

try:
    df = load_data()

    # 2. Barra Lateral - Filtros Dinâmicos
    st.sidebar.header("🎯 Filtros de Prospecção")

    segmentos = ["Todos"] + sorted(list(df.iloc[:, 3].dropna().unique()))
    seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

    ufs = ["Todos"] + sorted(list(df.iloc[:, 4].dropna().unique()))
    uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

    if uf_selecionada != "Todos":
        cidades = ["Todas"] + sorted(list(df[df.iloc[:, 4] == uf_selecionada].iloc[:, 5].dropna().unique()))
    else:
        cidades = ["Todas"] + sorted(list(df.iloc[:, 5].dropna().unique()))
    cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

    status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
    status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

    # Aplicar Filtros
    df_filtered = df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered.iloc[:, 3] == seg_selecionado]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered.iloc[:, 4] == uf_selecionada]
    if cidade_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered.iloc[:, 5] == cidade_selecionada]
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

    for idx, row in df_filtered.iterrows():
        razao = row.iloc[1] if len(row) > 1 else "Empresa"
        segmento = row.iloc[3] if len(row) > 3 else "N/A"
        cidade = row.iloc[5] if len(row) > 5 else "N/A"
        uf = row.iloc[4] if len(row) > 4 else "N/A"
        
        with st.expander(f"🏢 **{razao}** — {segmento} ({cidade}/{uf})"):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            
            with c1:
                st.markdown(f"**CNPJ:** {row.iloc[0]}")
                st.markdown(f"**Data de Abertura:** {row.iloc[2]}")
                st.markdown(f"**Endereço:** {row.iloc[6] if len(row) > 6 else 'N/A'}")
                st.markdown(f"**Telefone/WhatsApp:** {row.iloc[7] if len(row) > 7 else 'N/A'}")
                
            with c2:
                st.markdown(f"**Status Atual:** `{row['Status']}`")
                
                nome_busca = str(razao).replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
                url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
                
                if len(row) > 9 and pd.notnull(row.iloc[9]):
                    st.markdown(f"📍 [Ver no Google Maps]({row.iloc[9]})")
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
                
                if st.button("🚀 Gerar Landing Page", key=f"btn_lp_{idx}"):
                    st.info(f"Gerando LP para {razao}...")

except Exception as e:
    st.error(f"Erro ao carregar dados da planilha: {e}")
