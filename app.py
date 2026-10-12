import streamlit as st
import pandas as pd
import requests
import io
import csv
import urllib.parse
import hashlib

# 1. Configuração da página
st.set_page_config(
    page_title="Novas Empresas - Acompanhamento & Gerador LP Exclusivo",
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

# --- GERADOR MATEMÁTICO DE CORES ÚNICAS E VIBRANTES ---
def generate_unique_color_palette(text_seed):
    # Cria um hash hexadecimal único baseado no nome da empresa e CNPJ
    h = hashlib.sha256(text_seed.encode('utf-8')).hexdigest()
    
    # Extrai valores para matiz (Hue de 0 a 360), saturação e luminosidade ideais para design web
    hue = int(h[0:4], 16) % 360
    saturation = 65 + (int(h[4:6], 16) % 25) # Entre 65% e 90% (cores vivas)
    lightness = 45 + (int(h[6:8], 16) % 15)  # Entre 45% e 60% (bom contraste)
    
    # Converter HSL para HEX em Python puro
    def hsl_to_hex(h, s, l):
        s /= 100.0
        l /= 100.0
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        r, g, b = 0, 0, 0
        if 0 <= h < 60: r, g, b = c, x, 0
        elif 60 <= h < 120: r, g, b = x, c, 0
        elif 120 <= h < 180: r, g, b = 0, c, x
        elif 180 <= h < 240: r, g, b = 0, x, c
        elif 240 <= h < 300: r, g, b = x, 0, c
        elif 300 <= h < 360: r, g, b = c, 0, x
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    primary_hex = hsl_to_hex(hue, saturation, lightness)
    # Cor secundária complementar com matiz deslocada em 40 graus
    secondary_hex = hsl_to_hex((hue + 45) % 360, saturation, max(30, lightness - 15))
    
    return primary_hex, secondary_hex

# --- ENGINE CRIATIVA DE LANDING PAGE EXCLUSIVA ---
def generate_hyper_custom_lp(razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj):
    # Gerar cores 100% únicas para este lead
    primary_color, secondary_color = generate_unique_color_palette(razao + cnpj)
    
    seg_lower = segmento.lower()
    
    # Lógica de negócios específica por ramo
    if any(x in seg_lower for x in ['atacad', 'distribui', 'comercio', 'vestu', 'roupa', 'acessor']):
        headline = f"Distribuição e Atacado de Excelência em {cidade} e Região"
        subheadline = f"A <b>{razao}</b> é especialista em {segmento}, fornecendo produtos de alta qualidade, pontualidade e ótimas condições para lojistas e parceiros comerciais."
        bullet_1 = "Portfólio Selecionado"
        bullet_1_desc = "Produtos com rigoroso padrão de qualidade para o seu negócio."
        bullet_2 = "Agilidade nas Entregas"
        bullet_2_desc = "Logística estruturada para atender com rapidez."
        bullet_3 = "Parceria Comercial"
        bullet_3_desc = "Condições especiais e atendimento dedicado a lojistas."
        hero_img = "https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=1400&q=80"
    elif any(x in seg_lower for x in ['advoc', 'jurid', 'contab', 'consult']):
        headline = f"Assessoria Estratégica e Segurança Jurídica"
        subheadline = f"Atuação de alto nível no segmento de {segmento}, oferecendo suporte técnico rigoroso e focado na proteção dos seus interesses."
        bullet_1 = "Atuação Estratégica"
        bullet_1_desc = "Análise detalhada de cenários para tomadas de decisão seguras."
        bullet_2 = "Sigilo Absoluto"
        bullet_2_desc = "Compromisso ético e confidencialidade em todas as demandas."
        bullet_3 = "Atendimento Ágil"
        bullet_3_desc = "Canais diretos para esclarecimento rápido de dúvidas."
        hero_img = "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1400&q=80"
    elif any(x in seg_lower for x in ['estet', 'beleza', 'salao', 'spa']):
        headline = f"Transforme sua Experiência de Beleza e Bem-Estar"
        subheadline = f"Procedimentos exclusivos e atendimento personalizado em {cidade}/{uf} para realçar o que você tem de melhor."
        bullet_1 = "Ambiente Exclusivo"
        bullet_1_desc = "Espaço climatizado e preparado para o seu máximo conforto."
        bullet_2 = "Profissionais Qualificados"
        bullet_2_desc = "Técnicas modernas e produtos de altíssima qualidade."
        bullet_3 = "Agendamento VIP"
        bullet_3_desc = "Horários flexíveis reservados diretamente pelo WhatsApp."
        hero_img = "https://images.unsplash.com/photo-1560750588-73207b1ef5b8?auto=format&fit=crop&w=1400&q=80"
    else:
        headline = f"Soluções Especializadas em {segmento}"
        subheadline = f"A <b>{razao}</b> entrega excelência, agilidade e comprometimento em cada projeto realizado em {cidade} - {uf}."
        bullet_1 = "Atendimento Personalizado"
        bullet_1_desc = "Projetos desenhados sob medida para a sua necessidade."
        bullet_2 = "Compromisso com Prazos"
        bullet_2_desc = "Pontualidade e rigor técnico em todas as etapas."
        bullet_3 = "Suporte Dedicado"
        bullet_3_desc = "Equipe pronta para tirar dúvidas e prestar auxílio imediato."
        hero_img = "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1400&q=80"

    clean_tel = "".join(filter(str.isdigit, str(tel))) if tel else ""
    whats_link = f"https://wa.me/55{clean_tel}" if clean_tel else "#"

    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{razao} | {segmento} em {cidade}/{uf}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .unique-bg {{ background-color: {primary_color}; }}
        .unique-text {{ color: {primary_color}; }}
        .unique-border {{ border-color: {primary_color}; }}
        .unique-gradient {{ background: linear-gradient(135deg, {secondary_color}, {primary_color}); }}
    </style>
</head>
<body class="font-sans antialiased bg-slate-50 text-slate-800">

    <!-- Top Notice -->
    <div class="bg-slate-950 text-slate-300 text-xs py-2 px-4 text-center border-b border-slate-800">
        📍 {cidade} - {uf} | Especialistas em <b>{segmento}</b>
    </div>

    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="font-black text-xl tracking-tight text-slate-900 uppercase flex items-center gap-2">
                <span class="w-4 h-4 rounded-full inline-block unique-bg"></span>
                {razao}
            </div>
            <a href="{whats_link}" target="_blank" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs md:text-sm px-5 py-2.5 rounded-lg shadow transition flex items-center gap-2">
                💬 Atendimento via WhatsApp
            </a>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative text-white py-24 px-4" style="background-image: linear-gradient(rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.90)), url('{hero_img}'); background-size: cover; background-position: center;">
        <div class="max-w-4xl mx-auto text-center">
            <span class="inline-block unique-bg text-white text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider mb-4">Referência em {segmento}</span>
            <h1 class="text-3xl md:text-5xl font-black mb-6 leading-tight">{headline}</h1>
            <p class="text-base md:text-lg text-slate-300 mb-8 max-w-2xl mx-auto leading-relaxed">{subheadline}</p>
            <div class="flex flex-col sm:flex-row justify-center gap-4">
                <a href="{whats_link}" target="_blank" class="bg-emerald-500 hover:bg-emerald-600 text-white text-base font-bold px-8 py-4 rounded-xl shadow-lg transition transform hover:-translate-y-0.5">
                    🚀 Solicitar Orçamento no WhatsApp
                </a>
            </div>
        </div>
    </section>

    <!-- Quem Somos -->
    <section class="py-16 px-4 bg-white border-b border-slate-200">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-2xl md:text-3xl font-bold text-slate-900 mb-4">Quem Somos</h2>
            <div class="w-16 h-1 unique-bg mx-auto mb-6 rounded"></div>
            <p class="text-slate-600 leading-relaxed text-base mb-4">A <b>{razao}</b> iniciou suas atividades em <b>{data_abert}</b>, consolidando-se no setor de <b>{segmento}</b>. Nossa estrutura localizada em <i>{endereco if endereco else cidade + ' - ' + uf}</i> foi planejada para garantir excelência operacional e atendimento humanizado.</p>
            <p class="text-slate-500 text-sm"><b>CNPJ:</b> {cnpj}</p>
        </div>
    </section>

    <!-- Diferenciais -->
    <section class="py-16 px-4 max-w-6xl mx-auto">
        <div class="text-center mb-12">
            <h2 class="text-2xl md:text-3xl font-bold text-slate-900">Por que nos escolher?</h2>
            <p class="text-slate-600 mt-2">Pilares que sustentam a qualidade dos nossos serviços</p>
        </div>
        <div class="grid md:grid-cols-3 gap-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 unique-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">✓</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">{bullet_1}</h3>
                <p class="text-slate-600 text-sm leading-relaxed">{bullet_1_desc}</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 unique-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">⚡</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">{bullet_2}</h3>
                <p class="text-slate-600 text-sm leading-relaxed">{bullet_2_desc}</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="w-10 h-10 unique-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">🛡️</div>
                <h3 class="font-bold text-lg mb-2 text-slate-900">{bullet_3}</h3>
                <p class="text-slate-600 text-sm leading-relaxed">{bullet_3_desc}</p>
            </div>
        </div>
    </section>

    <!-- Contato Final -->
    <section class="py-16 px-4 bg-slate-900 text-white">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-2xl md:text-3xl font-bold mb-4">Entre em Contato Conosco</h2>
            <p class="text-slate-400 mb-8">Nossa equipe em {cidade} está pronta para lhe atender diretamente.</p>
            <div class="inline-block bg-slate-800 p-6 rounded-2xl border border-slate-700 text-left mb-8 w-full max-w-md">
                <p class="text-sm text-slate-300 mb-2"><b>📍 Endereço:</b> {endereco if endereco else cidade + ' - ' + uf}</p>
                <p class="text-sm text-slate-300 mb-2"><b>📞 WhatsApp:</b> {tel if tel else 'Disponível no chat'}</p>
                <p class="text-sm text-slate-300"><b>🗓️ Abertura Oficial:</b> {data_abert}</p>
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

# --- CARREGAMENTO DE DADOS COM CACHE ---
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
            <div class="banner-title">🚀 Novas Empresas - Acompanhamento & Gerador LP Exclusivo</div>
            <div class="banner-subtitle">Gera Landing Pages com cores e copywriting exclusivos e dinâmicos para cada empresa.</div>
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
                    with st.spinner("Gerando Landing Page com identidade cromática e copywriting exclusivo..."):
                        lp_html = generate_hyper_custom_lp(razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj)
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
