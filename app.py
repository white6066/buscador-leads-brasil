import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Painel de Prospecção & Inteligência Comercial",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Central de Leads & Novas Empresas")
st.markdown("Filtre as empresas recém-criadas, pesquise presença digital e gerencie a geração de Landing Pages.")

# Base de dados direta sem cache para forçar a atualização imediata
data = [
    ["68822545000117", "GOMES AUTO CENTER LTDA", "2026-08-27", "Comércio Varejista de Automóveis Usados", "AL", "CORURIPE", "ENGENHEIRO GUTTEMBERG BREDA NETO, 1226 - ALTO DA SAUDADE", "8293904127", "https://www.google.com/maps/search/?api=1&query=GOMES%20AUTO%20CENTER%20LTDA%20CORURIPE%20AL"],
    ["35482768000204", "FBS COMERCIO E SERVICOS LTDA", "2026-08-31", "Comércio Atacadista de Produtos Alimentícios", "AL", "MURICI", "MILITAO VIEIRA SAPUCAIA, 103 - CENTRO", "8132741010", "https://www.google.com/maps/search/?api=1&query=FBS%20COMERCIO%20E%20SERVICOS%20LTDA%20MURICI%20AL"],
    ["68806510000194", "LILY PRESENTES LTDA", "2026-08-26", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DA ALEGRIA, 258 - CENTRO", "8293885886", "https://www.google.com/maps/search/?api=1&query=LILY%20PRESENTES%20LTDA%20MACEIO%20AL"],
    ["63324700000232", "SILVA NERES IMPORTACAO E EXPORTACAO LTDA", "2026-09-08", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "LOURIVAL MELO MOTA, 15159 - SANTOS DUMONT", "1199370549", "https://www.google.com/maps/search/?api=1&query=SILVA%20NERES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL"],
    ["68632169000106", "SETE MARES IMPORTACAO E EXPORTACAO LTDA", "2026-08-13", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "DESEMBARGADOR ARTUR JUCÁ, 250 - CENTRO", "8232411988", "https://www.google.com/maps/search/?api=1&query=SETE%20MARES%20IMPORTACAO%20E%20EXPORTACAO%20LTDA%20MACEIO%20AL"],
    ["46531865000347", "LA SETTE IMPORTADORA E DISTRIBUIDORA LTDA", "2026-09-02", "Comércio Atacadista de Vestuário e Acessórios", "AL", "MACEIO", "PAULO HENRIQUE MENDES, 75 - TABULEIRO DO MARTINS", "2138609696", "https://www.google.com/maps/search/?api=1&query=LA%20SETTE%20IMPORTADORA%20E%20DISTRIBUIDORA%20LTDA%20MACEIO%20AL"],
    ["20799483000224", "C. DANTAS DE LIMA BARBOSA & CIA LTDA", "2026-08-26", "Supermercados", "AL", "DELMIRO GOUVEIA", "TEOTONIO VILELA, SN - NOVO", "8299622243", "https://www.google.com/maps/search/?api=1&query=C.%20DANTAS%20DE%20LIMA%20BARBOSA%20%26%20CIA%20LTDA%20DELMIRO%20GOUVEIA%20AL"],
    ["68656601000190", "MANA HOLDING PARTICIPACOES PATRIMONIAIS LTDA", "2026-08-18", "Holdings de Instituições Não-Financeiras", "AL", "ARAPIRACA", "SANTOS DUMONT, 378 - BAIXÃO", "8299999999", "https://www.google.com/maps/search/?api=1&query=MANA%20HOLDING%20PARTICIPACOES%20PATRIMONIAIS%20LTDA%20ARAPIRACA%20AL"],
    ["50264359000578", "MD NE NEGOCIOS LTDA", "2026-08-18", "Holdings de Instituições Não-Financeiras", "AL", "MACEIO", "COMENDADOR GUSTAVO PAIVA, 2789 - MANGABEIRAS", "8130870000", "https://www.google.com/maps/search/?api=1&query=MD%20NE%20NEGOCIOS%20LTDA%20MACEIO%20AL"],
    ["68690371000186", "VCX CAPITAL LTDA", "2026-08-19", "Holdings de Instituições Não-Financeiras", "AL", "MACEIO", "ÁLVARO OTACÍLIO, 3731 - JATIÚCA", "8230284221", "https://www.google.com/maps/search/?api=1&query=VCX%20CAPITAL%20LTDA%20MACEIO%20AL"],
    ["69041024000195", "LEIVA E ALMEIDA LTDA", "2026-09-09", "Holdings de Instituições Não-Financeiras", "AL", "MACEIO", "FERNANDES LIMA, 8 - FAROL", "8296637867", "https://www.google.com/maps/search/?api=1&query=LEIVA%20E%20ALMEIDA%20LTDA%20MACEIO%20AL"],
    ["68848678000162", "HELAIS CALHEIROS CORRETORA DE SEGUROS LTDA", "2026-08-28", "Corretores e Agentes de Seguros", "AL", "MARECHAL DEODORO", "MANOEL PEREIRA DA SILVA, 284 - FRANCÊS", "8299320190", "https://www.google.com/maps/search/?api=1&query=HELAIS%20CALHEIROS%20CORRETORA%20DE%20SEGUROS%20LTDA%20MARECHAL%20DEODORO%20AL"],
    ["68753584000100", "GENILSON SANTOS DE OLIVEIRA", "2026-08-24", "Reparação de Equipamentos de Comunicação", "AL", "MESSIAS", "CENTRO", "", "https://www.google.com/maps/search/?api=1&query=68.753.584%20GENILSON%20SANTOS%20DE%20OLIVEIRA%20MESSIAS%20AL"],
    ["68809605000161", "B GALVAO DOS SANTOS", "2026-08-26", "Reparação de Equipamentos de Comunicação", "AL", "UNIAO DOS PALMARES", "CENTRO", "", "https://www.google.com/maps/search/?api=1&query=B%20GALVAO%20DOS%20SANTOS%20UNIAO%20DOS%20PALMARES%20AL"],
    ["68820635000179", "F. LOPES BARBOSA LTDA", "2026-08-22", "Comércio Varejista de Automóveis Usados", "AP", "MACAPA", "PADRE JULIO MARIA LOMBAERD, 1326 - CENTRAL", "9681320032", "https://www.google.com/maps/search/?api=1&query=F.%20LOPES%20BARBOSA%20LTDA%20MACAPA%20AP"],
    ["37379766000724", "DELICIAS DA OCI LTDA", "2026-08-25", "Supermercados", "AP", "MACAPA", "HILDEMAR MAIA, 2626 - BURITIZAL", "9699999999", "https://www.google.com/maps/search/?api=1&query=DELICIAS%20DA%20OCI%20LTDA%20MACAPA%20AP"],
    ["68886658000186", "ATENA LTDA", "2026-08-30", "Holdings de Instituições Não-Financeiras", "AP", "MACAPA", "CANDIDO MENDES, 1420 - CENTRAL", "9691660945", "https://www.google.com/maps/search/?api=1&query=ATENA%20LTDA%20MACAPA%20AP"]
]

df = pd.DataFrame(data, columns=["CNPJ", "Razao Social", "Data Abertura", "Segmento", "UF", "Cidade", "Endereco", "Telefone", "Maps"])
df["Status"] = "Pendente"

# 2. Barra Lateral - Filtros Dinâmicos
st.sidebar.header("🎯 Filtros de Prospecção")

segmentos = ["Todos"] + sorted(list(df["Segmento"].dropna().unique()))
seg_selecionado = st.sidebar.selectbox("Segmento / Nicho:", segmentos)

ufs = ["Todos"] + sorted(list(df["UF"].dropna().unique()))
uf_selecionada = st.sidebar.selectbox("Estado (UF):", ufs)

if uf_selecionada != "Todos":
    cidades = ["Todas"] + sorted(list(df[df["UF"] == uf_selecionada]["Cidade"].dropna().unique()))
else:
    cidades = ["Todas"] + sorted(list(df["Cidade"].dropna().unique()))
cidade_selecionada = st.sidebar.selectbox("Cidade:", cidades)

status_opcoes = ["Todos", "Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"]
status_selecionado = st.sidebar.selectbox("Status do Lead:", status_opcoes)

# Aplicar Filtros
df_filtered = df.copy()
if seg_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Segmento"] == seg_selecionado]
if uf_selecionada != "Todos":
    df_filtered = df_filtered[df_filtered["UF"] == uf_selecionada]
if cidade_selecionada != "Todos":
    df_filtered = df_filtered[df_filtered["Cidade"] == cidade_selecionada]
if status_selecionado != "Todos":
    df_filtered = df_filtered[df_filtered["Status"] == status_selecionado]

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Leads Exibidos", len(df_filtered))
col2.metric("Pendentes", len(df_filtered[df_filtered["Status"] == "Pendente"]))
col3.metric("LPs Geradas", len(df_filtered[df_filtered["Status"] == "LP Gerada"]))
col4.metric("Vendas Fechadas", len(df_filtered[df_filtered["Status"] == "Finalizado Positivo"]))

st.divider()

# Exibição detalhada de cada lead
st.subheader("📋 Lista de Empresas")

for idx, row in df_filtered.iterrows():
    razao = row["Razao Social"]
    segmento = row["Segmento"]
    cidade = row["Cidade"]
    uf = row["UF"]
    
    with st.expander(f"🏢 **{razao}** — {segmento} ({cidade}/{uf})"):
        c1, c2, c3 = st.columns([2, 2, 1.5])
        
        with c1:
            st.markdown(f"**CNPJ:** {row['CNPJ']}")
            st.markdown(f"**Data de Abertura:** {row['Data Abertura']}")
            st.markdown(f"**Endereço:** {row['Endereco']}")
            tel = row['Telefone'] if row['Telefone'] != "" else "Não informado"
            st.markdown(f"**Telefone/WhatsApp:** {tel}")
            
        with c2:
            st.markdown(f"**Status Atual:** `{row['Status']}`")
            
            nome_busca = razao.replace(' ', '+')
            cidade_busca = f"{cidade}+{uf}".replace(' ', '+')
            url_google = f"https://www.google.com/search?q={nome_busca}+{cidade_busca}"
            url_instagram = f"https://www.google.com/search?q=site:instagram.com+{nome_busca}+{cidade_busca}"
            
            if row["Maps"]:
                st.markdown(f"📍 [Ver no Google Maps]({row['Maps']})")
            st.markdown(f"🔍 [Pesquisar Empresa no Google]({url_google})")
            st.markdown(f"📸 [Buscar Instagram da Empresa]({url_instagram})")

        with c3:
            st.markdown("### Ações")
            novo_status = st.selectbox(
                "Atualizar Status:",
                ["Pendente", "Em Análise", "LP Gerada", "Proposta Enviada", "Finalizado Positivo", "Finalizado Negativo"],
                index=0,
                key=f"status_{idx}"
            )
            df.at[idx, "Status"] = novo_status
            
            if st.button("🚀 Gerar Landing Page", key=f"btn_lp_{idx}"):
                st.info(f"Gerando LP para {razao}...")
