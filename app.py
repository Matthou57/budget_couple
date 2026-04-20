import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

st.set_page_config(
    page_title="Budget Couple",
    page_icon="💸",
    layout="centered"
)

st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 720px;
    }
    div[data-testid="stMetric"] {
        background: #f7f7f7;
        border-radius: 14px;
        padding: 12px;
        border: 1px solid #eaeaea;
    }
    .category-card {
        padding: 14px;
        border-radius: 16px;
        background: #fafafa;
        border: 1px solid #ececec;
        margin-bottom: 12px;
    }
    .small-muted {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Budget Couple")

DEFAULT_CATEGORIES = ["Courses", "Restaurants", "Essence", "Loisirs", "Maison", "Santé", "Bébé", "Autres"]
DEFAULT_PEOPLE = ["Toi", "Elle", "Commun"]


@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()


def current_month():
    today = date.today()
    return f"{today.year}-{today.month:02d}"


def format_euro(value):
    return f"{float(value):,.2f} €".replace(",", " ").replace(".", ",")


def load_categories():
    response = supabase.table("categories").select("*").order("name").execute()
    rows = response.data or []
    if not rows:
        for cat in DEFAULT_CATEGORIES:
            supabase.table("categories").insert({"name": cat}).execute()
        response = supabase.table("categories").select("*").order("name").execute()
        rows = response.data or []
    return [row["name"] for row in rows]


def load_transactions():
    response = supabase.table("transactions").select("*").order("date", desc=True).execute()
    rows = response.data or []
    if not rows:
        return pd.DataFrame(columns=["id", "date", "month", "libelle", "montant", "categorie", "personne"])
    df = pd.DataFrame(rows)
    df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)
    return df


def load_budgets():
    response = supabase.table("budgets").select("*").execute()
    rows = response.data or []
    budgets = {}
    for row in rows:
        month = row["month"]
        category = row["category"]
        amount = float(row["amount"])
        budgets.setdefault(month, {})[category] = amount
    return budgets


def save_budget(month, category, amount):
    existing = (
        supabase.table("budgets")
        .select("id")
        .eq("month", month)
        .eq("category", category)
        .execute()
    )
    if existing.data:
        budget_id = existing.data[0]["id"]
        supabase.table("budgets").update({"amount": float(amount)}).eq("id", budget_id).execute()
    else:
        supabase.table("budgets").insert({
            "month": month,
            "category": category,
            "amount": float(amount)
        }).execute()


def add_transaction(depense_date, libelle, montant, categorie, personne):
    month_value = f"{depense_date.year}-{depense_date.month:02d}"
    supabase.table("transactions").insert({
        "date": str(depense_date),
        "month": month_value,
        "libelle": libelle.strip(),
        "montant": -abs(float(montant)),
        "categorie": categorie,
        "personne": personne
    }).execute()


def delete_transaction(transaction_id):
    supabase.table("transactions").delete().eq("id", transaction_id).execute()


def add_category(name):
    supabase.table("categories").insert({"name": name.strip()}).execute()


def delete_category(name):
    supabase.table("categories").delete().eq("name", name).execute()


def budget_progress(spent, budget):
    if budget <= 0:
        return 0 if spent <= 0 else 1
    return min(spent / budget, 1.0)


def budget_status(spent, budget):
    if budget <= 0 and spent > 0:
        return "Aucun budget"
    if budget <= 0:
        return "OK"
    ratio = spent / budget if budget else 0
    if ratio < 0.8:
        return "OK"
    elif ratio <= 1:
        return "Attention"
    return "Dépassé"


categories = load_categories()
transactions = load_transactions()
budgets = load_budgets()

tabs = st.tabs(["Dashboard", "Ajouter", "Historique", "Budgets", "Catégories"])

with tabs[0]:
    st.subheader("Vue du mois")

    all_months = sorted(
        set(transactions["month"].dropna().astype(str).tolist() + [current_month()]),
        reverse=True
    ) if not transactions.empty else [current_month()]

    selected_month = st.selectbox("Mois", options=all_months, index=0)

    person_filter = st.segmented_control(
        "Filtre",
        options=["Tous", "Toi", "Elle", "Commun"],
        default="Tous"
    )

    df = transactions.copy()
    if not df.empty:
        df = df[df["month"] == selected_month]
        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

    total_depenses = abs(df["montant"].sum()) if not df.empty else 0.0
    budget_total = sum(budgets.get(selected_month, {}).get(cat, 0.0) for cat in categories)
    reste_total = budget_total - total_depenses
    nb_depenses = len(df) if not df.empty else 0

    c1, c2 = st.columns(2)
    c1.metric("Dépensé", format_euro(total_depenses))
    c2.metric("Reste budget", format_euro(reste_total))

    c3, c4 = st.columns(2)
    c3.metric("Budget total", format_euro(budget_total))
    c4.metric("Nb dépenses", nb_depenses)

    st.markdown("---")
    st.subheader("Suivi par catégorie")

    if df.empty and budget_total == 0:
        st.info("Aucune donnée pour ce mois.")
    else:
        for cat in categories:
            cat_df = df[df["categorie"] == cat] if not df.empty else pd.DataFrame()
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0.0
            budget = budgets.get(selected_month, {}).get(cat, 0.0)
            remaining = budget - spent
            progress = budget_progress(spent, budget)
            status = budget_status(spent, budget)

            st.markdown('<div class="category-card">', unsafe_allow_html=True)
            x1, x2 = st.columns([2, 1])
            x1.markdown(f"**{cat}**")
            x2.markdown(f"<div style='text-align:right'>{status}</div>", unsafe_allow_html=True)
            st.progress(progress)

            y1, y2, y3 = st.columns(3)
            y1.metric("Budget", format_euro(budget))
            y2.metric("Dépensé", format_euro(spent))
            y3.metric("Reste", format_euro(remaining))
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Dernières dépenses")

    if df.empty:
        st.caption("Aucune dépense sur ce mois.")
    else:
        recent = df.sort_values("date", ascending=False).head(10).copy()
        recent["montant"] = recent["montant"].apply(lambda x: format_euro(abs(x)))
        st.dataframe(
            recent[["date", "libelle", "categorie", "personne", "montant"]],
            use_container_width=True,
            hide_index=True
        )

with tabs[1]:
    st.subheader("Ajouter une dépense")

    with st.form("add_expense_form", clear_on_submit=True):
        depense_date = st.date_input("Date", value=date.today())
        libelle = st.text_input("Libellé", placeholder="Exemple : Carrefour, Total, Netflix")
        montant = st.number_input("Montant", min_value=0.0, step=1.0)
        categorie = st.selectbox("Catégorie", options=categories)
        personne = st.selectbox("Qui paie ?", options=DEFAULT_PEOPLE)

        submitted = st.form_submit_button("Ajouter la dépense")

        if submitted:
            if not libelle.strip():
                st.error("Le libellé est obligatoire.")
            elif montant <= 0:
                st.error("Le montant doit être supérieur à 0.")
            else:
                add_transaction(depense_date, libelle, montant, categorie, personne)
                st.success("Dépense ajoutée.")
                st.rerun()

with tabs[2]:
    st.subheader("Historique des dépenses")

    df = transactions.copy()

    if df.empty:
        st.info("Aucune dépense enregistrée.")
    else:
        months = sorted(df["month"].dropna().unique().tolist(), reverse=True)
        hist_month = st.selectbox("Filtrer par mois", options=["Tous"] + months)
        hist_person = st.selectbox("Filtrer par personne", options=["Tous"] + DEFAULT_PEOPLE)
        hist_category = st.selectbox("Filtrer par catégorie", options=["Toutes"] + categories)

        filtered = df.copy()

        if hist_month != "Tous":
            filtered = filtered[filtered["month"] == hist_month]
        if hist_person != "Tous":
            filtered = filtered[filtered["personne"] == hist_person]
        if hist_category != "Toutes":
            filtered = filtered[filtered["categorie"] == hist_category]

        filtered = filtered.sort_values("date", ascending=False).copy()

        if filtered.empty:
            st.warning("Aucune dépense avec ces filtres.")
        else:
            display_df = filtered.copy()
            display_df["montant"] = display_df["montant"].apply(lambda x: format_euro(abs(float(x))))
            st.dataframe(
                display_df[["date", "month", "libelle", "categorie", "personne", "montant"]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Supprimer une dépense")
            options_map = {}
            for _, row in filtered.iterrows():
                label = f"{row['date']} | {row['libelle']} | {row['categorie']} | {format_euro(abs(float(row['montant'])))}"
                options_map[label] = row["id"]

            selected_label = st.selectbox("Choisir une dépense", options=["Aucune"] + list(options_map.keys()))
            if selected_label != "Aucune":
                if st.button("Supprimer la dépense"):
                    delete_transaction(options_map[selected_label])
                    st.success("Dépense supprimée.")
                    st.rerun()

with tabs[3]:
    st.subheader("Budgets mensuels")

    existing_months = sorted(
        set(transactions["month"].dropna().astype(str).tolist() + [current_month()]),
        reverse=True
    ) if not transactions.empty else [current_month()]

    budget_month = st.selectbox("Mois à configurer", options=existing_months)

    for cat in categories:
        current_value = float(budgets.get(budget_month, {}).get(cat, 0.0))
        new_value = st.number_input(
            f"Budget {cat}",
            min_value=0.0,
            step=10.0,
            value=current_value,
            key=f"budget_{budget_month}_{cat}"
        )
        if new_value != current_value:
            save_budget(budget_month, cat, new_value)

    st.success("Budgets synchronisés avec Supabase.")

with tabs[4]:
    st.subheader("Catégories")

    st.write("Catégories actuelles :")
    for cat in categories:
        st.markdown(f"- {cat}")

    with st.form("add_category_form", clear_on_submit=True):
        new_category = st.text_input("Ajouter une catégorie", placeholder="Exemple : Vacances")
        add_cat_btn = st.form_submit_button("Ajouter la catégorie")

        if add_cat_btn:
            clean_cat = new_category.strip()
            if not clean_cat:
                st.error("Le nom de catégorie est vide.")
            elif clean_cat in categories:
                st.warning("Cette catégorie existe déjà.")
            else:
                add_category(clean_cat)
                st.success(f"Catégorie '{clean_cat}' ajoutée.")
                st.rerun()

    removable = [c for c in categories if c != "Autres"]
    to_delete = st.selectbox("Supprimer une catégorie", options=["Aucune"] + removable)

    if to_delete != "Aucune":
        st.warning("Évite de supprimer une catégorie déjà utilisée par beaucoup de dépenses.")
        if st.button("Supprimer la catégorie"):
            delete_category(to_delete)
            st.success(f"Catégorie '{to_delete}' supprimée.")
            st.rerun()
