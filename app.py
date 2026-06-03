import streamlit as st
import base64
import csv
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Last Mile SLA Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# STYLE
# =========================
PRIMARY = "#071B45"
BLUE = "#155EEF"
BLUE_DARK = "#0B3A75"
BLUE_LIGHT = "#EAF2FF"
CYAN = "#19A7E0"
GREEN = "#12B76A"
GREEN_DARK = "#027A48"
YELLOW = "#F79009"
RED = "#F04438"
GRAY = "#667085"

APP_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
LOGO_PATH = APP_DIR / "assets" / "logo_magalog.png"

def image_to_base64(path):
    try:
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        return ""
    return ""

st.markdown("""
<style>
.main { background: #F4F8FF; }
.block-container { 
    padding-top: 2.2rem !important;
    padding-left: 1.4rem; 
    padding-right: 1.4rem; 
    padding-bottom: 3rem; 
}
h1, h2, h3 { color: #071B45; font-weight: 900; letter-spacing: -0.02rem; }

.top-shell {
    background: linear-gradient(135deg, #071B45 0%, #0B3A75 48%, #8FD8FF 100%);
    padding: 28px 28px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 18px 38px rgba(7,27,69,.22);
    margin-bottom: 22px;
}
.top-title {
    font-size: 2.15rem;
    font-weight: 950;
    line-height: 1.2;
}
.top-subtitle {
    color: #D9E6FF;
    font-size: .98rem;
    margin-top: 10px;
}
.badge {
    display: inline-block;
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.28);
    padding: 7px 12px;
    border-radius: 999px;
    color: #FFFFFF;
    font-weight: 800;
    font-size: .82rem;
    margin-right: 8px;
}

[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 950 !important;
    color: #071B45 !important;
}
[data-testid="stMetricLabel"] {
    color: #667085 !important;
    font-size: .78rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: .055rem !important;
}
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D7E6FA;
    border-radius: 22px;
    padding: 14px 18px !important;
    box-shadow: 0 10px 24px rgba(11,58,117,.08);
}

.insight-card {
    background: linear-gradient(90deg, #EAF2FF 0%, #FFFFFF 100%);
    border-left: 7px solid #155EEF;
    border-radius: 18px;
    padding: 16px 18px;
    margin: 10px 0 18px 0;
    box-shadow: 0 6px 18px rgba(11,58,117,.06);
}
[data-testid="stTabs"] {
    margin-top: 8px;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 10px;
    border-bottom: 0 !important;
    align-items: center;
    background: transparent;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    height: 38px;
    min-height: 38px;
    padding: 0 18px;
    border-radius: 10px 10px 0 0;
    border: 1px solid #D7E6FA;
    border-bottom: 0;
    background: #FFFFFF;
    color: #667085;
    font-weight: 900;
    box-shadow: 0 6px 16px rgba(11,58,117,.06);
    transition: all .18s ease-in-out;
}
[data-testid="stTabs"] [data-baseweb="tab"] p {
    color: inherit !important;
    font-weight: 900 !important;
    font-size: .88rem;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: #EAF2FF;
    color: #0B3A75;
    border-color: #9EC5FE;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #155EEF 0%, #0B3A75 100%) !important;
    color: #FFFFFF !important;
    border-color: #155EEF !important;
    box-shadow: 0 10px 24px rgba(21,94,239,.22);
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] p {
    color: #FFFFFF !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}
[data-testid="stDataFrame"] {
    border: 1px solid #D7E6FA;
    border-radius: 16px;
    overflow: hidden;
}
.stSelectbox label, .stTextInput label, .stSlider label {
    color: #071B45 !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# UTILITIES
# =========================
DISPLAY_NAMES = {
    "modal": "Modal",
    "geografia_comercial": "Geografia",
    "uf cliente": "UF",
    "cidade cliente": "Cidade",
    "localizacao_comercial": "Localização comercial",
    "ecc": "ECC",
    "cd faturamento": "CD faturamento",
    "cd responsavel": "CD responsável",
    "transportador (grupo)": "Transportador (grupo)",
    "transportador": "Transportador",
    "situacao": "Situação",
    "pedido_gemco": "Pedido",
    "pedidos": "Pedidos",
    "antecipados": "Antecipados",
    "no_prazo": "No prazo",
    "atrasados": "Atrasados",
    "oportunidade": "Oportunidade",
    "atraso_total": "Atraso total",
    "media_ofertado": "Média ofertada",
    "media_realizado": "Média realizada",
    "p80_realizado": "P80 realizado",
    "mediana_realizado": "Mediana realizada",
    "oportunidade_media": "Oportunidade média",
    "gap_medio": "Gap médio",
    "eficiencia_media": "Efência média",
    "sla_sugerido_p80": "SLA sugerido P80",
    "reducao_media_potencial": "Redução média potencial",
    "score_prioridade": "Score prioridade",
    "classe_acao": "Classe ação",
    "cep_cliente": "CEP",
    "cep_prefixo3": "CEP3",
    "cep_prefixo5": "CEP5",
    "prazo_cliente": "Prazo cliente",
    "realizado_cliente": "Realizado cliente",
    "% antecipado": "% antecipado",
    "% no prazo": "% no prazo",
    "% atrasado": "% atrasado",
    "ns": "NS"
}

def fmt_num(x, dec=0):
    try:
        if pd.isna(x): return "0"
        return f"{float(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception: return str(x)

def fmt_pct(x):
    try:
        if pd.isna(x): return "0,0%"
        x = float(x)
        value = x if abs(x) > 1.5 else x * 100
        return f"{value:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception: return str(x)

def normalize_columns(df):
    out = df.copy()
    out.columns = [str(c).strip().strip('"').strip().lower() for c in out.columns]
    return out

# =========================
# CARREGAMENTO GLOBAL COMPARTILHADO (EVITA MULTIPLICAÇÃO DE RAM POR ABA)
# =========================
@st.cache_resource(ttl=86400, show_spinner="Inicializando base de dados global na nuvem... Por favor, aguarde alguns segundos.")
def carregar_dados_globais_compartilhados(url):
    tipos_colunas = {
        'geografia_comercial': 'category', 'modal': 'category', 'modal transp': 'category',
        'uf cliente': 'category', 'situacao': 'category', 'ecc': 'category',
        'cd faturamento': 'category', 'cd responsavel': 'category',
        'localizacao_comercial': 'category', 'transportador (grupo)': 'category',
        'transportador': 'category', 'cidade cliente': 'category', 'cep_cliente': 'str'
    }
    
    lista_blocos = []
    # Processa o arquivo em chunks pequenos para blindar o motor do Pandas
    for bloco in pd.read_csv(url, sep=";", chunksize=45000, dtype=tipos_colunas, low_memory=False):
        bloco.columns = [str(c).strip().strip('"').strip().lower() for c in bloco.columns]
        colunas_uteis = [c for c in bloco.columns if c in [
            'geografia_comercial', 'modal', 'modal transp', 'uf cliente', 'cidade cliente',
            'localizacao_comercial', 'ecc', 'cd faturamento', 'cd responsavel',
            'transportador (grupo)', 'transportador', 'situacao', 'pedido_gemco', 'prazo_cliente', 'realizado_cliente', 'cep_cliente'
        ]]
        lista_blocos.append(bloco[colunas_uteis])
        
    df = pd.concat(lista_blocos, ignore_index=True)
    
    for c in ["prazo_cliente", "realizado_cliente"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(np.int8)
    return df

LINK_DO_MEU_CSV = "https://github.com/gabrielsmartins-creator/dashboard-sla/releases/download/v1.0/modal_realizado.csv"

try:
    raw = carregar_dados_globais_compartilhados(LINK_DO_MEU_CSV)
    source_name = "modal_realizado.csv (GitHub Cloud)"
except Exception as e:
    st.error("Erro crítico de conexão com a base de dados central.")
    st.code(str(e))
    st.stop()

# =========================
# TRATAMENTO DE ENGENHARIA DE ATRIBUTOS
# =========================
@st.cache_data(show_spinner=False)
def processar_malha_operacional(df_raw):
    df = df_raw.copy()
    if "modal" not in df.columns and "modal transp" in df.columns:
        src = df["modal transp"].astype(str).str.upper()
        df["modal"] = np.select(
            [src.str.contains("COURIER|COURRIER", na=False), src.str.contains("RODO", na=False), src.str.contains("MICRO", na=False)],
            ["COURIER", "RODO", "MICRO"], default="OUTROS"
        )
    df["modal"] = df["modal"].astype(str).str.upper().str.strip().replace({"COURRIER": "COURIER", "RODOVIARIO": "RODO", "RODOVIÁRIO": "RODO"})

    defaults = {
        "geografia_comercial": "N/A", "uf cliente": "N/A", "cidade cliente": "N/A", "localizacao_comercial": "N/A",
        "ecc": "N/A", "cd faturamento": "N/A", "cd responsavel": "N/A", "transportador (grupo)": "N/A",
        "transportador": "N/A", "situacao": "N/A", "cep_cliente": "N/A", "cep_prefixo3": "N/A", "cep_prefixo5": "N/A"
    }
    for col, default in defaults.items():
        if col not in df.columns: df[col] = default
        df[col] = df[col].fillna(default).astype(str)

    if "cep_cliente" in df.columns:
        cep = df["cep_cliente"].str.replace(r"\D", "", regex=True)
        df["cep_prefixo3"] = cep.str[:3].replace("", "N/A")
        df["cep_prefixo5"] = cep.str[:5].replace("", "N/A")

    if "pedido_gemco" not in df.columns:
        df["pedido_gemco"] = np.arange(len(df)) + 1

    df["aux_antecipado"] = (df["realizado_cliente"] < df["prazo_cliente"]).astype(np.int8)
    df["aux_no_prazo"] = (df["realizado_cliente"] == df["prazo_cliente"]).astype(np.int8)
    df["aux_atrasado"] = (df["realizado_cliente"] > df["prazo_cliente"]).astype(np.int8)
    
    df["oportunidade"] = (df["prazo_cliente"] - df["realizado_cliente"]).clip(lower=0)
    df["atraso_dias"] = (df["realizado_cliente"] - df["prazo_cliente"]).clip(lower=0)
    df["gap_prazo"] = df["prazo_cliente"] - df["realizado_cliente"]
    df["eficiencia_entrega"] = np.where(df["prazo_cliente"] > 0, df["realizado_cliente"] / df["prazo_cliente"], np.nan)
    return df

df_all = processar_malha_operacional(raw)

# =========================
# FILTROS DINÂMICOS
# =========================
def filter_one_click(label, col, df, key_suffix):
    values = sorted([v for v in df[col].dropna().astype(str).unique() if v and v.lower() != "nan"])
    return st.selectbox(label, ["TODOS"] + values, key=f"sel_{col}_{key_suffix}")

def apply_filter(df, col, value):
    return df if value == "TODOS" else df[df[col].astype(str) == value]

def prazo_ate_filter(label, col, df, key_suffix):
    valores = df[col]
    max_dias = valores.max() if len(valores) else 0
    if max_dias < 1: return "TODOS"
    opcoes = ["TODOS"] + [f"Até {i} dia" if i == 1 else f"Até {i} dias" for i in range(1, int(max_dias) + 1)]
    return st.selectbox(label, opcoes, key=f"prazo_{col}_{key_suffix}")

def apply_prazo_ate_filter(df, col, value):
    if value == "TODOS" or col not in df.columns: return df
    limite = int(str(value).replace("Até", "").replace("dias", "").replace("dia", "").strip())
    return df[df[col] <= limite]

# =========================
# AGREGAÇÕES DE PERFORMANCE
# =========================
def agg_metrics(df, group_cols):
    g = df.groupby(group_cols, dropna=False).agg(
        pedidos=("pedido_gemco", "nunique"),
        antecipados=("aux_antecipado", "sum"),
        no_prazo=("aux_no_prazo", "sum"),
        atrasados=("aux_atrasado", "sum"),
        oportunidade=("oportunidade", "sum"),
        atraso_total=("atraso_dias", "sum"),
        media_ofertado=("prazo_cliente", "mean"),
        media_realizado=("realizado_cliente", "mean"),
        p80_realizado=("realizado_cliente", lambda x: np.nanpercentile(x, 80) if len(x) else np.nan),
        mediana_realizado=("realizado_cliente", "median"),
        oportunidade_media=("oportunidade", "mean"),
        gap_medio=("gap_prazo", "mean"),
        eficiencia_media=("eficiencia_entrega", "mean"),
    ).reset_index()

    g["% antecipado"] = g["antecipados"] / g["pedidos"].replace(0, np.nan)
    g["% no prazo"] = g["no_prazo"] / g["pedidos"].replace(0, np.nan)
    g["% atrasado"] = g["atrasados"] / g["pedidos"].replace(0, np.nan)
    g["ns"] = (g["antecipados"] + g["no_prazo"]) / g["pedidos"].replace(0, np.nan)
    g["sla_sugerido_p80"] = np.ceil(g["p80_realizado"]).clip(lower=1)
    g["reducao_media_potencial"] = (g["media_ofertado"] - g["sla_sugerido_p80"]).clip(lower=0)
    g["score_prioridade"] = (g["% antecipado"].fillna(0) * 35 + g["ns"].fillna(0) * 25 + np.log1p(g["oportunidade"].fillna(0)) * 8 + g["reducao_media_potencial"].fillna(0) * 16 - g["% atrasado"].fillna(0) * 25)
    
    g["classe_acao"] = np.select(
        [
            (g["pedidos"] >= 100) & (g["% antecipado"] >= .85) & (g["ns"] >= .95),
            (g["pedidos"] >= 100) & (g["% antecipado"] >= .70) & (g["reducao_media_potencial"] >= 2),
            (g["pedidos"] >= 50) & (g["ns"] >= .95) & (g["reducao_media_potencial"] >= 1),
            (g["% atrasado"] >= .12),
        ],
        ["Redução agressiva", "Atacar agora", "Testar redução", "Risco operacional"], default="Monitorar"
    )
    return g.sort_values(["score_prioridade", "oportunidade"], ascending=False)

def style_table(df):
    view = df.copy()
    view = view.rename(columns={c: DISPLAY_NAMES.get(c, c) for c in view.columns})
    for c in view.columns:
        if str(c).startswith("%") or str(c).lower() == "ns" or "eficiência" in str(c).lower():
            view[c] = pd.to_numeric(view[c], errors="coerce") * 100

    pct_cols = [c for c in view.columns if str(c).startswith("%") or str(c).lower() == "ns"]
    numeric_cols = [c for c in view.columns if c not in pct_cols and pd.api.types.is_numeric_dtype(view[c])]
    fmt = {c: "{:.1f}%" for c in pct_cols}
    
    for c in numeric_cols:
        if c in {"Pedido", "CD faturamento", "CD Faturamento", "CD responsável", "CD Responsável", "CEP", "CEP3", "CEP5"}: fmt[c] = "{:.0f}"
        elif c in {"Pedidos", "Antecipados", "No prazo", "Atrasados", "Atraso total", "Oportunidade"}: fmt[c] = "{:,.0f}"
        else: fmt[c] = "{:,.1f}"

    styler = view.style.format(fmt, decimal=",", thousands=".")
    for c in pct_cols:
        if c in view.columns: styler = styler.map(lambda v: "background-color: #D1FADF; color: #027A48; font-weight: 900" if float(v) >= 99 else "background-color: #EAF2FF; color: #155EEF; font-weight: 800" if float(v) >= 95 else "background-color: #FEF0C7; color: #B54708; font-weight: 800" if float(v) >= 85 else "background-color: #FEE4E2; color: #B42318; font-weight: 800", subset=[c])
        
    if "Classe ação" in view.columns:
        styler = styler.map(lambda v: "background-color:#D1FADF;color:#027A48;font-weight:900" if v == "Redução agressiva" else "background-color:#EAF2FF;color:#155EEF;font-weight:900" if v == "Atacar agora" else "background-color:#FEF0C7;color:#B54708;font-weight:900" if v == "Testar redução" else "background-color:#FEE4E2;color:#B42318;font-weight:900" if v == "Risco operacional" else "", subset=["Classe ação"])
    return styler

# =========================
# INTERFACE DE USUÁRIO
# =========================
st.markdown(f"""
<div class="top-shell">
    <div style="display:flex; justify-content:space-between; align-items:center; gap:18px; flex-wrap:wrap;">
        <div>
            <div class="top-title">Last Mile SLA Intelligence</div>
            <div class="top-subtitle">Painel operacional para redução de prazo cliente por Geografia, Modal, ECC, CDs, Localização, Transportador, Cidade e CEP.</div>
            <div style="margin-top:14px">
                <span class="badge">Fonte: {source_name}</span>
                <span class="badge">NS = Antecipado + No Prazo</span>
                <span class="badge">Foco: dados globais otimizados anti-crash</span>
            </div>
        </div>
        <div><img src="data:image/png;base64,{image_to_base64(LOGO_PATH)}" style="max-height:58px; max-width:190px; object-fit:contain;" /></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Filtros operacionais completos reestabelecidos
f0, f1, f2, f3, f4 = st.columns([1.4, 1, 1, 1, 1])
with f0: busca = st.text_input("Busca rápida", placeholder="Cidade, CEP, ECC, CD, localização ou transportador", key="txt_busca_main")
with f1: geografia = filter_one_click("Geografia", "geografia_comercial", df_all, "main")
with f2: modal = filter_one_click("Modal", "modal", df_all, "main")
with f3: uf = filter_one_click("UF", "uf cliente", df_all, "main")
with f4: situacao = filter_one_click("Situação", "situacao", df_all, "main")

f5, f6, f7, f8 = st.columns([1.2, 1.2, 1.2, 1])
with f5: ecc = filter_one_click("ECC", "ecc", df_all, "main")
with f6: cd_faturamento = filter_one_click("CD faturamento", "cd faturamento", df_all, "main")
with f7: cd_responsavel = filter_one_click("CD responsável", "cd responsavel", df_all, "main")
with f8: prazo_ofertado = prazo_ate_filter("Prazo ofertado", "prazo_cliente", df_all, "main")

f9, f10, f11, f12 = st.columns([1.2, 1.2, 1.2, 1])
with f9: localizacao = filter_one_click("Localização comercial", "localizacao_comercial", df_all, "main")
with f10: transportador = filter_one_click("Transportador (grupo)", "transportador (grupo)", df_all, "main")
with f11: cidade = filter_one_click("Cidade", "cidade cliente", df_all, "main")
with f12: prazo_realizado = prazo_ate_filter("Prazo realizado", "realizado_cliente", df_all, "main")

min_volume = st.slider("Volume mínimo para rankings", 1, 1000, 50, step=10, key="sld_volume_main")

df = df_all
for col, val in [
    ("geografia_comercial", geografia), ("modal", modal), ("uf cliente", uf), ("situacao", situacao),
    ("ecc", ecc), ("cd faturamento", cd_faturamento), ("cd responsavel", cd_responsavel),
    ("localizacao_comercial", localizacao), ("transportador (grupo)", transportador), ("cidade cliente", cidade)
]:
    df = apply_filter(df, col, val)

df = apply_prazo_ate_filter(df, "prazo_cliente", prazo_ofertado)
df = apply_prazo_ate_filter(df, "realizado_cliente", prazo_realizado)

if busca:
    mask = (
        df["cidade cliente"].str.contains(busca, case=False, na=False) |
        df["localizacao_comercial"].str.contains(busca, case=False, na=False) |
        df["transportador (grupo)"].str.contains(busca, case=False, na=False) |
        df["geografia_comercial"].str.contains(busca, case=False, na=False) |
        df["ecc"].str.contains(busca, case=False, na=False) |
        df["cd faturamento"].str.contains(busca, case=False, na=False) |
        df["cd responsavel"].str.contains(busca, case=False, na=False) |
        df["cep_cliente"].str.contains(busca, case=False, na=False)
    )
    df = df[mask]

if df.empty:
    st.warning("Nenhum dado encontrado com os filtros atuais.")
    st.stop()

pedidos = df["pedido_gemco"].nunique()
antecipados = int(df["aux_antecipado"].sum())
no_prazo = int(df["aux_no_prazo"].sum())
atrasados = int(df["aux_atrasado"].sum())

with st.container():
    a, b, c, d, e, f = st.columns(6)
    a.metric("Pedidos", fmt_num(pedidos))
    b.metric("NS geral", fmt_pct((antecipados + no_prazo) / max(pedidos, 1)))
    c.metric("% antecipado", fmt_pct(antecipados / max(pedidos, 1)))
    d.metric("% atraso", fmt_pct(atrasados / max(pedidos, 1)))
    e.metric("Prazo ofertado", f"{fmt_num(df['prazo_cliente'].mean(),1)}d")
    f.metric("Realizado", f"{fmt_num(df['realizado_cliente'].mean(),1)}d")

# =========================
# AS 4 ABAS SOLICITADAS TOTALMENTE COMPLETA E DETALHADA
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "🌎 Geografia",
    "⏱️ Prazo x Realizado",
    "🚚 Transportador",
    "📍 CEP / Cidade"
])

with tab1:
    st.subheader("Análise Completa por Geografia Comercial")
    geo = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel"])
    st.dataframe(style_table(geo[geo["pedidos"] >= min_volume].head(250)), width="stretch")

    st.subheader("Geografia x Localização")
    gl = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial"])
    st.dataframe(style_table(gl[gl["pedidos"] >= min_volume].head(250)), width="stretch")

with tab2:
    st.subheader("Lead Time Histórico: Prazo Prometido Cliente x Realizado")
    lead = df.groupby(["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial", "prazo_cliente", "realizado_cliente"], dropna=False).agg(
        pedidos=("pedido_gemco", "nunique"),
        oportunidade=("oportunidade", "sum"),
        antecipados=("aux_antecipado", "sum"),
        no_prazo=("aux_no_prazo", "sum"),
        atrasados=("aux_atrasado", "sum"),
    ).reset_index()
    lead["% antecipado"] = lead["antecipados"] / lead["pedidos"].replace(0, np.nan)
    lead["ns"] = (lead["antecipados"] + lead["no_prazo"]) / lead["pedidos"].replace(0, np.nan)
    
    st.dataframe(style_table(lead.sort_values(["oportunidade", "pedidos"], ascending=False).head(250)), width="stretch")

with tab3:
    st.subheader("Negociação Completa por Transportador")
    lt = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial", "transportador (grupo)", "transportador"])
    st.dataframe(style_table(lt[lt["pedidos"] >= min_volume].head(250)), width="stretch")

with tab4:
    st.subheader("Análise de Malhas por Cidade")
    cidade_df = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "uf cliente", "cidade cliente"])
    st.dataframe(style_table(cidade_df[cidade_df["pedidos"] >= min_volume].head(250)), width="stretch")

    st.subheader("Análise de Micro-região (Top CEP5 e CEP3)")
    cep5 = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "uf cliente", "cidade cliente", "cep_prefixo5", "localizacao_comercial", "transportador (grupo)"])
    st.dataframe(style_table(cep5[cep5["pedidos"] >= max(5, min_volume // 3)].head(250)), width="stretch")
