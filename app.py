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
btn_bg = "#1e293b" if is_dark else "#f1f5f9"
btn_text = "#ffffff" if is_dark else "#0f172a"
input_bg = "#1e293b" if is_dark else "#ffffff"
input_text = "#ffffff" if is_dark else "#0f172a"
expander_bg = "#1e293b" if is_dark else "#ffffff"
dropdown_bg = "#1e293b" if is_dark else "#ffffff"

# Estilização CSS completa para caixas, bordas e menus suspensos (dropdowns)
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_app}; color: {text_color}; }}
    
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
    
    /* Botões gerais e barra lateral */
    [data-testid="stSidebar"] button, .stDownloadButton button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] button:hover, .stDownloadButton button:hover {{
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }}
    
    h1, h2, h3, h4, h5, h6 {{ color: {text_color} !important; }}

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
    
    /* Popover / Lista de opções aberta dos Selectboxes */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {{
        background-color: {dropdown_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
    }}
    li[data-baseweb="option"] {{
        background-color: {dropdown_bg} !important;
        color: {text_color} !important;
    }}
    li[data-baseweb="option"]:hover {{
        background-color: #38bdf8 !important;
        color: #0f172a !important;
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
