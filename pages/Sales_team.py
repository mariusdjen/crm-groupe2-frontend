import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
# URL de l'API
API_URL = os.getenv("API_URL")

# Fonction pour récupérer les KPIs des équipes de vente
def fetch_kpis():
    with st.spinner("Chargement des données en cours..."):
        try:
            response = requests.get(f"{API_URL}getAllTeamsKpis/")  # API pour récupérer les KPIs des équipes
            response.raise_for_status()  # Si une erreur HTTP se produit, cela générera une exception
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"Erreur HTTP : {e}")
            return None
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            return None

# Fonction pour charger les données globales des produits
def load_global_data():
    with st.spinner("Chargement des données des produits en cours..."):
        try:
            response = requests.get(f"{API_URL}getAllProductsKpis")  # API pour récupérer les KPIs des produits
            response.raise_for_status()
            st.success("Données des produits chargées avec succès.")
            return response.json()
        except requests.RequestException as e:
            st.error(f"Erreur lors du chargement des données des produits : {e}")
            return None

# Fonction pour trouver le meilleur agent et le meilleur manager
def get_best_agent_and_manager(data):
    best_agent = max(data['total_revenue_per_agent'], key=data['total_revenue_per_agent'].get, default=None)
    best_manager = max(data['total_revenue_per_manager'], key=data['total_revenue_per_manager'].get, default=None)

    best_agent_sales = data['total_sales_per_agent'].get(best_agent, 0)
    best_agent_revenue = data['total_revenue_per_agent'].get(best_agent, 0)
    
    best_manager_sales = data['total_sales_per_manager'].get(best_manager, 0)
    best_manager_revenue = data['total_revenue_per_manager'].get(best_manager, 0)

    return best_agent, best_agent_sales, best_agent_revenue, best_manager, best_manager_sales, best_manager_revenue




def display_kpis(data):
    """Affiche les KPIs pour les meilleurs agents et managers"""
    st.title("🎯 **Évaluation des Performances de l'Équipe de Ventes**")
    st.markdown("---")

    # Meilleur Agent
    best_agent, best_agent_sales, best_agent_revenue, best_manager, best_manager_sales, best_manager_revenue = get_best_agent_and_manager(data)

    st.markdown("## 🏅 **Meilleur Agent :**")
    st.markdown(f"### 🌟 {best_agent}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Ventes", best_agent_sales)
    col2.metric("💰 Revenu Total (€)", f"{best_agent_revenue:.2f}")
    col3.metric(
        "💵 Revenu Moyen par Vente (€)",
        f"{best_agent_revenue / best_agent_sales:.2f}" if best_agent_sales > 0 else "0.00",
        delta_color="inverse"
    )

    st.markdown("---")

    # Meilleur Manager
    st.markdown("## 🏆 **Meilleur Manager :**")
    st.markdown(f"### 🌟 {best_manager}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Ventes", best_manager_sales)
    col2.metric("💰 Revenu Total (€)", f"{best_manager_revenue:.2f}")
    col3.metric(
        "💵 Revenu Moyen par Vente (€)",
        f"{best_manager_revenue / best_manager_sales:.2f}" if best_manager_sales > 0 else "0.00",
        delta_color="inverse"
    )

    st.markdown("---")

def display_agent_performance(data):
    """Affiche les performances des agents sous forme de graphiques"""
    st.header("📊 Performances des Agents de Vente")

    # Préparation des données
    agents = list(data['total_sales_per_agent'].keys())
    agent_data = pd.DataFrame({
        "Agent": agents,
        "Total des Ventes": [data['total_sales_per_agent'][agent] for agent in agents],
        "Revenu Total (€)": [data['total_revenue_per_agent'][agent] for agent in agents],
        "Revenu Moyen (€)": [data['avg_revenue_per_agent'].get(agent, 0) for agent in agents],
        "Ratio Ventes conclues  (%)": [data['won_ratio_per_agent'].get(agent, 0) for agent in agents],
        "Ratio Perdues (%)": [data['lost_ratio_per_agent'].get(agent, 0) for agent in agents],
    })

    # Graphiques
    st.plotly_chart(
        px.bar(
            agent_data, x='Agent', y=['Total des Ventes', 'Revenu Total (€)'],
            title="Ventes et Revenu Total par Agent",
            labels={"value": "Valeur", "variable": "Mesure"},
            barmode='stack', template='plotly_white',
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(
            agent_data, x='Agent', y=['Ratio Ventes conclues  (%)', 'Ratio Perdues (%)'],
            title="Ratios de Ventes conclues  et Perdues par Agent",
            labels={"value": "Ratio (%)", "variable": "Statut"},
            barmode='stack', template='plotly_white',
            color_discrete_sequence=["#2ca02c", "#d62728"]
        ),
        use_container_width=True
    )

def display_manager_performance(data):
    """Affiche les performances des managers sous forme de graphiques"""
    st.header("📊 Performances des Managers")

    # Préparation des données
    managers = list(data['total_sales_per_manager'].keys())
    manager_data = pd.DataFrame({
        "Manager": managers,
        "Total des Ventes": [data['total_sales_per_manager'][manager] for manager in managers],
        "Revenu Total (€)": [data['total_revenue_per_manager'][manager] for manager in managers],
        "Revenu Moyen (€)": [data['avg_revenue_per_manager'].get(manager, 0) for manager in managers],
        "Ratio Ventes conclues  (%)": [data['won_ratio_per_manager'].get(manager, 0) for manager in managers],
        "Ratio Perdues (%)": [data['lost_ratio_per_manager'].get(manager, 0) for manager in managers],
    })

    # Graphiques
    st.plotly_chart(
        px.bar(
            manager_data, x='Manager', y=['Total des Ventes', 'Revenu Total (€)'],
            title="Comparaison des Performances des Managers",
            labels={"value": "Valeur", "variable": "Critère"},
            barmode='group', template='plotly_white',
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.bar(
            manager_data, x='Manager', y=['Ratio Ventes conclues  (%)', 'Ratio Perdues (%)'],
            title="Ratios de Ventes conclues  et Perdues par Manager",
            labels={"value": "Ratio (%)", "variable": "Statut"},
            barmode='stack', template='plotly_white',
            color_discrete_sequence=["#2ca02c", "#d62728"]
        ),
        use_container_width=True
    )




# Fonction pour générer des recommandations basées sur les performances globales
def display_global_recommendations(data):
    st.title("🔍 **Recommandations Globales pour Améliorer les Performances**")
    st.markdown("---")  # Ligne de séparation

    # Calculer les métriques globales
    avg_agent_revenue = data['total_revenue_per_agent']
    avg_manager_revenue = data['total_revenue_per_manager']
    
    avg_agent_revenue = sum(avg_agent_revenue.values()) / len(avg_agent_revenue) if avg_agent_revenue else 0
    avg_manager_revenue = sum(avg_manager_revenue.values()) / len(avg_manager_revenue) if avg_manager_revenue else 0

    # Liste des recommandations
    recommendations = []

    if avg_agent_revenue < 1000:
        recommendations.append(("🚀", "Les agents peuvent bénéficier de **formations supplémentaires** pour améliorer leurs performances de vente."))
    else:
        recommendations.append(("🌟", "Les agents sont déjà performants. Encouragez-les à **partager leurs bonnes pratiques** avec leurs collègues."))

    if avg_manager_revenue < 2000:
        recommendations.append(("📈", "Les managers doivent peut-être **revoir leur stratégie** de gestion d'équipe et de coaching."))
    else:
        recommendations.append(("🏆", "Les managers ont une bonne gestion. Encouragez-les à **optimiser encore plus** les performances de leurs équipes."))

    # Affichage des recommandations avec mise en forme
    for icon, rec in recommendations:
        st.markdown(f"### {icon} {rec}")
        st.markdown("---")  # Ligne de séparation entre les recommandations

# Fonction principale
def main():
    # Charger les données
    data = fetch_kpis()

    if data:
        # Afficher les KPIs
        display_kpis(data)
        # Afficher les performances des agents et des managers
        display_agent_performance(data)
        display_manager_performance(data)
        # Afficher les recommandations
        display_global_recommendations(data)

# Exécution de la fonction principale
if __name__ == "__main__":
    main()
