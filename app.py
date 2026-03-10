import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
import json

# ===================== CONFIG =====================
st.set_page_config(
    page_title="HCP Intelligence — Equilibrium",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===================== CORES =====================
CP  = "#4B2D8F"
CP2 = "#6A42C2"
CO  = "#F47920"
CO2 = "#E05A00"
CG  = "#16A34A"
CB  = "#0284C7"

SEG_MED_CORES   = {"KOL": CO, "KOF": CP2, "HCP": CG, "": "#cccccc"}
SEG_INFLU_CORES = {"HCP": CG, "COF Micro": "#0891B2", "DOL Mid": "#9333EA",
                   "DOL Elite": "#BE185D", "KOF": CP2, "": "#cccccc"}
SEG_PRESC_CORES = {"HCP Tier 1": CO, "HCP Tier 2": CB, "HCP Tier 3": CG, "": "#cccccc"}

# ===================== CSS =====================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Open+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Open Sans', sans-serif;
    background-color: #F0EFF5;
}}
.main {{ background-color: #F0EFF5; }}
.block-container {{ padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }}

/* Header */
.dash-header {{
    background: linear-gradient(135deg, {CP} 0%, {CP2} 100%);
    padding: 14px 24px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    box-shadow: 0 2px 20px rgba(75,45,143,0.3);
}}
.dash-header h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: white;
    margin: 0;
}}
.dash-header small {{
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    font-weight: 300;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
.logo-q {{
    width: 38px; height: 38px; border-radius: 50%;
    background: {CO}; color: white;
    display: inline-flex; align-items: center; justify-content: center;
    font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 18px;
    margin-right: 10px; flex-shrink: 0;
}}

/* KPI Cards */
.kpi-card {{
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
    border: 1px solid #E2DCF0;
    box-shadow: 0 2px 16px rgba(75,45,143,0.08);
    position: relative;
    overflow: hidden;
}}
.kpi-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
}}
.kpi-c1::after {{ background: {CP}; }}
.kpi-c2::after {{ background: {CO}; }}
.kpi-c3::after {{ background: {CP2}; }}
.kpi-c4::after {{ background: {CB}; }}
.kpi-icon {{ font-size: 20px; margin-bottom: 6px; }}
.kpi-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px;
    color: #7A6FA0; margin-bottom: 4px;
}}
.kpi-value {{
    font-family: 'Montserrat', sans-serif;
    font-size: 26px; font-weight: 800;
    color: {CP}; line-height: 1;
}}
.kpi-sub {{ font-size: 11px; color: #7A6FA0; margin-top: 3px; }}

/* Seg Cards */
.seg-card {{
    background: #F7F5FB;
    border: 2px solid #E2DCF0;
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
}}
.seg-card-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; color: #7A6FA0;
}}
.seg-card-value {{
    font-family: 'Montserrat', sans-serif;
    font-size: 20px; font-weight: 800;
    line-height: 1.2;
}}
.seg-card-sub {{ font-size: 10px; color: #7A6FA0; }}

/* Section titles */
.section-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 13px; font-weight: 700;
    color: {CP}; margin-bottom: 4px;
}}
.section-sub {{
    font-size: 11px; color: #7A6FA0; margin-bottom: 10px;
}}

/* Card container */
.card {{
    background: white;
    border-radius: 14px;
    padding: 16px 18px;
    border: 1px solid #E2DCF0;
    box-shadow: 0 2px 16px rgba(75,45,143,0.08);
    margin-bottom: 14px;
}}

/* Tag badges */
.tag {{
    display: inline-block;
    padding: 2px 8px; border-radius: 5px;
    font-size: 10px; font-weight: 700;
    font-family: 'Montserrat', sans-serif;
}}
.tag-kol  {{ background: rgba(244,121,32,.12); color: {CO2}; }}
.tag-kof  {{ background: rgba(106,66,194,.12); color: {CP2}; }}
.tag-hcp  {{ background: rgba(22,163,74,.12);  color: {CG};  }}
.tag-sem  {{ background: rgba(150,150,150,.1); color: #bbb;  }}
.tag-tier1 {{ background: rgba(244,121,32,.12); color: {CO2}; }}
.tag-tier2 {{ background: rgba(2,132,199,.12);  color: {CB};  }}
.tag-tier3 {{ background: rgba(22,163,74,.12);  color: {CG};  }}

/* Completude */
.completude-row {{
    display: flex; align-items: center;
    gap: 10px; margin-bottom: 8px;
}}
.completude-name {{
    width: 80px; font-size: 11px;
    color: #7A6FA0; font-weight: 600;
}}
.completude-bar-bg {{
    flex: 1; background: #E2DCF0;
    border-radius: 4px; height: 7px; overflow: hidden;
}}
.completude-bar {{
    height: 7px; border-radius: 4px;
    background: linear-gradient(90deg, {CP}, {CO});
}}
.completude-pct {{
    width: 36px; text-align: right;
    font-size: 12px; font-weight: 700; color: {CP};
}}

/* Stmetric override */
[data-testid="stMetric"] {{ background: white; border-radius: 14px; padding: 16px; border: 1px solid #E2DCF0; }}
div[data-testid="stSelectbox"] label {{ font-size: 11px !important; color: #7A6FA0 !important; }}
</style>
""", unsafe_allow_html=True)


# ===================== CARREGAR DADOS =====================
@st.cache_data(ttl=300)
def carregar_google_sheets(sheet_url: str, aba: str):
    """Carrega dados de uma Google Sheets pública via CSV export."""
    try:
        # Extrai o ID da planilha da URL
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        # Busca as abas disponíveis primeiro
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba}"
        df = pd.read_csv(csv_url)
        return df, None
    except Exception as e:
        return None, str(e)


def normalizar_col(col):
    """Remove acentos, espaços e deixa minúsculo para matching."""
    import unicodedata
    col = str(col).strip()
    col = unicodedata.normalize('NFKD', col)
    col = ''.join(c for c in col if not unicodedata.combining(c))
    col = col.lower().replace(' ', '').replace('_', '').replace('-', '')
    return col


CMAP = {
    "uf":       ["ufmatricula", "uf"],
    "crm":      ["matricula", "crm"],
    "nome":     ["medico", "nutricionista", "nome", "profissional"],
    "seg":      ["segmentacao", "seg"],
    "segInflu": ["segmentacaoinfluencia", "seginfluencia", "seginflu"],
    "segPresc": ["segmentacaoprescricao", "segprescricao", "segpresc"],
    "nseg":     ["nseguidores", "seguidores", "followers"],
    "consulta": ["valorconsulta", "consulta"],
    "local":    ["localatendimento", "local"],
    "pacientes":["npacientes", "pacientes"],
    "esp1":     ["especialidade1", "especialidade"],
    "esp2":     ["especialidade2"],
    "temTel":   ["telefone1", "telefone"],
    "temCell":  ["celular1", "celular"],
    "temEmail": ["email1", "email"],
    "temEnd":   ["endereco"],
    "temInsta": ["enderecoredesocial", "instagram"],
    "cidade":   ["cidade", "municipio"],
}


def mapear_colunas(df):
    hdrs = list(df.columns)
    hn = [normalizar_col(h) for h in hdrs]
    c = {}
    for field, targets in CMAP.items():
        for t in targets:
            if normalizar_col(t) in hn:
                c[field] = hdrs[hn.index(normalizar_col(t))]
                break
    return c


def processar_df(df, is_nutri=False):
    c = mapear_colunas(df)

    def get(row, f):
        return str(row[c[f]]).strip() if f in c else ""

    def num(row, f):
        v = get(row, f)
        v = ''.join(ch for ch in v if ch.isdigit() or ch in '.,')
        v = v.replace(',', '.')
        try: return float(v)
        except: return 0.0

    def bool_val(row, f):
        v = get(row, f).lower()
        return v in ["sim", "s", "yes", "1", "true"]

    rows = []
    for i, row in df.iterrows():
        seg_raw = get(row, 'seg').upper()
        seg_influ = get(row, 'segInflu') if 'segInflu' in c else ''
        seg_presc = get(row, 'segPresc') if 'segPresc' in c else ''
        seg = seg_raw if seg_raw in ['KOL', 'KOF', 'HCP'] else ''
        if is_nutri and not seg_influ:
            seg_influ = seg_raw

        uf = get(row, 'uf').upper()[:2] if 'uf' in c else ''
        rows.append({
            "crm":      get(row, 'crm') or str(i+1),
            "nome":     get(row, 'nome') or f"Registro {i+1}",
            "uf":       uf or None,
            "cidade":   get(row, 'cidade') or None,
            "esp1":     get(row, 'esp1') or None,
            "esp2":     get(row, 'esp2') or None,
            "seg":      seg,
            "segInflu": seg_influ,
            "segPresc": seg_presc,
            "nseg":     num(row, 'nseg'),
            "consulta": num(row, 'consulta'),
            "pacientes":num(row, 'pacientes'),
            "local":    get(row, 'local'),
            "temTel":   bool(get(row, 'temTel')),
            "temCell":  bool(get(row, 'temCell')),
            "temEmail": bool(get(row, 'temEmail')),
            "temEnd":   bool(get(row, 'temEnd')),
            "temInsta": bool(get(row, 'temInsta')),
        })
    return pd.DataFrame(rows), c


# ===================== COMPONENTES VISUAIS =====================
def kpi_card(icon, label, value, sub, cls):
    st.markdown(f"""
    <div class="kpi-card {cls}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def seg_card(label, value, sub, cor):
    st.markdown(f"""
    <div class="seg-card">
        <div class="seg-card-label">{label}</div>
        <div class="seg-card-value" style="color:{cor}">{value:,}</div>
        <div class="seg-card-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def completude_bar(nome, pct):
    return f"""
    <div class="completude-row">
        <span class="completude-name">{nome}</span>
        <div class="completude-bar-bg">
            <div class="completude-bar" style="width:{pct}%"></div>
        </div>
        <span class="completude-pct">{pct}%</span>
    </div>"""


def fmt(n):
    try: return f"{int(n):,}".replace(",", ".")
    except: return "—"


def fmt_r(n):
    try:
        if n <= 0: return "—"
        return f"R$ {int(n):,}".replace(",", ".")
    except: return "—"



def hex_alpha(hex_color, alpha=0.53):
    """Converte hex color para rgba com transparência — Plotly 6 não aceita hex+88."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def plotly_bar_h(labels, values, selected=None, cor_sel=CO, cor_base=CP2):
    sel = selected if selected else []
    colors = [cor_sel if l in sel else hex_alpha(cor_base) for l in labels]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation='h',
        marker_color=colors, marker_line_color=[cor_sel if l in sel else cor_base for l in labels],
        marker_line_width=2
    ))
    fig.update_layout(
        margin=dict(l=0, r=10, t=5, b=5),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#E2DCF0", tickfont=dict(color="#7A6FA0", size=11)),
        yaxis=dict(showgrid=False, tickfont=dict(color="#7A6FA0", size=11), autorange="reversed"),
        height=max(200, len(labels) * 30),
        showlegend=False,
    )
    return fig


def plotly_bar_v(labels, values, selected=None, cor_sel=CO, cor_base=CP):
    colors = [cor_sel if (selected is not None and i == selected) else hex_alpha(cor_base) for i, _ in enumerate(labels)]
    fig = go.Figure(go.Bar(
        x=labels, y=values, orientation='v',
        marker_color=colors, marker_line_color=cor_base,
        marker_line_width=2
    ))
    fig.update_layout(
        margin=dict(l=0, r=10, t=5, b=5),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, tickfont=dict(color="#7A6FA0", size=11)),
        yaxis=dict(showgrid=True, gridcolor="#E2DCF0", tickfont=dict(color="#7A6FA0", size=11)),
        height=220, showlegend=False,
    )
    return fig


def plotly_donut(labels, values, cores):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=cores, line=dict(color='white', width=3)),
        textinfo='none',
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=5, b=5),
        legend=dict(font=dict(color="#7A6FA0", size=11), orientation="v"),
        height=180, showlegend=True,
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig


# ===================== APP PRINCIPAL =====================
def main():
    # Header
    st.markdown("""
    <div class="dash-header">
        <div style="display:flex;align-items:center">
            <div class="logo-q">Q</div>
            <div>
                <div style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;color:white">
                    HCP Intelligence
                </div>
                <div style="font-size:10px;color:rgba(255,255,255,0.5);letter-spacing:1px;text-transform:uppercase">
                    saúde · inovação · comunicação
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===================== SIDEBAR — Configuração =====================
    with st.sidebar:
        st.markdown("### ⚙️ Configuração")
        sheet_url = st.text_input(
            "URL da Google Sheets",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="A planilha deve estar compartilhada como 'qualquer pessoa com o link pode ver'"
        )
        aba_med  = st.text_input("Nome da aba — Médicos", value="Medicos")
        aba_nut  = st.text_input("Nome da aba — Nutricionistas", value="Nutricionistas")

        st.markdown("---")
        profissao = st.radio("Visualizar", ["Médicos", "Nutricionistas"], horizontal=True)
        st.markdown("---")
        st.markdown("### 🔍 Filtros")

    is_nutri = profissao == "Nutricionistas"

    # ===================== CARREGAR DADOS =====================
    df_raw = None
    colunas_ok = []
    colunas_miss = []

    if sheet_url:
        aba = aba_nut if is_nutri else aba_med
        with st.spinner(f"Carregando {aba}..."):
            df_raw, err = carregar_google_sheets(sheet_url, aba)
        if err:
            st.error(f"Erro ao carregar planilha: {err}")
            st.info("Verifique se a planilha está compartilhada como 'qualquer pessoa com o link pode ver'")
            df_raw = None
        else:
            c_map = mapear_colunas(df_raw)
            colunas_ok   = [f"{v}" for f, v in c_map.items()]
            colunas_miss = [f for f in CMAP if f not in c_map]

    # Chips de colunas reconhecidas
    if colunas_ok or colunas_miss:
        chips_html = " ".join([f'<span style="background:rgba(244,121,32,.1);color:#E05A00;border:1px solid rgba(244,121,32,.2);padding:2px 8px;border-radius:5px;font-size:10px;font-weight:700;font-family:Montserrat,sans-serif">✓ {c}</span>' for c in colunas_ok])
        chips_html += " " + " ".join([f'<span style="background:rgba(120,120,120,.07);color:#bbb;border:1px solid #e8e8e8;padding:2px 8px;border-radius:5px;font-size:10px;font-weight:700;font-family:Montserrat,sans-serif">? {c}</span>' for c in colunas_miss])
        st.markdown(f'<div style="margin-bottom:14px">{chips_html}</div>', unsafe_allow_html=True)

    # Usar dados reais ou demo
    if df_raw is not None:
        df, c_map = processar_df(df_raw, is_nutri)
        is_demo = False
    else:
        df = gerar_demo(is_nutri)
        is_demo = True
        if not sheet_url:
            st.info("💡 Configure a URL da Google Sheets na barra lateral para carregar dados reais.")

    # ===================== FILTROS (sidebar) =====================
    with st.sidebar:
        ufs = sorted([u for u in df['uf'].dropna().unique() if len(str(u)) == 2])
        cidades = sorted(df['cidade'].dropna().unique().tolist())
        esps = sorted(set(
            list(df['esp1'].dropna().unique()) +
            list(df['esp2'].dropna().unique())
        ))
        locais_set = set()
        df['local'].dropna().apply(lambda x: [locais_set.add(l.strip()) for l in str(x).split(',') if l.strip()])
        locais = sorted(locais_set)

        uf_sel     = st.multiselect("UF", ufs)
        cidade_sel = st.multiselect("Cidade", cidades)
        esp_sel    = st.multiselect("Especialidade", esps)
        local_sel  = st.multiselect("Local de Atendimento", locais)

        if is_nutri:
            influ_vals = sorted(df['segInflu'].dropna().unique().tolist())
            presc_vals = sorted(df['segPresc'].dropna().unique().tolist())
            influ_sel  = st.multiselect("Seg. Influência", influ_vals)
            presc_sel  = st.multiselect("Seg. Prescrição", presc_vals)
        else:
            seg_vals  = ["KOL", "KOF", "HCP"]
            seg_sel   = st.multiselect("Segmentação", seg_vals)

    # ===================== APLICAR FILTROS =====================
    f = df.copy()
    if uf_sel:      f = f[f['uf'].isin(uf_sel)]
    if cidade_sel:  f = f[f['cidade'].isin(cidade_sel)]
    if esp_sel:     f = f[f['esp1'].isin(esp_sel) | f['esp2'].isin(esp_sel)]
    if local_sel:
        f = f[f['local'].apply(lambda x: any(l in str(x).split(',') for l in local_sel))]
    if is_nutri:
        if influ_sel: f = f[f['segInflu'].isin(influ_sel)]
        if presc_sel: f = f[f['segPresc'].isin(presc_sel)]
    else:
        if seg_sel: f = f[f['seg'].isin(seg_sel)]

    n = len(f)

    # ===================== KPIs =====================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("👨‍⚕️", "Nutricionistas" if is_nutri else "Médicos",
                 fmt(n), "na base filtrada", "kpi-c1")
    with c2:
        avg_seg = int(f['nseg'].mean()) if n > 0 else 0
        kpi_card("📱", "Média de Seguidores", fmt(avg_seg), "por profissional", "kpi-c2")
    with c3:
        avg_pac = int(f['pacientes'].mean()) if n > 0 else 0
        kpi_card("🏥", "Média Pacientes/dia", f"{avg_pac}/dia", "por profissional", "kpi-c3")
    with c4:
        avg_con = int(f['consulta'].mean()) if n > 0 else 0
        kpi_card("💲", "Ticket Médio", fmt_r(avg_con), "valor médio consulta", "kpi-c4")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ===================== SEGMENTAÇÃO =====================
    col_seg, col_pie = st.columns([2, 1])

    with col_seg:
        st.markdown(f'<div class="section-title">{"Seg. por Influência" if is_nutri else "Segmentação"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Distribuição por segmento</div>', unsafe_allow_html=True)

        if is_nutri:
            cfg = [
                ("HCP",       "Base",    CG,      SEG_INFLU_CORES["HCP"]),
                ("COF Micro", "Micro",   "#0891B2", SEG_INFLU_CORES["COF Micro"]),
                ("DOL Mid",   "Mid",     "#9333EA", SEG_INFLU_CORES["DOL Mid"]),
                ("DOL Elite", "Elite",   "#BE185D", SEG_INFLU_CORES["DOL Elite"]),
                ("KOF",       "Acad.",   CP2,     SEG_INFLU_CORES["KOF"]),
            ]
            cols_seg = st.columns(len(cfg) + 1)
            for i, (key, sub, cor, _) in enumerate(cfg):
                with cols_seg[i]:
                    cnt = len(f[f['segInflu'] == key])
                    seg_card(key, cnt, sub, cor)
            with cols_seg[-1]:
                cnt = len(f[f['segInflu'] == ''])
                seg_card("Sem", cnt, "s/ seg.", "#ccc")
        else:
            cfg_med = [("KOL", ">10k", CO), ("KOF", "Acad.", CP2), ("HCP", "<10k", CG)]
            cols_seg = st.columns(4)
            for i, (key, sub, cor) in enumerate(cfg_med):
                with cols_seg[i]:
                    seg_card(key, len(f[f['seg'] == key]), sub, cor)
            with cols_seg[3]:
                seg_card("Sem", len(f[f['seg'] == '']), "s/ seg.", "#ccc")

    with col_pie:
        st.markdown('<div class="section-title">Distribuição</div>', unsafe_allow_html=True)
        if is_nutri:
            labels = ["HCP", "COF Micro", "DOL Mid", "DOL Elite", "KOF", "Sem"]
            values = [
                len(f[f['segInflu'] == 'HCP']),
                len(f[f['segInflu'] == 'COF Micro']),
                len(f[f['segInflu'] == 'DOL Mid']),
                len(f[f['segInflu'] == 'DOL Elite']),
                len(f[f['segInflu'] == 'KOF']),
                len(f[f['segInflu'] == '']),
            ]
            cores = [CG, "#0891B2", "#9333EA", "#BE185D", CP2, "#ccc"]
        else:
            labels = ["KOL", "KOF", "HCP", "Sem"]
            values = [len(f[f['seg'] == k]) for k in ['KOL', 'KOF', 'HCP', '']]
            cores  = [CO, CP2, CG, "#ccc"]
        st.plotly_chart(plotly_donut(labels, values, cores), width='stretch')

    # Seg Prescrição (só nutri)
    if is_nutri:
        st.markdown('<div class="section-title" style="margin-top:4px">Segmentação por Prescrição</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Interseção com Influência</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            cfg_p = [
                ("HCP Tier 1", "Alta prescr.", CO),
                ("HCP Tier 2", "Méd. prescr.", CB),
                ("HCP Tier 3", "Base prescr.", CG),
            ]
            cols_p = st.columns(4)
            for i, (key, sub, cor) in enumerate(cfg_p):
                with cols_p[i]:
                    seg_card(key.replace("HCP ", ""), len(f[f['segPresc'] == key]), sub, cor)
            with cols_p[3]:
                seg_card("Sem", len(f[f['segPresc'] == '']), "s/ seg.", "#ccc")
        with col_p2:
            labels_p = ["Tier 1", "Tier 2", "Tier 3", "Sem"]
            values_p = [len(f[f['segPresc'] == k]) for k in ['HCP Tier 1', 'HCP Tier 2', 'HCP Tier 3', '']]
            st.plotly_chart(plotly_donut(labels_p, values_p, [CO, CB, CG, "#ccc"]), width='stretch')

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ===================== ESPECIALIDADES + UF =====================
    col_esp, col_uf = st.columns([3, 2])

    with col_esp:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Especialidades</div>', unsafe_allow_html=True)
        esp_cnt = {}
        f['esp1'].dropna().apply(lambda x: esp_cnt.update({x: esp_cnt.get(x, 0) + 1}))
        f['esp2'].dropna().apply(lambda x: esp_cnt.update({x: esp_cnt.get(x, 0) + 1}))
        top_esp = sorted(esp_cnt.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_esp:
            labels_e = [x[0] for x in top_esp]
            values_e = [x[1] for x in top_esp]
            st.plotly_chart(plotly_bar_h(labels_e, values_e, esp_sel or None, CO, CP2), width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col_uf:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">HCPs por UF</div>', unsafe_allow_html=True)
        uf_cnt = f[f['uf'].notna() & (f['uf'].str.len() == 2)]['uf'].value_counts().head(12)
        if len(uf_cnt) > 0:
            st.plotly_chart(
                plotly_bar_v(uf_cnt.index.tolist(), uf_cnt.values.tolist(), None, CO, CP),
                width='stretch'
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ===================== LOCAL + CIDADE =====================
    col_loc, col_cid = st.columns([1, 2])

    with col_loc:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Local de Atendimento</div>', unsafe_allow_html=True)
        loc_cnt = {}
        f['local'].dropna().apply(lambda x: [loc_cnt.update({l.strip(): loc_cnt.get(l.strip(), 0) + 1}) for l in str(x).split(',') if l.strip()])
        if loc_cnt:
            top_loc = sorted(loc_cnt.items(), key=lambda x: x[1], reverse=True)
            st.plotly_chart(
                plotly_donut([x[0] for x in top_loc], [x[1] for x in top_loc],
                             [CP, CO, CP2, CO2, CG, CB, "#9333EA", "#CA8A04"][:len(top_loc)]),
                width='stretch'
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cid:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Cidades</div>', unsafe_allow_html=True)
        cid_cnt = f[f['cidade'].notna()]['cidade'].value_counts().head(10)
        if len(cid_cnt) > 0:
            st.plotly_chart(
                plotly_bar_h(cid_cnt.index.tolist(), cid_cnt.values.tolist(), cidade_sel or None, CO, CB),
                width='stretch'
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ===================== COMPLETUDE + SEGUIDORES =====================
    col_comp, col_faixa = st.columns(2)

    with col_comp:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Completude de Dados de Contato</div>', unsafe_allow_html=True)
        nn = max(n, 1)
        campos = [
            ("Telefone",  int(f['temTel'].sum()  / nn * 100)),
            ("Celular",   int(f['temCell'].sum()  / nn * 100)),
            ("E-mail",    int(f['temEmail'].sum() / nn * 100)),
            ("Endereço",  int(f['temEnd'].sum()   / nn * 100)),
            ("Instagram", int(f['temInsta'].sum() / nn * 100)),
        ]
        html_comp = "".join([completude_bar(nome, pct) for nome, pct in campos])
        st.markdown(f'<div style="margin-top:8px">{html_comp}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_faixa:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Distribuição de Seguidores</div>', unsafe_allow_html=True)
        faixas = [
            ("0–999",    0,      999),
            ("1k–5k",    1000,   4999),
            ("5k–10k",   5000,   9999),
            ("10k–50k",  10000,  49999),
            ("50k–100k", 50000,  99999),
            (">100k",    100000, 999999999),
        ]
        fx_labels = [fx[0] for fx in faixas]
        fx_values = [len(f[(f['nseg'] >= fx[1]) & (f['nseg'] <= fx[2])]) for fx in faixas]
        fig_fx = go.Figure(go.Bar(
            x=fx_labels, y=fx_values,
            marker_color=hex_alpha(CO), marker_line_color=CO, marker_line_width=2
        ))
        fig_fx.update_layout(
            margin=dict(l=0, r=10, t=5, b=5),
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(showgrid=False, tickfont=dict(color="#7A6FA0", size=11)),
            yaxis=dict(showgrid=True, gridcolor="#E2DCF0", tickfont=dict(color="#7A6FA0", size=11)),
            height=220, showlegend=False,
        )
        st.plotly_chart(fig_fx, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    # ===================== TABELA =====================
    st.markdown('<div class="section-title" style="margin-top:4px">Amostra — Top 15 por Seguidores</div>', unsafe_allow_html=True)
    top15 = f.nlargest(15, 'nseg')[['crm','nome','uf','cidade','esp1','seg','segInflu','segPresc','nseg','pacientes','consulta','local']]

    def format_seg(row):
        if is_nutri:
            influ = row['segInflu'] or '—'
            presc = row['segPresc'] or '—'
            return f"{influ} / {presc}"
        else:
            return row['seg'] or '—'

    top15 = top15.copy()
    top15['Segmentação'] = top15.apply(format_seg, axis=1)
    top15['Seguidores']  = top15['nseg'].apply(lambda x: fmt(x))
    top15['Consulta']    = top15['consulta'].apply(lambda x: fmt_r(x))
    top15['Pac./dia']    = top15['pacientes'].apply(lambda x: fmt(x) if x > 0 else '—')

    cols_show = ['crm', 'nome', 'uf', 'cidade', 'esp1', 'Segmentação', 'Seguidores', 'Pac./dia', 'Consulta', 'local']
    rename = {'crm': 'CRM', 'nome': 'Nome', 'uf': 'UF', 'cidade': 'Cidade',
              'esp1': 'Especialidade', 'local': 'Local'}
    st.dataframe(
        top15[cols_show].rename(columns=rename),
        width='stretch',
        hide_index=True,
    )

    sub = f"{'Demonstração' if is_demo else f'{n:,} registros carregados'.replace(',', '.')}"
    st.markdown(f'<div style="font-size:11px;color:#7A6FA0;margin-top:4px">{sub}</div>', unsafe_allow_html=True)


# ===================== DEMO DATA =====================
def gerar_demo(is_nutri):
    import random
    random.seed(99 if is_nutri else 42)
    nomes = ["Ana Paula Ferreira", "Carlos Eduardo Lima", "Márcia Rodrigues",
             "João Batista Costa", "Priscila Mendes", "Rafael Souza",
             "Beatriz Cavalcante", "Thiago Andrade", "Fernanda Gomes", "Leonardo Martins"]
    ufs = ["SP","SP","SP","RJ","RJ","MG","RS","PR","BA","SC","PE","CE","GO","DF"]
    cid_map = {"SP": ["São Paulo","Campinas","Santos"], "RJ": ["Rio de Janeiro","Niterói"],
               "MG": ["Belo Horizonte","Uberlândia"], "RS": ["Porto Alegre","Caxias do Sul"],
               "PR": ["Curitiba","Londrina"], "BA": ["Salvador"], "SC": ["Florianópolis"],
               "PE": ["Recife"], "CE": ["Fortaleza"], "GO": ["Goiânia"], "DF": ["Brasília"]}
    esps_m = ["Cardiologia","Endocrinologia","Clínica Geral","Neurologia","Ortopedia","Oncologia","Pediatria","Psiquiatria"]
    esps_n = ["Nutrição Clínica","Nutrição Esportiva","Nutrição Pediátrica","Nutrição Oncológica","Nutrição Funcional"]
    segs_m = ["KOL","KOF","HCP","HCP","HCP","","",""]
    segs_i = ["HCP","COF Micro","DOL Mid","DOL Elite","KOF","HCP","",""]
    segs_p = ["HCP Tier 1","HCP Tier 2","HCP Tier 3","HCP Tier 1","","HCP Tier 2","",""]
    locais = ["Clínica","Consultório","Hospital","Teleconsulta","Ambulatório"]
    esps = esps_n if is_nutri else esps_m
    rows = []
    for i in range(400):
        uf = random.choice(ufs)
        seg = "" if is_nutri else random.choice(segs_m)
        si  = random.choice(segs_i) if is_nutri else ""
        sp  = random.choice(segs_p) if is_nutri else ""
        nseg = random.randint(10001,350000) if (si=="DOL Elite" or seg=="KOL") else \
               random.randint(1000,9999) if (si in ["COF Micro","DOL Mid"] or seg=="KOF") else \
               random.randint(50,999)
        rows.append({
            "crm": str(random.randint(10000,99999)),
            "nome": nomes[i % len(nomes)] + f" {i+1}",
            "uf": uf, "cidade": random.choice(cid_map.get(uf, ["Cidade"])),
            "esp1": random.choice(esps), "esp2": random.choice(esps),
            "seg": seg, "segInflu": si, "segPresc": sp,
            "nseg": nseg, "consulta": random.randint(100,1200),
            "pacientes": random.randint(5,40),
            "local": random.choice(locais),
            "temTel": random.random() > 0.3, "temCell": random.random() > 0.4,
            "temEmail": random.random() > 0.2, "temEnd": random.random() > 0.5,
            "temInsta": random.random() > 0.6,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()
