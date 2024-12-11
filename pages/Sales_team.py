import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from pprint import pprint

# URL de l'API FastAPI
API_URL = "http://127.0.0.1:8000/getAllProductsKpis/"

# Titre de la page
st.set_page_config(page_title="PERFORMANCES DES AGENT", page_icon="📊", layout="wide")
st.title("📊 PERFORMANCES DES AGENTS") 


# Chargement des données
st.subheader("Chargement des données...")
with st.spinner("Chargement des données en cours..."):
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        kpi_data = response.json()
    except requests.RequestException as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.stop()



# Graphique des ventes par agent
st.header("Ventes par Agent", anchor="agent")
sales_agent_data = pd.DataFrame({
    "Agent": list(kpi_data["total_sales_per_agent"].keys()),
    "Nombre de Ventes": list(kpi_data["total_sales_per_agent"].values()),
})
fig_sales_agent = px.bar(sales_agent_data, x="Agent", y="Nombre de Ventes", 
                         title="Nombre de Ventes par Agent", color="Agent", color_continuous_scale='Blues')
fig_sales_agent.update_layout(xaxis_title="Agent", yaxis_title="Nombre de Ventes", 
                              template="plotly_dark", plot_bgcolor="#2b2b2b")
st.plotly_chart(fig_sales_agent, use_container_width=True)

# Graphique des revenus par localisation des bureaux
st.header("Revenus par Bureau", anchor="bureau")
office_location_data = pd.DataFrame({
    "Bureau": list(kpi_data["total_revenue_per_office_location"].keys()),
    "Revenu Total": list(kpi_data["total_revenue_per_office_location"].values()),
})
fig_office_location = px.bar(office_location_data, x="Bureau", y="Revenu Total", 
                             title="Revenus par Bureau", color="Bureau", color_continuous_scale='RdBu')
fig_office_location.update_layout(xaxis_title="Bureau", yaxis_title="Revenu Total", 
                                  template="plotly_dark", plot_bgcolor="#2b2b2b")
st.plotly_chart(fig_office_location, use_container_width=True)

# Tableau des performances par manager
st.header("Performance par Manager", anchor="manager")
manager_data = pd.DataFrame({
    "Manager": list(kpi_data["total_revenue_per_manager"].keys()),
    "Revenu Total": list(kpi_data["total_revenue_per_manager"].values()),
    "Nombre de Ventes": [
        kpi_data["total_sales_per_manager"].get(manager, 0) for manager in kpi_data["total_revenue_per_manager"].keys()
    ],
})
st.dataframe(manager_data.style.set_properties(**{'background-color': '#2b2b2b', 'color': 'white'}))

# Fin de la page
st.write("\n")
#st.success("Dashboard généré avec succès ! 🎉")
