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
st.markdown("Filtre as empresas recém-criadas diretamente da sua planilha, pesquise presença digital e gerencie a geração diária de Landing Pages.")

# Carregamento de dados seguro e sem exclusões acidentales
@st.cache_data(ttl=15)
def load_data_from_sheet():
    sheet_id = "14dpXXJyMKBoAXqEPVPrnQyACGI2wSa4-X8frGxHCJXo"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    reader = csv.reader(io.StringIO(response.text))
    rows = []
    for r in reader:
        if r and len(r) > 0:
            val0 = str(r[0]).strip().lower()
            # Ignorar apenas linhas de página em branco
            if val0 == "" or "página1" in val0:
                continue
            rows.append(r)
            
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
        
        # Descartar estritamente a linha de cabeçalho nominal se ela aparecer nos dados
        if cnpj.lower() == "cnpj" or razao.lower() == "razão social":
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

    # Sincronização e persistência de status na sessão
    if "df_status" not in st.session_state or len(st.session_state.df_status) != len(df):
        st.session_state.df_status = df.copy()
    else:
        df["Status"] = st.session_state.df_status["Status"]

    current_df = st.session_state.df_status

    # 2. Barra Lateral - Filtros Dinâmicos
    st.sidebar.header("🎯 Filtros de Prospecção")

    segmentos = ["Todos"] + sorted(list(current_df["Segmento"].dropna().unique().astype(str)))
    seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

    ufs = ["Todos"] + sorted(list(current_df["UF"].dropna().unique().astype(str)))
    uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

    if uf_selecionada != "Todos":
        cidades = ["Todas"] + sorted(list(current_df[current_df["UF"].astype(str).str.strip().str.upper() == uf_selecionada.strip().upper()]["Cidade"].dropna().unique().astype(str)))
    else:
        cidades = ["Todas"] + sorted(list(current_df["Cidade"].dropna().unique().astype(str)))
    cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

    status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
    status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

    # Aplicar Filtros com correspondência flexível e segura
    df_filtered = current_df.copy()
    if seg_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado.strip()]
    if uf_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada.strip().upper()]
    if cidade_selecionada != "Todos":
        df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada.strip().upper()]
    if status_selecionado != "Todos":
        df_filtered = df_filtered[df_filtered["Status"].astype(str).str.strip() == status_selecionado.strip()]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Leads Exibidos", len(df_filtered))
    col2.metric("Pendentes", len(current_df[current_df["Status"] == "Pendente"]))
    col3.metric("LPs Geradas", len(current_df[current_df["Status"] == "LP Gerada"]))
    col4.metric("Vendas Fechadas", len(current_df[current_df["Status"] == "Finalizado Positivo"]))

    st.divider()

    st.subheader("📋 Lista de Empresas Extraídas")

    if df_filtered.empty:
        st.info("Nenhum lead encontrado com os filtros selecionados. Tente redefinir os filtros na barra lateral.")
    else:
        # Cabeçalho da Tabela Estilo Planilha Corporativa
        cols_header = st.columns([2.5, 1.4, 1.0, 0.5, 1.1, 1.2, 1.3])
        cols_header[0].markdown("**Razão Social**")
        cols_header[1].markdown("**CNPJ**")
        cols_header[2].markdown("**Abertura**")
        cols_header[3].markdown("**UF**")
        cols_header[4].markdown("**Cidade**")
        cols_header[5].markdown("**Ações Rápidas**")
        cols_header[6].markdown("**Status**")
        
        st.markdown("<hr style='margin: 2px 0px 8px 0px;'>", unsafe_allow_html=True)

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

            st.markdown("<hr style='margin: 1px 0px 4px 0px; border-color: #f0f2f6;'>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar o painel: {e}")
