import streamlit as st
from data.drug_database import DrugDatabase
from data.database_loader import get_drug_alternatives_detailed, initialize_system_database
from models.ner_extractor import NERExtractor
import pandas as pd

def show():
    st.markdown("## 🔄 Alternative Drug Finder")
    st.markdown("Find detailed alternatives for any medication with comprehensive clinical information")
    
    # Initialize comprehensive database
    initialize_system_database()
    
    # Initialize models
    if 'drug_database' not in st.session_state:
        st.session_state.drug_database = DrugDatabase()
    
    if 'ner_extractor' not in st.session_state:
        st.session_state.ner_extractor = NERExtractor()
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Drug name input
        drug_search = st.text_input(
            "Enter drug name to find alternatives",
            placeholder="e.g., Aspirin, Metformin, Lisinopril",
            key="alternative_drug_search"
        )
        
        # Medical condition/indication (optional)
        indication = st.text_area(
            "Medical condition/indication (optional)",
            placeholder="e.g., Hypertension, Diabetes, Pain management",
            height=100,
            key="alternative_indication"
        )
    
    with col2:
        st.markdown("### 📋 Patient Factors")
        
        # Patient age
        patient_age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=150,
            value=45,
            key="alternative_patient_age"
        )
        
        # Known allergies
        known_allergies = st.text_area(
            "Known allergies (comma-separated)",
            placeholder="e.g., Penicillin, Sulfa drugs",
            height=80,
            key="alternative_allergies"
        )
    
    # Search button
    if st.button("🔍 Find Detailed Alternatives", type="primary", disabled=not drug_search):
        with st.spinner("Finding comprehensive alternatives..."):
            # Get detailed alternatives from comprehensive database
            detailed_alternatives = get_drug_alternatives_detailed(drug_search)
            
            if 'error' not in detailed_alternatives:
                st.session_state.alternative_results = detailed_alternatives
                st.session_state.patient_info = {
                    'age': patient_age,
                    'allergies': [a.strip() for a in known_allergies.split(',') if a.strip()],
                    'indication': indication
                }
                total_found = detailed_alternatives['total_alternatives_found']
                st.success(f"Found {total_found} detailed alternatives for {drug_search}")
            else:
                st.warning(detailed_alternatives['error'])
    
    # Display comprehensive results
    if hasattr(st.session_state, 'alternative_results'):
        results = st.session_state.alternative_results
        patient_info = st.session_state.get('patient_info', {})
        
        st.markdown("---")
        st.markdown("## 🎯 Comprehensive Alternative Analysis")
        
        # Original drug information
        original = results['original_drug']
        st.markdown(f"### 📋 Original Drug: {original['name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Category", original['category'])
        with col2:
            st.metric("Total Alternatives", results['total_alternatives_found'])
        with col3:
            patient_age = patient_info.get('age', 45)
            age_category = "Pediatric" if patient_age < 18 else "Geriatric" if patient_age >= 65 else "Adult"
            st.metric("Patient Category", age_category)
        
        # Original drug details
        with st.expander("📖 Original Drug Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Indications:**")
                for indication in original['indications']:
                    st.markdown(f"• {indication}")
            with col2:
                st.markdown("**Contraindications:**")
                for contraindication in original['contraindications']:
                    st.markdown(f"• {contraindication}")
        
        # Same category alternatives
        if results['same_category_alternatives']:
            st.markdown("### 🎯 Same Category Alternatives")
            st.markdown(f"Medications in the same therapeutic class: **{original['category']}**")
            
            for i, alt in enumerate(results['same_category_alternatives']):
                with st.expander(f"💊 {alt['name']} ({alt['generic_name']})", expanded=i < 2):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Category:** {alt['category']}")
                        st.markdown(f"**Brand Names:** {', '.join(alt['brand_names'])}")
                        st.markdown(f"**Dosage Forms:** {', '.join(alt['dosage_forms'])}")
                        st.markdown(f"**Strength Options:** {', '.join(alt['strength_options'])}")
                    
                    with col2:
                        st.markdown("**Common Indications:**")
                        for indication in alt['common_indications']:
                            st.markdown(f"• {indication.title()}")
                        
                        st.markdown("**Side Effects:**")
                        for side_effect in alt['side_effects'][:3]:  # Show first 3
                            st.markdown(f"• {side_effect}")
                    
                    # Age-specific information
                    age_key = 'pediatric' if patient_age < 18 else 'geriatric' if patient_age >= 65 else 'adult'
                    age_info = alt['age_suitability'].get(age_key, 'No specific information')
                    
                    st.markdown(f"**Age Suitability ({age_category}):** {age_info}")
        
        # Different category alternatives
        if results['different_category_alternatives']:
            st.markdown("### 🔄 Different Category Alternatives")
            st.markdown("Medications from different therapeutic classes with similar indications")
            
            for i, alt in enumerate(results['different_category_alternatives']):
                with st.expander(f"🔄 {alt['name']} - {alt['category']}", expanded=i < 1):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Generic Name:** {alt['generic_name']}")
                        st.markdown(f"**Category:** {alt['category']}")
                        st.markdown(f"**Brand Names:** {', '.join(alt['brand_names'])}")
                        st.markdown(f"**Dosage Forms:** {', '.join(alt['dosage_forms'])}")
                    
                    with col2:
                        st.markdown("**Shared Indications:**")
                        for indication in alt['common_indications']:
                            st.markdown(f"• {indication.title()}")
                        
                        st.markdown("**Key Side Effects:**")
                        for side_effect in alt['side_effects'][:3]:
                            st.markdown(f"• {side_effect}")
                    
                    # Age-specific information
                    age_key = 'pediatric' if patient_age < 18 else 'geriatric' if patient_age >= 65 else 'adult'
                    age_info = alt['age_suitability'].get(age_key, 'No specific information available')
                    
                    if 'contraindicated' in age_info.lower() or 'not recommended' in age_info.lower():
                        st.error(f"⚠️ **Age Consideration:** {age_info}")
                    else:
                        st.info(f"ℹ️ **Age Consideration:** {age_info}")
        
        # Summary recommendations
        st.markdown("### 📊 Clinical Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Best Same-Category Options:**")
            if results['same_category_alternatives']:
                for alt in results['same_category_alternatives'][:3]:
                    st.markdown(f"• **{alt['name']}** - {len(alt['common_indications'])} shared indications")
            else:
                st.markdown("No same-category alternatives found")
        
        with col2:
            st.markdown("**Cross-Category Options:**")
            if results['different_category_alternatives']:
                for alt in results['different_category_alternatives'][:3]:
                    st.markdown(f"• **{alt['name']}** ({alt['category']})")
            else:
                st.markdown("No cross-category alternatives found")
        
        # Patient-specific warnings
        allergies = patient_info.get('allergies', [])
        if allergies:
            st.warning(f"⚠️ **Patient Allergies:** {', '.join(allergies)} - Please verify compatibility with selected alternatives")
        
        if results['total_alternatives_found'] == 0:
            st.info("💡 **Tip:** Try searching with a more common drug name or check spelling")
    if hasattr(st.session_state, 'alternative_results') and indication:
        st.markdown("---")
        st.markdown("## 🎯 Condition-Based Recommendations")
        
        # Extract medical conditions from indication text
        with st.spinner("Analyzing medical indication..."):
            condition_entities = st.session_state.ner_extractor.extract_entities(indication, 'diseases')
            
            if condition_entities:
                st.markdown("### 🏥 Detected Medical Conditions")
                condition_data = []
                for entity in condition_entities:
                    if entity['confidence'] > 0.6:
                        condition_data.append({
                            'Condition': entity['text'],
                            'Confidence': f"{entity['confidence']:.1%}"
                        })
                
                if condition_data:
                    df_conditions = pd.DataFrame(condition_data)
                    st.dataframe(df_conditions, use_container_width=True)
                    
                    # Provide general recommendations
                    st.info("""
                    **💡 Recommendation Process:**
                    1. Verify detected conditions with healthcare provider
                    2. Consider patient-specific factors (allergies, age, other medications)
                    3. Review contraindications for each alternative
                    4. Monitor for drug interactions
                    5. Start with lowest effective dose
                    """)
    
    # Comprehensive drug search
    st.markdown("---")
    st.markdown("### 🔍 Search All Drugs by Condition")
    
    condition_search = st.text_input(
        "Search drugs by medical condition",
        placeholder="e.g., hypertension, diabetes, pain",
        key="condition_search"
    )
    
    if condition_search:
        with st.spinner("Searching drugs for condition..."):
            condition_drugs = st.session_state.drug_database.search_drugs(condition_search)
            
            if condition_drugs:
                st.success(f"Found {len(condition_drugs)} drugs for '{condition_search}':")
                
                # Display as pills/badges
                cols = st.columns(min(len(condition_drugs), 4))
                for i, drug in enumerate(condition_drugs):
                    with cols[i % 4]:
                        drug_info = st.session_state.drug_database.get_drug_info(drug)
                        category = drug_info.get('category', 'Unknown') if drug_info else 'Unknown'
                        st.info(f"**{drug.title()}**\n{category}")
    
    # Help section
    with st.expander("ℹ️ How to Use Alternative Drug Finder"):
        st.markdown("""
        **Finding Alternatives:**
        1. **Enter the drug name** you want to find alternatives for
        2. **Add medical condition** (optional) for context-specific recommendations
        3. **Enter patient information** for age-appropriate filtering
        4. **List known allergies** to avoid contraindicated alternatives
        5. **Click "Find Alternatives"** to search
        
        **Understanding Results:**
        - **✅ Suitable**: Appropriate for patient's age group
        - **⚠️ Caution**: May require special consideration or dose adjustment
        - **⚠️ Allergy Risk**: Potential allergy based on patient's known allergies
        
        **Safety Considerations:**
        - Always verify alternatives with healthcare provider
        - Check for drug interactions with current medications
        - Consider patient-specific factors (kidney function, liver function, etc.)
        - Review contraindications carefully
        
        **Search Tips:**
        - Try both generic and brand names
        - Use partial names (e.g., "aspir" for aspirin)
        - Search by medical condition to find suitable drugs
        
        **Note**: This tool provides educational information only. Always consult healthcare professionals before making medication changes.
        """)
