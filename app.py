import streamlit as st
import pandas as pd
import requests
import io
import csv

# 1. Configuração da página e Layout Moderno Compacto
st.set_page_config(
    page_title="Central de Leads & Novas Empresas",
    page_icon="🚀",
    layout="wide"
)

# Estilização CSS personalizada para compactar espaçamentos na barra lateral
st.markdown("""
<style>
    /* Estilo geral de fundo */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Barra lateral escura compactada */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #ffffff !important;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #f8fafc !important;
        font-weight: 500 !important;
    }

    /* Reduzir margens e espaçamentos entre widgets na barra lateral */
    [data-testid="stSidebar"] div.stSelectbox {
        margin-bottom: -10px !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 10px 0px !important;
        border-color: #334155 !important;
    }
    
    /* Cor dos títulos e textos principais do painel */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
    }

    /* Cartões de Métricas Estilizados */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }

    /* Banner Principal */
    .banner-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .banner-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: #ffffff !important;
    }
    .banner-subtitle {
        color: #cbd5e1;
        font-size: 0.9rem;
    }

    /* Rótulos dos filtros principais do corpo da página */
    .stSelectbox label, .stTextInput label {
        font-weight: 700 !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# Carregamento de dados com cache de alta performance
@st.cache_data(ttl=300, show_spinner="A carregar painel corporativo...")
def load_data_from_sheet():
    sheet_id = "14dpXXJyMKBoAXqEPVPrnQyACGI2wSa4-X8frGxHCJXo"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    reader = csv.reader(io.StringIO(response.text))
    rows = [r for r in reader if r]
            
    processed = []
    for r in rows:
        while len(r) < 10:
            r.append("")
            
        cnpj = str(r[0]).strip()
        razao = str(r[1]).strip() if str(r[1]).strip() != "" else "Empresa"
        data_abert = str(r[2]).strip()
        segmento = str(r[3]).strip() if str(r[3]).strip() != "" else "N/A"
        uf = str(r[4]).strip().upper() if str(r[4]).strip() != "" else "N/A"
        cidade = str(r[5]).strip().upper() if str(r[5]).strip() != "" else "N/A"
        
        if cnpj.lower() == "cnpj" or "razão social" in razao.lower():
            continue
            
        maps_url = ""
        telefone = ""
        for item in r:
            if "google.com/maps" in item:
                maps_url = item.strip()
                break
        for item in r:
            cleaned = item.strip()
            if cleaned.isdigit() and 8 <= len(cleaned) <= 12:
                telefone = cleaned
                break
                
        addr_parts = [p.strip() for p in r[6:-1] if p.strip() and "google.com/maps" not in p and not (p.strip().isdigit() and 8 <= len(p.strip()) <= 12)]
        endereco = ", ".join(addr_parts) if addr_parts else str(r[6]).strip()
        
        processed.append([cnpj, razao, data_abert, segmento, uf, cidade, endereco, telefone, maps_url, "Pendente"])
        
    cols = ["CNPJ", "Razao Social", "Data Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Maps", "Status"]
    return pd.DataFrame(processed, columns=cols)

try:
    df = load_data_from_sheet()

    # Sincronização de status na sessão
    if "df_status" not in st.session_state or len(st.session_state.df_status) != len(df):
        st.session_state.df_status = df.copy()
    else:
        df["Status"] = st.session_state.df_status["Status"]

    current_df = st.session_state.df_status

    # --- BARRA LATERAL COMPACTA ---
    with st.sidebar:
        st.markdown("### 🚀 Central de Leads")
        st.markdown("<p style='color: #cbd5e1; font-size: 0.8rem; margin-bottom: 0px;'>Prospecção & Inteligência Comercial</p>", unsafe_allow_html=True)
        st.divider()
        
        st.markdown("#### 🎯 Filtros")
        
        segmentos = ["Todos"] + sorted(list(current_df["Segmento"].dropna().unique().astype(str)))
        seg_selecionado = st.selectbox("Segmento / Nicho:", segmentos)

        ufs = ["Todos"] + sorted(list(current_df["UF"].dropna().unique().astype(str)))
        uf_selecionada = st.selectbox("Estado (UF):", ufs)

        if uf_selecionada != "Todos":
            cidades = ["Todas"] + sorted(list(current_df[current_df["UF"].astype(str).str.strip().str.upper() == uf_selecionada.strip().upper()]["Cidade"].dropna().unique().astype(str)))
        else:
            cidades = ["Todas"] + sorted(list(current_df["Cidade"].dropna().unique().astype(str)))
        cidade_selecionada = st.selectbox("Cidade:", cidades)

        status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
        status_selecionado = st.selectbox("Status do Lead:", status_opcoes)
        
        st.divider()
        st.markdown("<p style='font-size: 0.75rem; color: #94a3b8;'>💡 Dica: Use os expanders para gerenciar cada lead.</p>", unsafe_allow_html=True)

    # --- BANNER PRINCIPAL DO TOPO ---
    st.markdown("""
        <div class="banner-box">
            <div class="banner-title">🚀 Central de Leads & Novas Empresas</div>
            <div class="banner-subtitle">Filtre as empresas recém-criadas diretamente da sua planilha, pesquise presença digital e gerencie a geração diária de Landing Pages.</div>
        </div>
    """, unsafe_allow_html=True)

    # --- APLICAR FILTROS DE FORMA ROBUSTA ---
    df_filtered = current_df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado.strip()]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada.strip().upper()]
    if cidade_selecionada != "Todas" and cidade_selecionada != "Todas":
        df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada.strip().upper()]
    if status_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Status"].astype(str).str.strip() == status_selecionado.strip()]

    # --- CARTÕES DE MÉTRICAS MODERNOS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total de Leads Exibidos", len(df_filtered), "100% visível")
    m2.metric("Pendentes", len(current_df[current_df["Status"] == "Pendente"]), "Aguardando")
    m3.metric("LPs Geradas", len(current_df[current_df["Status"] == "LP Gerada"]), "Prontas")
    m4.metric("Vendas Fechadas", len(current_df[current_df["Status"] == "Finalizado Positivo"]), "Conversões")

    st.divider()

    # --- BARRA DE PESQUISA RÁPIDA DE EMPRESAS ---
    col_search, col_export = st.columns([5, 1])
    with col_search:
        search_query = st.text_input("🔍 Pesquisa Rápida", placeholder="Digite o nome da empresa, CNPJ ou cidade...", label_visibility="collapsed")
    with col_export:
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar CSV", data=csv_export, file_name="leads_prospeccao.csv", mime="text/csv", use_container_width=True)

    if search_query:
        query_lower = search_query.lower()
        df_filtered = df_filtered[
            df_filtered["Razao Social"].str.lower().str.contains(query_lower) |
            df_filtered["CNPJ"].str.lower().str.contains(query_lower) |
            df_filtered["Cidade"].str.lower().str.contains(query_lower)
        ]

    st.subheader("📋 Lista de Empresas Extraídas")

    if df_filtered.empty:
        st.warning("Nenhum lead encontrado com os filtros ou termo de pesquisa selecionados.")
    else:
        # Cabeçalho da Tabela Estilo Corporativo Moderno
        cols_header = st.columns([2.6, 1.4, 1.0, 0.5, 1.1, 1.2, 1.2])
        cols_header[0].markdown("**Razão Social**")
        cols_header[1].markdown("**CNPJ**")
        cols_header[2].markdown("**Abertura**")
        cols_header[3].markdown("**UF**")
        cols_header[4].markdown("**Cidade**")
        cols_header[5].markdown("**Ações Rápidas**")
        cols_header[6].markdown("**Status**")
        
        st.markdown("<hr style='margin: 4px 0px 10px 0px; border-color: #e2e8f0;'>", unsafe_allow_html=True)

        for idx, row in df_filtered.iterrows():
            razao = row["Razao Social"]
            segmento = row["Segmento"]
            cidade = row["Cidade"]
            uf = row["UF"]
            cnpj = row["CNPJ"]
            data_abert = row["Data Abertura"]
            endereco = row["Endereco"]
            tel = row["Telefone"]
            maps_link = row["Maps"]
            current_status = row["Status"]

            with st.expander(f"🏢 **{razao}**  |  {cnpj}  |  {data_abert}  |  {uf}  |  {cidade}  |  `Status: {current_status}`"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                
                with c1:
                    st.markdown(f"**Razão Social:** {razao}")
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**CNPJ:** {cnpj}")
                    st.markdown(f"**Data de Abertura:** {data_abert}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                    
                with c2:
                    tel_display = tel if tel != "" else "Não informado"
                    st.markdown(f"**Telefone:** {tel_display}")
                    
                    if tel:
                        clean_tel = "".join(filter(str.isdigit, str(tel)))
                        st.markdown(f"💬 [Abrir Conversa no WhatsApp](https://wa.me/55{clean_tel})")
                    
                    if maps_link:
                        st.markdown(f"🗺️ [Ver no Google Maps]({maps_link})")
                        
                    nome_busca = str(razao).replace(' ', '+')
                    cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                    st.markdown(f"🔍 [Pesquisar no Google](https://www.google.com/search?q={nome_busca}+{cidade_busca})")
                    st.markdown(f"📸 [Buscar Instagram](https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca})")

                with c3:
                    st.markdown("### Gestão do Lead")
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    try:
                        c_idx = status_list.index(current_status)
                    except ValueError:
                        c_idx = 0
                        
                    novo_status = st.selectbox(
                        "Atualizar Status:",
                        status_list,
                        index=c_idx,
                        key=f"status_exp_{idx}"
                    )
                    
                    if novo_status != current_status:
                        st.session_state.df_status.at[idx, "Status"] = novo_status
                        st.rerun()
                        
                    if st.button("🚀 Gerar Landing Page", key=f"btn_lp_{idx}"):
                        st.success(f"LP gerada para {razao}!")

            st.markdown("<hr style='margin: 2px 0px 6px 0px; border-color: #f1f5f9;'>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar o painel: {e}")
