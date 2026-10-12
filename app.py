import streamlit as st
import pandas as pd
import requests
import io
import csv

# 1. Configuração da página
st.set_page_config(
    page_title="Central de Leads & Novas Empresas",
    page_icon="🚀",
    layout="wide"
)

# Inicializar o estado do Tema (Dark por predefinição)
if "theme" not in st.session_state:
    st.session_state.theme = "Escuro"

# Alternar Tema
def toggle_theme():
    if st.session_state.theme == "Escuro":
        st.session_state.theme = "Claro"
    else:
        st.session_state.theme = "Escuro"

# Cores dinâmicas completas baseadas no tema selecionado
is_dark = st.session_state.theme == "Escuro"

bg_app = "#0f172a" if is_dark else "#f8fafc"
bg_card = "#1e293b" if is_dark else "#ffffff"
text_color = "#f8fafc" if is_dark else "#0f172a"
text_muted = "#94a3b8" if is_dark else "#475569"
border_color = "#334155" if is_dark else "#cbd5e1"
hr_color = "#334155" if is_dark else "#cbd5e1"
btn_bg = "#1e293b" if is_dark else "#ffffff"
btn_text = "#ffffff" if is_dark else "#0f172a"
input_bg = "#1e293b" if is_dark else "#ffffff"
input_text = "#ffffff" if is_dark else "#0f172a"
expander_bg = "#1e293b" if is_dark else "#ffffff"
dropdown_bg = "#1e293b" if is_dark else "#ffffff"
dropdown_text = "#f8fafc" if is_dark else "#0f172a"

# Estilização CSS completa (incluindo integração do cabeçalho superior)
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_app}; color: {text_color}; }}
    
    /* Integrar cabeçalho superior do Streamlit com o tema */
    [data-testid="stHeader"] {{
        background-color: {bg_app} !important;
        border-bottom: 1px solid {border_color} !important;
    }}
    [data-testid="stHeader"] * {{
        color: {text_color} !important;
    }}
    
    /* Barra lateral */
    [data-testid="stSidebar"] {{ 
        background-color: {bg_app}; 
        color: {text_color} !important; 
        padding-top: 1rem; 
        border-right: 1px solid {border_color}; 
    }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ 
        color: {text_color} !important; 
        font-weight: 500 !important; 
    }}
    [data-testid="stSidebar"] div.stSelectbox {{ margin-bottom: -10px !important; }}
    [data-testid="stSidebar"] hr {{ margin: 10px 0px !important; border-color: {border_color} !important; }}
    
    /* Botões gerais, barra lateral, expander e paginação */
    [data-testid="stSidebar"] button, .stDownloadButton button, div[data-testid="stExpander"] button, div.row-widget.stButton button, button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    [data-testid="stSidebar"] button:hover, .stDownloadButton button:hover, div[data-testid="stExpander"] button:hover, div.row-widget.stButton button:hover, button:hover {{
        background-color: {btn_bg} !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }}
    [data-testid="stSidebar"] button:focus, .stDownloadButton button:focus, div[data-testid="stExpander"] button:focus, div.row-widget.stButton button:focus, button:focus {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border-color: #38bdf8 !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}

    a, a:hover, a:focus, a:active {{
        text-decoration: none !important;
    }}

    /* Caixas de Texto / Pesquisa Rápida */
    input[type="text"] {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
    }}
    
    div[data-baseweb="input"] {{
        background-color: {input_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}

    /* Selectbox Geral e Caixas de Filtro */
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}
    div[data-baseweb="select"] span {{
        color: {input_text} !important;
    }}
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"], div.stSelectbox div[role="listbox"] {{
        background-color: {dropdown_bg} !important;
        color: {dropdown_text} !important;
        border: 1px solid {border_color} !important;
    }}
    li[data-baseweb="option"], div[role="option"] {{
        background-color: {dropdown_bg} !important;
        color: {dropdown_text} !important;
    }}
    li[data-baseweb="option"]:hover, div[role="option"]:hover {{
        background-color: #38bdf8 !important;
        color: #0f172a !important;
    }}
    div[data-baseweb="select"] * {{
        color: {dropdown_text} !important;
    }}

    /* Cartões de Métricas */
    div[data-testid="metric-container"] {{
        background-color: {bg_card}; border: 1px solid {border_color}; padding: 12px 16px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    div[data-testid="metric-container"] label {{ color: {text_muted} !important; font-weight: 700 !important; font-size: 0.85rem !important; }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"], 
    div[data-testid="metric-container"] [data-testid="stMetricValue"] > div {{ 
        color: {text_color} !important; 
        font-size: 1.4rem !important; 
        font-weight: 800 !important; 
    }}

    /* Banner Superior */
    .banner-box {{
        background-color: {bg_card}; padding: 20px 28px; border-radius: 14px; color: {text_color}; margin-bottom: 16px; border: 1px solid {border_color}; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    .banner-title {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; color: {text_color} !important; }}
    .banner-subtitle {{ color: {text_muted}; font-size: 0.9rem; }}
    
    .stSelectbox label, .stTextInput label {{ font-weight: 700 !important; color: {text_color} !important; }}

    /* Expander e Conteúdo Interno */
    div[data-testid="stExpander"] {{
        background-color: {expander_bg} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stExpander"] summary {{
        background-color: {expander_bg} !important;
        color: {text_color} !important;
    }}
    div[data-testid="stExpander"] summary span {{
        color: {text_color} !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {{
        background-color: {expander_bg} !important;
        color: {text_color} !important;
    }}
    
    p, span, div {{
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)

# Carregamento de dados com cache
@st.cache_data(ttl=300, show_spinner="A carregar leads...")
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

    if "df_status" not in st.session_state or len(st.session_state.df_status) != len(df):
        st.session_state.df_status = df.copy()
    else:
        df["Status"] = st.session_state.df_status["Status"]

    current_df = st.session_state.df_status

    if "page_num" not in st.session_state:
        st.session_state.page_num = 1

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("### 🚀 Central de Leads")
        st.markdown("<p style='font-size: 0.8rem; margin-bottom: 0px;'>Prospecção & Inteligência</p>", unsafe_allow_html=True)
        st.divider()
        
        theme_btn_label = "☀️ Modo Claro" if not is_dark else "🌙 Modo Escuro"
        if st.button(theme_btn_label, use_container_width=True):
            toggle_theme()
            st.rerun()

        st.divider()
        st.markdown("#### 🎯 Filtros")
        
        segmentos = ["Todos"] + sorted(list(current_df["Segmento"].dropna().astype(str).str.strip().unique()))
        seg_selecionado = st.selectbox("Segmento / Nicho:", segmentos)

        ufs = ["Todos"] + sorted(list(current_df["UF"].dropna().astype(str).str.strip().str.upper().unique()))
        uf_selecionada = st.selectbox("Estado (UF):", ufs)

        cidades = ["Todas"] + sorted(list(current_df["Cidade"].dropna().astype(str).str.strip().str.upper().unique()))
        cidade_selecionada = st.selectbox("Cidade:", cidades)

        status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
        status_selecionado = st.selectbox("Status do Lead:", status_opcoes)
        
        st.divider()
        st.markdown("<p style='font-size: 0.75rem;'>💡 Use 'Gerenciar' para atualizar status.</p>", unsafe_allow_html=True)

    # --- BANNER ---
    st.markdown("""
        <div class="banner-box">
            <div class="banner-title">🚀 Central de Leads & Novas Empresas</div>
            <div class="banner-subtitle">Filtre as empresas recém-criadas diretamente da sua planilha, pesquise presença digital e gerencie a geração diária de Landing Pages.</div>
        </div>
    """, unsafe_allow_html=True)

    # --- FILTRAGEM ---
    df_filtered = current_df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada]
    if cidade_selecionada != "Todas":
        df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada]
    if status_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Status"].astype(str).str.strip() == status_selecionado.strip()]

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Exibidos", len(df_filtered))
    m2.metric("Pendentes", len(current_df[current_df["Status"] == "Pendente"]))
    m3.metric("LPs Geradas", len(current_df[current_df["Status"] == "LP Gerada"]))
    m4.metric("Vendas Fechadas", len(current_df[current_df["Status"] == "Finalizado Positivo"]))

    st.divider()

    # --- PESQUISA & EXPORTAÇÃO ---
    col_search, col_export = st.columns([5, 1])
    with col_search:
        search_query = st.text_input("🔍 Pesquisa Rápida", placeholder="Digite o nome da empresa, CNPJ ou cidade...", label_visibility="collapsed")
    with col_export:
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar", data=csv_export, file_name="leads.csv", mime="text/csv", use_container_width=True)

    if search_query:
        ql = search_query.lower()
        df_filtered = df_filtered[
            df_filtered["Razao Social"].str.lower().str.contains(ql) |
            df_filtered["CNPJ"].str.lower().str.contains(ql) |
            df_filtered["Cidade"].str.lower().str.contains(ql)
        ]

    st.subheader("📋 Lista de Empresas Extraídas")

    if df_filtered.empty:
        st.warning("Nenhum lead encontrado com os filtros ou termo de pesquisa selecionados.")
    else:
        items_per_page = 25
        total_items = len(df_filtered)
        total_pages = max(1, (total_items - 1) // items_per_page + 1)
        
        if st.session_state.page_num > total_pages:
            st.session_state.page_num = total_pages

        cols_header = st.columns([2.6, 1.4, 1.0, 0.5, 1.1, 1.2, 1.2])
        cols_header[0].markdown("**Razão Social**")
        cols_header[1].markdown("**CNPJ**")
        cols_header[2].markdown("**Abertura**")
        cols_header[3].markdown("**UF**")
        cols_header[4].markdown("**Cidade**")
        cols_header[5].markdown("**Ações Rápidas**")
        cols_header[6].markdown("**Status**")
        
        st.markdown(f"<hr style='margin: 2px 0px 6px 0px; border-color: {hr_color};'>", unsafe_allow_html=True)

        start_idx = (st.session_state.page_num - 1) * items_per_page
        start_idx = max(0, min(start_idx, total_items - 1)) if total_items > 0 else 0
        end_idx = start_idx + items_per_page
        df_paginated = df_filtered.iloc[start_idx:end_idx]

        for idx, row in df_paginated.iterrows():
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

            r_cols = st.columns([2.6, 1.4, 1.0, 0.5, 1.1, 1.2, 1.2])
            
            with r_cols[0]:
                st.markdown(f"🏢 **{razao}**")
            with r_cols[1]:
                st.markdown(f"`{cnpj}`")
            with r_cols[2]:
                st.markdown(f"{data_abert}")
            with r_cols[3]:
                st.markdown(f"{uf}")
            with r_cols[4]:
                st.markdown(f"{cidade}")
            with r_cols[5]:
                action_str = []
                if tel:
                    clean_tel = "".join(filter(str.isdigit, str(tel)))
                    action_str.append(f"[📞](https://wa.me/55{clean_tel})")
                else:
                    action_str.append("📞")
                
                if maps_link:
                    action_str.append(f"[📍]({maps_link})")
                else:
                    action_str.append("📍")
                
                nome_busca = str(razao).replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                action_str.append(f"[🔍](https://www.google.com/search?q={nome_busca}+{cidade_busca})")
                
                st.markdown("  ".join(action_str))
            with r_cols[6]:
                st.markdown(f"🟢 `{current_status}`")

            with st.expander(f"⚙️ Gerenciar: {razao}"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                with c1:
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                with c2:
                    st.markdown(f"**Telefone:** {tel if tel else 'Não informado'}")
                    st.markdown(f"📸 [Abrir Perfil no Instagram](https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca})")
                with c3:
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    try:
                        c_idx = status_list.index(current_status)
                    except ValueError:
                        c_idx = 0
                    novo_status = st.selectbox("Status:", status_list, index=c_idx, key=f"status_exp_{idx}")
                    if novo_status != current_status:
                        st.session_state.df_status.at[idx, "Status"] = novo_status
                        st.rerun()
                    if st.button("🚀 Gerar LP", key=f"btn_lp_{idx}"):
                        st.success(f"LP gerada!")

            st.markdown(f"<hr style='margin: 1px 0px 3px 0px; border-color: {border_color};'>", unsafe_allow_html=True)

        # --- PAGINAÇÃO COM BOTÕES HARMONIZADOS ---
        st.divider()
        p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns([2, 1, 1.5, 1, 2])
        
        with p_col1:
            if st.button("⏮️ Início", use_container_width=True):
                st.session_state.page_num = 1
                st.
