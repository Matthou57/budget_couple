{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
\
st.set_page_config(page_title="Budget Couple", layout="wide")\
\
st.title("\uc0\u55357 \u56496  Suivi Budget Couple")\
\
# Initialisation session\
if "transactions" not in st.session_state:\
    st.session_state.transactions = pd.DataFrame(columns=["date", "libelle", "montant", "categorie", "personne"])\
\
if "budgets" not in st.session_state:\
    st.session_state.budgets = \{\}\
\
# --- MENU ---\
menu = st.sidebar.radio("Menu", ["Budgets", "Ajouter d\'e9pense", "Dashboard"])\
\
# --- BUDGETS ---\
if menu == "Budgets":\
    st.header("Budgets mensuels")\
\
    categories = ["Courses", "Restaurants", "Essence", "Loisirs"]\
\
    for cat in categories:\
        st.session_state.budgets[cat] = st.number_input(f"\{cat\}", min_value=0, step=50, key=cat)\
\
# --- AJOUT DEPENSE ---\
elif menu == "Ajouter d\'e9pense":\
    st.header("Ajouter une d\'e9pense")\
\
    date = st.date_input("Date")\
    libelle = st.text_input("Libell\'e9")\
    montant = st.number_input("Montant", step=1.0)\
    categorie = st.selectbox("Cat\'e9gorie", ["Courses", "Restaurants", "Essence", "Loisirs"])\
    personne = st.selectbox("Qui ?", ["Toi", "Elle", "Commun"])\
\
    if st.button("Ajouter"):\
        new_row = pd.DataFrame([[date, libelle, -abs(montant), categorie, personne]],\
                               columns=st.session_state.transactions.columns)\
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)\
        st.success("D\'e9pense ajout\'e9e")\
\
# --- DASHBOARD ---\
elif menu == "Dashboard":\
    st.header("Dashboard")\
\
    df = st.session_state.transactions\
\
    if df.empty:\
        st.info("Aucune d\'e9pense pour le moment")\
    else:\
        resume = df.groupby("categorie")["montant"].sum()\
\
        for cat, total in resume.items():\
            budget = st.session_state.budgets.get(cat, 0)\
            reste = budget + total  # total est n\'e9gatif\
\
            st.subheader(cat)\
            st.write(f"D\'e9pens\'e9 : \{abs(total):.2f\} \'80")\
            st.write(f"Budget : \{budget:.2f\} \'80")\
            st.write(f"Reste : \{reste:.2f\} \'80")\
\
            if reste < 0:\
                st.error("Budget d\'e9pass\'e9")\
            elif reste < budget * 0.2:\
                st.warning("Attention, presque fini")\
            else:\
                st.success("OK")}