"""
AI-Powered Analysis Page
Provides condition-based drug recommendations using NLP and comprehensive database
"""

import streamlit as st
from models.ner_extractor import NERExtractor
from data.database_loader import get_drug_alternatives_detailed, initialize_system_database
import pandas as pd
import re

def show():
    st.markdown("## 🤖 AI-Powered Medical Analysis")
    st.markdown("Get intelligent drug recommendations based on medical conditions and patient information")
    
    # Initialize comprehensive database
    initialize_system_database()
    
    # Initialize NER extractor
    if 'ner_extractor' not in st.session_state:
        st.session_state.ner_extractor = NERExtractor()
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Medical condition input
        medical_condition = st.text_area(
            "Enter medical condition or symptoms",
            placeholder="e.g., High blood pressure and diabetes, Chest pain with shortness of breath, Chronic back pain",
            height=120,
            key="ai_medical_condition"
        )
        
        # Additional symptoms
        additional_symptoms = st.text_area(
            "Additional symptoms or context (optional)",
            placeholder="e.g., Patient also experiences fatigue, nausea, difficulty sleeping",
            height=80,
            key="ai_additional_symptoms"
        )
    
    with col2:
        st.markdown("### 👤 Patient Information")
        
        # Patient demographics
        patient_age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=150,
            value=45,
            key="ai_patient_age"
        )
        
        patient_weight = st.number_input(
            "Weight (kg)",
            min_value=1.0,
            max_value=300.0,
            value=70.0,
            key="ai_patient_weight"
        )
        
        # Medical history
        medical_history = st.multiselect(
            "Medical History",
            ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", "Liver Disease", 
             "Asthma", "COPD", "Depression", "Anxiety", "Arthritis"],
            key="ai_medical_history"
        )
        
        # Current medications
        current_medications = st.text_area(
            "Current medications",
            placeholder="e.g., Metformin, Lisinopril, Aspirin",
            height=60,
            key="ai_current_meds"
        )
    
    # Analysis button
    if st.button("🔍 Analyze & Recommend", type="primary", use_container_width=True):
        if medical_condition.strip():
            with st.spinner("Analyzing medical information..."):
                # Combine all text for analysis
                full_text = f"{medical_condition}. {additional_symptoms}. Medical history: {', '.join(medical_history)}."
                
                # Extract medical entities
                analysis_result = analyze_medical_text(full_text, st.session_state.ner_extractor)
                
                # Get drug recommendations
                recommendations = get_drug_recommendations(
                    analysis_result, 
                    patient_age, 
                    patient_weight,
                    medical_history,
                    current_medications.split(',') if current_medications else []
                )
                
                st.session_state.ai_analysis_result = {
                    'analysis': analysis_result,
                    'recommendations': recommendations,
                    'patient_info': {
                        'age': patient_age,
                        'weight': patient_weight,
                        'history': medical_history,
                        'current_meds': current_medications
                    }
                }
                
                st.success("Analysis completed!")
        else:
            st.error("Please enter a medical condition or symptoms")
    
    # Display results
    if hasattr(st.session_state, 'ai_analysis_result'):
        display_ai_analysis_results()

def analyze_medical_text(text: str, ner_extractor: NERExtractor) -> dict:
    """Analyze medical text to extract conditions and symptoms"""
    
    # Extract diseases and drugs using NER
    diseases = ner_extractor.extract_entities(text, 'diseases')
    drugs = ner_extractor.extract_entities(text, 'drugs')
    
    # Extract symptoms using pattern matching
    symptoms = extract_symptoms_from_text(text)
    
    # Extract severity indicators
    severity = extract_severity_indicators(text)
    
    return {
        'diseases': diseases,
        'drugs': drugs,
        'symptoms': symptoms,
        'severity': severity,
        'original_text': text
    }

def extract_symptoms_from_text(text: str) -> list:
    """Extract common symptoms using pattern matching"""
    
    common_symptoms = [
        'chest pain', 'shortness of breath', 'fatigue', 'nausea', 'vomiting',
        'headache', 'dizziness', 'fever', 'cough', 'sore throat',
        'muscle pain', 'joint pain', 'back pain', 'abdominal pain',
        'difficulty sleeping', 'insomnia', 'anxiety', 'depression',
        'rapid heartbeat', 'palpitations', 'swelling', 'edema'
    ]
    
    found_symptoms = []
    text_lower = text.lower()
    
    for symptom in common_symptoms:
        if symptom in text_lower:
            found_symptoms.append(symptom.title())
    
    return found_symptoms

def extract_severity_indicators(text: str) -> str:
    """Extract severity level from text"""
    
    text_lower = text.lower()
    
    severe_indicators = ['severe', 'acute', 'emergency', 'critical', 'intense']
    moderate_indicators = ['moderate', 'persistent', 'chronic', 'ongoing']
    mild_indicators = ['mild', 'slight', 'minor', 'occasional']
    
    if any(indicator in text_lower for indicator in severe_indicators):
        return 'Severe'
    elif any(indicator in text_lower for indicator in moderate_indicators):
        return 'Moderate'
    elif any(indicator in text_lower for indicator in mild_indicators):
        return 'Mild'
    else:
        return 'Unspecified'

def get_drug_recommendations(analysis: dict, age: int, weight: float, history: list, current_meds: list) -> dict:
    """Get drug recommendations based on analysis and patient info"""
    
    recommendations = {
        'primary_recommendations': [],
        'alternative_options': [],
        'contraindications': [],
        'monitoring_requirements': []
    }
    
    # Get comprehensive drug database
    if 'drug_db' not in st.session_state:
        return recommendations
    
    drug_db = st.session_state.drug_db
    
    # Map detected diseases to drug categories
    disease_to_drug_mapping = {
        'hypertension': ['amlodipine', 'lisinopril', 'metoprolol', 'losartan'],
        'diabetes': ['metformin', 'glipizide', 'sitagliptin', 'insulin_glargine'],
        'depression': ['sertraline', 'fluoxetine', 'citalopram', 'trazodone'],
        'anxiety': ['lorazepam', 'alprazolam', 'sertraline'],
        'pain': ['ibuprofen', 'acetaminophen', 'tramadol'],
        'infection': ['amoxicillin', 'azithromycin', 'ciprofloxacin'],
        'asthma': ['albuterol', 'montelukast'],
        'gerd': ['omeprazole', 'pantoprazole']
    }
    
    # Find relevant drugs based on detected diseases
    detected_conditions = [disease['text'].lower() for disease in analysis['diseases']]
    
    for condition in detected_conditions:
        for disease_key, drug_list in disease_to_drug_mapping.items():
            if disease_key in condition or condition in disease_key:
                for drug_name in drug_list:
                    drug_info = drug_db.get_drug_info(drug_name)
                    if drug_info:
                        # Check age appropriateness
                        age_category = 'pediatric' if age < 18 else 'geriatric' if age >= 65 else 'adult'
                        age_info = drug_info.get('age_restrictions', {}).get(age_category, '')
                        
                        # Check for contraindications with current medications
                        interaction_risk = check_interaction_risk(drug_name, current_meds)
                        
                        recommendation = {
                            'drug_name': drug_name.title(),
                            'generic_name': drug_info.get('generic_name', ''),
                            'category': drug_info.get('category', ''),
                            'indication_match': condition.title(),
                            'age_appropriate': 'contraindicated' not in age_info.lower(),
                            'interaction_risk': interaction_risk,
                            'strength_options': drug_info.get('strength_options', []),
                            'age_specific_dosing': age_info
                        }
                        
                        if recommendation['age_appropriate'] and interaction_risk == 'Low':
                            recommendations['primary_recommendations'].append(recommendation)
                        else:
                            recommendations['alternative_options'].append(recommendation)
    
    # Add monitoring requirements based on patient characteristics
    if age >= 65:
        recommendations['monitoring_requirements'].append("Enhanced monitoring recommended for geriatric patient")
    
    if 'Kidney Disease' in history:
        recommendations['monitoring_requirements'].append("Renal function monitoring required")
    
    if 'Liver Disease' in history:
        recommendations['monitoring_requirements'].append("Hepatic function monitoring required")
    
    return recommendations

def check_interaction_risk(drug_name: str, current_meds: list) -> str:
    """Check interaction risk with current medications"""
    
    if not current_meds or 'interaction_checker' not in st.session_state:
        return 'Low'
    
    interaction_checker = st.session_state.interaction_checker
    high_risk_count = 0
    
    for med in current_meds:
        med = med.strip().lower()
        if med:
            interactions = interaction_checker.check_interaction(drug_name.lower(), med)
            if interactions and any(interaction.get('severity', '').lower() == 'high' for interaction in interactions):
                high_risk_count += 1
    
    if high_risk_count > 0:
        return 'High'
    elif len(current_meds) > 3:
        return 'Moderate'
    else:
        return 'Low'

def display_ai_analysis_results():
    """Display comprehensive AI analysis results"""
    
    result = st.session_state.ai_analysis_result
    analysis = result['analysis']
    recommendations = result['recommendations']
    patient_info = result['patient_info']
    
    st.markdown("---")
    st.markdown("## 🎯 AI Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Conditions Detected", len(analysis['diseases']))
    with col2:
        st.metric("Symptoms Found", len(analysis['symptoms']))
    with col3:
        st.metric("Primary Recommendations", len(recommendations['primary_recommendations']))
    with col4:
        st.metric("Severity Level", analysis['severity'])
    
    # Detected medical entities
    if analysis['diseases'] or analysis['symptoms']:
        st.markdown("### 🏥 Detected Medical Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Medical Conditions:**")
            if analysis['diseases']:
                for disease in analysis['diseases']:
                    confidence = disease.get('confidence', 0)
                    confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                    st.markdown(f"• {disease['text'].title()} {confidence_color} ({confidence:.1%})")
            else:
                st.markdown("No specific conditions detected")
        
        with col2:
            st.markdown("**Symptoms:**")
            if analysis['symptoms']:
                for symptom in analysis['symptoms']:
                    st.markdown(f"• {symptom}")
            else:
                st.markdown("No specific symptoms detected")
    
    # Primary recommendations
    if recommendations['primary_recommendations']:
        st.markdown("### 💊 Primary Drug Recommendations")
        
        for i, rec in enumerate(recommendations['primary_recommendations']):
            with st.expander(f"✅ {rec['drug_name']} ({rec['category']})", expanded=i < 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Generic Name:** {rec['generic_name']}")
                    st.markdown(f"**Indication Match:** {rec['indication_match']}")
                    st.markdown(f"**Interaction Risk:** {rec['interaction_risk']}")
                    
                with col2:
                    st.markdown(f"**Available Strengths:** {', '.join(rec['strength_options'])}")
                    st.markdown(f"**Age Appropriate:** {'✅ Yes' if rec['age_appropriate'] else '⚠️ Caution Required'}")
                
                if rec['age_specific_dosing']:
                    st.info(f"**Age-Specific Guidance:** {rec['age_specific_dosing']}")
    
    # Alternative options
    if recommendations['alternative_options']:
        st.markdown("### 🔄 Alternative Options")
        st.markdown("These medications may require additional monitoring or have specific considerations")
        
        for rec in recommendations['alternative_options']:
            with st.expander(f"⚠️ {rec['drug_name']} - Requires Monitoring"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Category:** {rec['category']}")
                    st.markdown(f"**Indication:** {rec['indication_match']}")
                
                with col2:
                    st.markdown(f"**Interaction Risk:** {rec['interaction_risk']}")
                    if not rec['age_appropriate']:
                        st.warning("Age-related contraindications present")
    
    # Monitoring requirements
    if recommendations['monitoring_requirements']:
        st.markdown("### 📊 Monitoring Requirements")
        
        for requirement in recommendations['monitoring_requirements']:
            st.info(f"ℹ️ {requirement}")
    
    # Patient-specific warnings
    st.markdown("### ⚠️ Patient-Specific Considerations")
    
    age = patient_info['age']
    history = patient_info['history']
    
    if age < 18:
        st.warning("Pediatric patient - Special dosing considerations apply")
    elif age >= 65:
        st.warning("Geriatric patient - Enhanced monitoring and dose adjustments may be needed")
    
    if 'Kidney Disease' in history:
        st.error("Renal impairment present - Dose adjustments required for renally eliminated drugs")
    
    if 'Liver Disease' in history:
        st.error("Hepatic impairment present - Avoid hepatotoxic medications")
    
    if patient_info['current_meds']:
        st.info(f"Current medications: {patient_info['current_meds']} - Drug interaction screening performed")