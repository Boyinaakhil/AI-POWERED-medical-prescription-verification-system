import streamlit as st
from models.drug_interaction import DrugInteractionChecker
from models.ner_extractor import NERExtractor
import pandas as pd

def show():
    st.markdown("## 🔍 Drug Interaction Detection")
    
    # Initialize models
    if 'drug_checker' not in st.session_state:
        st.session_state.drug_checker = DrugInteractionChecker()
    
    if 'ner_extractor' not in st.session_state:
        st.session_state.ner_extractor = NERExtractor()
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Manual Drug Entry")
        
        # Input method selection
        input_method = st.radio(
            "Input Method",
            ["Individual Drugs", "Text Input"],
            key="input_method"
        )
        
        drugs_to_check = []
        
        if input_method == "Individual Drugs":
            # Number of drugs selector
            num_drugs = st.number_input(
                "Number of drugs",
                min_value=1,
                max_value=10,
                value=2,
                key="num_drugs"
            )
            
            # Drug input fields
            for i in range(num_drugs):
                drug = st.text_input(
                    f"Drug {i+1}",
                    key=f"drug_{i}",
                    placeholder="e.g., Aspirin, Warfarin"
                )
                if drug.strip():
                    drugs_to_check.append(drug.strip())
        
        else:  # Text Input
            drug_text = st.text_area(
                "Enter drug list or prescription text",
                placeholder="Patient is taking aspirin 81mg daily and warfarin 5mg daily...",
                height=100,
                key="drug_text"
            )
            
            if drug_text:
                # Extract drugs using NER
                with st.spinner("Extracting drugs from text..."):
                    extracted_drugs = st.session_state.ner_extractor.extract_entities(drug_text, 'drugs')
                    drugs_to_check = [entity['text'] for entity in extracted_drugs if entity['confidence'] > 0.7]
                
                if drugs_to_check:
                    st.success(f"Extracted drugs: {', '.join(drugs_to_check)}")
        
        # Check interactions button
        if st.button("Check Drug Interactions", type="primary", disabled=len(drugs_to_check) < 2):
            if len(drugs_to_check) < 2:
                st.warning("Please enter at least 2 drugs to check for interactions.")
            else:
                with st.spinner("Checking for drug interactions..."):
                    # Check for interactions
                    interactions = st.session_state.drug_checker.check_interactions(drugs_to_check)
                    
                    # Store results in session state
                    st.session_state.interaction_results = interactions
                    st.session_state.checked_drugs = drugs_to_check
    
    with col2:
        st.markdown("### Patient Information")
        
        # Patient age
        patient_age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=150,
            value=45,
            key="patient_age"
        )
        
        # Patient weight
        patient_weight = st.number_input(
            "Patient Weight (kg)",
            min_value=0.0,
            max_value=300.0,
            value=70.0,
            step=0.1,
            key="patient_weight"
        )
        
        # Existing conditions
        existing_conditions = st.multiselect(
            "Existing Conditions",
            options=[
                "Hypertension", "Diabetes Type 2", "Hyperlipidemia",
                "Atrial Fibrillation", "Coronary Artery Disease", "Heart Failure",
                "Chronic Kidney Disease", "Osteoarthritis", "Depression",
                "Anxiety", "COPD", "Asthma", "Hypothyroidism", "GERD"
            ],
            key="existing_conditions"
        )
    
    # Display results
    if hasattr(st.session_state, 'interaction_results') and st.session_state.interaction_results:
        st.markdown("---")
        st.markdown("## 🚨 Interaction Analysis Results")
        
        interactions = st.session_state.interaction_results
        
        if interactions:
            # Summary
            high_severity = sum(1 for i in interactions if i['severity'] == 'High')
            moderate_severity = sum(1 for i in interactions if i['severity'] == 'Moderate')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Interactions", len(interactions))
            with col2:
                st.metric("High Severity", high_severity)
            with col3:
                st.metric("Moderate Severity", moderate_severity)
            
            # Detailed interactions
            for i, interaction in enumerate(interactions):
                severity_color = "🔴" if interaction['severity'] == 'High' else "🟡"
                
                with st.expander(f"{severity_color} {interaction['drug1']} + {interaction['drug2']} ({interaction['severity']} Severity)"):
                    st.write(f"**Description:** {interaction['description']}")
                    st.write(f"**Recommendation:** {interaction['recommendation']}")
                    
                    if interaction['severity'] == 'High':
                        st.error("⚠️ HIGH RISK INTERACTION - Immediate attention required")
                    else:
                        st.warning("⚠️ Monitor patient closely")
        else:
            st.success("✅ No known interactions found between the specified drugs.")
    
    # Individual drug analysis
    if hasattr(st.session_state, 'checked_drugs') and st.session_state.checked_drugs:
        st.markdown("---")
        st.markdown("## 💊 Individual Drug Analysis")
        
        drug_info = st.session_state.drug_checker.analyze_individual_drugs(st.session_state.checked_drugs)
        
        for drug in drug_info:
            with st.expander(f"📋 {drug['name']} - {drug['category']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Common Side Effects:**")
                    for effect in drug['common_side_effects']:
                        st.write(f"• {effect}")
                
                with col2:
                    st.markdown("**Contraindications:**")
                    for contraindication in drug['contraindications']:
                        st.write(f"• {contraindication}")
    
    # Help section
    with st.expander("ℹ️ How to Use This Tool"):
        st.markdown("""
        **Manual Drug Entry:**
        1. Choose your input method:
           - **Individual Drugs**: Enter each drug separately
           - **Text Input**: Paste prescription text or drug list
        
        2. Enter patient information for age-specific analysis
        
        3. Click "Check Drug Interactions" to analyze
        
        **Understanding Results:**
        - 🔴 **High Severity**: Serious interactions requiring immediate attention
        - 🟡 **Moderate Severity**: Interactions requiring monitoring
        - ✅ **No Interactions**: Safe to use together
        
        **Note**: This tool uses AI models for drug extraction and a curated database for interaction checking. Always consult healthcare professionals for medical decisions.
        """)
