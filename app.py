import streamlit as st
import pandas as pd
import requests
import io
import csv
import urllib.parse
import re
import hashlib
from datetime import datetime
from PIL import Image
import streamlit.components.v1 as components

# 1. Configuração da página
st.set_page_config(
    page_title="Novas Empresas - Gerador LP com IA de Imagem Realista",
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
        font-size: 0.78rem !important;
        padding: 3px 6px !important;
        min-height: 32px !important;
    }}
    [data-testid="stSidebar"] button:hover, .stDownloadButton button:hover, div[data-testid="stExpander"] button:hover, div.row-widget.stButton button:hover, button:hover {{
        background-color: {btn_bg} !important;
        border-color: #0ea5e9 !important;
        color: #0ea5e9 !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
    }}
    
    h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; font-family: system-ui, -apple-system, sans-serif; }}
    a {{ text-decoration: none !important; }}

    input[type="text"], input[type="date"] {{ background-color: {input_bg} !important; color: {input_text} !important; border: 1px solid {border_color} !important; font-size: 0.9rem !important; }}
    div[data-baseweb="input"] {{ background-color: {input_bg} !important; border: 1px solid {border_color} !important; border-radius: 4px !important; color: {input_text} !important; }}
    div[data-baseweb="input"] input {{ color: {input_text} !important; background-color: transparent !important; }}

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

def fix_encoding(text):
    if not text:
        return ""
    try:
        return str(text).encode('latin1').decode('utf-8')
    except Exception:
        return str(text)

def format_cnpj(cnpj_str):
    nums = "".join(filter(str.isdigit, str(cnpj_str)))
    if len(nums) == 14:
        return f"{nums[:2]}.{nums[2:5]}.{nums[5:8]}/{nums[8:12]}-{nums[12:]}"
    return cnpj_str

def format_phone(phone_str):
    nums = "".join(filter(str.isdigit, str(phone_str)))
    if len(nums) == 11:
        return f"({nums[:2]}) {nums[2]} {nums[3:7]}-{nums[7:]}"
    elif len(nums) == 10:
        return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return phone_str

def format_cep(cep_str):
    nums = "".join(filter(str.isdigit, str(cep_str)))
    if len(nums) == 8:
        return f"{nums[:5]}-{nums[5:]}"
    return cep_str

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

def deep_osint_company_analysis(razao, cnpj, cidade, uf, segmento):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    queries = [f"{razao} {cidade} {uf}", f"CNPJ {cnpj} business profile", f"{razao} instagram oficial"]
    
    found_logo, found_instagram, found_email, found_phone, found_fantasia, found_site, found_slogan = None, None, None, None, None, None, None
    extra_activities = []
    
    for q in queries:
        try:
            encoded_q = urllib.parse.quote(q)
            url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                page_text = soup.get_text()
                
                if not found_site:
                    for a in soup.find_all('a', class_='result__url'):
                        href = a.get('href', '')
                        if href and 'http' in href and 'duckduckgo' not in href and 'instagram' not in href:
                            found_site = href
                            break

                if not found_fantasia:
                    fantasia_match = re.search(r'(?:Nome Fantasia|fantasia|conhecida como)[:\s]+([A-ZÁ-Ú0-9\s]{3,35})', page_text, re.IGNORECASE)
                    if fantasia_match:
                        candidate = fantasia_match.group(1).strip()
                        if candidate.upper() not in razao.upper() and len(candidate) > 2:
                            found_fantasia = candidate

                for a in soup.find_all('a', class_='result__snippet'):
                    txt = a.get_text()
                    if txt:
                        if not found_slogan and any(w in txt.lower() for w in ['qualidade', 'referência', 'líder', 'compromisso', 'excelência', 'soluções', 'especializada']):
                            found_slogan = txt[:110] + "..."
                        if not found_instagram:
                            ig_matches = re.findall(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)', txt)
                            if ig_matches:
                                handle = ig_matches[0]
                                if handle.lower() not in ['p', 'reel', 'explore', 'accounts']:
                                    found_instagram = f"https://instagram.com/{handle}"
                        if not found_email:
                            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', txt)
                            if emails: found_email = emails[0]
                        if not found_phone:
                            phones = re.findall(r'(?:(?:\+|00)?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}[-\s]?\d{4}|\d{4}[-\s]?\d{4})', txt)
                            if phones:
                                clean_p = "".join(filter(str.isdigit, phones[0]))
                                if len(clean_p) >= 10: found_phone = phones[0]

                        for keyword in ['atendimento', 'suporte', 'assessoria', 'consultoria', 'gestão', 'fornecimento', 'comércio', 'serviços']:
                            if keyword in txt.lower() and len(txt) < 80:
                                clean_act = txt.strip()
                                if clean_act not in extra_activities: extra_activities.append(clean_act)

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
        "fantasia": fix_encoding(commercial_name),
        "logo": found_logo,
        "instagram": found_instagram,
        "email": found_email,
        "phone": found_phone,
        "site": found_site,
        "slogan": fix_encoding(found_slogan) if found_slogan else None,
        "extra_activities": [fix_encoding(a) for a in extra_activities[:3]]
    }

def translate_and_optimize_prompt(portuguese_text):
    text_lower = portuguese_text.lower()
    if any(w in text_lower for w in ['popular', 'populares', 'hatch', 'economico', 'varios carros', 'varios modelos']):
        return "wide showroom displaying multiple affordable new economy hatchback cars side by side, clean bright dealership floor, photorealistic commercial photography, 4k"
    elif 'carro' in text_lower or 'veiculo' in text_lower or 'automovel' in text_lower:
        return f"professional commercial photography of {portuguese_text}, modern dealership showroom, multiple vehicles, photorealistic, 4k resolution"
    elif 'loja' in text_lower or 'comercio' in text_lower:
        return f"modern high-end retail store interior, {portuguese_text}, bright professional architectural lighting, photorealistic, 4k"
    elif 'escritorio' in text_lower or 'sala' in text_lower:
        return f"sophisticated modern corporate office interior, {portuguese_text}, professional business atmosphere, architectural photography, 4k"
    else:
        return f"professional commercial photography of {portuguese_text}, photorealistic, 4k resolution, high quality business display, cinematic lighting"

def generate_superior_ai_image(segmento, razao, specific_instruction="", custom_seed=0):
    seg_lower = (segmento + " " + razao).lower()
    
    if specific_instruction:
        prompt = translate_and_optimize_prompt(specific_instruction)
    else:
        if any(x in seg_lower for x in ['veiculo', 'carro', 'automov', 'seminovo', 'auto', 'mecanica', 'revenda']):
            prompt = "professional car dealership showroom interior, clean polished floor, a mix of modern affordable sedans and hatchbacks on display, bright showroom lighting, realistic commercial photography, high quality"
        elif any(x in seg_lower for x in ['constr', 'material', 'obra', 'ferramenta', 'hardware']):
            prompt = "modern hardware store and building materials showroom interior, high-end construction materials neatly organized on shelves, bright professional architectural lighting, photorealistic, 4k"
        elif any(x in seg_lower for x in ['hospital', 'saude', 'medico', 'clinica', 'odont', 'laborat']):
            prompt = "modern high-end medical clinic interior, clean professional healthcare environment, advanced medical equipment, bright welcoming lighting, photorealistic, 4k"
        elif any(x in seg_lower for x in ['supermerc', 'mercado', 'aliment', 'varejo', 'comercio']):
            prompt = "high-end modern supermarket interior, beautifully organized shelves with grocery products, bright clean aisles, commercial retail photography, 4k"
        elif any(x in seg_lower for x in ['cafe', 'agropecu', 'agrop', 'agricult', 'rural', 'fazenda']):
            prompt = "modern agricultural business office and sustainable agribusiness landscape, professional corporate environment, high resolution, photorealistic"
        elif any(x in seg_lower for x in ['advoc', 'jurid', 'contab', 'consult', 'direito', 'gestao']):
            prompt = "sophisticated modern executive corporate office, meeting room with glass walls, professional business atmosphere, architectural photography, 4k"
        elif any(x in seg_lower for x in ['estet', 'beleza', 'salao', 'spa']):
            prompt = "luxury modern aesthetic beauty spa interior, elegant relaxing design, minimalist lighting, high-end wellness center, photorealistic, 4k"
        else:
            prompt = f"modern professional corporate workspace for {segmento}, elegant interior design, high-end business environment, photorealistic, 4k"

    encoded_prompt = urllib.parse.quote(prompt)
    base_seed = int(hashlib.md5((segmento + razao + specific_instruction).encode()).hexdigest(), 16) % 999999
    final_seed = base_seed + custom_seed
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=800&seed={final_seed}&model=flux&nologo=true"

def determine_harmonious_palette(razao, segmento, logo_url):
    if logo_url:
        extracted = extract_colors_from_logo(logo_url)
        if extracted:
            return extracted, "Identidade Visual Oficial (Logo)"
            
    seg_lower = segmento.lower()
    if any(w in seg_lower for w in ['veiculo', 'carro', 'automov', 'seminovo', 'auto']):
        return "#1e293b", "Azul Grafite (Automotivo & Confiança)"
    elif any(w in seg_lower for w in ['hospital', 'saude', 'medico', 'odont', 'estet', 'clinica']):
        return "#0f766e", "Verde Teal (Saúde & Bem-Estar)"
    elif any(w in seg_lower for w in ['financeiro', 'contab', 'direito', 'advoc', 'consult']):
        return "#1e3a8a", "Azul Executivo (Seriedade & Confiança)"
    elif any(w in seg_lower for w in ['agro', 'rural', 'fazenda', 'cafe']):
        return "#173f32", "Verde Floresta (Agro & Sustentabilidade)"
    elif any(w in seg_lower for w in ['constr', 'material', 'engenhar', 'obra']):
        return "#c2410c", "Laranja Terracota (Construção & Força)"
    else:
        h = int(hashlib.md5((razao + segmento).encode()).hexdigest(), 16)
        palettes = ["#173f32", "#1e3a8a", "#0f172a", "#3b2f2f", "#4338ca", "#047857", "#581c87"]
        return palettes[h % len(palettes)], "Paleta Exclusiva"

def apply_accumulated_modifications(html_content, instructions_list):
    custom_primary_color = None
    css_injections = []
    
    color_map = {
        "vermelho": "#dc2626", "azul": "#2563eb", "verde": "#16a34a", 
        "preto": "#000000", "branco": "#ffffff", "cinza": "#64748b",
        "laranja": "#ea580c", "roxo": "#7c3aed", "rosa": "#db2777",
        "bege": "#d4b996", "dourado": "#d97706", "amarelo": "#ca8a04",
        "azul marinho": "#1e3a8a", "azul escuro": "#0f172a"
    }

    for instruction in instructions_list:
        inst_lower = instruction.lower()
        if any(w in inst_lower for w in ["cor principal", "cor do tema", "mudar cor", "trocar cor", "cor"]):
            for c_name, c_hex in color_map.items():
                if c_name in inst_lower:
                    custom_primary_color = c_hex
                    break

        if "canais de atendimento" in inst_lower and ("cor" in inst_lower or "branco" in inst_lower or "white" in inst_lower):
            html_content = html_content.replace(
                '<p class="text-xs font-extrabold uppercase tracking-[.2em] text-emerald-300">Canais de Atendimento</p>',
                '<p class="text-xs font-extrabold uppercase tracking-[.2em] text-white">Canais de Atendimento</p>'
            )

        for c_name, c_hex in color_map.items():
            if c_name in inst_lower and ("cor da fonte" in inst_lower or "texto" in inst_lower or "cor do texto" in inst_lower or "fonte" in inst_lower):
                css_injections.append(f"body, p, span, h2, h3 {{ color: {c_hex} !important; }}")

    if custom_primary_color:
        html_content = re.sub(r'--primary:\s*[^;]+;', f'--primary: {custom_primary_color};', html_content)
        html_content = html_content.replace('bg-[#070e0b]', 'brand-bg')

    if css_injections:
        full_css = f"<style>\n" + "\n".join(css_injections) + "\n</style>"
        html_content = html_content.replace("</head>", f"{full_css}\n</head>")

    return html_content

def generate_ai_masterpiece_landing_page(razao, segmento, cidade, uf, endereco, tel_planilha, data_abert, cnpj, instructions_list, seed_offset_1=0, seed_offset_2=0):
    img1_inst = ""
    img2_inst = ""
    
    for inst in instructions_list:
        inst_l = inst.lower()
        if any(w in inst_l for w in ['foto', 'imagem', 'carro', 'veiculo', 'trocar', 'mudar', 'exibir', 'colocar', 'popular', '1', 'superior', 'topo', 'exemplo']):
            if "2" not in inst_l and "inferior" not in inst_l and "sobre" not in inst_l:
                img1_inst = inst
        if any(w in inst_l for w in ['2', 'inferior', 'segunda', 'sobre']):
            img2_inst = inst

    if not img1_inst and instructions_list:
        img1_inst = instructions_list[-1]
    if not img2_inst and len(instructions_list) > 1:
        img2_inst = instructions_list[-1]

    osint = deep_osint_company_analysis(razao, cnpj, cidade, uf, segmento)
    primary_color, color_rationale = determine_harmonious_palette(razao, segmento, osint["logo"])
    
    formatted_cnpj = format_cnpj(cnpj)
    active_tel = osint["phone"] if osint["phone"] else tel_planilha
    clean_tel = "".join(filter(str.isdigit, str(active_tel))) if active_tel else ""
    
    if clean_tel:
        if not clean_tel.startswith("55") and len(clean_tel) <= 11:
            clean_tel = "55" + clean_tel
        whats_link = f"https://wa.me/{clean_tel}"
        display_phone_text = format_phone(active_tel)
    else:
        whats_link = "https://wa.me/"
        display_phone_text = "WhatsApp indisponível"

    display_name = osint["fantasia"]
    custom_slogan = osint["slogan"] if osint["slogan"] else f"Excelência, segurança e compromisso incomparável em {segmento}. Soluções sob medida para superar suas expectativas."

    extra_acts = osint["extra_activities"]
    if not extra_acts:
        extra_acts = [f"Atuação especializada em {segmento}", "Atendimento consultivo e personalizado", "Compromisso com prazos e qualidade total"]

    activities_html = "".join([f'<li class="flex items-center gap-2 text-sm text-slate-700"><span class="brand-text font-bold">✓</span> {act}</li>' for act in extra_acts])

    formatted_address = endereco
    cep_match = re.search(r'\b\d{8}\b', endereco)
    if cep_match:
        raw_cep = cep_match.group(0)
        formatted_address = endereco.replace(raw_cep, f"CEP: {format_cep(raw_cep)}")

    full_address = formatted_address if formatted_address else f"{cidade} - {uf}"
    maps_query = urllib.parse.quote(f"{display_name}, {full_address}")
    maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    embed_maps_url = f"https://maps.google.com/maps?q={maps_query}&t=&z=15&ie=UTF8&iwloc=&output=embed"

    active_email = osint["email"] if osint["email"] else f"contato@{str(display_name).lower().replace(' ', '')}.com.br"
    active_instagram = osint["instagram"] if osint["instagram"] else f"https://instagram.com/{str(display_name).lower().replace(' ', '')}"

    img_feature_1 = generate_superior_ai_image(segmento, razao, img1_inst, seed_offset_1)
    img_feature_2 = generate_superior_ai_image(segmento, razao, img2_inst if img2_inst else img1_inst, seed_offset_2)

    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="{primary_color}">
  <title>{display_name} | {segmento}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root {{
      --primary: {primary_color};
      --primary-deep: #070e0b;
      --ink: #111816;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: "DM Sans", sans-serif; color: var(--ink); }}
    h1, h2, h3, .display {{ font-family: "Manrope", sans-serif; }}
    .brand-bg {{ background: var(--primary); }}
    .brand-text {{ color: var(--primary); }}
    .hero-bg {{
      background:
        radial-gradient(ellipse at 85% 15%, rgba(255,255,255,.14), transparent 40%),
        linear-gradient(135deg, var(--primary-deep), var(--primary) 70%, #0f172a);
    }}
    .lift {{ transition: transform .25s ease, box-shadow .25s ease; }}
    .lift:hover {{ transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,.12); }}
  </style>
</head>
<body class="bg-[#fafbf9] antialiased">
  <div class="brand-bg px-4 py-2.5 text-center text-xs font-semibold tracking-wider text-white shadow-inner">
    <span class="inline-flex items-center justify-center gap-2">
      ⭐ EXCELÊNCIA E CONFIABILIDADE EM {segmento.upper()} · {cidade.upper()} / {uf.upper()}
    </span>
  </div>

  <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur-md">
    <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 lg:px-8">
      <a href="#inicio" class="flex items-center gap-3">
        <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl brand-bg text-white font-bold text-lg shadow-md">
          {display_name[0].upper()}
        </span>
        <span class="min-w-0">
          <span class="block display truncate text-sm font-extrabold tracking-tight text-slate-900 sm:text-base uppercase">{display_name}</span>
          <span class="block text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">{segmento}</span>
        </span>
      </a>
      <nav class="hidden items-center gap-8 text-sm font-semibold text-slate-600 md:flex">
        <a class="hover:brand-text transition" href="#sobre">Sobre Nós</a>
        <a class="hover:brand-text transition" href="#servicos">Áreas de Atuação</a>
        <a class="hover:brand-text transition" href="#contato">Contato</a>
      </nav>
      <a href="{whats_link}" target="_blank" rel="noopener noreferrer" class="inline-flex shrink-0 items-center gap-2.5 rounded-xl brand-bg px-5 py-3 text-sm font-bold text-white shadow-md transition hover:opacity-90">
        <svg class="h-5 w-5 fill-current text-white" viewBox="0 0 24 24">
          <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
        </svg>
        <span>Falar pelo WhatsApp</span>
      </a>
    </div>
  </header>

  <main>
    <section id="inicio" class="hero-bg relative isolate overflow-hidden text-white py-20 lg:py-28">
      <div class="mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-[1.1fr_.9fr] lg:px-8">
        <div class="max-w-2xl">
          <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-2 text-xs font-semibold tracking-wide text-white/95 backdrop-blur-sm">
            <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
            REFERÊNCIA OFICIAL REGISTRADA
          </div>
          <h1 class="display max-w-xl text-4xl font-extrabold leading-[1.12] tracking-tight sm:text-5xl lg:text-6xl">{display_name}</h1>
          <p class="mt-6 max-w-xl text-base leading-8 text-white/85 sm:text-lg">"{custom_slogan}"</p>
          <div class="mt-9 flex flex-col gap-3 sm:flex-row">
            <a href="{whats_link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-center gap-2 rounded-xl bg-white text-slate-900 px-6 py-4 text-sm font-extrabold shadow-xl transition hover:bg-slate-100">
              Conversar com Especialistas ↗
            </a>
            <a href="#sobre" class="inline-flex items-center justify-center rounded-xl border border-white/35 px-6 py-4 text-sm font-bold text-white transition hover:bg-white/10">Conhecer Empresa</a>
          </div>
        </div>
        <div class="relative mx-auto w-full max-w-xl">
          <div class="overflow-hidden rounded-3xl border border-white/20 bg-white/10 p-3 shadow-2xl backdrop-blur-md">
            <div class="aspect-[4/3] w-full overflow-hidden rounded-2xl bg-slate-900">
              <img src="{img_feature_1}" alt="{display_name} - Destaque" class="h-full w-full object-cover object-center" loading="eager">
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="servicos" class="border-b border-slate-200/80 bg-white py-16 sm:py-20">
      <div class="mx-auto max-w-7xl px-5 lg:px-8">
        <div class="mx-auto mb-12 max-w-2xl text-center">
          <p class="text-xs font-extrabold uppercase tracking-[.2em] brand-text">Atuação Estratégica</p>
          <h2 class="display mt-3 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">Soluções completas e estruturadas.</h2>
          <p class="mt-4 leading-7 text-slate-600">Compromisso com alto desempenho, segurança jurídica e excelência operacional.</p>
        </div>
        <div class="grid gap-6 md:grid-cols-3">
          <article class="lift rounded-2xl border border-slate-200 bg-[#fbfcfb] p-7 shadow-sm">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 brand-text font-bold text-xl">🎯</div>
            <h3 class="display mt-5 text-lg font-bold text-slate-900">Atendimento Direto</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">Comunicação ágil e humanizada para compreender suas demandas com total precisão.</p>
            <ul class="mt-4 space-y-2">{activities_html}</ul>
          </article>
          <article class="lift rounded-2xl border border-slate-200 bg-[#fbfcfb] p-7 shadow-sm">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 brand-text font-bold text-xl">⚡</div>
            <h3 class="display mt-5 text-lg font-bold text-slate-900">Agilidade e Rigor</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">Processos estruturados para garantir eficiência e pontualidade em cada entrega realizada.</p>
          </article>
          <article class="lift rounded-2xl border border-slate-200 bg-[#fbfcfb] p-7 shadow-sm">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 brand-text font-bold text-xl">🛡️</div>
            <h3 class="display mt-5 text-lg font-bold text-slate-900">Segurança & Confiança</h3>
            <p class="mt-2 text-sm leading-6 text-slate-600">Empresa constituída sob rigorosos padrões de conformidade e idoneidade no mercado.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="sobre" class="py-16 sm:py-24">
      <div class="mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-2 lg:gap-20 lg:px-8">
        <div class="relative">
          <div class="aspect-[4/3] w-full overflow-hidden rounded-2xl bg-slate-100 shadow-xl">
            <img src="{img_feature_2}" alt="{display_name} - Sobre" class="h-full w-full object-cover object-center" loading="lazy">
          </div>
          <div class="absolute -bottom-5 right-4 rounded-xl bg-white px-5 py-4 shadow-lg sm:right-8 border border-slate-100">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-500">Fundação Oficial</p>
            <p class="display mt-1 font-extrabold brand-text">{data_abert}</p>
          </div>
        </div>
        <div class="pt-4 lg:pt-0">
          <p class="text-xs font-extrabold uppercase tracking-[.2em] brand-text">Quem Somos</p>
          <h2 class="display mt-3 text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl">Tradição e inovação na {display_name}.</h2>
          <p class="mt-5 leading-8 text-slate-600">Fundada em <b>{data_abert}</b> sob a Razão Social <i>{razao}</i>, a <b>{display_name}</b> destaca-se no mercado de <b>{segmento}</b> em <b>{cidade} - {uf}</b>. Nossa trajetória é pautada na entrega de valor real aos nossos clientes.</p>
          <p class="mt-4 leading-8 text-slate-600">Conecte-se diretamente com nossa equipe para tirar dúvidas, solicitar propostas ou iniciar parcerias de sucesso.</p>
        </div>
      </div>
    </section>

    <section id="contato" class="bg-[#f0f4f1] py-16 sm:py-20">
      <div class="mx-auto max-w-7xl px-5 lg:px-8">
        <div class="overflow-hidden rounded-3xl bg-white shadow-sm ring-1 ring-slate-200/70">
          <div class="grid lg:grid-cols-2">
            <!-- COLUNA ESQUERDA: MAPA DO GOOGLE MAPS EMBUTIDO -->
            <div class="p-6 sm:p-8 lg:p-10 bg-slate-900 flex flex-col justify-between">
              <div>
                <p class="text-xs font-extrabold uppercase tracking-[.2em] text-emerald-400">Canais de Atendimento</p>
                <h2 class="display mt-2 text-2xl font-extrabold text-white sm:text-3xl">Estamos à sua disposição.</h2>
                <p class="mt-2 text-sm text-slate-300">Localize nossa sede ou entre em contato instantaneamente através dos canais oficiais.</p>
              </div>
              <div class="mt-6 aspect-[16/10] w-full overflow-hidden rounded-2xl shadow-md border border-slate-700 bg-slate-800">
                <iframe src="{embed_maps_url}" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
              </div>
              <div class="mt-4 text-xs text-slate-400 flex items-center justify-between">
                <span>📍 {full_address}</span>
                <a href="{maps_url}" target="_blank" rel="noopener noreferrer" class="brand-text font-bold hover:underline text-emerald-400">Ampliar no Maps ↗</a>
              </div>
            </div>

            <!-- COLUNA DIREITA: CANAIS DE COMUNICAÇÃO -->
            <div class="p-8 sm:p-10 lg:p-12 flex flex-col justify-between bg-white">
              <div>
                <h3 class="display text-xl font-extrabold text-slate-900">Canais de Comunicação</h3>
                <p class="mt-1 text-sm text-slate-500">Fale diretamente com nossa equipe por nossos canais oficiais:</p>
                
                <div class="mt-6 space-y-5">
                  <div class="flex items-center gap-4 p-3 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700 font-bold">💬</span>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs font-bold uppercase tracking-wider text-slate-500">WhatsApp / Telefone Principal</p>
                      <p class="text-sm font-bold text-slate-900">{display_phone_text}</p>
                    </div>
                    <a href="{whats_link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 rounded-lg brand-bg px-3 py-1.5 text-xs font-bold text-white shadow-sm transition hover:opacity-90">
                      <span>Conversar ↗</span>
                    </a>
                  </div>

                  <div class="flex items-center gap-4 p-3 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700 font-bold">📧</span>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs font-bold uppercase tracking-wider text-slate-500">E-mail Oficial</p>
                      <p class="text-sm font-bold text-slate-900 truncate">{active_email}</p>
                    </div>
                    <a href="mailto:{active_email}" class="inline-flex items-center gap-1 rounded-lg bg-slate-200 px-3 py-1.5 text-xs font-bold text-slate-800 transition hover:bg-slate-300">
                      <span>Enviar ↗</span>
                    </a>
                  </div>

                  <div class="flex items-center gap-4 p-3 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-pink-100 text-pink-700 font-bold">📸</span>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs font-bold uppercase tracking-wider text-slate-500">Instagram Oficial</p>
                      <p class="text-sm font-bold text-slate-900 truncate">{active_instagram}</p>
                    </div>
                    <a href="{active_instagram}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 rounded-lg bg-slate-200 px-3 py-1.5 text-xs font-bold text-slate-800 transition hover:bg-slate-300">
                      <span>Aceder ↗</span>
                    </a>
                  </div>
                </div>
              </div>

              <!-- ENDEREÇO POR ESCRITO ABAIXO -->
              <div class="mt-8 pt-6 border-t border-slate-100">
                <p class="text-xs font-bold uppercase tracking-wider text-slate-400">Endereço Oficial da Sede</p>
                <p class="mt-1 text-sm font-medium text-slate-700 leading-relaxed">{full_address}</p>
                <p class="mt-1 text-xs text-slate-500">Razão Social: {razao} · CNPJ: {formatted_cnpj}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="bg-[#070e0b] px-5 py-8 text-white/70">
    <div class="mx-auto flex max-w-7xl flex-col gap-5 sm:flex-row sm:items-center sm:justify-between lg:px-3">
      <div>
        <p class="display text-sm font-extrabold tracking-wide text-white uppercase">{display_name}</p>
        <p class="mt-1 text-xs">{razao} · {cidade}/{uf}</p>
      </div>
      <div class="text-xs sm:text-right">
        <p>CNPJ: {formatted_cnpj}</p>
        <p class="mt-1 text-white/50">&copy; <span id="year">2026</span> {display_name}. Todos os direitos reservados.</p>
      </div>
    </div>
  </footer>
  <script>document.getElementById("year").textContent = new Date().getFullYear();</script>
</body>
</html>"""
    
    html_code = apply_accumulated_modifications(html_code, instructions_list)
    return html_code

# --- CARREGAMENTO DA PLANILHA ---
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
        razao = fix_encoding(str(r[1]).strip()) if str(r[1]).strip() != "" else "Empresa"
        
        raw_date = str(r[2]).strip()
        data_abert = raw_date
        parsed_dt_str = ""
        if raw_date:
            try:
                clean_date_str = raw_date.split("T")[0].split(" ")[0]
                if "-" in clean_date_str:
                    parts = clean_date_str.split("-")
                    if len(parts) == 3 and len(parts[0]) == 4:
                        data_abert = f"{parts[2]}/{parts[1]}/{parts[0]}"
                        parsed_dt_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
                elif "/" in clean_date_str:
                    parts = clean_date_str.split("/")
                    if len(parts) == 3 and len(parts[2]) == 2:
                        data_abert = f"{parts[0]}/{parts[1]}/20{parts[2]}"
                        parsed_dt_str = f"20{parts[2]}-{parts[1]}-{parts[0]}"
                    elif len(parts) == 3 and len(parts[2]) == 4:
                        data_abert = f"{parts[0]}/{parts[1]}/{parts[2]}"
                        parsed_dt_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
            except Exception: data_abert = raw_date

        segmento = fix_encoding(str(r[3]).strip()) if str(r[3]).strip() != "" else "N/A"
        uf = str(r[4]).strip().upper() if str(r[4]).strip() != "" else "N/A"
        cidade = fix_encoding(str(r[5]).strip().upper()) if str(r[5]).strip() != "" else "N/A"
        
        if cnpj.lower() == "cnpj" or "razão social" in razao.lower(): continue
            
        maps_url = ""
        telefone = ""
        for item in r:
            if "google.com/maps" in item: maps_url = item.strip(); break
        for item in r:
            cleaned = item.strip()
            if cleaned.isdigit() and 8 <= len(cleaned) <= 12: telefone = cleaned; break
                
        addr_parts = [fix_encoding(p.strip()) for p in r[6:-1] if p.strip() and "google.com/maps" not in p and not (p.strip().isdigit() and 8 <= len(p.strip()) <= 12)]
        endereco = ", ".join(addr_parts) if addr_parts else fix_encoding(str(r[6]).strip())
        
        processed.append([cnpj, razao, data_abert, parsed_dt_str, segmento, uf, cidade, endereco, telefone, maps_url, "Pendente"])
        
    cols = ["CNPJ", "Razao Social", "Data Abertura", "DataAberturaParsed", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Maps", "Status"]
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
        st.markdown("#### 🎯 Filtros por Período")
        
        filtro_data_inicio = st.date_input("Data Abertura (Início):", value=None, format="DD/MM/YYYY")
        filtro_data_fim = st.date_input("Data Abertura (Fim):", value=None, format="DD/MM/YYYY")

        st.divider()
        st.markdown("#### 🎯 Filtros Gerais")
        
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
            <div class="banner-title">🚀 Novas Empresas - Gerador LP com IA de Imagem Realista</div>
            <div class="banner-subtitle">Sistema inteligente com histórico acumulado de comandos, formatação oficial e alta conversão.</div>
        </div>
    """, unsafe_allow_html=True)

    df_filtered = current_df.copy()
    if filtro_data_inicio and "DataAberturaParsed" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["DataAberturaParsed"] >= filtro_data_inicio.strftime("%Y-%m-%d")]
    if filtro_data_fim and "DataAberturaParsed" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["DataAberturaParsed"] <= filtro_data_fim.strftime("%Y-%m-%d")]

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
        cols_to_export = [c for c in df_filtered.columns if c != "DataAberturaParsed"]
        csv_export = df_filtered[cols_to_export].to_csv(index=False).encode('utf-8')
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
            r_cols[1].markdown(f"`{format_cnpj(cnpj)}`")
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

            with st.expander(f"⚙️ Gerenciar & Criar LP Masterpiece: {razao}"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                with c1:
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                with c2:
                    st.markdown(f"**Telefone:** {format_phone(tel) if tel else 'Não informado'}")
                    st.markdown(f"📸 [Pesquisar Instagram / Maps](https://www.google.com/search?q={nome_busca}+{cidade_busca}+instagram)")
                with c3:
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    c_idx = status_list.index(current_status) if current_status in status_list else 0
                    novo_status = st.selectbox("Status:", status_list, index=c_idx, key=f"status_exp_{idx}")
                    if novo_status != current_status:
                        st.session_state.df_status.at[idx, "Status"] = novo_status
                        st.rerun()
                
                st.markdown(f"<hr style='margin: 8px 0px; border-color: {border_color};'>", unsafe_allow_html=True)
                
                # --- CAMPO DE TEXTO INTELIGENTE COM SUPORTE A COLAGEM (CTRL+V) ---
                input_val_key = f"cust_val_{idx}"
                if input_val_key not in st.session_state:
                    st.session_state[input_val_key] = ""

                pasted_img_key = f"pasted_img_{idx}"
                if pasted_img_key not in st.session_state:
                    st.session_state[pasted_img_key] = ""

                paste_component_html = f"""
                <div id="paste-box-{idx}" contenteditable="true" style="
                    border: 2px dashed {border_color}; 
                    background: {input_bg}; 
                    color: {text_muted}; 
                    padding: 8px; 
                    text-align: center; 
                    border-radius: 6px; 
                    font-size: 0.82rem;
                    outline: none;
                    cursor: text;
                    margin-bottom: 8px;
                ">
                    📋 Clique aqui e cole um print do modelo com <b>Ctrl + V</b>
                </div>
                <div id="thumb-preview-{idx}" style="text-align:center; margin-bottom: 6px;"></div>
                <input type="hidden" id="img-data-{idx}" value="">
                <script>
                    const box = document.getElementById('paste-box-{idx}');
                    box.addEventListener('paste', (e) => {{
                        let items = (e.clipboardData || e.originalEvent.clipboardData).items;
                        for (let index in items) {{
                            let item = items[index];
                            if (item.kind === 'file') {{
                                let blob = item.getAsFile();
                                let reader = new FileReader();
                                reader.onload = function(event) {{
                                    let base64Img = event.target.result;
                                    document.getElementById('thumb-preview-{idx}').innerHTML = '<img src="' + base64Img + '" style="max-height: 70px; border-radius: 4px; border: 1px solid #0ea5e9;" /><span style="font-size:11px; color:#10b981; display:block;">✔ Imagem anexada com sucesso!</span>';
                                    
                                    // Sincroniza com Streamlit via URL params simulados ou salvando no sessionStorage
                                    sessionStorage.setItem('pasted_img_{idx}', base64Img);
                                }};
                                reader.readAsDataURL(blob);
                            }}
                        }}
                    }});
                </script>
                """
                components.html(paste_component_html, height=115)

                col_btn_gen, col_inst_txt, col_btn_conf = st.columns([0.9, 3.4, 0.9])
                
                hist_key = f"instructions_history_{idx}"
                if hist_key not in st.session_state:
                    st.session_state[hist_key] = []
                
                seed1_key = f"seed_off_1_{idx}"
                if seed1_key not in st.session_state:
                    st.session_state[seed1_key] = 0

                seed2_key = f"seed_off_2_{idx}"
                if seed2_key not in st.session_state:
                    st.session_state[seed2_key] = 0

                with col_btn_gen:
                    if st.button("🌐 Gerar LP", key=f"btn_auto_lp_{idx}", use_container_width=True):
                        st.session_state[hist_key] = []
                        st.session_state[seed1_key] = 0
                        st.session_state[seed2_key] = 0
                        
                        typed_instruction = st.session_state[input_val_key].strip()
                        full_instruction = f"{typed_instruction} (com base no exemplo visual fornecido)" if typed_instruction else "gerar com base no exemplo visual fornecido"
                        
                        if full_instruction:
                            st.session_state[hist_key].append(full_instruction)
                            
                        with st.spinner("Gerando Landing Page com IA..."):
                            lp_html = generate_ai_masterpiece_landing_page(
                                razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj, 
                                st.session_state[hist_key], st.session_state[seed1_key], st.session_state[seed2_key]
                            )
                            st.session_state[f"lp_data_{idx}"] = lp_html
                            st.session_state.df_status.at[idx, "Status"] = "LP Gerada"
                            st.success("Landing Page gerada!")
                            st.rerun()

                with col_inst_txt:
                    typed_text = st.text_input(
                        "O que mudar na LP", 
                        value=st.session_state[input_val_key],
                        placeholder="Ex: se baseia no exemplo e faz igual na imagem", 
                        label_visibility="collapsed",
                        key=f"text_input_{idx}"
                    )
                    st.session_state[input_val_key] = typed_text

                with col_btn_conf:
                    if st.button("🔄 Confirmar", key=f"btn_conf_lp_{idx}", use_container_width=True):
                        typed_instruction = st.session_state[input_val_key].strip()
                        full_instruction = f"{typed_instruction} (seguindo padrão do modelo)" if typed_instruction else "seguir padrão do modelo colado"
                        
                        if full_instruction:
                            st.session_state[hist_key].append(full_instruction)
                            c_lower = full_instruction.lower()
                            if "2" in c_lower or "inferior" in c_lower or "sobre" in c_lower:
                                st.session_state[seed2_key] += 1
                            else:
                                st.session_state[seed1_key] += 1

                        with st.spinner("Aplicando alterações da IA..."):
                            lp_html = generate_ai_masterpiece_landing_page(
                                razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj, 
                                st.session_state[hist_key], st.session_state[seed1_key], st.session_state[seed2_key]
                            )
                            st.session_state[f"lp_data_{idx}"] = lp_html
                            st.session_state.df_status.at[idx, "Status"] = "LP Gerada"
                            st.session_state[input_val_key] = ""
                            st.success("Alteração aplicada!")
                            st.rerun()

                if f"lp_data_{idx}" in st.session_state:
                    lp_html_content = st.session_state[f"lp_data_{idx}"]
                    st.markdown("#### ⚡ Pré-visualização da Landing Page")
                    
                    st.components.v1.html(lp_html_content, height=520, scrolling=True)
                    
                    st.download_button(
                        label="📥 Baixar Código HTML",
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
