import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Budget Couple", page_icon="💸", layout="centered")

# ======================
# DESIGN
# ======================
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 760px;
}

body {
    background-color: #f7f2ec;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f7f2ec 0%, #ffffff 45%);
}

h1 {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em;
}

h2, h3 {
    letter-spacing: -0.02em;
}

div[data-testid="stMetric"] {
    background: white;
    border-radius: 18px;
    padding: 16px;
    border: 1px solid #eadfD3;
    box-shadow: 0 8px 24px rgba(80, 55, 30, 0.08);
}

.card {
    background: white;
    border: 1px solid #eadfD3;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(80, 55, 30, 0.07);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.muted {
    color: #7c6f64;
    font-size: 0.9rem;
}

.good {
    color: #1f7a4d;
    font-weight: 700;
}

.warn {
    color: #b36b00;
    font-weight: 700;
}

.bad {
    color: #b42318;
    font-weight: 700;
}

.stButton button {
    border-radius: 14px;
    padding: 0.65rem 1rem;
    font-weight: 700;
    border: 1px solid #d8c8b8;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 8px 12px;
    background: rgba(255,255,255,0.65);
}
</style>
""", unsafe_allow_html=True)

st.title("Budget Couple")
st.caption("Suivi simple de vos dépenses, budgets et catégories.")

# ======================
# SUPABASE
# ======================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def get_transactions():
    res = supabase.table("transactions").select("*").order("date", desc=True).execute()
    data = res.data if res.data else []
    return pd.DataFrame(data)

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
# LOCAL TEMPORAIRE
# ======================
DEFAULT_CATEGORIES = ["Courses", "Restaurants", "Essence", "Loisirs", "Maison", "Santé", "Bébé", "Autres"]
DEFAULT_PEOPLE = ["Toi", "Elle", "Commun"]

if "budgets" not in st.session_state:
    st.session_state.budgets = {}

if "categories" not in st.session_state:
    st.session_state.categories = DEFAULT_CATEGORIES.copy()

def current_month():
    today = date.today()
    return f"{today.year}-{today.month:02d}"

def format_euro(value):
    return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")

def status_label(spent, budget):
    if budget <= 0 and spent > 0:
        return "<span class='warn'>Aucun budget</span>"
    if budget <= 0:
        return "<span class='muted'>Non défini</span>"
    ratio = spent / budget
    if ratio < 0.75:
        return "<span class='good'>OK</span>"
    if ratio <= 1:
        return "<span class='warn'>Attention</span>"
    return "<span class='bad'>Dépassé</span>"

# ======================
# UI
# ======================
tabs = st.tabs(["Dashboard", "Ajouter", "Historique", "Budgets", "Catégories"])

# ======================
# DASHBOARD
# ======================
with tabs[0]:
    st.subheader("Vue du mois")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense pour le moment.")
    else:
        all_months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        selected_month = st.selectbox("Mois", options=all_months)

        person_filter = st.segmented_control(
            "Filtre",
            ["Tous", "Toi", "Elle", "Commun"],
            default="Tous"
        )

        df = df[df["month"] == selected_month]

        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)

        total_depenses = abs(df["montant"].sum())
        budget_total = sum(st.session_state.budgets.get(selected_month, {}).values()) if selected_month in st.session_state.budgets else 0
        reste_total = budget_total - total_depenses
        nb_depenses = len(df)

        c1, c2 = st.columns(2)
        c1.metric("Dépensé", format_euro(total_depenses))
        c2.metric("Reste", format_euro(reste_total))

        c3, c4 = st.columns(2)
        c3.metric("Budget total", format_euro(budget_total))
        c4.metric("Dépenses", nb_depenses)

        st.markdown("---")
        st.subheader("Budgets par catégorie")

        for cat in st.session_state.categories:
            cat_df = df[df["categorie"] == cat]
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0
            budget = st.session_state.budgets.get(selected_month, {}).get(cat, 0)
            remaining = budget - spent
            progress = min(spent / budget, 1.0) if budget > 0 else (1.0 if spent > 0 else 0)

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="card-title">{cat}</div>
                <div class="muted">Statut : {status_label(spent, budget)}</div>
                """,
                unsafe_allow_html=True
            )

            st.progress(progress)

            a, b, c = st.columns(3)
            a.metric("Budget", format_euro(budget))
            b.metric("Dépensé", format_euro(spent))
            c.metric("Reste", format_euro(remaining))

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Dernières dépenses")

        if df.empty:
            st.caption("Aucune dépense sur ce filtre.")
        else:
            recent = df.sort_values("date", ascending=False).head(8).copy()
            recent["montant"] = recent["montant"].apply(lambda x: format_euro(abs(float(x))))
            st.dataframe(
                recent[["date", "libelle", "categorie", "personne", "montant"]],
                use_container_width=True,
                hide_index=True
            )

# ======================
# AJOUT
# ======================
with tabs[1]:
    st.subheader("Ajouter une dépense")
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    with st.form("add_expense_form", clear_on_submit=True):
        depense_date = st.date_input("Date", value=date.today())
        libelle = st.text_input("Libellé", placeholder="Ex : Carrefour, Total, restaurant...")
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
    st.subheader("Historique")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense.")
    else:
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)

        months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        hist_month = st.selectbox("Mois", ["Tous"] + months)
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

# ======================
# BUDGETS
# ======================
with tabs[3]:
    st.subheader("Budgets")
    st.caption("Pour l’instant les budgets restent locaux. Prochaine étape : les stocker dans Supabase.")

    budget_month = st.text_input("Mois", value=current_month())

    if budget_month not in st.session_state.budgets:
        st.session_state.budgets[budget_month] = {}

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    for cat in st.session_state.categories:
        value = st.number_input(
            f"{cat}",
            min_value=0.0,
            step=10.0,
            value=float(st.session_state.budgets[budget_month].get(cat, 0.0)),
            key=f"budget_{budget_month}_{cat}"
        )
        st.session_state.budgets[budget_month][cat] = value

    st.success("Budgets enregistrés pour cette session.")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# CATEGORIES
# ======================
with tabs[4]:
    st.subheader("Catégories")
    st.caption("Pour l’instant les catégories restent locales. Prochaine étape : les stocker dans Supabase.")

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    for cat in st.session_state.categories:
        st.write(f"• {cat}")

    new_cat = st.text_input("Nouvelle catégorie")

    if st.button("Ajouter catégorie"):
        clean = new_cat.strip()
        if clean and clean not in st.session_state.categories:
            st.session_state.categories.append(clean)
            st.success("Catégorie ajoutée")
            st.rerun()
        elif clean in st.session_state.categories:
            st.warning("Cette catégorie existe déjà.")

    st.markdown("</div>", unsafe_allow_html=True)
