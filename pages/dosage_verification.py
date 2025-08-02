import streamlit as st
from utils.dosage_calculator import DosageCalculator
from data.drug_database import DrugDatabase
import pandas as pd

def show():
    st.markdown("## 💊 Enhanced Dosage Verification & Calculation")
    
    # Initialize models
    if 'dosage_calculator' not in st.session_state:
        st.session_state.dosage_calculator = DosageCalculator()
    
    if 'drug_database' not in st.session_state:
        st.session_state.drug_database = DrugDatabase()
    
    # Create columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 👤 Patient Information")
        
        # Patient Age
        patient_age = st.number_input(
            "Patient Age (years)",
            min_value=0,
            max_value=150,
            value=45,
            key="dosage_patient_age"
        )
        
        # Gender
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            key="dosage_gender"
        )
        
        # Age Category Display
        age_category = st.session_state.dosage_calculator.calculate_age_category(patient_age)
        age_category_display = {
            'pediatric': 'Child/Adolescent',
            'adult': 'Adult', 
            'geriatric': 'Elderly'
        }
        st.info(f"**Age Category:** {age_category_display[age_category]}")
        
        # Patient Weight
        patient_weight = st.number_input(
            "Patient Weight (kg)",
            min_value=0.0,
            max_value=300.0,
            value=70.0,
            step=0.1,
            key="dosage_patient_weight"
        )
        
        # Kidney function
        kidney_function = st.selectbox(
            "Kidney Function",
            ["Normal", "Mild Impairment", "Moderate Impairment", "Severe Impairment"],
            key="dosage_kidney_function"
        )
        
        # BMI Calculation and Display
        if patient_weight > 0:
            # Assume average height for BMI calculation if not provided
            height_cm = st.number_input(
                "Height (cm) - Optional for BMI calculation",
                min_value=50.0,
                max_value=250.0,
                value=170.0,
                step=0.1,
                key="dosage_height"
            )
            
            bmi, bmi_category = st.session_state.dosage_calculator.calculate_bmi(patient_weight, height_cm)
            
            col_bmi1, col_bmi2 = st.columns(2)
            with col_bmi1:
                st.metric("BMI", f"{bmi}")
            with col_bmi2:
                bmi_color = {
                    'Underweight': '🔵',
                    'Normal': '🟢', 
                    'Overweight': '🟡',
                    'Obese': '🔴'
                }
                st.metric("BMI Status", f"{bmi_color.get(bmi_category, '⚪')} {bmi_category}")
    
    with col2:
        st.markdown("### 💊 Drug Information")
        
        # Drug Name
        available_drugs = st.session_state.drug_database.get_all_drugs()
        drug_name = st.selectbox(
            "Drug Name",
            [""] + [drug.title() for drug in available_drugs],
            key="dosage_drug_name",
            help="Select a drug from the database or type to search"
        )
        
        if not drug_name:
            drug_name = st.text_input(
                "Or enter drug name manually",
                placeholder="e.g., Paracetamol, Ibuprofen",
                key="manual_drug_name"
            )
        
        # Indication
        indication = st.selectbox(
            "Indication",
            ["General", "Pain Management", "Cardiovascular", "Diabetes", "Hypertension", "Other"],
            key="dosage_indication"
        )
        
        # Prescribed Dosage
        prescribed_dosage = st.text_input(
            "Prescribed Dosage",
            placeholder="e.g., 500mg twice daily",
            key="dosage_prescribed_dosage"
        )
        
        # Frequency
        frequency = st.selectbox(
            "Frequency",
            ["Once daily", "Twice daily", "Three times daily", "Four times daily", "As needed", "Other"],
            key="dosage_frequency"
        )
        
        # Medical Conditions
        medical_conditions = st.multiselect(
            "Medical Conditions",
            st.session_state.drug_database.get_medical_conditions(),
            key="dosage_medical_conditions"
        )
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        verify_button = st.button(
            "🔍 Verify Prescribed Dosage", 
            type="primary", 
            use_container_width=True,
            disabled=not (drug_name and prescribed_dosage)
        )
    
    with col2:
        calculate_button = st.button(
            "📊 Calculate Recommended Dosage", 
            type="secondary", 
            use_container_width=True,
            disabled=not drug_name
        )
    
    # Dosage Verification
    if verify_button and drug_name and prescribed_dosage:
        with st.spinner("Verifying dosage..."):
            verification_result = st.session_state.dosage_calculator.verify_dosage(
                drug_name.lower(),
                prescribed_dosage,
                patient_age,
                patient_weight
            )
            
            st.session_state.dosage_verification_result = verification_result
    
    # Display Verification Results
    if hasattr(st.session_state, 'dosage_verification_result'):
        result = st.session_state.dosage_verification_result
        
        st.markdown("---")
        st.markdown("## 📊 Dosage Verification Results")
        
        # Status indicator
        if result['is_appropriate']:
            st.success("✅ **Dosage is APPROPRIATE for this patient**")
        else:
            st.error("⚠️ **Dosage requires REVIEW**")
        
        # Details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Prescription Details")
            st.write(f"**Drug:** {result['drug']}")
            st.write(f"**Prescribed:** {result['prescribed_dosage']}")
            st.write(f"**Patient Age Category:** {result['age_category'].title()}")
            
            if result['parsed_dosage']['dose']:
                st.write(f"**Parsed Dose:** {result['parsed_dosage']['dose']}{result['parsed_dosage']['unit']}")
                if result['parsed_dosage']['frequency']:
                    st.write(f"**Frequency:** {result['parsed_dosage']['frequency']}")
        
        with col2:
            st.markdown("### 📖 Guidelines")
            guidelines = result['guidelines']
            if guidelines:
                st.write(f"**Recommended Range:** {guidelines['min']}-{guidelines['max']} {guidelines['unit']}")
                if guidelines['note']:
                    st.info(f"**Note:** {guidelines['note']}")
        
        # Warnings
        if result['warnings']:
            st.markdown("### ⚠️ Warnings")
            for warning in result['warnings']:
                st.warning(warning)
        
        # Recommendations
        if result['recommendations']:
            st.markdown("### 💡 Recommendations")
            for recommendation in result['recommendations']:
                st.info(recommendation)
    
    # Calculate Recommended Dosage
    if calculate_button and drug_name:
        with st.spinner("Calculating recommended dosage..."):
            recommendation = st.session_state.dosage_calculator.calculate_recommended_dosage(
                drug_name.lower(),
                patient_age,
                patient_weight,
                medical_conditions
            )
            
            st.session_state.dosage_recommendation = recommendation
    
    # Display Dosage Recommendation
    if hasattr(st.session_state, 'dosage_recommendation'):
        recommendation = st.session_state.dosage_recommendation
        
        st.markdown("---")
        st.markdown("## 📋 Recommended Dosage")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💊 Dosage Recommendation")
            st.write(f"**Drug:** {recommendation['drug']}")
            st.write(f"**Age Category:** {recommendation['age_category'].title()}")
            if recommendation['recommended_dose']:
                st.success(f"**Recommended Dose:** {recommendation['recommended_dose']}")
            if recommendation['dosing_frequency']:
                st.write(f"**Frequency:** {recommendation['dosing_frequency']}")
        
        with col2:
            st.markdown("### 🩺 Special Considerations")
            if recommendation['special_considerations']:
                for consideration in recommendation['special_considerations']:
                    st.info(f"• {consideration}")
            
            if recommendation['contraindications']:
                st.markdown("**⚠️ Contraindications:**")
                for contraindication in recommendation['contraindications']:
                    st.warning(f"• {contraindication}")
    
    # Drug Information Display
    if drug_name:
        drug_info = st.session_state.drug_database.get_drug_info(drug_name.lower())
        if drug_info:
            with st.expander(f"📚 {drug_name} - Drug Information"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Generic Name:**")
                    st.write(drug_info.get('generic_name', 'N/A'))
                    
                    st.markdown("**Brand Names:**")
                    brands = drug_info.get('brand_names', [])
                    st.write(', '.join(brands) if brands else 'N/A')
                    
                    st.markdown("**Category:**")
                    st.write(drug_info.get('category', 'N/A'))
                    
                    st.markdown("**Available Strengths:**")
                    strengths = drug_info.get('strength_options', [])
                    st.write(', '.join(strengths) if strengths else 'N/A')
                
                with col2:
                    st.markdown("**Indications:**")
                    indications = drug_info.get('indications', [])
                    for indication in indications:
                        st.write(f"• {indication}")
                    
                    st.markdown("**Contraindications:**")
                    contraindications = drug_info.get('contraindications', [])
                    for contraindication in contraindications:
                        st.write(f"• {contraindication}")
    
    # Help section
    with st.expander("ℹ️ How to Use Dosage Verification"):
        st.markdown("""
        **Dosage Verification Process:**
        1. **Enter patient information** - Age, weight, medical conditions
        2. **Select or enter drug name** - Choose from database or enter manually
        3. **Enter prescribed dosage** - Include dose amount and frequency
        4. **Verify or Calculate** - Choose verification or recommendation
        
        **Understanding Results:**
        - ✅ **Appropriate**: Dosage is within recommended guidelines
        - ⚠️ **Requires Review**: Dosage may need adjustment
        - 💡 **Recommendations**: Specific guidance for the patient
        
        **Age Categories:**
        - **Pediatric**: 0-17 years (special weight-based dosing)
        - **Adult**: 18-64 years (standard dosing)
        - **Geriatric**: 65+ years (often requires dose reduction)
        
        **Note**: This tool provides guidance based on standard dosing guidelines. Always consult healthcare professionals for patient-specific dosing decisions.
        """)
