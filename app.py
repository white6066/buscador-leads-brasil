import streamlit as st
import pandas as pd
import requests
import io
import csv
import urllib.parse
import re
import hashlib
from PIL import Image

# 1. Configuração da página
st.set_page_config(
    page_title="Novas Empresas - Gerador LP com OSINT Avançado",
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
btn_text = "#f3f4f6" if is_dark else "#f3f4f6"
input_bg = "#111827" if is_dark else "#ffffff"
input_text = "#f3f4f6" if is_dark else "#0f172a"
expander_bg = "#111827" if is_dark else "#ffffff"
dropdown_bg = "#111827" if is_dark else "#ffffff"
dropdown_text = "#f3f4f6" if is_dark else "#f3f4f6"

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

def format_cnpj(cnpj_str):
    nums = "".join(filter(str.isdigit, str(cnpj_str)))
    if len(nums) == 14:
        return f"{nums[:2]}.{nums[2:5]}.{nums[5:8]}/{nums[8:12]}-{nums[12:]}"
    return cnpj_str

def extract_colors_from_logo(image_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(image_url, headers=headers, timeout=3)
        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content)).convert('RGB')
            img = img.resize((40, 40))
            colors = img.getcolors(40*40)
            if colors:
                colors.sort(key=lambda x: x[0], reverse=True)
                for count, (r, g, b) in colors:
                    if not (r > 240 and g > 240 and b > 240) and not (r < 15 and g < 15 and b < 15):
                        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        pass
    return None

# --- BUSCA OSINT PROFUNDA E INTELIGENTE (SITE OFICIAL, FANTASIA, TELEFONE E IMAGENS) ---
def deep_web_osint_search(razao, cnpj, cidade, uf, segmento):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    queries = [
        f"{razao} {cidade} {uf}",
        f"CNPJ {cnpj} biz",
        f"{razao} instagram site"
    ]
    
    found_logo = None
    found_instagram = None
    found_email = None
    found_phone = None
    found_fantasia = None
    found_site = None
    found_images = []
    
    for q in queries:
        try:
            encoded_q = urllib.parse.quote(q)
            url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                page_text = soup.get_text()
                
                # Capturar Site Oficial
                if not found_site:
                    for a in soup.find_all('a', class_='result__url'):
                        href = a.get('href', '')
                        if href and 'http' in href and 'duckduckgo' not in href and 'instagram' not in href and 'facebook' not in href:
                            found_site = href
                            break

                # Capturar Nome Fantasia
                if not found_fantasia:
                    fantasia_match = re.search(r'(?:Nome Fantasia|fantasia|conhecida como)[:\s]+([A-ZÁ-Ú0-9\s]{3,35})', page_text, re.IGNORECASE)
                    if fantasia_match:
                        candidate = fantasia_match.group(1).strip()
                        if candidate.upper() not in razao.upper() and len(candidate) > 2:
                            found_fantasia = candidate

                for a in soup.find_all('a', class_='result__snippet'):
                    txt = a.get_text()
                    if txt:
                        if not found_instagram:
                            ig_matches = re.findall(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)', txt)
                            if ig_matches:
                                handle = ig_matches[0]
                                if handle.lower() not in ['p', 'reel', 'explore', 'accounts']:
                                    found_instagram = f"https://instagram.com/{handle}"
                                    
                        if not found_email:
                            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', txt)
                            if emails:
                                found_email = emails[0]
                                
                        if not found_phone:
                            phones = re.findall(r'(?:(?:\+|00)?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})', txt)
                            if phones:
                                clean_p = "".join(filter(str.isdigit, phones[0]))
                                if len(clean_p) >= 10:
                                    found_phone = phones[0]

                # Capturar imagens indexadas na busca relevantes ao negócio
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if 'http' in src and 'icon' not in src and 'logo' not in src.lower():
                        found_images.append(src)

                if not found_logo:
                    for img in soup.find_all('img'):
                        src = img.get('src', '')
                        if 'http' in src and ('logo' in src.lower() or 'icon' in src.lower()):
                            found_logo = src
                            break
        except Exception:
            continue
            
    commercial_name = found_fantasia if found_fantasia else razao
    
    return {
        "fantasia": commercial_name,
        "logo": found_logo,
        "instagram": found_instagram,
        "email": found_email,
        "phone": found_phone,
        "site": found_site,
        "images": found_images
    }

# --- GERAÇÃO DE IMAGEM DINÂMICA BASEADA NO NOME, RAMO E DADOS ENCONTRADOS ---
def get_dynamic_contextual_image(display_name, segmento, osint_images):
    # Se a varredura encontrou imagens reais na web, prioriza uma delas
    if osint_images and len(osint_images) > 0:
        return osint_images[0]
        
    # Caso contrário, gera uma imagem fotográfica de altíssima qualidade baseada no segmento e nome
    seed = hashlib.md5((display_name + segmento).encode()).hexdigest()[:6]
    seg_lower = (segmento + " " + display_name).lower()
    
    if any(x in seg_lower for x in ['automov', 'carro', 'veiculo', 'seminovo', 'auto']):
        return f"https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=80&sig={seed}"
    elif any(x in seg_lower for x in ['supermerc', 'mercado', 'aliment', 'varejo', 'atacad']):
        return f"https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=1200&q=80&sig={seed}"
    elif any(x in seg_lower for x in ['cafe', 'cafeicult', 'agropecu', 'agrop', 'agricult', 'rural', 'fazenda']):
        return f"https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1200&q=80&sig={seed}"
    elif any(x in seg_lower for x in ['advoc', 'jurid', 'contab', 'consult', 'direito']):
        return f"https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80&sig={seed}"
    elif any(x in seg_lower for x in ['estet', 'beleza', 'salao', 'spa', 'saude', 'odont', 'clinica']):
        return f"https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1200&q=80&sig={seed}"
    else:
        return f"https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&w=1200&q=80&sig={seed}"

# --- GERAÇÃO DA LANDING PAGE ORIGINAL E PERSONALIZADA ---
def generate_perfect_landing_page(razao, segmento, cidade, uf, endereco, tel_planilha, data_abert, cnpj):
    # 1. Executar varredura profunda primeiro
    osint = deep_web_osint_search(razao, cnpj, cidade, uf, segmento)
    
    # 2. Cores da marca extraídas da logo encontrada ou geradas de forma única
    primary_color = None
    if osint["logo"]:
        primary_color = extract_colors_from_logo(osint["logo"])
    
    if not primary_color:
        h = hashlib.md5((razao + cnpj).encode()).hexdigest()
        primary_color = f"#{int(h[4:6], 16) % 150:02x}{int(h[6:8], 16) % 180:02x}{int(h[8:10], 16) % 200:02x}"
        if primary_color == "#000000": primary_color = "#1e3a8a"

    formatted_cnpj = format_cnpj(cnpj)
    
    active_tel = osint["phone"] if osint["phone"] else tel_planilha
    clean_tel = "".join(filter(str.isdigit, str(active_tel))) if active_tel else ""
    whats_link = f"https://wa.me/55{clean_tel}" if clean_tel else "#"

    display_name = osint["fantasia"]

    # Redes Sociais & Site Oficial
    social_links_html = ""
    if osint["instagram"]:
        social_links_html += f'<p class="text-sm text-slate-700 flex items-center gap-2"><b>📸 Instagram:</b> <a href="{osint["instagram"]}" target="_blank" class="brand-text underline font-semibold">Aceder ao Perfil</a></p>'
    else:
        social_links_html += f'<p class="text-sm text-slate-500 flex items-center gap-2 italic"><b>📸 Instagram:</b> <span class="text-xs bg-slate-100 px-2 py-0.5 rounded border border-slate-200">Campo Reservado (Adicionar Futuramente)</span></p>'

    if osint["site"]:
        social_links_html += f'<p class="text-sm text-slate-700 flex items-center gap-2 mt-1"><b>🌐 Site Oficial:</b> <a href="{osint["site"]}" target="_blank" class="brand-text underline font-semibold">{osint["site"]}</a></p>'

    # 3. Imagem dinâmica inteligente gerada por último
    img_feature = get_dynamic_contextual_image(display_name, segmento, osint["images"])

    headline = f"Excelência e Qualidade em {segmento}"

    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_name} | {segmento} em {cidade}/{uf}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .brand-bg {{ background-color: {primary_color}; }}
        .brand-text {{ color: {primary_color}; }}
        .brand-border {{ border-color: {primary_color}; }}
    </style>
</head>
<body class="font-sans antialiased bg-slate-50 text-slate-800">

    <div class="brand-bg text-white text-xs py-2 px-4 text-center font-semibold">
        📍 {cidade} - {uf} | Atendimento Especializado em {segmento}
    </div>

    <header class="bg-white shadow-sm sticky top-0 z-50 border-b border-slate-100">
        <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
            <div class="font-black text-lg md:text-xl tracking-tight text-slate-900 uppercase flex items-center gap-3">
                {f'<img src="{osint["logo"]}" class="w-10 h-10 rounded-full object-cover border border-slate-200">' if osint["logo"] else f'<span class="w-3.5 h-3.5 rounded-full inline-block brand-bg"></span>'}
                <span>{display_name}</span>
            </div>
            {f'<a href="{whats_link}" target="_blank" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs md:text-sm px-5 py-2.5 rounded-lg shadow transition flex items-center gap-2">💬 WhatsApp</a>' if clean_tel else ''}
        </div>
    </header>

    <section class="relative text-white py-24 px-4 brand-bg">
        <div class="max-w-4xl mx-auto text-center">
            <h1 class="text-3xl md:text-5xl font-black mb-6 leading-tight">{headline}</h1>
            <p class="text-base md:text-lg text-slate-100 mb-8 max-w-2xl mx-auto leading-relaxed">A <b>{display_name}</b> atua com rigor técnico, agilidade e compromisso para garantir os melhores resultados aos nossos parceiros e clientes em {cidade} e região.</p>
            {f'<div class="flex justify-center"><a href="{whats_link}" target="_blank" class="bg-white text-slate-900 hover:bg-slate-100 text-base font-bold px-8 py-4 rounded-xl shadow-lg transition transform hover:-translate-y-0.5">🚀 Entrar em Contato Agora</a></div>' if clean_tel else ''}
        </div>
    </section>

    <!-- 1º OS PILARES (Sempre antes do Sobre) -->
    <section class="py-16 px-4 bg-slate-50 border-b border-slate-200">
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-12">
                <h2 class="text-2xl md:text-3xl font-bold text-slate-900">Nossos Pilares</h2>
                <p class="text-slate-600 mt-2">Compromisso total com a qualidade e satisfação</p>
            </div>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div class="w-10 h-10 brand-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">✓</div>
                    <h3 class="font-bold text-lg mb-2 text-slate-900">Atendimento Sob Medida</h3>
                    <p class="text-slate-600 text-sm leading-relaxed">Foco absoluto nas necessidades individuais de cada cliente em {cidade}.</p>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div class="w-10 h-10 brand-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">⚡</div>
                    <h3 class="font-bold text-lg mb-2 text-slate-900">Agilidade e Rapidez</h3>
                    <p class="text-slate-600 text-sm leading-relaxed">Canais diretos via WhatsApp e suporte eficiente sem burocracia.</p>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div class="w-10 h-10 brand-bg text-white rounded-lg flex items-center justify-center font-bold text-lg mb-4">🛡️</div>
                    <h3 class="font-bold text-lg mb-2 text-slate-900">Confiança e Rigor</h3>
                    <p class="text-slate-600 text-sm leading-relaxed">Transparência e excelência garantidas em todas as etapas de atuação.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- 2º SOBRE A EMPRESA (Com imagem dinâmica inteligente gerada por último) -->
    <section class="py-16 px-4 bg-white">
        <div class="max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center">
            <div>
                <h2 class="text-2xl md:text-3xl font-bold text-slate-900 mb-4">Sobre a Nossa Empresa</h2>
                <div class="w-16 h-1 brand-bg mb-6 rounded"></div>
                <p class="text-slate-600 leading-relaxed text-base mb-4">Constituída oficialmente em <b>{data_abert}</b>, a <b>{display_name}</b> (Razão Social: <i>{razao}</i>) destaca-se no segmento de <b>{segmento}</b>. Nossa estrutura em <i>{endereco if endereco else cidade + ' - ' + uf}</i> foi planejada para oferecer excelência e suporte completo.</p>
                
                <div class="space-y-3 mt-6">
                    <p class="text-sm text-slate-700 flex items-center gap-2"><b>📍 Endereço:</b> {endereco if endereco else cidade + ' - ' + uf}</p>
                    {f'<p class="text-sm text-slate-700 flex items-center gap-2"><b>📞 Contato:</b> {active_tel}</p>' if active_tel else ''}
                    {f'<p class="text-sm text-slate-700 flex items-center gap-2"><b>✉️ E-mail:</b> {osint["email"]}</p>' if osint["email"] else ''}
                    {social_links_html}
                </div>
            </div>
            <div>
                <img src="{img_feature}" alt="Ambiente Profissional" class="rounded-2xl shadow-lg object-cover w-full h-80 border border-slate-100">
            </div>
        </div>
    </section>

    <footer class="brand-bg text-white py-8 text-center text-xs border-t border-slate-800">
        <div class="max-w-4xl mx-auto px-4">
            <p class="font-bold text-sm mb-2">{display_name}</p>
            <p class="text-white/80 mb-1">Razão Social: {razao}</p>
            <p class="text-white/80 mb-2">CNPJ: {formatted_cnpj} | {cidade}/{uf}</p>
            <p class="text-white/60">&copy; 2026 Todos os direitos reservados.</p>
        </div>
    </footer>

</body>
</html>"""
    return html_code

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

    st.markdown("""
        <div class="banner-box">
            <div class="banner-title">🚀 Novas Empresas - Gerador LP com OSINT Avançado</div>
            <div class="banner-subtitle">Varredura profunda do site oficial, nome fantasia, redes sociais e geração dinâmica de imagens contextuais por último.</div>
        </div>
    """, unsafe_allow_html=True)

    df_filtered = current_df.copy()
    if seg_selecionado != "Todos": df_filtered = df_filtered[df_filtered["Segmento"].astype(str).str.strip() == seg_selecionado]
    if uf_selecionada != "Todos": df_filtered = df_filtered[df_filtered["UF"].astype(str).str.strip().str.upper() == uf_selecionada]
    if cidade_selecionada != "Todas": df_filtered = df_filtered[df_filtered["Cidade"].astype(str).str.strip().str.upper() == cidade_selecionada]
    if status_selecionado != "Todos": df_filtered = df_filtered[df_filtered["Status"].astype(str).str.strip() == status_selecionado.strip()]

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
        st.download_button("📥 Exportar", data=csv_export, file_name="leads.csv", mime="text/csv")

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

            with st.expander(f"⚙️ Gerenciar & Criar LP: {razao}"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                with c1:
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                with c2:
                    st.markdown(f"**Telefone:** {tel if tel else 'Não informado'}")
                    st.markdown(f"📸 [Pesquisar Instagram / Maps](https://www.google.com/search?q={nome_busca}+{cidade_busca}+instagram)")
                with c3:
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    c_idx = status_list.index(current_status) if current_status in status_list else 0
                    novo_status = st.selectbox("Status:", status_list, index=c_idx, key=f"status_exp_{idx}")
                    if novo_status != current_status:
                        st.session_state.df_status.at[idx, "Status"] = novo_status
                        st.rerun()
                
                st.markdown("<hr style='margin: 8px 0px; border-color: " + border_color + ";'>", unsafe_allow_html=True)
                
                if st.button("🌐 Executar Busca Avançada & Gerar LP Original", key=f"btn_auto_lp_{idx}"):
                    with st.spinner("Executando varredura profunda (Site, Nome Fantasia, Contato, Redes) e gerando LP original..."):
                        lp_html = generate_perfect_landing_page(razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj)
                        st.session_state[f"lp_data_{idx}"] = lp_html
                        st.session_state.df_status.at[idx, "Status"] = "LP Gerada"
                        st.success("Busca realizada e Landing Page gerada com sucesso!")

                if f"lp_data_{idx}" in st.session_state:
                    lp_html_content = st.session_state[f"lp_data_{idx}"]
                    st.markdown("#### ⚡ Pré-visualização da Landing Page")
                    
                    st.components.v1.html(lp_html_content, height=520, scrolling=True)
                    
                    st.download_button(
                        label="📥 Baixar Código HTML da Landing Page",
                        data=lp_html_content,
                        file_name=f"landing_page_{cnpj}.html",
                        mime="text/html",
                        key=f"dl_html_{idx}"
                    )

            st.markdown(f"<hr style='margin: 1px 0px 3px 0px; border-color: {border_color};'>", unsafe_allow_html=True)

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
