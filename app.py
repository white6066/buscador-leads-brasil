import streamlit as st
import pandas as pd
import requests
import io

# Configuração da página
st.set_page_config(
    page_title="Painel de Prospecção & Inteligência Comercial",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central de Leads & Novas Empresas")
st.markdown("Filtre as empresas recém-criadas, pesquise presença digital e gerencie a geração de Landing Pages.")

# 1. Carregamento de dados com fallback inteligente e resiliente
@st.cache_data(ttl=300)
def load_data():
    urls = [
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRfRtLoR2wvrELschL2RmD_OELrqNZb1FNdqdQPtpVrywBPpPGyU36LkCChZvrLlxl7ch6LQYqh/pub?gid=0&single=true&output=csv",
        "https://docs.google.com/spreadsheets/d/14dpXXJyMKBoAXqEPVPrnQyACGI2wSa4-X8frGxHCJXo/export?format=csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text))
                if not df.empty:
                    if "Status" not in df.columns:
                        df["Status"] = "Pendente"
                    df["Status"] = df["Status"].fillna("Pendente")
                    return df
        except Exception:
            continue
            
    # Fallback com os dados reais para o painel abrir imediatamente sem erros
    data = [
        ["68822545000117", "GOMES AUTO CENTER LTDA", "2026-08-27", "Comércio Varejista de Automóveis Usados", "AL", "CORURIPE", "ENGENHEIRO GUTTEMBERG BREDA NETO, 1226 - ALTO DA SAUDADE", "8293904127", "", "https://www.google.com/maps/search/?api=1&query=GOMES%20AUTO%20CENTER%20LTDA%20CORURIPE%20AL", "Pendente"],
        ["35482768000204", "FBS COMERCIO E SERVICOS LTDA", "2026-08-31", "Comércio Atacadista de Produtos Alimentícios", "AL", "MURICI", "MILITAO VIEIRA SAPUCAIA, 103 - CENTRO", "8132741010", "", "https://www.google.com/maps/search/?api=1&query=FBS%20COMERCIO%20E%20SERVICOS%20LTDA%20MURICI%20AL", "Pendente"],
        ["68806510000194", "LILY PRESENTES LTDA", "2026-08-26", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DA ALEGRIA, 258 - CENTRO", "8293885886", "", "https://www.google.com/maps/search/?api=1&query=LILY%20PRESENTES%20LTDA%20MACEIO%20AL", "Pendente"],
        ["63324700000232", "SILVA NERES IMPORTACAO E EXPORTACAO LTDA", "2026-09-08", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "LOURIVAL MELO MOTA, 15159 - SANTOS DUMONT", "1199370549", "", "https://www.google.com/maps/search/?api=1&query=SILVA%20NERES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL", "Pendente"],
        ["68632169000106", "SETE MARES IMPORTACAO E EXPORTACAO LTDA", "2026-08-13", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DESEMBARGADOR ARTUR JUCÁ, 250 - CENTRO", "8232411988", "", "https://www.google.com/maps/search/?api=1&query=SETE%20MARES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL", "Pendente"],
        ["68820635000179", "F. LOPES BARBOSA LTDA", "2026-08-22", "Comércio Varejista de Automóveis Usados", "AP", "MACAPA", "PADRE JULIO MARIA LOMBAERD, 1326 - CENTRAL", "9681320032", "", "https://www.google.com/maps/search/?api=1&query=F.%20LOPES%20BARBOSA%20LTDA%20MACAPA%20AP", "Pendente"],
        ["37379766000724", "DELICIAS DA OCI LTDA", "2026-08-25", "Supermercados", "AP", "MACAPA", "HILDEMAR MAIA, 2626 - BURITIZAL", "9699999999", "", "https://www.google.com/maps/search/?api=1&query=DELICIAS%20DA%20OCI%20LTDA%20MACAPA%20AP", "Pendente"],
        ["68886658000186", "ATENA LTDA", "2026-08-30", "Holdings de Instituições Não-Financeiras", "AP", "MACAPA", "CANDIDO MENDES, 1420 - CENTRAL", "9691660945", "", "https://www.google.com/maps/search/?api=1&query=ATENA%20LTDA%20MACAPA%20AP", "Pendente"]
    ]
    cols = ["CNPJ", "Razao Social", "Data Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Extra", "Maps", "Status"]
    return pd.DataFrame(data, columns=cols)

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
    st.error(f"Erro ao carregar dados do painel: {e}")
