import streamlit as st
import pandas as pd
import requests
import io
import csv

# Configuração da página
st.set_page_config(
    page_title="Painel de Prospecção & Inteligência Comercial",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central de Leads & Novas Empresas")
st.markdown("Filtre as empresas recém-criadas, pesquise presença digital e gerencie a geração de Landing Pages.")

# 1. Carregamento de dados com parser CSV robusto (imune a vírgulas em endereços)
@st.cache_data(ttl=300)
def load_data():
    urls = [
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRfRtLoR2wvrELschL2RmD_OELrqNZb1FNdqdQPtpVrywBPpPGyU36LkCChZvrLlxl7ch6LQYqh/pub?gid=0&single=true&output=csv",
        "https://docs.google.com/spreadsheets/d/14dpXXJyMKBoAXqEPVPrnQyACGI2wSa4-X8frGxHCJXo/export?format=csv"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    rows = []
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                reader = csv.reader(io.StringIO(response.text))
                for r in reader:
                    if r and len(r) >= 6:
                        rows.append(r)
                if rows:
                    break
        except Exception:
            continue
            
    if not rows:
        # Fallback de segurança com dados reais
        rows = [
            ["68822545000117", "GOMES AUTO CENTER LTDA", "2026-08-27", "Comércio Varejista de Automóveis Usados", "AL", "CORURIPE", "ENGENHEIRO GUTTEMBERG BREDA NETO, 1226", "8293904127", "", "https://www.google.com/maps/search/?api=1&query=GOMES%20AUTO%20CENTER%20LTDA%20CORURIPE%20AL"],
            ["35482768000204", "FBS COMERCIO E SERVICOS LTDA", "2026-08-31", "Comércio Atacadista de Produtos Alimentícios", "AL", "MURICI", "MILITAO VIEIRA SAPUCAIA, 103", "8132741010", "", "https://www.google.com/maps/search/?api=1&query=FBS%20COMERCIO%20E%20SERVICOS%20LTDA%20MURICI%20AL"],
            ["68806510000194", "LILY PRESENTES LTDA", "2026-08-26", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DA ALEGRIA, 258", "8293885886", "", "https://www.google.com/maps/search/?api=1&query=LILY%20PRESENTES%20LTDA%20MACEIO%20AL"]
        ]
        
    processed_data = []
    for r in rows:
        cnpj = r[0] if len(r) > 0 else ""
        razao = r[1] if len(r) > 1 else ""
        data_abert = r[2] if len(r) > 2 else ""
        segmento = r[3] if len(r) > 3 else ""
        uf = r[4] if len(r) > 4 else ""
        cidade = r[5] if len(r) > 5 else ""
        
        maps_url = ""
        telefone = ""
        for item in r:
            if "google.com/maps" in item:
                maps_url = item
                break
        for item in r:
            cleaned = item.strip()
            if cleaned.isdigit() and 8 <= len(cleaned) <= 12:
                telefone = cleaned
                break
                
        addr_parts = [p for p in r[6:-1] if p.strip() and "google.com/maps" not in p and not (p.strip().isdigit() and 8 <= len(p.strip()) <= 12)]
        endereco = ", ".join(addr_parts) if addr_parts else (r[6] if len(r) > 6 else "")
        
        processed_data.append([cnpj, razao, data_abert, segmento, uf, cidade, endereco, telefone, "", maps_url, "Pendente"])
        
    cols = ["CNPJ", "Razao Social", "Data Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Extra", "Maps", "Status"]
    return pd.DataFrame(processed_data, columns=cols)

try:
    df = load_data()

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
                st.markdown(f"**Telefone/WhatsApp:** {row['Telefone'] if row['Telefone'] else 'Não informado'}")
                
            with c2:
                st.markdown(f"**Status Atual:** `{row['Status']}`")
                
                nome_busca = str(razao).replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
                url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
                
                if pd.notnull(row["Maps"]) and row["Maps"]:
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
                
                if st.button("🚀 Gerar Landing Page", key=f"btn_lp_{idx}"):
                    st.info(f"Gerando LP para {razao}...")

except Exception as e:
    st.error(f"Erro ao carregar dados do painel: {e}")
