import streamlit as st
import pandas as pd

st.set_page_config(page_title="Budget Couple", layout="wide")

st.title("Suivi Budget Couple")

# Initialisation
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["date", "libelle", "montant", "categorie", "personne"])

if "budgets" not in st.session_state:
    st.session_state.budgets = {}

menu = st.sidebar.radio("Menu", ["Budgets", "Ajouter dépense", "Dashboard"])

# --- BUDGETS ---
if menu == "Budgets":
    st.header("Budgets mensuels")

    categories = ["Courses", "Restaurants", "Essence", "Loisirs"]

    for cat in categories:
        st.session_state.budgets[cat] = st.number_input(f"{cat}", min_value=0, step=50, key=cat)

# --- AJOUT DEPENSE ---
elif menu == "Ajouter dépense":
    st.header("Ajouter une dépense")

    date = st.date_input("Date")
    libelle = st.text_input("Libellé")
    montant = st.number_input("Montant", step=1.0)
    categorie = st.selectbox("Catégorie", ["Courses", "Restaurants", "Essence", "Loisirs"])
    personne = st.selectbox("Qui ?", ["Toi", "Elle", "Commun"])

    if st.button("Ajouter"):
        new_row = pd.DataFrame([[date, libelle, -abs(montant), categorie, personne]],
                               columns=st.session_state.transactions.columns)
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
        st.success("Dépense ajoutée")

# --- DASHBOARD ---
elif menu == "Dashboard":
    st.header("Dashboard")

    df = st.session_state.transactions

    if df.empty:
        st.info("Aucune dépense pour le moment")
    else:
        resume = df.groupby("categorie")["montant"].sum()

        for cat, total in resume.items():
            budget = st.session_state.budgets.get(cat, 0)
            reste = budget + total

            st.subheader(cat)
            st.write(f"Dépensé : {abs(total):.2f} €")
            st.write(f"Budget : {budget:.2f} €")
            st.write(f"Reste : {reste:.2f} €")

            if reste < 0:
                st.error("Budget dépassé")
            elif reste < budget * 0.2:
                st.warning("Attention, presque fini")
            else:
                st.success("OK")
