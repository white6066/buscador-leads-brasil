import streamlit as st
import pandas as pd
import requests
import io
import csv

# 1. Configuração da página e Layout Moderno Unificado
st.set_page_config(
    page_title="Central de Leads & Novas Empresas",
    page_icon="🚀",
    layout="wide"
)

# Estilização CSS para unificar o fundo e garantir clareza visual
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #0f172a; color: #ffffff !important; padding-top: 1rem; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #f8fafc !important; font-weight: 500 !important; }
    [data-testid="stSidebar"] div.stSelectbox { margin-bottom: -10px !important; }
    [data-testid="stSidebar"] hr { margin: 10px 0px !important; border-color: #334155 !important; }
    h1, h2, h3, h4, h5, h6 { color: #0f172a !important; }

    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e2e8f0; padding: 10px 14px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label { color: #475569 !important; font-weight: 700 !important; font-size: 0.85rem !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #0f172a !important; font-size: 1.4rem !important; font-weight: 800 !important; }

    .banner-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 16px 24px; border-radius: 14px; color: white; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .banner-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 2px; color: #ffffff !important; }
    .banner-subtitle { color: #cbd5e1; font-size: 0.85rem; }
    .stSelectbox label, .stTextInput label { font-weight: 700 !important; color: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# Carregamento de dados otimizado com cache
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

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.markdown("### 🚀 Central de Leads")
        st.markdown("<p style='color: #cbd5e1; font-size: 0.8rem; margin-bottom: 0px;'>Prospecção & Inteligência</p>", unsafe_allow_html=True)
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
        st.markdown("<p style='font-size: 0.75rem; color: #94a3b8;'>💡 Clique em 'Gerenciar' para alterar status.</p>", unsafe_allow_html=True)

    # --- BANNER ---
    st.markdown("""
        <div class="banner-box">
            <div class="banner-title">🚀 Central de Leads & Novas Empresas</div>
            <div class="banner-subtitle">Filtre as empresas recém-criadas diretamente da sua planilha, pesquise presença digital e gerencie a geração diária de Landing Pages.</div>
        </div>
    """, unsafe_allow_html=True)

    # --- FILTRAGEM FLEXÍVEL E SEGURA ---
    df_filtered = current_df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado.strip()]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada.strip().upper()]
    if cidade_selecionada != "Todas":
        df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada.strip().upper()]
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
        # --- PAGINAÇÃO (25 itens por página) ---
        items_per_page = 25
        total_items = len(df_filtered)
        total_pages = max(1, (total_items - 1) // items_per_page + 1)
        
        c_p1, c_p2, c_p3 = st.columns([2, 4, 2])
        with c_p2:
            page_num = st.number_input(f"Página (Total de registos: {total_items})", min_value=1, max_value=total_pages, value=1, step=1)
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_paginated = df_filtered.iloc[start_idx:end_idx]

        # Cabeçalho Perfeitamente Alinhado com as colunas abaixo
        cols_header = st.columns([2.6, 1.4, 1.0, 0.5, 1.1, 1.2, 1.2])
        cols_header[0].markdown("**Razão Social**")
        cols_header[1].markdown("**CNPJ**")
        cols_header[2].markdown("**Abertura**")
        cols_header[3].markdown("**UF**")
        cols_header[4].markdown("**Cidade**")
        cols_header[5].markdown("**Ações Rápidas**")
        cols_header[6].markdown("**Status**")
        
        st.markdown("<hr style='margin: 2px 0px 6px 0px; border-color: #cbd5e1;'>", unsafe_allow_html=True)

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

            # Linha Principal em colunas alinhadas com os 4 ícones exatos: WhatsApp, Google Maps, Pesquisa, Instagram
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
                # 1. WhatsApp
                if tel:
                    clean_tel = "".join(filter(str.isdigit, str(tel)))
                    action_str.append(f"[🟢](https://wa.me/55{clean_tel})")
                else:
                    action_str.append("🟢")
                
                # 2. Google Maps
                if maps_link:
                    action_str.append(f"[📍]({maps_link})")
                else:
                    action_str.append("📍")
                
                # 3. Pesquisa Google
                nome_busca = str(razao).replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                action_str.append(f"[🔍](https://www.google.com/search?q={nome_busca}+{cidade_busca})")
                
                # 4. Instagram
                action_str.append(f"[📸](https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca})")
                
                st.markdown("  ".join(action_str))
            with r_cols[6]:
                st.markdown(f"🟢 `{current_status}`")

            # Expander compacto discreto para gestão do lead
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

            st.markdown("<hr style='margin: 1px 0px 3px 0px; border-color: #f1f5f9;'>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar o painel: {e}")
