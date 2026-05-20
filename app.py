import streamlit as st
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

st.markdown("""
<style>
.main { background: #F4F8FF; }
.block-container { padding-top: 1rem; padding-left: 1.4rem; padding-right: 1.4rem; padding-bottom: 3rem; }
h1, h2, h3 { color: #071B45; font-weight: 900; letter-spacing: -0.02rem; }

.top-shell {
    background: linear-gradient(135deg, #071B45 0%, #0B3A75 52%, #155EEF 100%);
    padding: 24px 26px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 18px 38px rgba(7,27,69,.22);
    margin-bottom: 18px;
}
.top-title {
    font-size: 2.15rem;
    font-weight: 950;
    line-height: 1.05;
}
.top-subtitle {
    color: #D9E6FF;
    font-size: .98rem;
    margin-top: 8px;
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
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #D7E6FA;
    border-radius: 22px;
    padding: 18px 20px;
    min-height: 126px;
    box-shadow: 0 10px 24px rgba(11,58,117,.08);
}
.kpi-label {
    color: #667085;
    font-size: .78rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: .055rem;
}
.kpi-value {
    color: #071B45;
    font-size: 2rem;
    font-weight: 950;
    margin-top: 8px;
}
.kpi-sub {
    color: #667085;
    font-size: .82rem;
    margin-top: 5px;
}
.kpi-good .kpi-value { color: #027A48; }
.kpi-bad .kpi-value { color: #D92D20; }
.kpi-blue .kpi-value { color: #155EEF; }

.insight-card {
    background: linear-gradient(90deg, #EAF2FF 0%, #FFFFFF 100%);
    border-left: 7px solid #155EEF;
    border-radius: 18px;
    padding: 16px 18px;
    margin: 10px 0 18px 0;
    box-shadow: 0 6px 18px rgba(11,58,117,.06);
}
.section-card {
    background: white;
    border: 1px solid #D7E6FA;
    border-radius: 22px;
    padding: 16px;
    box-shadow: 0 8px 22px rgba(11,58,117,.07);
}
.small-note {
    font-size: .85rem;
    color: #667085;
}
[data-testid="stTabs"] button {
    color: #0B3A75;
    font-weight: 800;
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
    "eficiencia_media": "Eficiência média",
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
    "ns": "NS",
    "% dentro se reduzir 1d": "% dentro se reduzir 1d",
    "% dentro se reduzir 2d": "% dentro se reduzir 2d",
    "% dentro se reduzir 3d": "% dentro se reduzir 3d",
    "% dentro_do_prazo_oferta": "% dentro do prazo oferta",
}

def fmt_num(x, dec=0):
    try:
        if pd.isna(x):
            return "0"
        return f"{float(x):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)

def fmt_pct(x):
    try:
        if pd.isna(x):
            return "0,0%"
        x = float(x)
        value = x if abs(x) > 1.5 else x * 100
        return f"{value:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(x)

def kpi(label, value, sub="", kind="blue"):
    cls = "kpi-card"
    if kind == "good":
        cls += " kpi-good"
    elif kind == "bad":
        cls += " kpi-bad"
    else:
        cls += " kpi-blue"
    st.markdown(f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

def normalize_columns(df):
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    return out

def find_excel_file():
    base = Path.cwd()
    preferred = [
        "MODAL REALIZADO_Dados completos.xlsx",
        "dashboard_base_com_geografia.xlsx",
    ]
    for name in preferred:
        p = base / name
        if p.exists() and p.is_file():
            return p

    for pattern in ["*.xlsx", "*.xlsm", "*.xls", "*.csv"]:
        files = [p for p in base.glob(pattern) if p.is_file()]
        if files:
            return files[0]
    return None

@st.cache_data(show_spinner=False)
def load_excel_path(path_str):
    path = Path(path_str)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    xls = pd.ExcelFile(path)
    sheet = "Base_Filtrada" if "Base_Filtrada" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(path, sheet_name=sheet)

@st.cache_data(show_spinner=False)
def load_excel_upload(uploaded):
    if uploaded.name.endswith('.csv'):
        return pd.read_csv(uploaded, sep=None, engine="python", encoding="utf-8-sig")
    xls = pd.ExcelFile(uploaded)
    sheet = "Base_Filtrada" if "Base_Filtrada" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(uploaded, sheet_name=sheet)

# =========================
# NOVA FUNÇÃO DE PREPARAÇÃO (ETL AUTOMATIZADO)
# =========================
def prep_data(df_raw):
    df = normalize_columns(df_raw)

    # 1. Mapeamento de Colunas da Base Bruta
    rename_map = {
        'data entrega prevista cliente': 'data_entrega_prevista',
        'data finalização': 'data_entrega_realizada',
        'pedido': 'pedido_gemco'
    }
    df = df.rename(columns=rename_map)

    # 2. Conversão de Datas
    date_cols = ['data_libfat', 'data_entrega_prevista', 'data_entrega_realizada']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.normalize()

    # 3. Cálculo de Lead Time (Dias entre Faturamento e Entrega)
    data_base = df.get('data_libfat', pd.Series(pd.NaT, index=df.index))
    
    if 'data_entrega_prevista' in df.columns:
        df['prazo_cliente'] = (df['data_entrega_prevista'] - data_base).dt.days
    else:
        df['prazo_cliente'] = np.nan

    if 'data_entrega_realizada' in df.columns:
        df['realizado_cliente'] = (df['data_entrega_realizada'] - data_base).dt.days
    else:
        df['realizado_cliente'] = np.nan

    # 4. Tratamento do Modal
    if "modal transp" in df.columns:
        src = df["modal transp"].astype(str).str.upper()
        df["modal"] = np.select(
            [
                src.str.contains("COURIER|COURRIER", na=False),
                src.str.contains("RODO|RODOV", na=False),
                src.str.contains("MICRO", na=False),
            ],
            ["COURIER", "RODO", "MICRO"],
            default="OUTROS",
        )
    elif "modal" not in df.columns:
        df["modal"] = "OUTROS"

    # 5. Criação de Colunas de Status e KPIs (Lógica Reconstruída)
    df['prazo_cliente'] = pd.to_numeric(df['prazo_cliente'], errors="coerce")
    df['realizado_cliente'] = pd.to_numeric(df['realizado_cliente'], errors="coerce")

    conditions = [
        df["realizado_cliente"] < df["prazo_cliente"],
        df["realizado_cliente"] == df["prazo_cliente"],
        df["realizado_cliente"] > df["prazo_cliente"],
    ]
    df["status_sla"] = np.select(conditions, ["Antecipado", "No Prazo", "Atrasado"], default="Indefinido")

    df["aux_antecipado"] = (df["status_sla"] == "Antecipado").astype(int)
    df["aux_no_prazo"] = (df["status_sla"] == "No Prazo").astype(int)
    df["aux_atrasado"] = (df["status_sla"] == "Atrasado").astype(int)

    df["oportunidade"] = (df["prazo_cliente"] - df["realizado_cliente"]).clip(lower=0)
    df["atraso_dias"] = (df["realizado_cliente"] - df["prazo_cliente"]).clip(lower=0)
    df["gap_prazo"] = df["prazo_cliente"] - df["realizado_cliente"]
    df["eficiencia_entrega"] = np.where(df["prazo_cliente"] > 0, df["realizado_cliente"] / df["prazo_cliente"], np.nan)

    # 6. Preenchimento de Dimensões e Normalização
    defaults = {
        "geografia_comercial": "N/A", "uf cliente": "N/A", "cidade cliente": "N/A",
        "localizacao_comercial": "N/A", "ecc": "N/A", "cd faturamento": "N/A",
        "cd responsavel": "N/A", "transportador (grupo)": "N/A", "transportador": "N/A",
        "situacao": "N/A", "cep_cliente": "N/A", "mes": "N/A"
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default).astype(str)

    # 7. CEP e Mês
    if 'data_libfat' in df.columns:
        df['mes'] = df['data_libfat'].dt.to_period("M").astype(str)
    
    if "cep_cliente" in df.columns:
        cep = df["cep_cliente"].astype(str).str.replace(r"\D", "", regex=True)
        df["cep_prefixo3"] = cep.str[:3].replace("", "N/A")
        df["cep_prefixo5"] = cep.str[:5].replace("", "N/A")

    if "pedido_gemco" not in df.columns:
        df["pedido_gemco"] = np.arange(len(df)) + 1

    return df

def filter_one_click(label, col, df):
    values = sorted([v for v in df[col].dropna().astype(str).unique() if v and v.lower() != "nan"])
    return st.selectbox(label, ["TODOS"] + values)

def apply_filter(df, col, value):
    if value == "TODOS":
        return df
    return df[df[col].astype(str) == value]

def agg_metrics(df, group_cols):
    if isinstance(group_cols, str):
        group_cols = [group_cols]

    g = df.groupby(group_cols, dropna=False).agg(
        pedidos=("pedido_gemco", "nunique"),
        antecipados=("aux_antecipado", "sum"),
        no_prazo=("aux_no_prazo", "sum"),
        atrasados=("aux_atrasado", "sum"),
        oportunidade=("oportunidade", "sum"),
        atraso_total=("atraso_dias", "sum"),
        media_ofertado=("prazo_cliente", "mean"),
        media_realizado=("realizado_cliente", "mean"),
        p80_realizado=("realizado_cliente", lambda x: np.nanpercentile(x.dropna(), 80) if len(x.dropna()) else np.nan),
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
    g["score_prioridade"] = (
        g["% antecipado"].fillna(0) * 35 +
        g["ns"].fillna(0) * 25 +
        np.log1p(g["oportunidade"].fillna(0)) * 8 +
        g["reducao_media_potencial"].fillna(0) * 16 -
        g["% atrasado"].fillna(0) * 25
    )
    g["classe_acao"] = np.select(
        [
            (g["pedidos"] >= 100) & (g["% antecipado"] >= .85) & (g["ns"] >= .95),
            (g["pedidos"] >= 100) & (g["% antecipado"] >= .70) & (g["reducao_media_potencial"] >= 2),
            (g["pedidos"] >= 50) & (g["ns"] >= .95) & (g["reducao_media_potencial"] >= 1),
            (g["% atrasado"] >= .12),
        ],
        ["Redução agressiva", "Atacar agora", "Testar redução", "Risco operacional"],
        default="Monitorar",
    )
    return g.sort_values(["score_prioridade", "oportunidade"], ascending=False)

def prepare_display(df):
    out = df.copy()
    out = out.rename(columns={c: DISPLAY_NAMES.get(c, c) for c in out.columns})
    for c in out.columns:
        if str(c).startswith("%") or str(c).lower() == "ns" or "eficiência" in str(c).lower():
            out[c] = pd.to_numeric(out[c], errors="coerce") * 100
    return out

def style_table(df):
    view = prepare_display(df)

    def background_performance(v):
        try:
            v = float(v)
        except Exception:
            return ""
        if v >= 99:
            return "background-color: #D1FADF; color: #027A48; font-weight: 900"
        if v >= 95:
            return "background-color: #EAF2FF; color: #155EEF; font-weight: 800"
        if v >= 85:
            return "background-color: #FEF0C7; color: #B54708; font-weight: 800"
        return "background-color: #FEE4E2; color: #B42318; font-weight: 800"

    def is_integer_like(series):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty:
            return False
        return np.all(np.isclose(s, np.round(s)))

    pct_cols = [c for c in view.columns if str(c).startswith("%") or str(c).lower() == "ns"]
    numeric_cols = [c for c in view.columns if c not in pct_cols and pd.api.types.is_numeric_dtype(view[c])]

    count_cols = {
        "Pedidos", "Antecipados", "No prazo", "Atrasados", "Atraso total", "Oportunidade"
    }
    id_cols = {
        "Pedido", "CD faturamento", "CD Faturamento", "CD responsável", "CD Responsável", "CEP", "CEP3", "CEP5"
    }

    fmt = {c: "{:.1f}%" for c in pct_cols}

    for c in numeric_cols:
        if c in id_cols:
            fmt[c] = "{:.0f}"
        elif c in count_cols or is_integer_like(view[c]):
            fmt[c] = "{:,.0f}"
        else:
            fmt[c] = "{:,.1f}"

    styler = view.style.format(fmt, decimal=",", thousands=".")

    for c in pct_cols:
        if c in view.columns:
            styler = styler.map(background_performance, subset=[c])

    if "Classe ação" in view.columns:
        def color_action(v):
            if v == "Redução agressiva":
                return "background-color:#D1FADF;color:#027A48;font-weight:900"
            if v == "Atacar agora":
                return "background-color:#EAF2FF;color:#155EEF;font-weight:900"
            if v == "Testar redução":
                return "background-color:#FEF0C7;color:#B54708;font-weight:900"
            if v == "Risco operacional":
                return "background-color:#FEE4E2;color:#B42318;font-weight:900"
            return ""
        styler = styler.map(color_action, subset=["Classe ação"])

    return styler


def format_dataframe_values(df):
    view = prepare_display(df)
    out = view.copy()

    pct_cols = [c for c in out.columns if str(c).startswith("%") or str(c).lower() == "ns"]
    id_cols = {"Pedido", "CD faturamento", "CD Faturamento", "CD responsável", "CD Responsável", "CEP", "CEP3", "CEP5"}

    def is_integer_like(series):
        s = pd.to_numeric(series, errors="coerce").dropna()
        if s.empty:
            return False
        return np.all(np.isclose(s, np.round(s)))

    for c in out.columns:
        if c in pct_cols:
            out[c] = pd.to_numeric(out[c], errors="coerce").map(
                lambda x: "" if pd.isna(x) else f"{x:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        elif pd.api.types.is_numeric_dtype(out[c]):
            if c in id_cols:
                out[c] = pd.to_numeric(out[c], errors="coerce").map(lambda x: "" if pd.isna(x) else f"{x:.0f}")
            elif is_integer_like(out[c]):
                out[c] = pd.to_numeric(out[c], errors="coerce").map(
                    lambda x: "" if pd.isna(x) else f"{x:,.0f}".replace(",", ".")
                )
            else:
                out[c] = pd.to_numeric(out[c], errors="coerce").map(
                    lambda x: "" if pd.isna(x) else f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )
    return out

def bar(df, x, y, title, color=None, orientation="v", height=430, text=None):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        text=text,
        orientation=orientation,
        title=title,
        color_discrete_map={
            "Redução agressiva": GREEN,
            "Atacar agora": BLUE,
            "Testar redução": YELLOW,
            "Risco operacional": RED,
            "Monitorar": GRAY,
            "COURIER": BLUE,
            "RODO": BLUE_DARK,
            "MICRO": CYAN,
            "OUTROS": GRAY,
        },
        color_discrete_sequence=[BLUE, CYAN, BLUE_DARK, GREEN, YELLOW, RED],
    )
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=PRIMARY,
        title_font_color=PRIMARY,
        title_font_size=20,
        height=height,
        margin=dict(l=20, r=20, t=58, b=20),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#E5EEF9")
    fig.update_yaxes(gridcolor="#E5EEF9")
    if isinstance(x, str) and (x.startswith("%") or x == "ns"):
        fig.update_xaxes(tickformat=".0%")
    if isinstance(y, str) and (y.startswith("%") or y == "ns"):
        fig.update_yaxes(tickformat=".0%")
    return fig

def line(df, x, y, title, color=None, height=420):
    fig = px.line(
        df, x=x, y=y, color=color, markers=True, title=title,
        color_discrete_sequence=[BLUE, CYAN, GREEN, YELLOW, RED, BLUE_DARK]
    )
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color=PRIMARY,
        title_font_color=PRIMARY,
        height=height,
        margin=dict(l=20, r=20, t=58, b=20),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#E5EEF9")
    fig.update_yaxes(gridcolor="#E5EEF9")
    if isinstance(y, str) and (y.startswith("%") or y == "ns"):
        fig.update_yaxes(tickformat=".0%")
    return fig

# =========================
# LOAD ATUALIZADO
# =========================
uploaded = st.file_uploader("Carregar planilha Bruta (Excel ou CSV)", type=["xlsx", "xlsm", "xls", "csv"])
try:
    if uploaded is not None:
        raw = load_excel_upload(uploaded)
        source_name = uploaded.name
    else:
        excel_path = find_excel_file()
        if excel_path is None:
            st.error("Não encontrei nenhuma planilha na pasta. Envie o arquivo bruto pelo botão acima.")
            st.stop()
        raw = load_excel_path(str(excel_path))
        source_name = excel_path.name
except Exception as e:
    st.error("Não consegui abrir a planilha. Verifique o formato do arquivo.")
    st.code(str(e))
    st.stop()

# Aplica a preparação que agora faz o ETL completo
df_all = prep_data(raw)


# =========================
# HEADER
# =========================
st.markdown(f"""
<div class="top-shell">
    <div class="top-title">Last Mile SLA Intelligence</div>
    <div class="top-subtitle">Painel operacional para redução de prazo cliente por Geografia, Modal, ECC, CDs, Localização, Transportador, Cidade e CEP.</div>
    <div style="margin-top:14px">
        <span class="badge">Fonte: {source_name}</span>
        <span class="badge">NS = Antecipado + No Prazo</span>
        <span class="badge">Foco: redução de prazo com baixo risco</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# FILTERS
# =========================
f0, f1, f2, f3, f4 = st.columns([1.4, 1, 1, 1, 1])
with f0:
    busca = st.text_input("Busca rápida", placeholder="Cidade, CEP, ECC, CD, localização ou transportador")
with f1:
    geografia = filter_one_click("Geografia", "geografia_comercial", df_all)
with f2:
    modal = filter_one_click("Modal", "modal", df_all)
with f3:
    uf = filter_one_click("UF", "uf cliente", df_all)
with f4:
    situacao = filter_one_click("Situação", "situacao", df_all)

f5, f6, f7, f8 = st.columns([1.2, 1.2, 1.2, 1])
with f5:
    ecc = filter_one_click("ECC", "ecc", df_all)
with f6:
    cd_faturamento = filter_one_click("CD faturamento", "cd faturamento", df_all)
with f7:
    cd_responsavel = filter_one_click("CD responsável", "cd responsavel", df_all)
with f8:
    periodo = filter_one_click("Período", "mes", df_all)

f9, f10, f11 = st.columns([1.2, 1.2, 1.2])
with f9:
    localizacao = filter_one_click("Localização comercial", "localizacao_comercial", df_all)
with f10:
    transportador = filter_one_click("Transportador (grupo)", "transportador (grupo)", df_all)
with f11:
    cidade = filter_one_click("Cidade", "cidade cliente", df_all)

min_volume = st.slider("Volume mínimo para rankings", 1, 1000, 50, step=10)

df = df_all.copy()
for col, val in [
    ("geografia_comercial", geografia),
    ("modal", modal),
    ("uf cliente", uf),
    ("situacao", situacao),
    ("ecc", ecc),
    ("cd faturamento", cd_faturamento),
    ("cd responsavel", cd_responsavel),
    ("localizacao_comercial", localizacao),
    ("transportador (grupo)", transportador),
    ("cidade cliente", cidade),
    ("mes", periodo),
]:
    df = apply_filter(df, col, val)

if busca:
    mask = (
        df["cidade cliente"].str.contains(busca, case=False, na=False) |
        df["localizacao_comercial"].str.contains(busca, case=False, na=False) |
        df["transportador (grupo)"].str.contains(busca, case=False, na=False) |
        df["geografia_comercial"].str.contains(busca, case=False, na=False) |
        df["ecc"].str.contains(busca, case=False, na=False) |
        df["cd faturamento"].str.contains(busca, case=False, na=False) |
        df["cd responsavel"].str.contains(busca, case=False, na=False) |
        df["cep_cliente"].str.contains(busca, case=False, na=False) |
        df["cep_prefixo5"].str.contains(busca, case=False, na=False) |
        df["cep_prefixo3"].str.contains(busca, case=False, na=False)
    )
    df = df[mask]

if df.empty:
    st.warning("Nenhum dado encontrado com os filtros atuais.")
    st.stop()

# =========================
# KPIS
# =========================
pedidos = df["pedido_gemco"].nunique()
antecipados = df["aux_antecipado"].sum()
no_prazo = df["aux_no_prazo"].sum()
atrasados = df["aux_atrasado"].sum()
pct_ant = antecipados / max(pedidos, 1)
pct_prazo = no_prazo / max(pedidos, 1)
pct_atr = atrasados / max(pedidos, 1)
ns = (antecipados + no_prazo) / max(pedidos, 1)
op_total = df["oportunidade"].sum()
prazo_m = df["prazo_cliente"].mean()
real_m = df["realizado_cliente"].mean()
gap_m = df["gap_prazo"].mean()
p80 = np.nanpercentile(df["realizado_cliente"].dropna(), 80) if df["realizado_cliente"].notna().any() else np.nan

a,b,c,d,e,f = st.columns(6)
with a: kpi("Pedidos", fmt_num(pedidos), "Pedidos únicos filtrados", "blue")
with b: kpi("NS geral", fmt_pct(ns), "Antecipado + no prazo", "good" if ns >= .95 else "bad" if ns < .85 else "blue")
with c: kpi("% antecipado", fmt_pct(pct_ant), "Principal alavanca de redução", "good" if pct_ant >= .70 else "blue")
with d: kpi("% atraso", fmt_pct(pct_atr), "Risco operacional", "bad" if pct_atr >= .10 else "good")
with e: kpi("Prazo ofertado", f"{fmt_num(prazo_m,1)}d", "Média cliente", "blue")
with f: kpi("Realizado", f"{fmt_num(real_m,1)}d", "Média real", "blue")

g,h,i,j = st.columns(4)
with g: kpi("Oportunidade", f"{fmt_num(op_total)} dias", "Soma de dias antecipados", "good")
with h: kpi("Gap médio", f"{fmt_num(gap_m,1)}d", "Ofertado - realizado", "blue")
with i: kpi("P80 realizado", f"{fmt_num(p80,1)}d", "Base para SLA sugerido", "blue")
with j: kpi("Atrasos", fmt_num(atrasados), "Pedidos fora do prazo", "bad" if atrasados > 0 else "good")

# Insight
rank_loc = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial"])
rank_loc = rank_loc[rank_loc["pedidos"] >= min_volume]
if not rank_loc.empty:
    r = rank_loc.iloc[0]
    st.markdown(f"""
    <div class="insight-card">
        <b>Melhor alvo operacional:</b> <b>{r['localizacao_comercial']}</b> na geografia <b>{r['geografia_comercial']}</b>,
        modal <b>{r['modal']}</b>, com <b>{fmt_num(r['pedidos'])}</b> pedidos,
        <b>{fmt_pct(r['% antecipado'])}</b> antecipado, <b>{fmt_pct(r['ns'])}</b> NS e
        <b>{fmt_num(r['oportunidade'])} dias</b> de oportunidade. Ação sugerida: <b>{r['classe_acao']}</b>.
    </div>
    """, unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📌 Executivo",
    "🌎 Geografia",
    "🎯 SLA sugerido",
    "⏱️ Prazo x Realizado",
    "🚚 Transportador",
    "📍 CEP / Cidade",
    "🧾 Base"
])

with tab1:
    c1, c2 = st.columns([1.1, 1])
    with c1:
        top = rank_loc.head(15)
        if not top.empty:
            st.plotly_chart(
                bar(top.sort_values("oportunidade"), "oportunidade", "localizacao_comercial",
                    "Top Localizações por oportunidade", color="classe_acao", orientation="h", height=560),
                use_container_width=True
            )
    with c2:
        status = pd.DataFrame({
            "Status": ["Antecipado", "No Prazo", "Atrasado"],
            "Pedidos": [antecipados, no_prazo, atrasados],
        })
        fig = px.pie(
            status,
            names="Status",
            values="Pedidos",
            hole=.54,
            title="Composição do NS",
            color="Status",
            color_discrete_map={"Antecipado": CYAN, "No Prazo": GREEN, "Atrasado": RED},
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(paper_bgcolor="white", title_font_color=PRIMARY, height=360, margin=dict(l=20,r=20,t=55,b=20))
        st.plotly_chart(fig, use_container_width=True)

        modal_rank = agg_metrics(df, ["modal", "ecc", "cd faturamento", "cd responsavel"])
        st.dataframe(style_table(modal_rank[["modal","pedidos","% antecipado","% no prazo","% atrasado","ns","oportunidade","media_ofertado","media_realizado","classe_acao"]]), use_container_width=True)

    periodo_df = agg_metrics(df, ["mes", "modal"])
    if not periodo_df.empty:
        st.plotly_chart(line(periodo_df, "mes", "ns", "Evolução do NS por Modal", color="modal", height=430), use_container_width=True)

with tab2:
    st.subheader("Análise por Geografia Comercial")
    geo = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel"])
    geo = geo[geo["pedidos"] >= min_volume]
    st.dataframe(style_table(geo.head(200)), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar(geo.head(20).sort_values("ns"), "ns", "geografia_comercial",
                            "NS por Geografia", color="modal", orientation="h", height=600), use_container_width=True)
    with c2:
        st.plotly_chart(bar(geo.head(20).sort_values("oportunidade"), "oportunidade", "geografia_comercial",
                            "Oportunidade por Geografia", color="modal", orientation="h", height=600), use_container_width=True)

    st.subheader("Geografia x Localização")
    gl = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial"])
    gl = gl[gl["pedidos"] >= min_volume]
    st.dataframe(style_table(gl.head(250)), use_container_width=True)

with tab3:
    st.subheader("Ranking de SLA sugerido e redução de prazo")
    dim_label = st.selectbox(
        "Dimensão",
        ["Geografia + Localização", "Geografia + Transportador", "Geografia + Cidade", "Localização + Transportador", "ECC + CDs", "CEP5", "CEP3", "Modal"]
    )
    dim_map = {
        "Geografia + Localização": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial"],
        "Geografia + Transportador": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "transportador (grupo)"],
        "Geografia + Cidade": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "cidade cliente"],
        "Localização + Transportador": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial", "transportador (grupo)"],
        "ECC + CDs": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel"],
        "CEP5": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "cep_prefixo5"],
        "CEP3": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "cep_prefixo3"],
        "Modal": ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel"],
    }
    rank = agg_metrics(df, dim_map[dim_label])
    rank = rank[rank["pedidos"] >= min_volume]
    cols = [c for c in rank.columns if c in dim_map[dim_label] + ["pedidos", "% antecipado", "% no prazo", "% atrasado", "ns", "oportunidade", "media_ofertado", "media_realizado", "p80_realizado", "sla_sugerido_p80", "reducao_media_potencial", "score_prioridade", "classe_acao"]]
    st.dataframe(style_table(rank[cols].head(300)), use_container_width=True)

    if not rank.empty:
        first_dim = dim_map[dim_label][-1]
        st.plotly_chart(bar(rank.head(25).sort_values("score_prioridade"), "score_prioridade", first_dim,
                            "Score de prioridade para redução", color="classe_acao", orientation="h", height=720),
                        use_container_width=True)

with tab4:
    st.subheader("Lead Time: prazo prometido x realizado")
    lead = df.groupby(["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial", "prazo_cliente", "realizado_cliente"], dropna=False).agg(
        pedidos=("pedido_gemco", "nunique"),
        oportunidade=("oportunidade", "sum"),
        antecipados=("aux_antecipado", "sum"),
        no_prazo=("aux_no_prazo", "sum"),
        atrasados=("aux_atrasado", "sum"),
    ).reset_index()
    lead["% antecipado"] = lead["antecipados"] / lead["pedidos"].replace(0, np.nan)
    lead["ns"] = (lead["antecipados"] + lead["no_prazo"]) / lead["pedidos"].replace(0, np.nan)

    heat = lead.pivot_table(index="prazo_cliente", columns="realizado_cliente", values="pedidos", aggfunc="sum", fill_value=0)
    fig = px.imshow(heat, aspect="auto", color_continuous_scale="Blues", title="Mapa de calor: prazo ofertado x prazo realizado")
    fig.update_layout(paper_bgcolor="white", title_font_color=PRIMARY, height=560, margin=dict(l=20,r=20,t=60,b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(style_table(lead.sort_values(["oportunidade", "pedidos"], ascending=False).head(300)), use_container_width=True)

    oferta = df.groupby(["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "prazo_cliente"], dropna=False).agg(
        pedidos=("pedido_gemco", "nunique"),
        antecipados=("aux_antecipado", "sum"),
        no_prazo=("aux_no_prazo", "sum"),
        media_realizado=("realizado_cliente", "mean"),
        p80_realizado=("realizado_cliente", lambda x: np.nanpercentile(x.dropna(), 80) if len(x.dropna()) else np.nan),
        oportunidade=("oportunidade", "sum"),
    ).reset_index()
    oferta["% antecipado"] = oferta["antecipados"] / oferta["pedidos"].replace(0, np.nan)
    oferta["ns"] = (oferta["antecipados"] + oferta["no_prazo"]) / oferta["pedidos"].replace(0, np.nan)
    st.plotly_chart(bar(oferta.sort_values("pedidos").tail(20), "pedidos", "prazo_cliente",
                        "Volume por prazo ofertado", color="modal", orientation="h", height=540),
                    use_container_width=True)

with tab5:
    st.subheader("Negociação por Transportador")
    lt = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "localizacao_comercial", "transportador (grupo)"])
    lt = lt[lt["pedidos"] >= min_volume]
    st.dataframe(style_table(lt.head(300)), use_container_width=True)
    if not lt.empty:
        st.plotly_chart(bar(lt.head(25).sort_values("oportunidade"), "oportunidade", "transportador (grupo)",
                            "Oportunidade por Transportador (grupo)", color="classe_acao", orientation="h", height=720),
                        use_container_width=True)

        fig = px.scatter(
            lt,
            x="ns",
            y="oportunidade",
            size="pedidos",
            color="classe_acao",
            hover_data=["geografia_comercial", "modal", "localizacao_comercial", "transportador (grupo)", "% antecipado", "% atrasado", "media_ofertado", "media_realizado"],
            title="Mapa de negociação: NS x oportunidade",
            color_discrete_map={
                "Redução agressiva": GREEN,
                "Atacar agora": BLUE,
                "Testar redução": YELLOW,
                "Risco operacional": RED,
                "Monitorar": GRAY,
            },
        )
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white", title_font_color=PRIMARY, height=560)
        fig.update_xaxes(tickformat=".0%", gridcolor="#E5EEF9")
        fig.update_yaxes(gridcolor="#E5EEF9")
        st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Cidade e CEP")
    cidade_df = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "uf cliente", "cidade cliente"])
    cidade_df = cidade_df[cidade_df["pedidos"] >= min_volume]
    st.dataframe(style_table(cidade_df.head(250)), use_container_width=True)
    if not cidade_df.empty:
        st.plotly_chart(bar(cidade_df.head(25).sort_values("score_prioridade"), "score_prioridade", "cidade cliente",
                            "Prioridade por Cidade", color="classe_acao", orientation="h", height=720), use_container_width=True)

    cep5 = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "uf cliente", "cidade cliente", "cep_prefixo5", "localizacao_comercial", "transportador (grupo)"])
    cep5 = cep5[cep5["pedidos"] >= max(5, min_volume // 3)]
    st.subheader("Top CEP5")
    st.dataframe(style_table(cep5.head(300)), use_container_width=True)
    if not cep5.empty:
        st.plotly_chart(bar(cep5.head(30).sort_values("oportunidade"), "oportunidade", "cep_prefixo5",
                            "Top CEP5 por oportunidade", color="classe_acao", orientation="h", height=760),
                        use_container_width=True)

    cep3 = agg_metrics(df, ["geografia_comercial", "modal", "ecc", "cd faturamento", "cd responsavel", "cep_prefixo3"])
    if not cep3.empty:
        matrix = cep3.pivot_table(index="cep_prefixo3", columns="geografia_comercial", values="oportunidade", aggfunc="sum", fill_value=0)
        fig = px.imshow(matrix, aspect="auto", color_continuous_scale="Blues", title="Densidade CEP3 x Geografia")
        fig.update_layout(paper_bgcolor="white", title_font_color=PRIMARY, height=650, margin=dict(l=20,r=20,t=60,b=20))
        st.plotly_chart(fig, use_container_width=True)

with tab7:
    st.subheader("Base filtrada")
    st.caption("A base abaixo já respeita todos os filtros aplicados no topo.")
    st.dataframe(format_dataframe_values(df), use_container_width=True)
    st.download_button(
        "Baixar base filtrada em CSV",
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name="base_filtrada_last_mile_geografia_ecc_cd.csv",
        mime="text/csv",
    )
