import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
from supabase import create_client
import io
import re

st.set_page_config(page_title="Budget Couple", page_icon="💗", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #fff8f3 0%, #ffffff 45%);
    color: #16171f;
}
.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #16171f !important;
}
h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.05em;
}
.hero-subtitle {
    color: #6f625b !important;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff;
    border: 1px solid #f0dfd8;
    border-radius: 20px;
    padding: 10px;
    gap: 10px;
    box-shadow: 0 10px 30px rgba(90, 50, 30, 0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 16px;
    padding: 12px 18px;
    font-weight: 700;
}
.stTabs [aria-selected="true"] {
    background: #fff0f2 !important;
    border-bottom: 3px solid #ff4266 !important;
}
.card {
    background: #ffffff;
    border: 1px solid #f0dfd8;
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 16px 40px rgba(90, 50, 30, 0.07);
    margin-bottom: 20px;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #f0dfd8;
    border-radius: 24px;
    padding: 26px 24px;
    min-height: 190px;
    box-shadow: 0 16px 40px rgba(90, 50, 30, 0.07);
    text-align: center;
}
.kpi-icon {
    width: 72px;
    height: 72px;
    margin: auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    margin-bottom: 14px;
}
.kpi-label {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 8px;
}
.kpi-value-pink { color: #f43f6c !important; font-size: 2.4rem; font-weight: 800; }
.kpi-value-green { color: #3ca266 !important; font-size: 2.4rem; font-weight: 800; }
.kpi-value-blue { color: #2d7eea !important; font-size: 2.4rem; font-weight: 800; }
.kpi-value-orange { color: #f28a00 !important; font-size: 2.4rem; font-weight: 800; }
.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 14px;
    background: #fff0f2;
    color: #f43f6c !important;
    font-weight: 700;
    margin-top: 12px;
}
div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #ffb9c7 !important;
    border-radius: 16px !important;
    min-height: 58px;
}
div[data-baseweb="select"] * {
    color: #16171f !important;
}
input, textarea {
    color: #16171f !important;
}
.stTextInput input, .stNumberInput input {
    background: #ffffff !important;
    color: #16171f !important;
    border-radius: 14px !important;
}
button[kind="secondary"], button[data-baseweb="button"] {
    color: #16171f !important;
}
.stButton button, .stFormSubmitButton button {
    border-radius: 16px;
    padding: 0.75rem 1.2rem;
    font-weight: 800;
    background: #ff4266;
    color: white !important;
    border: none;
    box-shadow: 0 12px 24px rgba(244, 63, 108, 0.22);
}
.category-row {
    display: grid;
    grid-template-columns: 46px 1.2fr 1fr 0.6fr;
    gap: 12px;
    align-items: center;
    padding: 12px 0;
}
.cat-icon {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}
.cat-name {
    font-weight: 800;
}
.muted {
    color: #746a64 !important;
}
.expense-card {
    background: #fff5f6;
    border: 1px solid #ffd6de;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 10px;
}
.footer {
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #f0dfd8;
    display: flex;
    justify-content: space-between;
    color: #7b7069 !important;
    font-size: 0.9rem;
}
.notif-item-warn {
    padding: 8px 0;
    border-bottom: 1px solid #ffeaa0;
    color: #7a4e00 !important;
}
.notif-item-error {
    padding: 8px 0;
    border-bottom: 1px solid #ffb9c7;
    color: #9b0022 !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

url = st.secrets.get("SUPABASE_URL", "").strip()
key = st.secrets.get("SUPABASE_KEY", "").strip()

if not url or not key:
    st.error("🔑 Secrets Supabase manquants. Va dans Settings → Secrets de ton app Streamlit et vérifie SUPABASE_URL et SUPABASE_KEY.")
    st.stop()

bad_chars = chr(34) + chr(39) + chr(0x201C) + chr(0x201D) + chr(0x2018) + chr(0x2019)
url = url.strip(bad_chars)
key = key.strip(bad_chars)

st.info("Debug — URL len=" + str(len(url)) + "  debut=" + repr(url[:8]) + "  fin=" + repr(url[-5:]))
st.stop()

supabase = create_client(url, key)

DEFAULT_CATEGORIES = ["Courses", "Restaurants", "Essence", "Loisirs", "Maison", "Santé", "Bébé", "Autres"]
DEFAULT_PEOPLE = ["Toi", "Elle", "Commun"]

CATEGORY_ICONS = {
    "Courses": "🛒",
    "Restaurants": "🍴",
    "Essence": "⛽",
    "Loisirs": "🎮",
    "Maison": "🏠",
    "Santé": "➕",
    "Bébé": "👶",
    "Autres": "•••"
}

CATEGORY_COLORS = {
    "Courses": "#ffd5df",
    "Restaurants": "#ffe2c8",
    "Essence": "#dfd2ff",
    "Loisirs": "#d8f3dc",
    "Maison": "#d7ebff",
    "Santé": "#ffd1d1",
    "Bébé": "#fff0bf",
    "Autres": "#eeeeee"
}

CHART_COLORS = ["#f43f6c", "#f28a00", "#8b5cf6", "#3ca266", "#2d7eea", "#ef4444", "#f59e0b", "#9ca3af"]

CATEGORY_KEYWORDS = {
    "Courses": [
        "carrefour", "leclerc", "auchan", "lidl", "intermarche", "monoprix",
        "franprix", "casino ", "super u", "picard", "biocoop", "naturalia",
        "action ", "boulangerie", "epicerie", "cora ", "netto", "aldi", "spar",
        "g20", "simply market", "match ", "supermarche", "supermarché",
    ],
    "Restaurants": [
        "mcdonald", "mcdo", "burger king", "kfc", "pizza", "subway",
        "ubereats", "uber eat", "deliveroo", "just eat", "justeat",
        "restaurant", "brasserie", "bistro", "kebab", "domino", "sushi",
        "heura", "brioche doree", "paul ", "brioche dorée",
    ],
    "Essence": [
        "total ", "totalenergies", "shell", "esso ", "bp ", "carburant",
        "sans plomb", "diesel", "gazole", "q8 ", "station service",
    ],
    "Loisirs": [
        "cinema", "netflix", "spotify", "amazon prime", "disney", "fnac",
        "steam ", "concert", "theatre", "musee", "gym", "fitness",
        "canal+", "deezer", "prime video", "arte ", "playstation", "xbox",
        "switch", "jeux video", "bowling", "karting", "escape game",
    ],
    "Maison": [
        "loyer", "edf", "engie", "eau ", "internet", "sfr ", "orange ",
        "free ", "bouygues", "ikea", "leroy merlin", "bricorama",
        "castorama", "conforama", "maif", "assurance", "syndic", "charges",
        "brico depot", "mr bricolage",
    ],
    "Santé": [
        "pharmacie", "medecin", "docteur", "hopital", "clinique",
        "dentiste", "opticien", "mutuelle", "secu", "kinesithera",
        "laboratoire", "cpam", "ameli",
    ],
    "Bébé": [
        "bebe ", "bébé", "puericulture", "puériculture", "mothercare",
        "orchestra", "natalys", "pampers", "couches", "lait infantile",
        "jouet", "toys r us", "kidilou",
    ],
}


def current_month():
    today = date.today()
    return f"{today.year}-{today.month:02d}"


def month_label(month):
    months = {
        "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
        "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
        "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
    }
    if "-" not in month:
        return month
    year, m = month.split("-")
    return f"{months.get(m, m)} {year}"


def format_euro(value):
    return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")


def normalize_amount(value):
    """Convert a string amount to float, handling French and international formats."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if not pd.isna(value) else None
    s = str(value).strip().replace('\xa0', '').replace(' ', '')
    s = re.sub(r'[€$£]', '', s)
    if not s or s in ['-', '+']:
        return None
    # European: 1.234,56 → dot is thousands separator
    if ',' in s and '.' in s:
        if s.index('.') < s.index(','):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except Exception:
        return None


def parse_date_value(value):
    """Try to parse a date value to a date object."""
    if value is None:
        return None
    if isinstance(value, (date,)):
        return value
    try:
        import datetime as dt
        if isinstance(value, dt.datetime):
            return value.date()
    except Exception:
        pass
    try:
        return pd.to_datetime(str(value), dayfirst=True).date()
    except Exception:
        return None


def auto_categorize(description):
    """Assign a category based on keywords in the description."""
    if not description:
        return "Autres"
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "Autres"


def detect_columns(df):
    """Detect date, description, debit, credit and single-amount columns."""
    col_map = {c.lower().strip(): c for c in df.columns}

    date_keys = [
        'date', 'date de comptabilisation', "date d'opération", "date d'operation",
        'dateop', 'date started', 'started date', 'completed date', 'jour',
        'date opération', 'date operation', 'date valeur',
    ]
    desc_keys = [
        'libellé', 'libelle', 'libellé simplifié', 'libelle simplifie',
        'label', 'description', 'opération', 'operation', 'payee',
        'bénéficiaire', 'beneficiaire', 'suppl label', 'detail',
        'libellé complet', 'libelle complet',
    ]
    debit_keys = [
        'débit', 'debit', 'montant débit', 'montant debit', 'sortie', 'retrait',
    ]
    credit_keys = [
        'crédit', 'credit', 'montant crédit', 'montant credit', 'entrée', 'entree',
    ]
    amount_keys = [
        'montant', 'amount', 'amount (eur)', 'solde', 'montant (eur)',
    ]

    date_col = next((col_map[k] for k in date_keys if k in col_map), None)
    desc_col = next((col_map[k] for k in desc_keys if k in col_map), None)
    debit_col = next((col_map[k] for k in debit_keys if k in col_map), None)
    credit_col = next((col_map[k] for k in credit_keys if k in col_map), None)
    amount_col = next((col_map[k] for k in amount_keys if k in col_map), None)

    # Fallback: scan columns for date-parseable values
    if not date_col:
        for orig_col in df.columns:
            sample = df[orig_col].dropna().head(5)
            if len(sample) >= 2:
                parsed = [parse_date_value(v) for v in sample]
                if sum(1 for p in parsed if p is not None) >= 2:
                    date_col = orig_col
                    break

    return date_col, desc_col, debit_col, credit_col, amount_col


def parse_bank_file(file):
    """
    Parse a bank CSV or Excel file.
    Returns (list_of_dicts, warning_or_none) on success,
    or (None, error_message) on failure.
    """
    filename = file.name.lower()
    content = file.read()
    df = None

    if filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
        except Exception as e:
            return None, f"Erreur lecture Excel : {e}"
    elif filename.endswith('.xls'):
        try:
            df = pd.read_excel(io.BytesIO(content))
        except Exception as e:
            return None, f"Erreur lecture XLS : {e}"
    else:
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            for sep in [';', ',', '\t', '|']:
                try:
                    tmp = pd.read_csv(
                        io.BytesIO(content), sep=sep, encoding=encoding,
                        on_bad_lines='skip', dtype=str,
                    )
                    if len(tmp.columns) >= 2 and len(tmp) > 0:
                        df = tmp
                        break
                except Exception:
                    pass
            if df is not None:
                break

    if df is None or df.empty:
        return None, "Impossible de lire le fichier. Vérifiez le format (CSV, XLSX, XLS)."

    df.columns = [str(c).strip() for c in df.columns]

    date_col, desc_col, debit_col, credit_col, amount_col = detect_columns(df)

    if not date_col:
        return None, (
            f"Colonne de date non détectée. Colonnes trouvées : {', '.join(df.columns.tolist()[:10])}"
        )
    if not desc_col:
        return None, (
            f"Colonne de libellé non détectée. Colonnes trouvées : {', '.join(df.columns.tolist()[:10])}"
        )

    transactions = []

    for _, row in df.iterrows():
        parsed_date = parse_date_value(row.get(date_col))
        if parsed_date is None:
            continue

        libelle = str(row.get(desc_col, '')).strip()
        if not libelle or libelle in ['nan', 'None', '']:
            continue

        amount = None

        if debit_col and debit_col in df.columns:
            raw_debit = row.get(debit_col)
            amount = normalize_amount(raw_debit)
            if amount is not None:
                amount = abs(amount)
            else:
                # No debit value → it's a credit line, skip
                continue
        elif amount_col and amount_col in df.columns:
            raw_amount = row.get(amount_col)
            amount = normalize_amount(raw_amount)
            if amount is None:
                continue
            if amount > 0:
                # Positive = income/credit, skip
                continue
            amount = abs(amount)
        else:
            # Last resort: scan all numeric-looking columns
            for col in df.columns:
                if col in [date_col, desc_col, credit_col]:
                    continue
                val = normalize_amount(row.get(col))
                if val is not None and val != 0:
                    amount = abs(val)
                    break

        if amount is None or amount == 0:
            continue

        transactions.append({
            'date': parsed_date,
            'libelle': libelle,
            'montant': amount,
            'categorie': auto_categorize(libelle),
            'personne': 'Commun',
        })

    return transactions, None


def get_transactions():
    res = supabase.table("transactions").select("*").order("date", desc=True).execute()
    data = res.data if res.data else []
    df = pd.DataFrame(data)
    if not df.empty:
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)
    return df


def add_transaction_db(depense_date, libelle, montant, categorie, personne):
    month_value = f"{depense_date.year}-{depense_date.month:02d}"
    supabase.table("transactions").insert({
        "date": str(depense_date),
        "month": month_value,
        "libelle": libelle,
        "montant": -abs(float(montant)),
        "categorie": categorie,
        "personne": personne
    }).execute()


def add_transactions_batch(transactions):
    rows = []
    for t in transactions:
        d = t['date']
        month_value = f"{d.year}-{d.month:02d}"
        rows.append({
            "date": str(d),
            "month": month_value,
            "libelle": t['libelle'],
            "montant": -abs(float(t['montant'])),
            "categorie": t['categorie'],
            "personne": t['personne'],
        })
    if rows:
        supabase.table("transactions").insert(rows).execute()


def delete_transaction_db(transaction_id):
    supabase.table("transactions").delete().eq("id", transaction_id).execute()


def get_categories():
    res = supabase.table("categories").select("*").order("name").execute()
    data = res.data if res.data else []
    if not data:
        for cat in DEFAULT_CATEGORIES:
            supabase.table("categories").insert({"name": cat}).execute()
        res = supabase.table("categories").select("*").order("name").execute()
        data = res.data if res.data else []
    cats = [x["name"] for x in data]
    return cats if cats else DEFAULT_CATEGORIES


def add_category_db(name):
    supabase.table("categories").insert({"name": name}).execute()


def delete_category_db(name):
    supabase.table("categories").delete().eq("name", name).execute()


def get_budgets():
    res = supabase.table("budgets").select("*").execute()
    data = res.data if res.data else []
    result = {}
    for row in data:
        result.setdefault(row["month"], {})[row["category"]] = float(row["amount"])
    return result


def save_budget_db(month, category, amount):
    existing = (
        supabase.table("budgets")
        .select("id")
        .eq("month", month)
        .eq("category", category)
        .execute()
    )
    if existing.data:
        supabase.table("budgets").update({"amount": float(amount)}).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("budgets").insert({"month": month, "category": category, "amount": float(amount)}).execute()


def get_budget(budgets_dict, month, cat):
    return float(budgets_dict.get(month, {}).get(cat, 0.0))


# ─── Load shared data ────────────────────────────────────────────────────────
categories = get_categories()
budgets = get_budgets()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("# Budget Couple 💕")
st.markdown("<div class='hero-subtitle'>Gérez vos dépenses, budgets et projets à deux.</div>", unsafe_allow_html=True)

tabs = st.tabs([
    "🏠 Dashboard",
    "➕ Ajouter",
    "📂 Import",
    "☷ Historique",
    "◔ Budgets",
    "📊 Graphiques",
    "🏷️ Catégories",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 0 — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    transactions = get_transactions()

    if transactions.empty:
        all_months = [current_month()]
    else:
        all_months = sorted(set(transactions["month"].dropna().tolist() + [current_month()]), reverse=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        selected_month = st.selectbox("Mois", options=all_months, format_func=month_label)
    with c2:
        person_filter = st.segmented_control("Filtre", ["Tous", "Toi", "Elle", "Commun"], default="Tous")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Budget notifications ──────────────────────────────────────────────────
    month_df_full = transactions[transactions["month"] == selected_month] if not transactions.empty else pd.DataFrame()

    notifs_error = []
    notifs_warn = []
    for cat in categories:
        budget_val = get_budget(budgets, selected_month, cat)
        if budget_val <= 0:
            continue
        cat_spent = (
            abs(month_df_full[month_df_full["categorie"] == cat]["montant"].sum())
            if not month_df_full.empty else 0.0
        )
        pct = cat_spent / budget_val
        icon = CATEGORY_ICONS.get(cat, "•")
        if pct >= 1.0:
            notifs_error.append(
                f"{icon} <b>{cat}</b> — Budget dépassé ! "
                f"({format_euro(cat_spent)} / {format_euro(budget_val)})"
            )
        elif pct >= 0.8:
            notifs_warn.append(
                f"{icon} <b>{cat}</b> — {int(pct * 100)}% utilisé "
                f"({format_euro(cat_spent)} / {format_euro(budget_val)})"
            )

    if notifs_error or notifs_warn:
        label = (
            f"🔔 Alertes budget — "
            f"{len(notifs_error)} dépassement(s), {len(notifs_warn)} avertissement(s)"
        )
        with st.expander(label, expanded=True):
            for n in notifs_error:
                st.markdown(f"<div class='notif-item-error'>🚨 {n}</div>", unsafe_allow_html=True)
            for n in notifs_warn:
                st.markdown(f"<div class='notif-item-warn'>⚠️ {n}</div>", unsafe_allow_html=True)

    # ── Filtered data for KPIs ────────────────────────────────────────────────
    df = transactions.copy()
    if not df.empty:
        df = df[df["month"] == selected_month]
        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

    total_depenses = abs(df["montant"].sum()) if not df.empty else 0.0
    budget_total = sum(get_budget(budgets, selected_month, cat) for cat in categories)
    reste_total = budget_total - total_depenses
    nb_depenses = len(df)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#ffd5df;">🛒</div>
            <div class="kpi-label">Dépensé</div>
            <div class="kpi-value-pink">{format_euro(total_depenses)}</div>
            <div class="badge">Suivi mensuel</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#d8f3dc;">👛</div>
            <div class="kpi-label">Reste à dépenser</div>
            <div class="kpi-value-green">{format_euro(reste_total)}</div>
            <div class="badge">Budget restant</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#d7ebff;">◔</div>
            <div class="kpi-label">Budget total</div>
            <div class="kpi-value-blue">{format_euro(budget_total)}</div>
            <div class="muted">{sum(1 for c in categories if get_budget(budgets, selected_month, c) > 0)} catégorie(s) budgétée(s)</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#fff0bf;">🧾</div>
            <div class="kpi-label">Dépenses</div>
            <div class="kpi-value-orange">{nb_depenses}</div>
            <div class="muted">Transaction(s) ce mois</div>
        </div>
        """, unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ◔ Budget par catégorie")

        for cat in categories:
            cat_df = df[df["categorie"] == cat] if not df.empty else pd.DataFrame()
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0.0
            budget = get_budget(budgets, selected_month, cat)
            remaining = budget - spent
            percent = int(min(spent / budget, 1) * 100) if budget > 0 else (100 if spent > 0 else 0)
            icon = CATEGORY_ICONS.get(cat, "•")
            bg = CATEGORY_COLORS.get(cat, "#eeeeee")

            st.markdown(f"""
            <div class="category-row">
                <div class="cat-icon" style="background:{bg};">{icon}</div>
                <div>
                    <div class="cat-name">{cat}</div>
                    <div class="muted">{format_euro(spent)} / {format_euro(budget)}</div>
                </div>
                <div>
                    <div class="muted">{percent}%</div>
                </div>
                <div style="text-align:right;font-weight:800;">{format_euro(remaining)}</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(percent / 100)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 〽 Dernières dépenses")

        if df.empty:
            st.markdown("""
            <div style="text-align:center;padding:60px 10px;">
                <div style="font-size:72px;">👛</div>
                <h3>Plus aucune dépense</h3>
                <p class="muted">pour le moment</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            recent = df.sort_values("date", ascending=False).head(6)
            for _, row in recent.iterrows():
                cat = row["categorie"]
                icon = CATEGORY_ICONS.get(cat, "•")
                st.markdown(f"""
                <div class="expense-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <div style="font-weight:800;">{icon} {cat}</div>
                            <div class="muted">{row['libelle']} · {row['personne']}</div>
                        </div>
                        <div style="font-weight:900;color:#f43f6c!important;">
                            {format_euro(abs(float(row['montant'])))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        <div>💗 Fait pour vous, avec 💗</div>
        <div>🛡️ Données sécurisées avec Supabase</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — AJOUTER
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Ajouter une dépense")

    with st.form("add_expense_form", clear_on_submit=True):
        depense_date = st.date_input("Date", value=date.today())
        libelle = st.text_input("Libellé", placeholder="Ex : Carrefour, restaurant, pharmacie...")
        montant = st.number_input("Montant", min_value=0.0, step=1.0)
        categorie = st.selectbox("Catégorie", options=categories)
        personne = st.selectbox("Qui paie ?", options=DEFAULT_PEOPLE)

        submitted = st.form_submit_button("Ajouter la dépense")

        if submitted:
            if not libelle.strip():
                st.error("Libellé obligatoire")
            elif montant <= 0:
                st.error("Montant invalide")
            else:
                add_transaction_db(depense_date, libelle.strip(), montant, categorie, personne)
                st.success("Dépense ajoutée")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — IMPORT CSV / EXCEL
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📂 Import depuis extrait bancaire")
    st.markdown(
        "<p class='muted'>Formats supportés : CSV et Excel (.xlsx, .xls).<br>"
        "Compatible avec Crédit Agricole, BNP Paribas, Société Générale, "
        "Boursorama, Revolut, N26 et la plupart des banques françaises.</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Choisir un fichier", type=["csv", "xlsx", "xls"])

    if uploaded is not None:
        with st.spinner("Analyse du fichier en cours…"):
            result, error = parse_bank_file(uploaded)

        if result is None:
            st.error(f"Impossible de traiter le fichier : {error}")
        elif len(result) == 0:
            st.warning("Aucune dépense (débit) détectée dans ce fichier.")
            if error:
                st.info(error)
        else:
            if error:
                st.warning(error)
            st.success(f"✅ {len(result)} dépense(s) détectée(s) — vérifiez avant d'importer.")

            preview_df = pd.DataFrame([{
                "✓": True,
                "Date": r["date"],
                "Libellé": r["libelle"],
                "Montant": r["montant"],
                "Catégorie": r["categorie"],
                "Qui": r["personne"],
            } for r in result])

            st.markdown("#### Aperçu et corrections")
            st.markdown(
                "<p class='muted'>Décochez les lignes à exclure. "
                "Modifiez les catégories ou la personne si nécessaire.</p>",
                unsafe_allow_html=True,
            )

            edited = st.data_editor(
                preview_df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "✓": st.column_config.CheckboxColumn("Importer", default=True),
                    "Date": st.column_config.DateColumn("Date"),
                    "Montant": st.column_config.NumberColumn("Montant (€)", format="%.2f"),
                    "Catégorie": st.column_config.SelectboxColumn("Catégorie", options=categories),
                    "Qui": st.column_config.SelectboxColumn("Qui", options=DEFAULT_PEOPLE),
                },
            )

            to_import = edited[edited["✓"] == True]
            st.markdown(f"**{len(to_import)} transaction(s) sélectionnée(s)**")

            if st.button("⬆️ Importer les transactions sélectionnées", disabled=len(to_import) == 0):
                batch = [
                    {
                        "date": row["Date"],
                        "libelle": str(row["Libellé"]),
                        "montant": float(row["Montant"]),
                        "categorie": row["Catégorie"],
                        "personne": row["Qui"],
                    }
                    for _, row in to_import.iterrows()
                ]
                add_transactions_batch(batch)
                st.success(f"✅ {len(batch)} transaction(s) importée(s) avec succès !")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — HISTORIQUE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Historique")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense.")
    else:
        months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        hist_month = st.selectbox("Mois", ["Tous"] + months, format_func=lambda x: x if x == "Tous" else month_label(x))
        hist_person = st.selectbox("Personne", ["Tous"] + DEFAULT_PEOPLE)
        hist_category = st.selectbox("Catégorie", ["Toutes"] + categories)

        filtered = df.copy()
        if hist_month != "Tous":
            filtered = filtered[filtered["month"] == hist_month]
        if hist_person != "Tous":
            filtered = filtered[filtered["personne"] == hist_person]
        if hist_category != "Toutes":
            filtered = filtered[filtered["categorie"] == hist_category]

        if filtered.empty:
            st.warning("Aucune dépense avec ces filtres.")
        else:
            display_df = filtered.sort_values("date", ascending=False).copy()
            display_df["montant"] = display_df["montant"].apply(lambda x: format_euro(abs(float(x))))
            st.dataframe(
                display_df[["date", "month", "libelle", "categorie", "personne", "montant"]],
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("### Supprimer une dépense")
            options = {
                f"{row['date']} | {row['libelle']} | {row['categorie']} | {format_euro(abs(float(row['montant'])))}": row["id"]
                for _, row in filtered.iterrows()
            }
            selected = st.selectbox("Choisir", ["Aucune"] + list(options.keys()))

            if selected != "Aucune":
                if st.button("Supprimer"):
                    delete_transaction_db(options[selected])
                    st.success("Dépense supprimée")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — BUDGETS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Budgets")

    budget_month = st.text_input("Mois", value=current_month())

    with st.form("budget_form"):
        new_values = {}

        for cat in categories:
            new_values[cat] = st.number_input(
                f"{CATEGORY_ICONS.get(cat, '•')} {cat}",
                min_value=0.0,
                step=10.0,
                value=get_budget(budgets, budget_month, cat),
                key=f"budget_{budget_month}_{cat}",
            )

        save_btn = st.form_submit_button("Enregistrer les budgets")

        if save_btn:
            for cat, amount in new_values.items():
                save_budget_db(budget_month, cat, amount)
            st.success("Budgets sauvegardés dans Supabase")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — GRAPHIQUES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("📊 Graphiques")

    all_transactions = get_transactions()

    if all_transactions.empty:
        st.info("Aucune donnée à afficher. Ajoutez des dépenses d'abord.")
    else:
        all_months_chart = sorted(
            set(all_transactions["month"].dropna().tolist() + [current_month()]),
            reverse=True,
        )
        chart_month = st.selectbox(
            "Mois de référence",
            options=all_months_chart,
            format_func=month_label,
            key="chart_month",
        )

        df_month = all_transactions[all_transactions["month"] == chart_month].copy()
        df_month["montant_abs"] = df_month["montant"].abs()

        # ── Row 1 : Pie + Budget vs Réel ─────────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Répartition par catégorie")
            if df_month.empty:
                st.info("Aucune dépense ce mois.")
            else:
                cat_data = df_month.groupby("categorie")["montant_abs"].sum().reset_index()
                cat_data.columns = ["Catégorie", "Montant"]
                fig_pie = px.pie(
                    cat_data,
                    values="Montant",
                    names="Catégorie",
                    color_discrete_sequence=CHART_COLORS,
                    hole=0.4,
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                fig_pie.update_layout(
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=320,
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("#### Budget vs Réel")
            budgets_fresh = get_budgets()
            bar_data = []
            for cat in categories:
                spent_val = float(
                    df_month[df_month["categorie"] == cat]["montant_abs"].sum()
                ) if not df_month.empty else 0.0
                budget_val = get_budget(budgets_fresh, chart_month, cat)
                if spent_val > 0 or budget_val > 0:
                    bar_data.append({"Catégorie": cat, "Dépensé": spent_val, "Budget": budget_val})

            if bar_data:
                bar_df = pd.DataFrame(bar_data)
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    name="Budget",
                    x=bar_df["Catégorie"],
                    y=bar_df["Budget"],
                    marker_color="#d7ebff",
                    marker_line_color="#2d7eea",
                    marker_line_width=1.5,
                ))
                fig_bar.add_trace(go.Bar(
                    name="Dépensé",
                    x=bar_df["Catégorie"],
                    y=bar_df["Dépensé"],
                    marker_color="#f43f6c",
                ))
                fig_bar.update_layout(
                    barmode="group",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=320,
                    margin=dict(t=10, b=10, l=10, r=10),
                    legend=dict(orientation="h", y=-0.25),
                    xaxis=dict(tickfont=dict(size=11), showgrid=False),
                    yaxis=dict(gridcolor="#f0dfd8"),
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Aucune donnée à comparer ce mois.")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Row 2 : Évolution mensuelle ───────────────────────────────────────
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### Évolution mensuelle des dépenses")

        monthly = all_transactions.copy()
        monthly["montant_abs"] = monthly["montant"].abs()
        monthly_sum = monthly.groupby("month")["montant_abs"].sum().reset_index()
        monthly_sum.columns = ["Mois", "Total"]
        monthly_sum = monthly_sum.sort_values("Mois")
        monthly_sum["Mois_label"] = monthly_sum["Mois"].apply(month_label)

        fig_line = px.line(
            monthly_sum,
            x="Mois_label",
            y="Total",
            markers=True,
            labels={"Mois_label": "Mois", "Total": "Dépenses (€)"},
            color_discrete_sequence=["#f43f6c"],
        )
        fig_line.update_traces(line_width=3, marker_size=8)
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f0dfd8"),
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Row 3 : Dépenses par personne ─────────────────────────────────────
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### Dépenses par personne — ce mois")

        if df_month.empty:
            st.info("Aucune dépense ce mois.")
        else:
            person_data = (
                df_month.groupby(["personne", "categorie"])["montant_abs"]
                .sum()
                .reset_index()
            )
            person_data.columns = ["Personne", "Catégorie", "Montant"]

            fig_person = px.bar(
                person_data,
                x="Personne",
                y="Montant",
                color="Catégorie",
                labels={"Montant": "Dépenses (€)", "Personne": ""},
                color_discrete_sequence=CHART_COLORS,
                height=320,
            )
            fig_person.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", y=-0.3),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f0dfd8"),
            )
            st.plotly_chart(fig_person, use_container_width=True)

            # Equity summary
            totals = df_month.groupby("personne")["montant_abs"].sum()
            toi = totals.get("Toi", 0.0)
            elle = totals.get("Elle", 0.0)
            commun = totals.get("Commun", 0.0)
            diff = toi - elle
            st.markdown(
                f"<p class='muted' style='margin-top:8px;'>"
                f"Toi : <b>{format_euro(toi)}</b> &nbsp;·&nbsp; "
                f"Elle : <b>{format_euro(elle)}</b> &nbsp;·&nbsp; "
                f"Commun : <b>{format_euro(commun)}</b>"
                f"{'&nbsp; — &nbsp;⚖️ Toi dois <b>' + format_euro(abs(diff)/2) + '</b> à Elle' if diff > 1 else ''}"
                f"{'&nbsp; — &nbsp;⚖️ Elle doit <b>' + format_euro(abs(diff)/2) + '</b> à Toi' if diff < -1 else ''}"
                f"</p>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — CATÉGORIES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Catégories")

    for cat in categories:
        st.write(f"{CATEGORY_ICONS.get(cat, '•')} {cat}")

    new_cat = st.text_input("Nouvelle catégorie")

    if st.button("Ajouter catégorie"):
        clean = new_cat.strip()
        if clean and clean not in categories:
            add_category_db(clean)
            st.success("Catégorie ajoutée")
            st.rerun()
        elif clean in categories:
            st.warning("Cette catégorie existe déjà.")

    st.markdown("### Supprimer une catégorie")
    removable = [c for c in categories if c != "Autres"]

    to_delete = st.selectbox("Catégorie à supprimer", ["Aucune"] + removable)

    if to_delete != "Aucune":
        st.warning("Attention : les anciennes dépenses gardent cette catégorie.")
        if st.button("Supprimer cette catégorie"):
            delete_category_db(to_delete)
            st.success("Catégorie supprimée")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
