import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Performances commerciales HeticEtronics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
    )
st.empty()  # Ajoute un espace vide
col1, col2 = st.columns([2, 1]) 

with col1:
    st.header("Performances commerciales ")

with col2:
    st.image("public/logo/logo.png", width=160)

st.empty()
st.empty()


import streamlit as st

with st.container():
    col1, col2 = st.columns([3,1])
    
    with col1:
        st.header("CRM")
        
        # Create three columns for images
        col1, col2, col3 = st.columns(3)
        
        # Account Navigation
        with col1:
            # Store the image
            st.image("public/nav_account.png", width=200, use_container_width=False)
            
            # Add a transparent button over the image area
            if st.button("Account", key="account_nav", type="secondary", use_container_width=True):
                st.switch_page("pages/Account.py")
        
        # Agent Navigation
        with col2:
            st.image("public/nav_agent.png", width=200, use_container_width=False)
            
            if st.button("Agent", key="agent_nav", type="primary", use_container_width=True):
                st.switch_page("pages/Sales_team.py")
        
        # Sales Navigation
        with col3:
            st.image("public/nav_sales.png", width=200, use_container_width=False)
            
            if st.button("Sales", key="sales_nav", type="primary", use_container_width=True):
                st.switch_page("pages/Sales.py")