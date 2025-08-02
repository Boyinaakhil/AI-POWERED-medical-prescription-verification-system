import streamlit as st
import os
from pages import (
    drug_interaction, 
    prescription_analysis, 
    dosage_verification, 
    alternative_finder, 
    ai_analysis,
    drug_administration,
    training_models, 
    system_info
)
from data.database_loader import initialize_system_database

# Set page config
st.set_page_config(
    page_title="AI Medical Prescription Verification System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
    .main-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
    .header-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .nav-item {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 0.5rem;
        cursor: pointer;
    }
    .nav-item:hover {
        background-color: #f0f2f6;
    }
    .nav-item.active {
        background-color: #ff6b6b;
        color: white;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Drug Interaction Checker'
    
    # Initialize comprehensive database on startup
    if 'database_initialized' not in st.session_state:
        with st.spinner("Loading comprehensive drug database..."):
            initialize_system_database()
            st.session_state.database_initialized = True
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <span class="header-icon">🏥</span>
        <h1>AI Medical Prescription Verification System</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("**Select Function**")
    
    pages = {
        'Drug Interaction Checker': ('🔍', drug_interaction),
        'Prescription Image Analysis': ('📄', prescription_analysis),
        'Dosage Verification': ('💊', dosage_verification),
        'Alternative Drug Finder': ('🔄', alternative_finder),
        'AI-Powered Analysis': ('🤖', ai_analysis),
        'Drug Administration': ('🔧', drug_administration),
        'Training & Models': ('📚', training_models),  
        'System Information': ('ℹ️', system_info)
    }
    
    # Navigation buttons
    for page_name, (icon, page_func) in pages.items():
        if st.sidebar.button(f"{icon} {page_name}", key=page_name, use_container_width=True):
            st.session_state.current_page = page_name
    
    # Highlight current page
    current_page = st.session_state.current_page
    
    # Display the selected page
    if current_page in pages:
        pages[current_page][1].show()

if __name__ == "__main__":
    main()
