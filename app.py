import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client

st.set_page_config(page_title="Budget Couple", page_icon="💸", layout="centered")

st.title("Budget Couple")

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
# LOCAL (TEMPORAIRE)
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

# ======================
# UI
# ======================
tabs = st.tabs([
    "Dashboard",
    "Ajouter",
    "Historique",
    "Budgets",
    "Catégories"
])

# ======================
# DASHBOARD
# ======================
with tabs[0]:
    st.subheader("Vue du mois")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense pour le moment")
    else:
        all_months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        selected_month = st.selectbox("Mois", options=all_months)

        person_filter = st.selectbox("Filtre", ["Tous", "Toi", "Elle", "Commun"])

        df = df[df["month"] == selected_month]

        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

        total_depenses = abs(df["montant"].sum())
        budget_total = sum(st.session_state.budgets.get(selected_month, {}).values()) if selected_month in st.session_state.budgets else 0
        reste_total = budget_total - total_depenses

        c1, c2 = st.columns(2)
        c1.metric("Dépensé", format_euro(total_depenses))
        c2.metric("Reste budget", format_euro(reste_total))

        st.markdown("---")

        for cat in st.session_state.categories:
            cat_df = df[df["categorie"] == cat]
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0
            budget = st.session_state.budgets.get(selected_month, {}).get(cat, 0)
            remaining = budget - spent

            st.markdown(f"### {cat}")
            st.write(f"Budget : {format_euro(budget)}")
            st.write(f"Dépensé : {format_euro(spent)}")
            st.write(f"Reste : {format_euro(remaining)}")

            progress = min(spent / budget, 1.0) if budget > 0 else (1.0 if spent > 0 else 0)
            st.progress(progress)

# ======================
# AJOUT
# ======================
with tabs[1]:
    st.subheader("Ajouter une dépense")

    with st.form("add_expense_form", clear_on_submit=True):
        depense_date = st.date_input("Date", value=date.today())
        libelle = st.text_input("Libellé")
        montant = st.number_input("Montant", min_value=0.0, step=1.0)
        categorie = st.selectbox("Catégorie", options=st.session_state.categories)
        personne = st.selectbox("Qui paie ?", options=DEFAULT_PEOPLE)

        submitted = st.form_submit_button("Ajouter")

        if submitted:
            if not libelle.strip():
                st.error("Libellé obligatoire")
            elif montant <= 0:
                st.error("Montant invalide")
            else:
                add_transaction_db(depense_date, libelle, montant, categorie, personne)
                st.success("Dépense ajoutée")
                st.rerun()

# ======================
# HISTORIQUE
# ======================
with tabs[2]:
    st.subheader("Historique")

    df = get_transactions()

    if df.empty:
        st.info("Aucune dépense")
    else:
        display_df = df.sort_values("date", ascending=False).copy()
        display_df["montant"] = display_df["montant"].apply(lambda x: format_euro(abs(float(x))))

        st.dataframe(
            display_df[["date", "month", "libelle", "categorie", "personne", "montant"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Supprimer une dépense")

        options = {f"{row['date']} | {row['libelle']}": row["id"] for _, row in df.iterrows()}
        selected = st.selectbox("Choisir", ["Aucune"] + list(options.keys()))

        if selected != "Aucune":
            if st.button("Supprimer"):
                delete_transaction_db(options[selected])
                st.success("Supprimée")
                st.rerun()

# ======================
# BUDGETS (LOCAL)
# ======================
with tabs[3]:
    st.subheader("Budgets")

    budget_month = st.text_input("Mois", value=current_month())

    if budget_month not in st.session_state.budgets:
        st.session_state.budgets[budget_month] = {}

    for cat in st.session_state.categories:
        value = st.number_input(
            f"{cat}",
            min_value=0.0,
            step=10.0,
            value=float(st.session_state.budgets[budget_month].get(cat, 0.0)),
            key=f"budget_{budget_month}_{cat}"
        )

        st.session_state.budgets[budget_month][cat] = value

# ======================
# CATEGORIES (LOCAL)
# ======================
with tabs[4]:
    st.subheader("Catégories")

    for cat in st.session_state.categories:
        st.write(f"- {cat}")

    new_cat = st.text_input("Nouvelle catégorie")

    if st.button("Ajouter catégorie"):
        if new_cat and new_cat not in st.session_state.categories:
            st.session_state.categories.append(new_cat)
            st.success("Ajoutée")
            st.rerun()
