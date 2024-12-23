import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# URL de l'API FastAPI
API_URL = os.getenv("API_URL")

# Configuration de la page
st.set_page_config(page_title="Dashboard Ventes", page_icon="📊", layout="wide")
st.title("📊 Dashboard  Performances Ventes")

# Fonction pour charger les données globales
def load_global_data():
    with st.spinner("Chargement des données en cours..."):
        try:
            response = requests.get(f"{API_URL}getAllProductsKpis")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Erreur lors du chargement des données : {e}")
            return None

# Fonction pour obtenir la liste des produits
def get_products():
    try:
        response = requests.get(f"{API_URL}/getAllProducts")
        response.raise_for_status()
        data = response.json()
        products = [product['fields']['product'] for product in data]
        return products
    except requests.RequestException as e:
        st.error(f"Erreur lors du chargement des produits : {e}")
        return []

# Fonction pour obtenir les KPIs d'un produit spécifique
def get_product_kpis(product_name):
    try:
        response = requests.get(f"{API_URL}/getProductKpis/{product_name}")
        response.raise_for_status()
        data = response.json()
        if "message" in data:
            st.error(data["message"])
            return None
        return data
    except requests.RequestException as e:
        st.error(f"Erreur lors du chargement des données pour le produit '{product_name}': {e}")
        return None

# Fonction pour afficher les KPIs globaux
def display_global_kpis(kpi_data):
    st.markdown("<h2 style='text-align: center; color: #00ED9A;'>Vue d'ensemble des performances</h2>", unsafe_allow_html=True)
    
    # Première ligne de métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Revenu Total", f"{kpi_data['total_revenue']:,.2f} €")
    col2.metric("🎯 Ventes conclues ", kpi_data["total_sales_won"])
    col3.metric("💼 Ventes en cours", kpi_data["total_sales_engaging"])
    col4.metric("❌ Ventes Perdues", kpi_data["total_sales_lost"])

    # Deuxième ligne de métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💡 Revenu Moyen par Produit", f"{kpi_data['avg_revenue_per_product']:,.2f} €")
    col2.metric("🚀 Taux d'Engagement", f"{kpi_data['engagement_rate']*100:.2f}%")
    col3.metric("📊 Revenus Gagnés", f"{kpi_data['total_won_revenue']:,.2f} €")
    col4.metric("📉 Revenus Perdus", f"{kpi_data['total_lost_revenue']:,.2f} €")

    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en anneau pour la répartition des ventes
        fig_sales = go.Figure(data=[go.Pie(
            labels=['Gagnées', 'En cours', 'Perdues', 'Prospection'], 
            values=[kpi_data['total_sales_won'], kpi_data['total_sales_engaging'], 
                    kpi_data['total_sales_lost'], kpi_data['total_sales_prospecting']],
            hole=.3,
            marker_colors=['#00ED9A', '#FFA500', '#FF6347', '#4169E1']
        )])
        fig_sales.update_layout(title_text="Répartition des Ventes")
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        # Graphique en barres pour les revenus par secteur
        sector_revenue = pd.DataFrame(list(kpi_data['total_revenue_per_sector'].items()), 
                                      columns=['Secteur', 'Revenu'])
        sector_revenue = sector_revenue.sort_values('Revenu', ascending=False).head(5)
        fig_sector = px.bar(sector_revenue, x='Secteur', y='Revenu', 
                            title="Top 5 des Revenus par Secteur",
                            color='Revenu', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_sector, use_container_width=True)

    # Analyse et recommandations
    st.markdown("### 📊 Analyse et Recommandations")
    
    engagement_rate = kpi_data['engagement_rate']
    if engagement_rate >= 0.5:
        st.success(f"🎉 Excellent taux d'engagement de {engagement_rate*100:.2f}% ! Continuez vos stratégies actuelles.")
    elif engagement_rate >= 0.3:
        st.warning(f"⚠️ Taux d'engagement moyen de {engagement_rate*100:.2f}%. Cherchez à améliorer vos techniques d'engagement client.")
    else:
        st.error(f"🚨 Faible taux d'engagement de {engagement_rate*100:.2f}%. Une révision urgente de vos stratégies d'engagement est nécessaire.")

    win_rate = kpi_data['total_sales_won'] / (kpi_data['total_sales_won'] + kpi_data['total_sales_lost'])
    if win_rate >= 0.7:
        st.success(f"🏆 Excellent taux de réussite des ventes de {win_rate*100:.2f}% ! Votre équipe performe très bien.")
    elif win_rate >= 0.5:
        st.info(f"ℹ️ Taux de réussite des ventes correct de {win_rate*100:.2f}%. Il y a encore de la marge d'amélioration.")
    else:
        st.warning(f"⚠️ Faible taux de réussite des ventes de {win_rate*100:.2f}%. Formez votre équipe pour améliorer ce taux.")

    top_sector = max(kpi_data['total_revenue_per_sector'], key=kpi_data['total_revenue_per_sector'].get)
    st.info(f"💡 Le secteur le plus performant est '{top_sector}'. Concentrez-vous sur ce secteur pour maximiser vos revenus.")

    if kpi_data['total_sales_prospecting'] > 0:
        st.info(f"🎯 Vous avez {kpi_data['total_sales_prospecting']} opportunités en phase de prospection. Assurez-vous de les convertir en engagements.")

    st.empty()

# Fonction pour afficher les graphiques globaux
def display_global_charts(kpi_data):
    st.html('<h3 style="color: #00ED9A;">Répartition des Revenus(en €) et du nombre de Ventes par Mois </h3>')

    if "revenue_per_month" in kpi_data and "sales_per_month" in kpi_data:
        revenue_month_data = pd.DataFrame({
            "Mois": list(kpi_data["revenue_per_month"].keys()),
            "Revenu Total": list(kpi_data["revenue_per_month"].values())
        })

        sales_month_data = pd.DataFrame({
            "Mois": list(kpi_data["sales_per_month"].keys()),
            "Ventes Totales": list(kpi_data["sales_per_month"].values())
        })

        col1, col2 = st.columns(2)

        with col1:
            fig_revenue_month = px.bar(revenue_month_data, x="Mois", y="Revenu Total",
                                       title="Revenus par Mois",
                                       color="Revenu Total", color_continuous_scale=px.colors.sequential.Plasma)
            fig_revenue_month.update_layout(template="plotly_dark", xaxis_title="Mois", yaxis_title="Revenu Total (€)")
            fig_revenue_month.update_yaxes(tickprefix="€", tickformat=".2f")
            st.plotly_chart(fig_revenue_month, use_container_width=True, key="revenue_month_chart")

        with col2:
            fig_sales_month = px.bar(sales_month_data, x="Mois", y="Ventes Totales",
                                     title="Nombre de Ventes par Mois",
                                     color="Ventes Totales", color_continuous_scale=px.colors.sequential.Viridis)
            fig_sales_month.update_layout(template="plotly_dark", xaxis_title="Mois", yaxis_title="Nombre de Ventes")
            st.plotly_chart(fig_sales_month, use_container_width=True, key="sales_month_chart")

    else:
        st.error("Les données des revenus et des ventes par mois ne sont pas disponibles.")

    st.html('<h3 style="color: #00ED9A;">Visualisation du nombre de produits vendus et des revenus par secteur.  </h3>')

    col1, col2 = st.columns(2)

    with col1:
        sector_data = pd.DataFrame({
            "Secteur": list(kpi_data["products_per_sector"].keys()),
            "Nombre de Produits": list(kpi_data["products_per_sector"].values()),
        })

        fig_sector = px.bar(sector_data, x="Secteur", y="Nombre de Produits", title="Nombre de produits vendus par secteur",
                            color="Secteur", color_continuous_scale='Viridis')
        fig_sector.update_layout(xaxis_title="Secteur", yaxis_title="Nombre de Produits",
                                template="plotly_dark", plot_bgcolor="#2b2b2b")
        st.plotly_chart(fig_sector, use_container_width=True, key="sector_chart")

    with col2:
        revenue_sector_data = pd.DataFrame({
            "Secteur": list(kpi_data["total_revenue_per_sector"].keys()),
            "Revenu Total": list(kpi_data["total_revenue_per_sector"].values()),
        })

        fig_revenue_sector = px.pie(revenue_sector_data, names="Secteur", values="Revenu Total",
                                    title="Revenus par Secteur(en €)",
                                    color_discrete_sequence=px.colors.sequential.Plasma)
        fig_revenue_sector.update_layout(template="plotly_dark")
        st.plotly_chart(fig_revenue_sector, use_container_width=True, key="revenue_sector_chart")

# Fonction pour afficher les KPIs d'un produit spécifique
def display_product_kpis(product_name):
    kpis = get_product_kpis(product_name)
    if kpis:
        st.title(f"Analyse des performances du produit : {kpis['product_name']}")
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total des transactions", kpis['total_deals'])
        with col2:
            st.metric("Ventes conclues ", kpis['total_sales_won'])
        with col3:
            st.metric("Ventes perdues", kpis['total_sales_lost'])
        with col4:
            st.metric("Chiffre d'affaires total", f"{kpis['total_revenue']:,} €")

        # Taux d'engagement et de résiliation
        st.subheader("Taux d'engagement et de résiliation")
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = kpis['engagement_rate'],
            domain = {'x': [0, 0.5], 'y': [0, 1]},
            title = {'text': "Taux d'engagement"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "darkblue"},
                     'steps' : [
                         {'range': [0, 30], 'color': "lightgray"},
                         {'range': [30, 70], 'color': "gray"},
                         {'range': [70, 100], 'color': "darkgray"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = kpis['resignation_rate'],
            domain = {'x': [0.5, 1], 'y': [0, 1]},
            title = {'text': "Taux de résiliation"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "darkred"},
                     'steps' : [
                         {'range': [0, 20], 'color': "lightgray"},
                         {'range': [20, 50], 'color': "gray"},
                         {'range': [50, 100], 'color': "darkgray"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}}))
        st.plotly_chart(fig)

        # Analyse des ventes
        st.subheader("Analyse des ventes")
        col1, col2 = st.columns(2)
        with col1:
            fig_funnel = go.Figure(go.Funnel(
                y = ['Total des transactions', 'Ventes totales', 'Ventes conclues '],
                x = [kpis['total_deals'], kpis['total_sales'], kpis['total_sales_won']],
                textinfo = "value+percent initial"))
            fig_funnel.update_layout(title_text = "Entonnoir de ventes")
            st.plotly_chart(fig_funnel)
        
        with col2:
            labels = ['Ventes conclues ', 'Ventes perdues', 'En cours']
            values = [kpis['total_sales_won'], kpis['total_sales_lost'], 
                      kpis['total_deals'] - kpis['total_sales_won'] - kpis['total_sales_lost']]
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
            fig_pie.update_layout(title_text="Répartition des ventes")
            st.plotly_chart(fig_pie)

        # Ventes par région
        st.subheader("Ventes par région")
        sales_by_region_df = pd.DataFrame(list(kpis['sales_by_region'].items()), columns=['Region', 'Ventes'])
        fig_region = px.bar(sales_by_region_df, x='Region', y='Ventes', 
                            title="Ventes par région",
                            color='Ventes',
                            color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig_region)

        # Ventes par secteur
        st.subheader("Ventes par secteur")
        sales_by_sector_df = pd.DataFrame(list(kpis['sales_by_sector'].items()), columns=['Secteur', 'Ventes'])
        fig_sector = px.pie(sales_by_sector_df, names='Secteur', values='Ventes', 
                            title="Répartition des ventes par secteur",
                            color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_sector)

        # Analyse du chiffre d'affaires
        st.subheader("Analyse du chiffre d'affaires")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Chiffre d'affaires moyen par vente", f"{kpis['avg_revenue']:,} €")
        with col2:
            st.metric("Chiffre d'affaires total", f"{kpis['total_revenue']:,} €")

        # Recommandations
        st.subheader("Recommandations")
        if kpis['engagement_rate'] < 50:
            st.warning("Le taux d'engagement est faible. Envisagez d'améliorer vos stratégies de vente et de marketing pour augmenter l'intérêt des clients potentiels.")
        if kpis['resignation_rate'] > 20:
            st.warning("Le taux de résiliation est élevé. Concentrez-vous sur l'amélioration de la satisfaction client et la rétention.")
        if kpis['total_sales_lost'] / kpis['total_deals'] > 0.3:
            st.warning("Le taux de perte de ventes est élevé. Analysez les raisons des échecs de vente et ajustez votre approche en conséquence.")
        
        top_region = sales_by_region_df.loc[sales_by_region_df['Ventes'].idxmax(), 'Region']
        st.info(f"La région {top_region} montre les meilleures performances. Considérez d'étendre vos efforts de vente dans cette région.")
        
        top_sector = sales_by_sector_df.loc[sales_by_sector_df['Ventes'].idxmax(), 'Secteur']
        st.info(f"Le secteur {top_sector} est le plus performant. Explorez des opportunités pour développer davantage votre présence dans ce secteur.")

    else:
        st.error(f"Aucune donnée disponible pour le produit '{product_name}'.")

# Fonction principale
def main():
    # Obtention de la liste des produits
    products = get_products()
    
    if products:
        # Ajout d'une option par défaut au début de la liste
        options = ["Vue globale"] + products
        
        # Affichage d'un selectbox dans la sidebar avec une valeur par défaut
        selected_option = st.sidebar.selectbox("Vous pouvez consulter la performance d'un produit spécifique (veuillez sélectionner le produit)", options)

        if selected_option == "Vue globale":
            # Chargement et affichage des données globales
            kpi_data = load_global_data()
            if kpi_data:
                display_global_kpis(kpi_data)
                display_global_charts(kpi_data)
        else:
            # Affichage des KPIs du produit sélectionné
            display_product_kpis(selected_option)
    else:
        st.sidebar.error("Aucun produit disponible.")
        # Affichage des données globales si aucun produit n'est disponible
        kpi_data = load_global_data()
        if kpi_data:
            display_global_kpis(kpi_data)
            display_global_charts(kpi_data)

if __name__ == "__main__":
    main()

