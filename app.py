import streamlit as st
import pandas as pd
from datetime import date

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
        max-width: 700px;
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
    return f"{value:,.2f} €".replace(",", " ").replace(".", ",")

def get_month_categories():
    return st.session_state.categories

def get_budget(month, category):
    return st.session_state.budgets.get(month, {}).get(category, 0.0)

def set_budget(month, category, amount):
    if month not in st.session_state.budgets:
        st.session_state.budgets[month] = {}
    st.session_state.budgets[month][category] = float(amount)

def budget_progress(spent, budget):
    if budget <= 0:
        return 0 if spent <= 0 else 1
    return min(spent / budget, 1.0)

def budget_status(spent, budget):
    if budget <= 0 and spent > 0:
        return "Aucun budget défini"
    if budget <= 0:
        return "OK"
    ratio = spent / budget if budget else 0
    if ratio < 0.8:
        return "OK"
    elif ratio <= 1:
        return "Attention"
    return "Dépassé"

tabs = st.tabs(["Dashboard", "Ajouter", "Historique", "Budgets", "Catégories"])

with tabs[0]:
    st.subheader("Vue du mois")

    all_months = sorted(
        set(st.session_state.transactions["mois"].dropna().astype(str).tolist() + [current_month()]),
        reverse=True
    )
    selected_month = st.selectbox("Mois", options=all_months, index=0)

    person_filter = st.segmented_control(
        "Filtre",
        options=["Tous", "Toi", "Elle", "Commun"],
        default="Tous"
    )

    df = st.session_state.transactions.copy()
    if not df.empty:
        df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0.0)
        df = df[df["mois"] == selected_month]

        if person_filter != "Tous":
            df = df[df["personne"] == person_filter]

    total_depenses = abs(df["montant"].sum()) if not df.empty else 0.0
    nb_depenses = len(df) if not df.empty else 0
    budget_total = sum(get_budget(selected_month, cat) for cat in get_month_categories())
    reste_total = budget_total - total_depenses

    col1, col2 = st.columns(2)
    col1.metric("Dépensé", format_euro(total_depenses))
    col2.metric("Reste budget", format_euro(reste_total))

    col3, col4 = st.columns(2)
    col3.metric("Budget total", format_euro(budget_total))
    col4.metric("Nb dépenses", nb_depenses)

    st.markdown("---")
    st.subheader("Suivi par catégorie")

    categories = get_month_categories()

    if df.empty and budget_total == 0:
        st.info("Aucune donnée pour ce mois. Commence par définir des budgets et ajouter des dépenses.")
    else:
        for cat in categories:
            cat_df = df[df["categorie"] == cat] if not df.empty else pd.DataFrame()
            spent = abs(cat_df["montant"].sum()) if not cat_df.empty else 0.0
            budget = get_budget(selected_month, cat)
            remaining = budget - spent
            progress = budget_progress(spent, budget)
            status = budget_status(spent, budget)

            st.markdown('<div class="category-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"**{cat}**")
            c2.markdown(f"<div style='text-align:right'>{status}</div>", unsafe_allow_html=True)

            st.progress(progress)

            d1, d2, d3 = st.columns(3)
            d1.metric("Budget", format_euro(budget))
            d2.metric("Dépensé", format_euro(spent))
            d3.metric("Reste", format_euro(remaining))
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
        libelle = st.text_input("Libellé", placeholder="Exemple : Carrefour, Total, Netflix...")
        montant = st.number_input("Montant", min_value=0.0, step=1.0)
        categorie = st.selectbox("Catégorie", options=get_month_categories())
        personne = st.selectbox("Qui paie ?", options=DEFAULT_PEOPLE)

        submitted = st.form_submit_button("Ajouter la dépense")

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
    st.subheader("Historique des dépenses")

    df = st.session_state.transactions.copy()

    if df.empty:
        st.info("Aucune dépense enregistrée.")
    else:
        months = sorted(df["mois"].dropna().unique().tolist(), reverse=True)
        hist_month = st.selectbox("Filtrer par mois", options=["Tous"] + months)
        hist_person = st.selectbox("Filtrer par personne", options=["Tous"] + DEFAULT_PEOPLE)
        hist_category = st.selectbox("Filtrer par catégorie", options=["Toutes"] + get_month_categories())

        filtered = df.copy()

        if hist_month != "Tous":
            filtered = filtered[filtered["mois"] == hist_month]
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
                display_df[["date", "mois", "libelle", "categorie", "personne", "montant"]],
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Supprimer une ligne")
            indices = filtered.index.tolist()
            labels = [
                f"{filtered.loc[i, 'date']} | {filtered.loc[i, 'libelle']} | {filtered.loc[i, 'categorie']} | {format_euro(abs(float(filtered.loc[i, 'montant'])))}"
                for i in indices
            ]

            selected_label = st.selectbox("Choisir une dépense à supprimer", options=["Aucune"] + labels)

            if selected_label != "Aucune":
                selected_idx = indices[labels.index(selected_label)]
                if st.button("Supprimer la dépense"):
                    st.session_state.transactions = st.session_state.transactions.drop(index=selected_idx).reset_index(drop=True)
                    st.success("Dépense supprimée.")
                    st.rerun()

with tabs[3]:
    st.subheader("Budgets mensuels")

    existing_months = sorted(
        set(st.session_state.transactions["mois"].dropna().astype(str).tolist() + [current_month()]),
        reverse=True
    )

    budget_month = st.selectbox("Mois à configurer", options=existing_months, key="budget_month_select")

    st.markdown(f"<div class='small-muted'>Configure les montants pour {budget_month}</div>", unsafe_allow_html=True)

    for cat in get_month_categories():
        current_value = float(get_budget(budget_month, cat))
        new_value = st.number_input(
            f"Budget {cat}",
            min_value=0.0,
            step=10.0,
            value=current_value,
            key=f"budget_{budget_month}_{cat}"
        )
        set_budget(budget_month, cat, new_value)

    st.success("Budgets enregistrés automatiquement.")

with tabs[4]:
    st.subheader("Catégories")

    st.write("Catégories actuelles :")
    for cat in get_month_categories():
        st.markdown(f"- {cat}")

    with st.form("add_category_form", clear_on_submit=True):
        new_category = st.text_input("Ajouter une catégorie", placeholder="Exemple : Vacances")
        add_cat = st.form_submit_button("Ajouter la catégorie")

        if add_cat:
            clean_cat = new_category.strip()
            if not clean_cat:
                st.error("Le nom de catégorie est vide.")
            elif clean_cat in st.session_state.categories:
                st.warning("Cette catégorie existe déjà.")
            else:
                st.session_state.categories.append(clean_cat)
                st.success(f"Catégorie '{clean_cat}' ajoutée.")
                st.rerun()

    st.markdown("### Supprimer une catégorie")
    removable = [c for c in get_month_categories() if c != "Autres"]

    if removable:
        to_delete = st.selectbox("Choisir une catégorie à supprimer", options=["Aucune"] + removable)
        if to_delete != "Aucune":
            st.warning("Les anciennes dépenses gardent leur valeur actuelle. Évite de supprimer une catégorie déjà beaucoup utilisée.")
            if st.button("Supprimer la catégorie"):
                st.session_state.categories.remove(to_delete)
                st.success(f"Catégorie '{to_delete}' supprimée.")
                st.rerun()
