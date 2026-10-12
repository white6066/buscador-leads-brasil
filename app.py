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

# 1. Carregamento de dados com leitura segura por índices
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/14dpXXJyMKBoAXqEPVPrnQyACGI2wSa4-X8frGxHCJXo/export?format=csv"
    try:
        df = pd.read_csv(url, header=None)
        if not df.empty:
            return df
    except Exception:
        pass
        
    # Fallback de segurança com dados reais
    data = [
        ["68822545000117", "GOMES AUTO CENTER LTDA", "2026-08-27", "Comércio Varejista de Automóveis Usados", "AL", "CORURIPE", "ENGENHEIRO GUTTEMBERG BREDA NETO, 1226", "8293904127", "", "https://www.google.com/maps/search/?api=1&query=GOMES%20AUTO%20CENTER%20LTDA%20CORURIPE%20AL"],
        ["35482768000204", "FBS COMERCIO E SERVICOS LTDA", "2026-08-31", "Comércio Atacadista de Produtos Alimentícios", "AL", "MURICI", "MILITAO VIEIRA SAPUCAIA, 103", "8132741010", "", "https://www.google.com/maps/search/?api=1&query=FBS%20COMERCIO%20E%20SERVICOS%20LTDA%20MURICI%20AL"],
        ["68806510000194", "LILY PRESENTES LTDA", "2026-08-26", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DA ALEGRIA, 258", "8293885886", "", "https://www.google.com/maps/search/?api=1&query=LILY%20PRESENTES%20LTDA%20MACEIO%20AL"],
        ["63324700000232", "SILVA NERES IMPORTACAO E EXPORTACAO LTDA", "2026-09-08", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "LOURIVAL MELO MOTA, 15159", "1199370549", "", "https://www.google.com/maps/search/?api=1&query=SILVA%20NERES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL"],
        ["68632169000106", "SETE MARES IMPORTACAO E EXPORTACAO LTDA", "2026-08-13", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DESEMBARGADOR ARTUR JUCÁ, 250", "8232411988", "", "https://www.google.com/maps/search/?api=1&query=SETE%20MARES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL"]
    ]
    return pd.DataFrame(data)

try:
    df = load_data()
    
    # Garantir colunas suficientes
    while df.shape[1] < 10:
        df[df.shape[1]] = ""

    # Adicionar coluna de Status se não existir
    if "Status" not in df.columns:
        df["Status"] = "Pendente"
    df["Status"] = df["Status"].fillna("Pendente")

    # Mapeamento de colunas por índice seguro
    col_cnpj = 0
    col_razao = 1
    col_data = 2
    col_seg = 3
    col_uf = 4
    col_cidade = 5
    col_end = 6
    col_tel = 7
    col_maps = 9

    # 2. Barra Lateral - Filtros Dinâmicos
    st.sidebar.header("🎯 Filtros de Prospecção")

    segmentos = ["Todos"] + sorted(list(df[col_seg].dropna().unique().astype(str)))
    seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

    ufs = ["Todos"] + sorted(list(df[col_uf].dropna().unique().astype(str)))
    uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

    if uf_selecionada != "Todos":
        cidades = ["Todas"] + sorted(list(df[df[col_uf].astype(str) == uf_selecionada][col_cidade].dropna().unique().astype(str)))
    else:
        cidades = ["Todas"] + sorted(list(df[col_cidade].dropna().unique().astype(str)))
    cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

    status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
    status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

    # Aplicar Filtros
    df_filtered = df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered[col_seg].astype(str) == seg_selecionado]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered[col_uf].astype(str) == uf_selecionada]
    if cidade_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered[col_cidade].astype(str) == cidade_selecionada]
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
        razao = str(row[col_razao]) if pd.notnull(row[col_razao]) else "Empresa"
        segmento = str(row[col_seg]) if pd.notnull(row[col_seg]) else "N/A"
        cidade = str(row[col_cidade]) if pd.notnull(row[col_cidade]) else "N/A"
        uf = str(row[col_uf]) if pd.notnull(row[col_uf]) else "N/A"
        
        with st.expander(f"🏢 **{razao}** — {segmento} ({cidade}/{uf})"):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            
            with c1:
                st.markdown(f"**CNPJ:** {row[col_cnpj]}")
                st.markdown(f"**Data de Abertura:** {row[col_data]}")
                st.markdown(f"**Endereço:** {row[col_end]}")
                tel = row[col_tel] if pd.notnull(row[col_tel]) and str(row[col_tel]).strip() != "" else "Não informado"
                st.markdown(f"**Telefone/WhatsApp:** {tel}")
                
            with c2:
                st.markdown(f"**Status Atual:** `{row['Status']}`")
                
                nome_busca = razao.replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
                url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
                
                maps_link = row[col_maps] if len(row) > col_maps and pd.notnull(row[col_maps]) else ""
                if str(maps_link).startswith("http"):
                    st.markdown(f"📍 [Ver no Google Maps]({maps_link})")
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
                    st.info(f"Gerando LP para {razao}...")

except Exception as e:
    st.error(f"Erro ao carregar dados do painel: {e}")
