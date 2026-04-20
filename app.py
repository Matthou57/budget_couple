import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

st.set_page_config(page_title="Budget Couple", page_icon="💸", layout="centered")

DEFAULT_CATEGORIES = ["Courses", "Restaurants", "Essence", "Loisirs", "Maison", "Santé", "Bébé", "Autres"]
DEFAULT_PEOPLE = ["Toi", "Elle", "Commun"]

@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

def debug_supabase_error(err, context="Supabase"):
    st.error(f"Erreur {context}. Vérifie les tables, la RLS/policies et les secrets Streamlit.")
    st.code(str(err))

def load_categories():
    try:
        response = supabase.table("categories").select("id,name").order("name").execute()
        rows = response.data or []

        if not rows:
            for cat in DEFAULT_CATEGORIES:
                supabase.table("categories").insert({"name": cat}).execute()

            response = supabase.table("categories").select("id,name").order("name").execute()
            rows = response.data or []

        return [row["name"] for row in rows]

    except Exception as e:
        debug_supabase_error(e, "chargement des catégories")
        return DEFAULT_CATEGORIES.copy()

def load_transactions():
    try:
        response = supabase.table("transactions").select("*").order("date", desc=True).execute()
        rows = response.data or []
        if not rows:
            return pd.DataFrame(columns=["id", "date", "month", "libelle", "montant", "categorie", "personne"])
        df = pd.DataFrame(rows)
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)
        return df
    except Exception as e:
        debug_supabase_error(e, "chargement des transactions")
        return pd.DataFrame(columns=["id", "date", "month", "libelle", "montant", "categorie", "personne"])

def load_budgets():
    try:
        response = supabase.table("budgets").select("*").execute()
        rows = response.data or []
        budgets = {}
        for row in rows:
            month = row["month"]
            category = row["category"]
            amount = float(row["amount"])
            budgets.setdefault(month, {})[category] = amount
        return budgets
    except Exception as e:
        debug_supabase_error(e, "chargement des budgets")
        return {}
