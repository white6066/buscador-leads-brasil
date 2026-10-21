import streamlit as st
import pandas as pd
import requests
import io
import csv
import urllib.parse
import re
import hashlib
import json
import os
from datetime import datetime
from PIL import Image
import base64

# 1. Configuração da página
st.set_page_config(
    page_title="Novas Empresas - Gerador LP com Comando IA Total",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 0.92rem !important; }
    
    [data-testid="stSidebar"] { 
        padding-top: 1.5rem; 
    }
    [data-testid="stSidebar"] div.stSelectbox { margin-bottom: 2px !important; }
    [data-testid="stSidebar"] hr { margin: 16px 0px !important; }
    
    .stDownloadButton button, div[data-testid="stExpander"] button, div.row-widget.stButton button, button {
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
        font-size: 0.82rem !important;
        padding: 6px 12px !important;
        min-height: 38px !important;
        font-weight: 600 !important;
    }
    
    h1, h2, h3, h4, h5, h6 { font-family: system-ui, -apple-system, sans-serif; }
    a { text-decoration: none !important; }

    .banner-box { 
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: #ffffff;
        padding: 26px 34px; 
        border-radius: 14px; 
        margin-bottom: 24px; 
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
    }
    .banner-title { font-size: 1.45rem; font-weight: 800; margin-bottom: 6px; color: #ffffff; }
    .banner-subtitle { font-size: 0.9rem; line-height: 1.5; color: rgba(255,255,255,0.85); }
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
        res = requests.get(image_url, headers=headers, timeout=2)
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

@st.cache_data(ttl=3600, show_spinner=False)
def deep_osint_company_analysis(razao, cnpj, cidade, uf, segmento):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    queries = [f"{razao} {cidade} {uf}", f"CNPJ {cnpj} business profile"]
    
    found_logo, found_instagram, found_email, found_phone, found_fantasia, found_site, found_slogan = None, None, None, None, None, None, None
    extra_activities = []
    
    for q in queries:
        try:
            encoded_q = urllib.parse.quote(q)
            url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
            res = requests.get(url, headers=headers, timeout=2)
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

def search_real_photo_by_query(query_text, segmento, index_offset=0):
    query_lower = query_text.lower()
    
    if any(w in query_lower for w in ['esportivo', 'esporte', 'luxo', 'mercedes', 'bmw', 'audi', 'porsche', 'ranger']):
        cars = [
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=1200&auto=format&fit=crop"
        ]
        return cars[index_offset % len(cars)]
    elif any(w in query_lower for w in ['oficina', 'mecanica', 'reparo', 'manutencao']):
        return "https://images.unsplash.com/photo-1486006920555-c77dce18193b?q=80&w=1200&auto=format&fit=crop"
    elif any(w in query_lower for w in ['fachada', 'loja', 'frente', 'comercio', 'predio']):
        return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=1200&auto=format&fit=crop"
    
    seg_l = segmento.lower()
    if 'veiculo' in seg_l or 'carro' in seg_l or 'auto' in seg_l:
        default_cars = [
            "https://images.unsplash.com/photo-1563720223185-11003d516935?q=80&w=1200&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=1200&auto=format&fit=crop"
        ]
        return default_cars[index_offset % len(default_cars)]
    
    return "https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=1200&auto=format&fit=crop"

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
    
    color_map = {
        "azul bebe": "#89cff0", "azul bebê": "#89cff0", "azul claro": "#38bdf8",
        "azul celeste": "#0ea5e9", "azul": "#2563eb", "azul royal": "#1d4ed8",
        "azul marinho": "#1e3a8a", "azul escuro": "#0f172a", "cyan": "#06b6d4",
        "turquesa": "#14b8a6", "verde": "#16a34a", "verde claro": "#4ade80",
        "verde lima": "#84cc16", "verde esmeralda": "#10b981", "verde oliva": "#65a30d",
        "verde escuro": "#14532d", "mint": "#6ee7b7", "menta": "#6ee7b7",
        "vermelho": "#dc2626", "vermelho escuro": "#991b1b", "vinho": "#881337",
        "rosa": "#ec4899", "rosa claro": "#f472b6", "rosa choque": "#f43f5e",
        "pink": "#db2777", "magenta": "#d946ef", "roxo": "#7c3aed",
        "violeta": "#8b5cf6", "lilás": "#c084fc", "lilas": "#c084fc",
        "púrpura": "#581c87", "purpura": "#581c87", "índigo": "#4338ca",
        "indigo": "#4338ca", "laranja": "#ea580c", "laranja queimado": "#c2410c",
        "terracota": "#b45309", "amarelo": "#eab308", "dourado": "#d97706",
        "amarelo claro": "#fef08a", "preto": "#0f172a", "grafite": "#1e293b",
        "cinza": "#64748b", "cinza claro": "#cbd5e1", "cinza escuro": "#334155",
        "branco": "#ffffff", "bege": "#d4b996", "marrom": "#78350f"
    }

    for instruction in reversed(instructions_list):
        inst_lower = instruction.lower()
        hex_match = re.search(r'#(?:[0-9a-fA-F]{3}){1,2}\b', instruction)
        if hex_match:
            custom_primary_color = hex_match.group(0)
            break
        else:
            found_color_name = False
            for c_name in sorted(color_map.keys(), key=len, reverse=True):
                if c_name in inst_lower:
                    custom_primary_color = color_map[c_name]
                    found_color_name = True
                    break
            if found_color_name:
                break

        if "imagem" in inst_lower and ("aumentar" in inst_lower or "largo" in inst_lower or "maior" in inst_lower):
            html_content = html_content.replace('max-w-xl', 'max-w-3xl')
            html_content = html_content.replace('aspect-[4/3]', 'aspect-[16/9]')
        elif "imagem" in inst_lower and ("diminuir" in inst_lower or "menor" in inst_lower):
            html_content = html_content.replace('max-w-xl', 'max-w-md')

    if custom_primary_color:
        html_content = re.sub(r'--primary:\s*[^;]+;', f'--primary: {custom_primary_color};', html_content)
        html_content = html_content.replace('bg-[#070e0b]', 'brand-bg')
        html_content = re.sub(r'<meta name="theme-color" content="[^"]+">', f'<meta name="theme-color" content="{custom_primary_color}">', html_content)

    return html_content

def generate_masterpiece_landing_page(razao, segmento, cidade, uf, endereco, tel_planilha, data_abert, cnpj, instructions_list, current_img1=None, current_img2=None, logo_b64=None):
    osint = deep_osint_company_analysis(razao, cnpj, cidade, uf, segmento)
    primary_color, color_rationale = determine_harmonious_palette(razao, segmento, osint["logo"])
    
    formatted_cnpj = format_cnpj(cnpj)
    active_tel = osint["phone"] if osint["phone"] else tel_planilha
    
    clean_tel = "".join(filter(str.isdigit, str(active_tel))) if active_tel else ""
    if clean_tel:
        if not clean_tel.startswith("55") and (len(clean_tel) == 10 or len(clean_tel) == 11):
            clean_tel = "55" + clean_tel
        msg_padrao = urllib.parse.quote(f"Olá! Entrei em contato através do site oficial da {osint['fantasia']}.")
        whats_link = f"https://wa.me/{clean_tel}?text={msg_padrao}"
        display_phone_text = format_phone(active_tel)
    else:
        whats_link = "#"
        display_phone_text = "WhatsApp indisponível"

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
    display_name = osint["fantasia"]
    maps_query = urllib.parse.quote(f"{display_name}, {full_address}")
    maps_url = f"https://www.google.com/maps/search/?api=1&query={maps_query}"
    embed_maps_url = f"https://maps.google.com/maps?q={maps_query}&t=&z=15&ie=UTF8&iwloc=&output=embed"

    active_email = osint["email"] if osint["email"] else f"contato@{str(display_name).lower().replace(' ', '')}.com.br"
    active_instagram = osint["instagram"] if osint["instagram"] else f"https://instagram.com/{str(display_name).lower().replace(' ', '')}"

    if logo_b64:
        logo_header_html = f'<img src="{logo_b64}" alt="{display_name}" class="h-11 w-11 object-contain rounded-xl shadow-sm border border-slate-200">'
    else:
        logo_header_html = f'<span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl brand-bg text-white font-bold text-lg shadow-md">{display_name[0].upper()}</span>'

    img1_query = ""
    img2_query = ""
    for inst in instructions_list:
        inst_l = inst.lower()
        if "imagem 1" in inst_l or ("foto" in inst_l and ("topo" in inst_l or "superior" in inst_l or "1" in inst_l)):
            img1_query = inst
        elif "imagem 2" in inst_l or ("foto" in inst_l and ("inferior" in inst_l or "sobre" in inst_l or "2" in inst_l)):
            img2_query = inst

    img_feature_1 = current_img1 if current_img1 else (search_real_photo_by_query(img1_query, segmento, 0) if img1_query else search_real_photo_by_query("", segmento, 0))
    img_feature_2 = current_img2 if current_img2 else (search_real_photo_by_query(img2_query, segmento, 1) if img2_query else search_real_photo_by_query("", segmento, 1))

    whatsapp_svg_icon = '<svg class="h-6 w-6 fill-current text-emerald-600" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>'
    instagram_svg_icon = '<svg class="h-6 w-6 fill-current text-pink-600" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'

    map_container_html = f"""
    <div id="map-wrapper" style="position: relative; width: 100%; height: 240px; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.2); background: #0f172a;">
      <iframe id="map-iframe" src="{embed_maps_url}" width="100%" height="100%" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
    """

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
    body {{ font-family: "DM Sans", sans-serif; color: var(--ink); background-color: #fafbf9; margin: 0; padding: 0; }}
    h1, h2, h3, .display {{ font-family: "Manrope", sans-serif; }}
    .brand-bg {{ background: var(--primary); }}
    .brand-text {{ color: var(--primary); }}
    .hero-bg {{
      background:
        radial-gradient(ellipse at 85% 15%, rgba(255,255,255,.14), transparent 40%),
        linear-gradient(135deg, var(--primary-deep), var(--primary) 70%, #0f172a);
    }}
    .map-box-bg {{
      background: linear-gradient(145deg, var(--primary) 0%, var(--primary-deep, #0f172a) 100%);
    }}
    .lift {{ transition: transform .25s ease, box-shadow .25s ease; }}
    .lift:hover {{ transform: translateY(-4px); box-shadow: 0 20px 40px rgba(0,0,0,.12); }}
  </style>
</head>
<body class="bg-[#fafbf9] antialiased">
  <div id="btn-pdf-container" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
    <button onclick="gerarPDF()" style="background: {primary_color}; color: #ffffff; border: none; padding: 12px 20px; border-radius: 30px; font-weight: bold; font-family: 'Manrope', sans-serif; box-shadow: 0 10px 25px rgba(0,0,0,0.3); cursor: pointer; display: flex; align-items: center; gap: 8px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
      📥 Baixar PDF
    </button>
  </div>

  <div id="conteudo-lp" class="w-full bg-white">
    <div class="brand-bg px-4 py-2.5 text-center text-xs font-semibold tracking-wider text-white shadow-inner">
      <span class="inline-flex items-center justify-center gap-2">
        ⭐ EXCELÊNCIA E CONFIABILIDADE EM {segmento.upper()} · {cidade.upper()} / {uf.upper()}
      </span>
    </div>

    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur-md">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4 lg:px-8">
        <a href="#inicio" class="flex items-center gap-3">
          {logo_header_html}
          <span class="min-w-0">
            <span class="block display truncate text-sm font-extrabold tracking-tight text-slate-900 sm:text-base uppercase">{display_name}</span>
            <span class="block text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">{segmento}</span>
          </span>
        </a>
        <nav class="hidden items-center gap-8 text-sm font-semibold text-slate-600 md:flex">
          <a class="hover:brand-text transition" href="#servicos">Áreas de Atuação</a>
          <a class="hover:brand-text transition" href="#sobre">Sobre Nós</a>
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
              <div class="p-6 sm:p-8 lg:p-10 map-box-bg flex flex-col justify-between">
                <div>
                  <h2 class="display text-2xl font-extrabold text-white sm:text-3xl">Estamos à sua disposição.</h2>
                  <p class="mt-2 text-sm text-white/80">Localize nossa sede ou entre em contato instantaneamente através dos canais oficiais.</p>
                </div>
                <div class="mt-6">
                  {map_container_html}
                </div>
                <div class="mt-4 text-xs text-white/90 flex items-center justify-between">
                  <span>📍 {full_address}</span>
                  <a href="{maps_url}" target="_blank" rel="noopener noreferrer" class="font-bold hover:underline text-white bg-white/20 px-3 py-1.5 rounded-lg transition">Ampliar no Maps ↗</a>
                </div>
              </div>

              <div class="p-8 sm:p-10 lg:p-12 flex flex-col justify-between bg-white">
                <div>
                  <h3 class="display text-xl font-extrabold text-slate-900">Canais de Comunicação</h3>
                  <p class="mt-1 text-sm text-slate-500">Fale diretamente com nossa equipe por nossos canais oficiais:</p>
                  
                  <div class="mt-6 space-y-5">
                    <div class="flex items-center gap-4 p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                      <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-100/70 shadow-sm">
                        {whatsapp_svg_icon}
                      </span>
                      <div class="flex-1 min-w-0">
                        <p class="text-[11px] font-bold uppercase tracking-wider text-slate-500">WhatsApp / Telefone Principal</p>
                        <p class="text-sm font-bold text-slate-900">{display_phone_text}</p>
                      </div>
                      <a href="{whats_link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 rounded-lg brand-bg px-3.5 py-2 text-xs font-bold text-white shadow-sm transition hover:opacity-90">
                        <span>Conversar ↗</span>
                      </a>
                    </div>

                    <div class="flex items-center gap-4 p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                      <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-100/70 shadow-sm text-blue-600 font-bold text-lg">
                        ✉️
                      </span>
                      <div class="flex-1 min-w-0">
                        <p class="text-[11px] font-bold uppercase tracking-wider text-slate-500">E-mail Oficial</p>
                        <p class="text-sm font-bold text-slate-900 truncate">{active_email}</p>
                      </div>
                      <a href="mailto:{active_email}" class="inline-flex items-center gap-1 rounded-lg bg-slate-200 px-3.5 py-2 text-xs font-bold text-slate-800 transition hover:bg-slate-300">
                        <span>Enviar ↗</span>
                      </a>
                    </div>

                    <div class="flex items-center gap-4 p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                      <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-pink-100/70 shadow-sm">
                        {instagram_svg_icon}
                      </span>
                      <div class="flex-1 min-w-0">
                        <p class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Instagram Oficial</p>
                        <p class="text-sm font-bold text-slate-900 truncate">{active_instagram}</p>
                      </div>
                      <a href="{active_instagram}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 rounded-lg bg-slate-200 px-3.5 py-2 text-xs font-bold text-slate-800 transition hover:bg-slate-300">
                        <span>Aceder ↗</span>
                      </a>
                    </div>
                  </div>
                </div>

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
  </div>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();

    function gerarPDF() {{
      const btnContainer = document.getElementById('btn-pdf-container');
      if (btnContainer) btnContainer.style.display = 'none';

      const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html' }});
      const url = URL.createObjectURL(blob);
      const novaAba = window.open(url, '_blank');
      
      if (novaAba) {{
        novaAba.onload = function() {{
          setTimeout(() => {{
            novaAba.print();
            if (btnContainer) btnContainer.style.display = 'block';
          }}, 800);
        }};
      }} else {{
        if (btnContainer) btnContainer.style.display = 'block';
        alert('Permita pop-ups no navegador para gerar o PDF automaticamente.');
      }}
    }}
  </script>
</body>
</html>"""
    
    html_code = apply_accumulated_modifications(html_code, instructions_list)
    return html_code

# --- GERENCIAMENTO DE PERSISTÊNCIA DUPLA (SESSÃO + DISCO) ---
STATUS_FILE = "status_leads.json"
LPS_FILE = "saved_lps_data.json"

def load_persistent_store(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_persistent_store(file_path, data_dict):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

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
    df_base = pd.DataFrame(processed, columns=cols)

    saved_status_map = load_persistent_store(STATUS_FILE)
    for i, row in df_base.iterrows():
        c_key = str(row["CNPJ"])
        if c_key in saved_status_map:
            df_base.at[i, "Status"] = saved_status_map[c_key]

    return df_base

def sync_status_change(cnpj, new_status, df_target):
    saved_status_map = load_persistent_store(STATUS_FILE)
    saved_status_map[str(cnpj)] = new_status
    save_persistent_store(STATUS_FILE, saved_status_map)

    for i, row in df_target.iterrows():
        if str(row["CNPJ"]) == str(cnpj):
            df_target.at[i, "Status"] = new_status
            break

def sync_lp_content_save(cnpj, html_code):
    saved_lps_map = load_persistent_store(LPS_FILE)
    saved_lps_map[str(cnpj)] = html_code
    save_persistent_store(LPS_FILE, saved_lps_map)

    os.makedirs("clientes_salvos", exist_ok=True)
    caminho = f"clientes_salvos/landing_page_{cnpj}.html"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(html_code)

def sync_lp_content_delete(cnpj):
    saved_lps_map = load_persistent_store(LPS_FILE)
    if str(cnpj) in saved_lps_map:
        del saved_lps_map[str(cnpj)]
        save_persistent_store(LPS_FILE, saved_lps_map)

    caminho = f"clientes_salvos/landing_page_{cnpj}.html"
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except Exception:
            pass

try:
    df = load_data_from_sheet()

    if "df_status" not in st.session_state or len(st.session_state.df_status) != len(df):
        st.session_state.df_status = df.copy()
    else:
        df["Status"] = st.session_state.df_status["Status"]

    current_df = st.session_state.df_status

    if "page_num" not in st.session_state:
        st.session_state.page_num = 1

    saved_lps_store = load_persistent_store(LPS_FILE)

    with st.sidebar:
        st.markdown("### 🚀 Central de Leads")
        st.markdown("<p style='font-size: 0.8rem; margin-bottom: 0px;'>Prospecção & Inteligência</p>", unsafe_allow_html=True)
        st.divider()

        st.markdown("#### 📅 Filtros por Período")
        
        filtro_data_inicio = st.date_input("Data Abertura (Início):", value=None, format="DD/MM/YYYY")
        filtro_data_fim = st.date_input("Data Abertura (Fim):", value=None, format="DD/MM/YYYY")

        st.divider()
        st.markdown("#### 🔍 Filtros Gerais")
        
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
            <div class="banner-title">🚀 Novas Empresas - Gerador LP com Comando IA Total</div>
            <div class="banner-subtitle">Gerencie leads, aplique alterações de imagens, redimensionamentos, cores e textos mantendo o padrão visual original.</div>
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

    tot_1, tot_2, tot_3, tot_4 = st.columns(4)
    
    with tot_1:
        st.metric(label="📊 Total Exibidos", value=len(df_filtered))
    with tot_2:
        st.metric(label="⏳ Pendentes", value=len(current_df[current_df["Status"] == "Pendente"]))
    with tot_3:
        st.metric(label="⚡ LPs Geradas", value=len(current_df[current_df["Status"] == "LP Gerada"]))
    with tot_4:
        st.metric(label="🏆 Vendas Fechadas", value=len(current_df[current_df["Status"] == "Finalizado Positivo"]))

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    col_search, col_export = st.columns([5, 1])
    with col_search:
        search_query = st.text_input("🔍 Pesquisa Rápida", placeholder="Digite o nome da empresa, CNPJ ou cidade...", label_visibility="collapsed")
    with col_export:
        cols_to_export = [c for c in df_filtered.columns if c != "DataAberturaParsed"]
        csv_export = df_filtered[cols_to_export].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar", data=csv_export, file_name="leads.csv", mime="text/html", use_container_width=True)

    if search_query:
        ql = search_query.lower()
        df_filtered = df_filtered[
            df_filtered["Razao Social"].str.lower().str.contains(ql) |
            df_filtered["CNPJ"].str.lower().str.contains(ql) |
            df_filtered["Cidade"].str.lower().str.contains(ql)
        ]

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
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
        
        st.markdown("<hr style='margin: 6px 0px 10px 0px;'>", unsafe_allow_html=True)

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

            clean_tel_link = ''.join(filter(str.isdigit, str(tel))) if tel else ""
            if clean_tel_link and not clean_tel_link.startswith("55") and len(clean_tel_link) <= 11:
                clean_tel_link = "55" + clean_tel_link

            texto_proposta = (
                f"Olá, pessoal da *{razao}*! Tudo bem?\n\n"
                f"Me chamo Wesley e sou responsável pela Kritech, especializada na criação de sites profissionais com preços acessíveis.\n\n"
                f"Acompanho a abertura de novas empresas e acredito que investir em uma boa presença na internet desde o início pode ser um grande diferencial para transmitir confiança, fortalecer a marca e conquistar novos clientes.\n\n"
                f"Por isso, tomei a liberdade de desenvolver um modelo de site personalizado para a *{razao}*, sem compromisso, que estou enviando em anexo para vocês conhecerem. O projeto pode ser adaptado conforme suas preferências e necessidades.\n\n"
                f"Minha proposta é oferecer um investimento acessível, com mensalidade econômica para manter o site no ar e realizar a manutenção. Assim, vocês podem fortalecer a presença digital da empresa, facilitar o contato com interessados e criar novas oportunidades de negócio, sem precisar investir grandes valores.\n\n"
                f"Se gostarem da ideia, podemos conversar, ajustar o projeto e formalizar tudo por contrato, com valores e condições transparentes.\n\n"
                f"Que tal dar esse primeiro passo para destacar a *{razao}* no mercado?\n\n"
                f"Atenciosamente,\n"
                f"Wesley | Kritech — Soluções Digitais"
            )
            msg_prospeccao = urllib.parse.quote(texto_proposta)
            wa_pitch_link = f"https://wa.me/{clean_tel_link}?text={msg_prospeccao}" if clean_tel_link else "#"

            r_cols = st.columns([2.6, 1.4, 1.0, 0.5, 1.1, 1.2, 1.2])
            r_cols[0].markdown(f"🏢 **{razao}**")
            r_cols[1].markdown(f"`{format_cnpj(cnpj)}`")
            r_cols[2].markdown(f"{data_abert}")
            r_cols[3].markdown(f"{uf}")
            r_cols[4].markdown(f"{cidade}")
            
            with r_cols[5]:
                action_str = []
                if clean_tel_link: 
                    action_str.append(f"[💬]({wa_pitch_link})")
                else: 
                    action_str.append("📞")
                if maps_link: 
                    action_str.append(f"[📍]({maps_link})")
                else: 
                    action_str.append("📍")
                
                nome_encoded = urllib.parse.quote(f"{razao} {cidade} {uf}")
                action_str.append(f"[🔍](https://www.google.com/search?q={nome_encoded})")
                st.markdown(" &nbsp; ".join(action_str))
                
            r_cols[6].markdown(f"🟢 `{current_status}`")

            with st.expander(f"⚙️ Gerenciar & Criar LP Masterpiece: {razao}"):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                with c1:
                    st.markdown(f"**Segmento:** {segmento}")
                    st.markdown(f"**Endereço:** {endereco if endereco else 'Não informado'}")
                with c2:
                    st.markdown(f"**Telefone:** {format_phone(tel) if tel else 'Não informado'}")
                    if clean_tel_link:
                        st.markdown(f"📲 [**Enviar Proposta via WhatsApp**]({wa_pitch_link})")
                    st.markdown(f"📸 [Pesquisar Instagram / Maps](https://www.google.com/search?q={nome_encoded}+instagram)")
                with c3:
                    status_list = ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
                    c_idx = status_list.index(current_status) if current_status in status_list else 0
                    novo_status = st.selectbox("Status:", status_list, index=c_idx, key=f"status_exp_{idx}")
                    if novo_status != current_status:
                        sync_status_change(cnpj, novo_status, st.session_state.df_status)
                        st.rerun()
                
                st.markdown("<hr style='margin: 10px 0px;'>", unsafe_allow_html=True)
                
                img1_key = f"saved_img1_{idx}"
                img2_key = f"saved_img2_{idx}"
                logo_key = f"saved_logo_{idx}"
                hist_key = f"instructions_history_{idx}"
                input_val_key = f"cust_val_{idx}"
                import_file_key = f"imported_html_{idx}"

                if img1_key not in st.session_state:
                    st.session_state[img1_key] = search_real_photo_by_query("", segmento, 0)
                if img2_key not in st.session_state:
                    st.session_state[img2_key] = search_real_photo_by_query("", segmento, 1)
                if logo_key not in st.session_state:
                    st.session_state[logo_key] = None
                if hist_key not in st.session_state:
                    st.session_state[hist_key] = []
                if input_val_key not in st.session_state:
                    st.session_state[input_val_key] = ""

                # Carregamento persistente inicial caso ainda não esteja na memória da sessão
                if f"lp_data_{idx}" not in st.session_state and str(cnpj) in saved_lps_store:
                    st.session_state[f"lp_data_{idx}"] = saved_lps_store[str(cnpj)]

                # IMPORTAR E SOBRESCREVER ARQUIVO HTML MODIFICADO
                up_html_file = st.file_uploader(
                    "📥 Importar arquivo HTML alterado externamente (.html)",
                    type=["html"],
                    key=import_file_key
                )
                if up_html_file is not None:
                    html_bytes = up_html_file.getvalue()
                    html_content_imported = html_bytes.decode('utf-8')
                    
                    # Força a atualização imediata da variável de sessão e grava na persistência
                    st.session_state[f"lp_data_{idx}"] = html_content_imported
                    sync_lp_content_save(cnpj, html_content_imported)
                    sync_status_change(cnpj, "LP Gerada", st.session_state.df_status)
                    
                    st.success("LP alterada importada, sobrescrita e salva com sucesso!")
                    st.rerun()

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

                up_col1, up_col2 = st.columns([2, 2])
                with up_col1:
                    uploaded_ref_image = st.file_uploader("📎 Enviar imagem/foto própria", type=["png", "jpg", "jpeg"], key=f"uploader_{idx}")
                with up_col2:
                    image_position = st.selectbox(
                        "Onde aplicar a imagem enviada:",
                        ["Imagem 1 (Superior / Topo)", "Imagem 2 (Inferior / Sobre)", "Logótipo Oficial do Cabeçalho"],
                        key=f"pos_{idx}"
                    )

                col_btn_gen, col_inst_txt, col_btn_conf = st.columns([0.9, 3.4, 0.9])

                with col_btn_gen:
                    if st.button("🌐 Gerar LP", key=f"btn_auto_lp_{idx}", use_container_width=True):
                        st.session_state[hist_key] = []
                        st.session_state[img1_key] = search_real_photo_by_query("", segmento, 0)
                        st.session_state[img2_key] = search_real_photo_by_query("", segmento, 1)
                        st.session_state[logo_key] = None
                        
                        typed_instruction = st.session_state[input_val_key].strip()
                        if typed_instruction:
                            st.session_state[hist_key].append(typed_instruction)
                            
                        with st.spinner("Executando busca OSINT e gerando Landing Page..."):
                            lp_html = generate_masterpiece_landing_page(
                                razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj, 
                                st.session_state[hist_key],
                                st.session_state[img1_key],
                                st.session_state[img2_key],
                                st.session_state[logo_key]
                            )
                            st.session_state[f"lp_data_{idx}"] = lp_html
                            sync_status_change(cnpj, "LP Gerada", st.session_state.df_status)
                            sync_lp_content_save(cnpj, lp_html)
                            st.success("Landing Page gerada e salva com sucesso!")
                            st.rerun()

                with col_inst_txt:
                    typed_text = st.text_input(
                        "O que mudar na LP", 
                        value=st.session_state[input_val_key],
                        placeholder="Ex: trocar cor para azul bebe, verde menta, #89cff0...", 
                        label_visibility="collapsed",
                        key=f"text_input_{idx}"
                    )
                    st.session_state[input_val_key] = typed_text

                with col_btn_conf:
                    if st.button("🔄 Confirmar", key=f"btn_conf_lp_{idx}", use_container_width=True):
                        if uploaded_ref_image is not None:
                            bytes_data = uploaded_ref_image.getvalue()
                            mime_type = uploaded_ref_image.type if hasattr(uploaded_ref_image, 'type') else "image/jpeg"
                            b64_str = f"data:{mime_type};base64,{base64.b64encode(bytes_data).decode('utf-8')}"

                            if "Imagem 1" in image_position:
                                st.session_state[img1_key] = b64_str
                            elif "Imagem 2" in image_position:
                                st.session_state[img2_key] = b64_str
                            elif "Logótipo" in image_position:
                                st.session_state[logo_key] = b64_str

                        typed_instruction = st.session_state[input_val_key].strip()
                        if typed_instruction:
                            st.session_state[hist_key].append(typed_instruction)
                            inst_l = typed_instruction.lower()
                            if "foto" in inst_l or "imagem" in inst_l or "carro" in inst_l or "esportivo" in inst_l:
                                if "2" in inst_l or "inferior" in inst_l or "sobre" in inst_l:
                                    st.session_state[img2_key] = search_real_photo_by_query(typed_instruction, segmento, 1)
                                else:
                                    st.session_state[img1_key] = search_real_photo_by_query(typed_instruction, segmento, 0)

                        with st.spinner("Atualizando modificações e dados..."):
                            lp_html = generate_masterpiece_landing_page(
                                razao, segmento, cidade, uf, endereco, tel, data_abert, cnpj, 
                                st.session_state[hist_key],
                                st.session_state[img1_key],
                                st.session_state[img2_key],
                                st.session_state[logo_key]
                            )
                            st.session_state[f"lp_data_{idx}"] = lp_html
                            sync_status_change(cnpj, "LP Gerada", st.session_state.df_status)
                            sync_lp_content_save(cnpj, lp_html)
                            st.session_state[input_val_key] = ""
                            st.success("Modificações aplicadas e salvas!")
                            st.rerun()

                if f"lp_data_{idx}" in st.session_state:
                    lp_html_content = st.session_state[f"lp_data_{idx}"]
                    st.markdown("#### ⚡ Pré-visualização da Landing Page")
                    
                    st.components.v1.html(lp_html_content, height=520, scrolling=True)
                    
                    b_save, b_del, b_dl = st.columns([1, 1, 2])
                    with b_save:
                        if st.button("💾 Salvar LP no Projeto", key=f"btn_save_{idx}", use_container_width=True):
                            sync_lp_content_save(cnpj, lp_html_content)
                            sync_status_change(cnpj, "LP Gerada", st.session_state.df_status)
                            st.success("LP salva com sucesso!")
                    with b_del:
                        if st.button("🗑️ Apagar LP", key=f"btn_del_{idx}", use_container_width=True):
                            if f"lp_data_{idx}" in st.session_state:
                                del st.session_state[f"lp_data_{idx}"]
                            sync_lp_content_delete(cnpj)
                            st.warning("LP apagada.")
                            st.rerun()
                    with b_dl:
                        st.download_button(
                            label="📥 Baixar Código HTML",
                            data=lp_html_content,
                            file_name=f"landing_page_{cnpj}.html",
                            mime="text/html",
                            key=f"dl_html_{idx}",
                            use_container_width=True
                        )

            st.markdown("<hr style='margin: 2px 0px 4px 0px;'>", unsafe_allow_html=True)

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
