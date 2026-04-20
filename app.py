import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Budget Couple", page_icon="💸", layout="centered")

st.title("Budget Couple")

DEFAULT_CATEGORIES = ["Courses", "Restaurants", "Essence", "Loisirs", "Maison", "Santé", "Bébé", "Autres"]
DEFAULT_PEOPLE = ["Toi", "Elle", "Commun"]

if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=[
        "date", "mois", "libelle", "montant", "categorie", "personne"
    ])

if "budgets" not in st.session_state:
    st.session_state.budgets = {}

if "categories" not in st.session_state:
    st.session_state.categories = DEFAULT_CATEGORIES.copy()

def current_month():
    today = date.today()
    return f"{today.year}-{today.month:02d}"

def format_euro(value):
    return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")

tabs = st.tabs(["Dashboard", "Ajouter", "Historique", "Budgets", "Catégories"])

with tabs[0]:
    st.subheader("Vue du mois")

    all_months = sorted(
        set(st.session_state.transactions["mois"].dropna().astype(str).tolist() + [current_month()]),
        reverse=True
    )
    selected_month = st.selectbox("Mois", options=all_months, index=0)

    person_filter = st.selectbox("Filtre", ["Tous", "Toi", "Elle", "Commun"])

    df = st.session_state.transactions.copy()
    if not df.empty:
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)
        df = df[df["mois"] == selected_month]

        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

    total_depenses = abs(df["montant"].sum()) if not df.empty else 0.0
    budget_total = sum(st.session_state.budgets.get(selected_month, {}).values()) if selected_month in st.session_state.budgets else 0.0
    reste_total = budget_total - total_depenses

    c1, c2 = st.columns(2)
    c1.metric("Dépensé", format_euro(total_depenses))
    c2.metric("Reste budget", format_euro(reste_total))

    st.markdown("---")
    st.subheader("Suivi par catégorie")

    for cat in st.session_state.categories:
        cat_df = df[df["categorie"] == cat] if not df.empty else pd.DataFrame()
        spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0.0
        budget = st.session_state.budgets.get(selected_month, {}).get(cat, 0.0)
        remaining = budget - spent

        st.markdown(f"### {cat}")
        st.write(f"Budget : {format_euro(budget)}")
        st.write(f"Dépensé : {format_euro(spent)}")
        st.write(f"Reste : {format_euro(remaining)}")

        progress = 0.0
        if budget > 0:
            progress = min(spent / budget, 1.0)
        elif spent > 0:
            progress = 1.0

        st.progress(progress)

    st.markdown("---")
    st.subheader("Dernières dépenses")

    if df.empty:
        st.info("Aucune dépense pour le moment.")
    else:
        recent = df.sort_values("date", ascending=False).head(10).copy()
        recent["montant"] = recent["montant"].apply(lambda x: format_euro(abs(float(x))))
        st.dataframe(
            recent[["date", "libelle", "categorie", "personne", "montant"]],
            use_container_width=True,
            hide_index=True
        )

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
                st.error("Le libellé est obligatoire.")
            elif montant <= 0:
                st.error("Le montant doit être supérieur à 0.")
            else:
                month_value = f"{depense_date.year}-{depense_date.month:02d}"
                new_row = pd.DataFrame([{
                    "date": str(depense_date),
                    "mois": month_value,
                    "libelle": libelle.strip(),
                    "montant": -abs(float(montant)),
                    "categorie": categorie,
                    "personne": personne
                }])

                st.session_state.transactions = pd.concat(
                    [st.session_state.transactions, new_row],
                    ignore_index=True
                )
                st.success("Dépense ajoutée.")

with tabs[2]:
    st.subheader("Historique")

    df = st.session_state.transactions.copy()

    if df.empty:
        st.info("Aucune dépense enregistrée.")
    else:
        display_df = df.sort_values("date", ascending=False).copy()
        display_df["montant"] = display_df["montant"].apply(lambda x: format_euro(abs(float(x))))
        st.dataframe(
            display_df[["date", "mois", "libelle", "categorie", "personne", "montant"]],
            use_container_width=True,
            hide_index=True
        )

with tabs[3]:
    st.subheader("Budgets mensuels")

    budget_month = st.text_input("Mois", value=current_month())

    if budget_month not in st.session_state.budgets:
        st.session_state.budgets[budget_month] = {}

    for cat in st.session_state.categories:
        current_value = float(st.session_state.budgets[budget_month].get(cat, 0.0))
        new_value = st.number_input(
            f"Budget {cat}",
            min_value=0.0,
            step=10.0,
            value=current_value,
            key=f"budget_{budget_month}_{cat}"
        )
        st.session_state.budgets[budget_month][cat] = new_value

    st.success("Budgets enregistrés.")

with tabs[4]:
    st.subheader("Catégories")

    st.write("Catégories actuelles :")
    for cat in st.session_state.categories:
        st.markdown(f"- {cat}")

    new_category = st.text_input("Nouvelle catégorie")
    if st.button("Ajouter la catégorie"):
        clean = new_category.strip()
        if clean and clean not in st.session_state.categories:
            st.session_state.categories.append(clean)
            st.success(f"Catégorie ajoutée : {clean}")
            st.rerun()
