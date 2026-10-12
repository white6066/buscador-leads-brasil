import streamlit as st
import pandas as pd
import requests
import io
import csv
import urllib.parse
import random
import hashlib

# 1. Configuração da página
st.set_page_config(
    page_title="Novas Empresas - Acompanhamento & Gerador LP Avançado",
    page_icon="🚀",
    layout="wide"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Claro"

def toggle_theme():
    st.session_state.theme = "Claro" if st.session_state.theme == "Escuro" else "Escuro"

is_dark = st.session_state.theme == "Escuro"

bg_app = "#090d16" if is_dark else "#f1f5f9"
bg_card = "#111827" if is_dark else "#ffffff"
text_color = "#f3f4f6" if is_dark else "#0f172a"
text_muted = "#9ca3af" if is_dark else "#64748b"
border_color = "#1f2937" if is_dark else "#cbd5e1"
hr_color = "#1f2937" if is_dark else "#cbd5e1"
btn_bg = "#1f2937" if is_dark else "#ffffff"
btn_text = "#f3f4f6" if is_dark else "#0f172a"
input_bg = "#111827" if is_dark else "#ffffff"
input_text = "#f3f4f6" if is_dark else "#0f172a"
expander_bg = "#111827" if is_dark else "#ffffff"
dropdown_bg = "#111827" if is_dark else "#ffffff"
dropdown_text = "#f3f4f6" if is_dark else "#0f172a"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_app}; color: {text_color}; }}
    html, body, [class*="st-"] {{ font-size: 0.92rem !important; }}
    
    [data-testid="stHeader"] {{ background-color: {bg_app} !important; border-bottom: 1px solid {border_color} !important; }}
    [data-testid="stHeader"] * {{ color: {text_color} !important; }}
    
    [data-testid="stSidebar"] {{ background-color: {bg_app}; color: {text_color} !important; padding-top: 1rem; border-right: 1px solid {border_color}; }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: {text_color} !important; font-weight: 500 !important; font-size: 0.9rem !important; }}
    [data-testid="stSidebar"] div.stSelectbox {{ margin-bottom: -10px !important; }}
    [data-testid="stSidebar"] hr {{ margin: 12px 0px !important; border-color: {border_color} !important; }}
    
    [data-testid="stSidebar"] button, .stDownloadButton button, div[data-testid="stExpander"] button, div.row-widget.stButton button, button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        transition: all 0.2s ease-in-out;
        font-size: 0.88rem !important;
    }}
    [data-testid="stSidebar"] button:hover, .stDownloadButton button:hover, div[data-testid="stExpander"] button:hover, div.row-widget.stButton button:hover, button:hover {{
        background-color: {btn_bg} !important;
        border-color: #0ea5e9 !important;
        color: #0ea5e9 !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
    }}
    
    h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; font-family: system-ui, -apple-system, sans-serif; }}
    a {{ text-decoration: none !important; }}

    input[type="text"] {{ background-color: {input_bg} !important; color: {input_text} !important; border: 1px solid {border_color} !important; font-size: 0.9rem !important; }}
    div[data-baseweb="input"] {{ background-color: {input_bg} !important; border: 1px solid {border_color} !important; border-radius: 4px !important; }}

    div[data-baseweb="select"] > div {{ background-color: {input_bg} !important; color: {input_text} !important; border: 1px solid {border_color} !important; border-radius: 4px !important; overflow: hidden !important; }}
    div[data-baseweb="select"] span {{ color: {input_text} !important; font-size: 0.9rem !important; }}
    div[data-baseweb="select"] div[role="button"] {{ border-left: none !important; box-shadow: none !important; }}
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"], div.stSelectbox div[role="listbox"] {{ background-color: {dropdown_bg} !important; color: {dropdown_text} !important; border: 1px solid {border_color} !important; border-radius: 4px !important; }}
    li[data-baseweb="option"], div[role="option"] {{ background-color: {dropdown_bg} !important; color: {dropdown_text} !important; font-size: 0.9rem !important; }}
    li[data-baseweb="option"]:hover, div[role="option"]:hover {{ background-color: #0ea5e9 !important; color: #ffffff !important; }}

    div[data-testid="metric-container"] {{ background-color: {bg_card}; border: 1px solid {border_color}; padding: 14px 18px; border-radius: 6px; }}
    div[data-testid="metric-container"] label {{ color: {text_muted} !important; font-weight: 600 !important; font-size: 0.8rem !important; }}
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: {text_color} !important; font-size: 1.35rem !important; font-weight: 800 !important; }}

    .banner-box {{ background-color: {bg_card}; padding: 20px 28px; border-radius: 6px; color: {text_color}; margin-bottom: 20px; border: 1px solid {border_color}; }}
    .banner-title {{ font-size: 1.35rem; font-weight: 800; margin-bottom: 4px; color: {text_color} !important; }}
    .banner-subtitle {{ color: {text_muted}; font-size: 0.85rem; line-height: 1.4; }}
    
    div[data-testid="stExpander"] {{ background-color: {expander_bg} !important; border: 1px solid {border_color} !important; border-radius: 6px !important; }}
    div[data-testid="stExpander"] summary {{ background-color: {expander_bg} !important; color: {text_color} !important; border-radius: 6px !important; font-size: 0.9rem !important; }}
    p, span, div {{ color: {text_color}; font-size: 0.9rem !important; }}
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE CONSULTA EXTERNA & WEB SCRAPING INTELIGENTE ---
def fetch_external_web_intelligence(razao, segmento, cidade, uf):
    query = f"{razao} {segmento} {cidade} {uf}"
    encoded_q = urllib.parse.quote(query)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    snippets = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', class_='result__snippet', limit=4):
                txt = a.get_text().strip()
                if txt:
                    snippets.append(txt)
    except Exception:
        pass
        
    return snippets

# --- ENGINE DE GERAÇÃO INTELIGENTE DE CORES E LÓGICA DE SEGMENTO ---
def generate_unique_landing_page(razao, segmento, cidade, uf, endereco, tel, data_abert):
    # 1. Executar consulta externa
    snippets = fetch_external_web_intelligence(razao, segmento, cidade, uf)
    context_research = " ".join(snippets[:2]) if snippets else f"Excelência e referência em {segmento} para clientes exigentes."

    # 2. Gerar cores exclusivas por criptografia e características do nicho
    seg_lower = segmento.lower()
    
    # Hash único para criar paletas de cores irrepetíveis por empresa
    hash_object = hashlib.md5((razao + segmento).encode())
    hex_digest = hash_object.hexdigest()
    
    # Cores baseadas no nicho com variação única por hash
    if any(x in seg_lower for x in ['advoc', 'jurid', 'contab', 'consult', 'peric']):
        # Tons corporativos sofisticados (Azul Profundo / Grafite / Dourado)
        primary = f"#{hex_digest[:6]}" if int(hex_digest[:2], 16) < 150 else "#1e3a8a"
        secondary = "#0f172a"
        scope_logic = "Atendimento jurídico e consultoria estratégica com abrangência nacional e suporte digital dedicado."
        cta_text = "Falar com Advogado / Consultor"
    elif any(x in seg_lower for x in ['estet', 'beleza', 'salao', 'cosmet', 'spa', 'sobrancelh']):
        # Tons elegantes (Rose / Vinho / Nude)
        primary = f"#{hex_digest[:6]}" if int(hex_digest[:2], 16) > 100 else "#db2777"
        secondary = "#831843"
        scope_logic = f"Atendimento presencial exclusivo com hora marcada em {cidade}/{uf} para elevar sua autoestima e bem-estar."
        cta_text = "Agendar Horário VIP"
    elif any(x in seg_lower for x in ['saude', 'medic', 'clinica', 'odont', 'denta', 'psic']):
        # Tons clínicos de confiança (Turquesa / Azul Clínico)
        primary = f"#{hex_digest[:6]}" if int(hex_digest[:2], 16) < 200 else "#0d9488"
        secondary = "#115e59"
        scope_logic = f"Estrutura clínica moderna e acolhedora localizada em {cidade} com foco em saúde preventiva e tratamentos avançados."
        cta_text = "Agendar Consulta"
    elif any(x in seg_lower for x in ['auto', 'veicul', 'mecanic', 'carro', 'pneu']):
        # Tons fortes (Vermelho / Grafite Industrial)
        primary = f"#{hex_digest[:6]}" if int(hex_digest[:2], 16) < 200 else "#dc2626"
        secondary = "#18181b"
        scope_logic = f"Oficina e soluções automotivas completas em {cidade}/{uf} com equipamentos de última geração e peças genuínas."
        cta_text = "Solicitar Orçamento Rápido"
    else:
        # Padrão dinâmico exclusivo baseado no hash da empresa
        primary = f"#{hex_digest[:6]}"
        secondary = "#0f172a"
        scope_logic = f"Soluções profissionais e personalizadas no segmento de {segmento} com atendimento ágil em {cidade} e região."
        cta_text = "Entrar em Contato Agora"

    clean_tel = "".join(filter(str.isdigit, str(tel))) if tel else ""
    whats_link = f"https://wa.me/55{clean_tel}" if clean_tel else "#"

    # Imagens de fundo dinâmicas
    bg_images = [
        "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=80",
        "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1400&q=80"
    ]
    hero_bg_img = bg_images[abs(hash(razao)) % len(bg_images)]

    # HTML da Landing Page Exclusiva
    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{razao} | {segmento} em {cidade}/{uf}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .custom-primary {{ background-color: {primary}; }}
        .custom-text {{ color: {primary}; }}
        .custom-border {{ border-color: {primary}; }}
        .custom-hero {{ background: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), url('{hero_bg_img}'); background-size: cover; background-position: center; }}
    </style>
</head>
<body class="font-sans antialiased bg-slate-50 text-slate-800">

    <!-- Top Notice Bar -->
    <div class="bg-slate-950 text-slate-300 text-xs py-2 px-4 text-center border-b border-slate-800">
        ⭐ Especialistas em {segmento} | Atendimento Dedicado
    </div>

    <!-- Sticky Header -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="font-black text-xl tracking-tight text-slate-900 uppercase flex items-center gap-2">
                <span class="w-3.5 h-3.5 rounded-full inline-block custom-primary"></span>
                {razao}
            </div>
            <a href="{whats_link}" target="_blank" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs md:text-sm px-5 py-2.5 rounded-lg shadow transition flex items-center gap-2">
                💬 WhatsApp Direto
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative text-white py-24 px-4 custom-hero">
        <div class="max-w-4xl mx-auto text-center">
            <span class="inline-block custom-primary text-white text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider mb-4">Referência em {segmento}</span>
            <h1 class="text-3xl md:text-5xl font-black mb-6 leading-tight">Soluções Especializadas de Alto Padrão</h1>
            <p class="text-base md:text-lg text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">{context_research}</p>
            <div class="flex flex-col sm:flex-row justify-center gap-4">
                <a href="{whats_link}" target="_blank" class="bg-emerald-500 hover:bg-emerald-600 text-white text-base font-bold px-8 py-4 rounded-xl shadow-lg transition transform hover:-translate-y-0.5">
                    🚀 {cta_text}
                </a>
            </div>
        </div>
    </section>

    <!-- Quem Somos & Lógica de Atuação -->
    <section class="py-16 px-4 bg-white border-b border-slate-200">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-2xl md:text-3xl font-bold text-slate-900 mb-4">Quem Somos & Nossa Proposta</h2>
            <div class="w-16 h-1 custom-primary mx-auto mb-6 rounded"></div>
            <p class="text-slate-600 leading-relaxed text-base mb-6">A <b>{razao}</b> foi constituída em <b>{data_abert}</b> com o compromisso firme de excelência no segmento de <b>{segmento}</b>. {scope_logic}</p>
            <p class="text-slate-600 text-sm">📍 <b>Localização de Apoio:</b> {endereco if endereco else cidade + ' - ' + uf}</p>
        </div>
    </section>

    <!-- Pilares / Serviços -->
    <section class="py-16 px-4 max-w-6xl mx-auto">
        <div class="text-center mb-12">
            <h2 class="text-2xl md:text-3xl font-bold text-slate-900">Nossos Diferenciais</h2>
            <p class="text-slate-600 mt-2">Por que escolher a {razao}?</p>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 custom-primary text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">✓</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Estratégia Personalizada</h3>
                <p class="text-slate-600 text-sm leading-relaxed">Atendimento desenhado sob medida para atender exatamente à sua demanda com eficiência.</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 custom-primary text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">⚡</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Agilidade e Rigor</h3>
                <p class="text-slate-600 text-sm leading-relaxed">Processos estruturados para garantir prazos cumpridos e padrão superior de entrega.</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 custom-primary text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">🛡️</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">Compromisso e Ética</h3>
                <p class="text-slate-600 text-sm leading-relaxed">Transparência em todas as etapas para construir parcerias sólidas e duradouras.</p>
            </div>
        </div>
    </section>

    <!-- Contato & Call to Action Final -->
    <section class="py-16 px-4 bg-slate-900 text-white">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-2xl md:text-3xl font-bold mb-4">Vamos Conversar?</h2>
            <p class="text-slate-400 mb-8">Entre em contato direto com os especialistas da <b>{razao}</b>.</p>
            <div class="inline-block bg-slate-800 p-6 rounded-2xl border border-slate-700 text-left mb-8 w-full max-w-md">
                <p class="text-sm text-slate-300 mb-2"><b>📍 Endereço:</b> {endereco if endereco else cidade + ' - ' + uf}</p>
                <p class="text-sm text-slate-300 mb-2"><b>📞 Contato:</b> {tel if tel else 'Disponível no chat'}</p>
                <p class="text-sm text-slate-300"><b>🗓️ Abertura:</b> {data_abert}</p>
            </div>
            <br>
            <a href="{whats_link}" target="_blank" class="inline-block bg-emerald-500 hover:bg-emerald-600 text-white font-bold px-8 py-4 rounded-xl shadow-lg transition">
                💬 Iniciar Atendimento via WhatsApp
            </a>
        </div>
    </section>

    <footer class="bg-slate-950 text-slate-500 py-6 text-center text-xs border-t border-slate-800">
        <p>&copy; 2026 {razao}. Todos os direitos reservados. | {cidade}/{uf}</p>
    </footer>

</body>
</html>"""
    return html_code

# --- CARREGAMENTO DE DADOS DA PLANILHA ---
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
        while len(r) < 10: r.append("")
        cnpj = str(r[0]).strip()
        razao = str(r[1]).strip() if str(r[1]).strip() != "" else "Empresa"
        
        raw_date = str(r[2]).strip()
        data_abert = raw_date
        if raw_date:
            try:
                clean_date_str = raw_date.split("T")[0].split(" ")[0]
                if "-" in clean_date_str:
                    parts = clean_date_str.split("-")
                    if len(parts) == 3 and len(parts[0]) == 4:
                        data_abert = f"{parts[2]}/{parts[1]}/{parts[0]}"
                elif "/" in clean_date_str:
                    parts = clean_date_str.split("/")
                    if len(parts) == 3 and len(parts[2]) == 2:
                        data_abert = f"{parts[0]}/{parts[1]}/20{parts[2]}"
            except Exception: data_abert = raw_date

        segmento = str(r[3]).strip() if str(r[3]).strip() != "" else "N/A"
        uf = str(r[4]).strip().upper() if str(r[4]).strip() != "" else "N/A"
        cidade = str(r[5]).strip().upper() if str(r[5]).strip() != "" else "N/A"
        
        if cnpj.lower() == "cnpj" or "razão social" in razao.lower(): continue
            
        maps_url = ""
        telefone = ""
        for item in r:
            if "google.com/maps" in item: maps_url = item.strip(); break
        for item in r:
            cleaned = item.strip()
            if cleaned.isdigit() and 8 <= len(cleaned) <= 12: telefone = cleaned; break
                
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
        
        theme_btn_label = "🌙 Modo Escuro" if not is_dark else "☀️ Modo Claro"
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

    # --- BANNER ---
    st.markdown("""
        <div class="banner-box">
            <div class="banner-title">🚀 Novas Empresas - Acompanhamento & Gerador LP Avançado</div>
            <div class="banner-subtitle">Consulta externa na web, lógica de atuação específica por segmento e cores exclusivas para cada Landing Page.</div>
        </div>
    """, unsafe_allow_html=True)

    # --- FILTRAGEM ---
    df_filtered = current_df.copy()
    if seg_selecionado != "Todos": df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado]
    if uf_selecionada != "Todos": df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada]
    if cidade_selecionada != "Todas": df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada]
    if status_selecionado != "Todos": df_filtered = df_filtered[df_filtered["Status"].astype(str).str.strip() == status_selecionado.strip()]

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Exibidos", len(df_filtered))
    m2.metric("Pendentes", len(current_df[current_df["Status"] == "Pendente"]))
    m3.metric("LPs Geradas", len(current_df[current_df["Status"] == "LP Gerada"]))
    m4.metric("Vendas Fechadas", len(current_df[current_df["Status"] == "Finalizado Positivo"]))

    st.divider()

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

    st.subheader("📋 Lista de Empresas Localizadas na Busca")

    if df_filtered.empty:
        st.warning("Nenhum lead encontrado com os filtros ou termo de pesquisa selecionados.")
    else:
        items_per_page = 25
        total_items = len(df_filtered)
        total_pages = max(1, (total_items - 1) // items_per_page + 1)
        
        if st.session_state.page_num > total_pages: st.session_state.page_num = total_pages

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
            r_cols[0].markdown(f"🏢 **{razao}**")
            r_cols[1].markdown(f"`{cnpj}`")
            r_cols[2].markdown(f"{data_abert}")
            r_cols[3].markdown(f"{uf}")
            r_cols[4].markdown(f"{cidade}")
            
            with r_cols[5]:
                action_str = []
                if tel: action_str.append(f"[📞](https://wa.me/55{''.join(filter(str.isdigit, str(tel)))})")
                else: action_str.append("📞")
                if maps_link: action_str.append(f"[📍]({maps_link})")
                else: action_str.append("📍")
                nome_busca = str(razao).replace(' ', '+')
                cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
                action_str.append(f"[🔍](https://www.google.com/search?q={nome_busca}+{cidade_busca})")
                st.markdown("  ".join(action_str))
                
            r_cols[6].markdown(f"🟢 `{current_status}`")

            with st.expander(f"⚙️ Gerenciar & Automação LP: {razao}"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                with c1:
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                with c2:
                    st.markdown(f"**Telefone:** {tel if tel else 'Não informado'}")
                    st.markdown(f"📸 [Perfil Instagram](https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca})")
                with c3:
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    c_idx = status_list.index(current_status) if current_status in status_list else 0
                    novo_status = st.selectbox("Status:", status_list, index=c_idx, key=f"status_exp_{idx}")
                    if novo_status != current_status:
                        st.session_state.df_status.at[idx, "Status"] = novo_status
                        st.rerun()
                
                st.markdown("<hr style='margin: 8px 0px; border-color: " + border_color + ";'>", unsafe_allow_html=True)
                
                if st.button("🔍 Analisar Web & Criar LP Exclusiva", key=f"btn_auto_lp_{idx}"):
                    with st.spinner("Executando varredura web, aplicando lógica do segmento e gerando LP única..."):
                        lp_html = generate_unique_landing_page(razao, segmento, cidade, uf, endereco, tel, data_abert)
                        st.session_state[f"lp_data_{idx}"] = lp_html
                        st.session_state.df_status.at[idx, "Status"] = "LP Gerada"
                        st.success("Landing Page exclusiva gerada com sucesso!")

                if f"lp_data_{idx}" in st.session_state:
                    lp_html_content = st.session_state[f"lp_data_{idx}"]
                    st.markdown("#### ⚡ Pré-visualização da Landing Page Exclusiva")
                    
                    st.components.v1.html(lp_html_content, height=520, scrolling=True)
                    
                    st.download_button(
                        label="📥 Baixar Código HTML da Landing Page",
                        data=lp_html_content,
                        file_name=f"landing_page_{cnpj}.html",
                        mime="text/html",
                        key=f"dl_html_{idx}"
                    )

            st.markdown(f"<hr style='margin: 1px 0px 3px 0px; border-color: {border_color};'>", unsafe_allow_html=True)

        # --- PAGINAÇÃO ---
        st.divider()
        p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns([2, 1, 1.5, 1, 2])
        with p_col1:
            if st.button("⏮️ Início", use_container_width=True): st.session_state.page_num = 1; st.rerun()
        with p_col2:
            if st.button("◀️", use_container_width=True):
                if st.session_state.page_num > 1: st.session_state.page_num -= 1; st.rerun()
        with p_col3:
            st.markdown(f"<div style='text-align: center; padding-top: 6px; font-weight: 700;'>Página {st.session_state.page_num} de {total_pages}</div>", unsafe_allow_html=True)
        with p_col4:
            if st.button("▶️", use_container_width=True):
                if st.session_state.page_num < total_pages: st.session_state.page_num += 1; st.rerun()
        with p_col5:
            if st.button("Fim ⏭️", use_container_width=True): st.session_state.page_num = total_pages; st.rerun()

except Exception as e:
    st.error(f"Erro ao carregar o painel: {e}")
