import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Budget Couple", page_icon="💗", layout="wide")

# ======================
# DESIGN V3++
# ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #fff8f3 0%, #ffffff 45%);
    color: #16171f;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* TEXTE */
h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #16171f !important;
}

h1 {
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.05em;
    margin-bottom: 0.2rem;
}

h2, h3 {
    letter-spacing: -0.03em;
}

/* HEADER */
.hero-subtitle {
    color: #6f625b !important;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

/* TABS */
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
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: #fff0f2 !important;
    border-bottom: 3px solid #ff4266 !important;
}

/* CARTES */
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

.kpi-value-pink {
    color: #f43f6c !important;
    font-size: 2.4rem;
    font-weight: 800;
}

.kpi-value-green {
    color: #3ca266 !important;
    font-size: 2.4rem;
    font-weight: 800;
}

.kpi-value-blue {
    color: #2d7eea !important;
    font-size: 2.4rem;
    font-weight: 800;
}

.kpi-value-orange {
    color: #f28a00 !important;
    font-size: 2.4rem;
    font-weight: 800;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 14px;
    background: #fff0f2;
    color: #f43f6c !important;
    font-weight: 700;
    margin-top: 12px;
}

/* INPUTS */
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

/* SEGMENTED */
button[kind="secondary"], button[data-baseweb="button"] {
    color: #16171f !important;
}

/* BOUTONS */
.stButton button, .stFormSubmitButton button {
    border-radius: 16px;
    padding: 0.75rem 1.2rem;
    font-weight: 800;
    background: #ff4266;
    color: white !important;
    border: none;
    box-shadow: 0 12px 24px rgba(244, 63, 108, 0.22);
}

.stButton button:hover, .stFormSubmitButton button:hover {
    background: #f02f59;
    color: white !important;
}

/* TABLES */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

/* PROGRESS */
.stProgress > div > div > div > div {
    background-color: #ff4266;
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
</style>
""", unsafe_allow_html=True)

# ======================
# SUPABASE
# ======================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

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

def delete_transaction_db(transaction_id):
    supabase.table("transactions").delete().eq("id", transaction_id).execute()

# ======================
# PARAMS
# ======================
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

if "budgets" not in st.session_state:
    st.session_state.budgets = {}

if "categories" not in st.session_state:
    st.session_state.categories = DEFAULT_CATEGORIES.copy()

def current_month():
    today = date.today()
    return f"{today.year}-{today.month:02d}"

def month_label(month):
    months = {
        "01": "Janvier", "02": "Février", "03": "Mars", "04": "Avril",
        "05": "Mai", "06": "Juin", "07": "Juillet", "08": "Août",
        "09": "Septembre", "10": "Octobre", "11": "Novembre", "12": "Décembre"
    }
    year, m = month.split("-")
    return f"{months.get(m, m)} {year}"

def format_euro(value):
    return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")

def get_budget(month, cat):
    return float(st.session_state.budgets.get(month, {}).get(cat, 0.0))

# ======================
# HEADER
# ======================
st.markdown("# Budget Couple 💕")
st.markdown("<div class='hero-subtitle'>Gérez vos dépenses, budgets et projets à deux.</div>", unsafe_allow_html=True)

tabs = st.tabs(["🏠 Dashboard", "➕ Ajouter", "☷ Historique", "◔ Budgets", "🏷️ Catégories"])

# ======================
# DASHBOARD
# ======================
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

    df = transactions.copy()
    if not df.empty:
        df = df[df["month"] == selected_month]
        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

    total_depenses = abs(df["montant"].sum()) if not df.empty else 0.0
    budget_total = sum(get_budget(selected_month, cat) for cat in st.session_state.categories)
    reste_total = budget_total - total_depenses
    nb_depenses = len(df)

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#ffd5df;">🛒</div>
            <div class="kpi-label">Dépensé</div>
            <div class="kpi-value-pink">{format_euro(total_depenses)}</div>
            <div class="badge">↑ vs budget</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#d8f3dc;">👛</div>
            <div class="kpi-label">Reste à dépenser</div>
            <div class="kpi-value-green">{format_euro(reste_total)}</div>
            <div class="badge">Suivi mensuel</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:#d7ebff;">◔</div>
            <div class="kpi-label">Budget total</div>
            <div class="kpi-value-blue">{format_euro(budget_total)}</div>
            <div class="muted">{sum(1 for c in st.session_state.categories if get_budget(selected_month, c) > 0)} catégorie budgétée</div>
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

        for cat in st.session_state.categories:
            cat_df = df[df["categorie"] == cat] if not df.empty else pd.DataFrame()
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0.0
            budget = get_budget(selected_month, cat)
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

        st.markdown("""
        <div style="background:#fff5ef;border:1px solid #ffe0cf;border-radius:18px;padding:16px;margin-top:18px;">
            💡 <b>Astuce :</b> définissez vos budgets dans l’onglet <b>Budgets</b> pour mieux suivre vos dépenses.
        </div>
        """, unsafe_allow_html=True)
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

# ======================
# AJOUTER
# ======================
with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Ajouter une dépense")

    with st.form("add_expense_form", clear_on_submit=True):
        depense_date = st.date_input("Date", value=date.today())
        libelle = st.text_input("Libellé", placeholder="Ex : Carrefour, restaurant, pharmacie...")
        montant = st.number_input("Montant", min_value=0.0, step=1.0)
        categorie = st.selectbox("Catégorie", options=st.session_state.categories)
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

# ======================
# HISTORIQUE
# ======================
with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Historique")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense.")
    else:
        months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        hist_month = st.selectbox("Mois", ["Tous"] + months, format_func=lambda x: x if x == "Tous" else month_label(x))
        hist_person = st.selectbox("Personne", ["Tous"] + DEFAULT_PEOPLE)
        hist_category = st.selectbox("Catégorie", ["Toutes"] + st.session_state.categories)

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
                hide_index=True
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

# ======================
# BUDGETS
# ======================
with tabs[3]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Budgets")

    budget_month = st.text_input("Mois", value=current_month())

    if budget_month not in st.session_state.budgets:
        st.session_state.budgets[budget_month] = {}

    for cat in st.session_state.categories:
        value = st.number_input(
            f"{CATEGORY_ICONS.get(cat, '•')} {cat}",
            min_value=0.0,
            step=10.0,
            value=float(st.session_state.budgets[budget_month].get(cat, 0.0)),
            key=f"budget_{budget_month}_{cat}"
        )
        st.session_state.budgets[budget_month][cat] = value

    st.success("Budgets enregistrés pour cette session.")
    st.caption("Prochaine étape : stocker les budgets dans Supabase.")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# CATEGORIES
# ======================
with tabs[4]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Catégories")

    for cat in st.session_state.categories:
        st.write(f"{CATEGORY_ICONS.get(cat, '•')} {cat}")

    new_cat = st.text_input("Nouvelle catégorie")

    if st.button("Ajouter catégorie"):
        clean = new_cat.strip()
        if clean and clean not in st.session_state.categories:
            st.session_state.categories.append(clean)
            st.success("Catégorie ajoutée")
            st.rerun()
        elif clean in st.session_state.categories:
            st.warning("Cette catégorie existe déjà.")

    st.caption("Prochaine étape : stocker les catégories dans Supabase.")
    st.markdown("</div>", unsafe_allow_html=True)
