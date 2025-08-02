"""
Database Loader for Comprehensive Drug Dataset
Loads 100+ drugs and interactions into the system
"""

from data.comprehensive_drug_dataset import COMPREHENSIVE_DRUG_DATA, COMPREHENSIVE_INTERACTIONS
from data.drug_database import DrugDatabase
from models.drug_interaction import DrugInteractionChecker
import streamlit as st

def load_comprehensive_database():
    """Load the comprehensive drug database into the system"""
    
    # Initialize database components
    drug_db = DrugDatabase()
    interaction_checker = DrugInteractionChecker()
    
    # Load all drugs from the comprehensive dataset
    success_count = 0
    failed_drugs = []
    
    for drug_name, drug_data in COMPREHENSIVE_DRUG_DATA.items():
        try:
            success = drug_db.add_drug(drug_name, drug_data)
            if success:
                success_count += 1
            else:
                failed_drugs.append(drug_name)
        except Exception as e:
            failed_drugs.append(f"{drug_name} ({str(e)})")
    
    # Load all interactions
    interaction_success = 0
    failed_interactions = []
    
    for interaction in COMPREHENSIVE_INTERACTIONS:
        try:
            success = interaction_checker.add_interaction(
                interaction["drug1"],
                interaction["drug2"], 
                interaction["severity"],
                interaction["description"],
                interaction["recommendation"]
            )
            if success:
                interaction_success += 1
            else:
                failed_interactions.append(f"{interaction['drug1']}-{interaction['drug2']}")
        except Exception as e:
            failed_interactions.append(f"{interaction['drug1']}-{interaction['drug2']} ({str(e)})")
    
    # Update session state with loaded databases
    st.session_state.drug_db = drug_db
    st.session_state.interaction_checker = interaction_checker
    st.session_state.database_loaded = True
    
    return {
        'drugs_loaded': success_count,
        'drugs_failed': failed_drugs,
        'interactions_loaded': interaction_success,
        'interactions_failed': failed_interactions,
        'total_drugs': len(COMPREHENSIVE_DRUG_DATA),
        'total_interactions': len(COMPREHENSIVE_INTERACTIONS)
    }

def get_drug_alternatives_detailed(drug_name: str) -> dict:
    """Get detailed alternatives for a specific drug"""
    
    if 'drug_db' not in st.session_state:
        load_comprehensive_database()
    
    drug_db = st.session_state.drug_db
    drug_info = drug_db.get_drug_info(drug_name.lower())
    
    if not drug_info:
        return {'error': f'Drug {drug_name} not found in database'}
    
    # Find alternatives in the same category
    same_category_alternatives = []
    different_category_alternatives = []
    
    drug_category = drug_info.get('category', '')
    
    for other_drug, other_info in drug_db.drugs.items():
        if other_drug.lower() == drug_name.lower():
            continue
        
        other_category = other_info.get('category', '')
        
        # Check if indications overlap
        drug_indications = set(indication.lower() for indication in drug_info.get('indications', []))
        other_indications = set(indication.lower() for indication in other_info.get('indications', []))
        
        overlap = drug_indications.intersection(other_indications)
        
        if overlap:
            alternative_data = {
                'name': other_drug.title(),
                'generic_name': other_info.get('generic_name', ''),
                'category': other_category,
                'brand_names': other_info.get('brand_names', []),
                'common_indications': list(overlap),
                'strength_options': other_info.get('strength_options', []),
                'dosage_forms': other_info.get('dosage_forms', []),
                'side_effects': other_info.get('side_effects', []),
                'age_suitability': other_info.get('age_restrictions', {})
            }
            
            if other_category == drug_category:
                same_category_alternatives.append(alternative_data)
            else:
                different_category_alternatives.append(alternative_data)
    
    return {
        'original_drug': {
            'name': drug_name.title(),
            'category': drug_category,
            'indications': drug_info.get('indications', []),
            'contraindications': drug_info.get('contraindications', [])
        },
        'same_category_alternatives': same_category_alternatives,
        'different_category_alternatives': different_category_alternatives,
        'total_alternatives_found': len(same_category_alternatives) + len(different_category_alternatives)
    }

def check_database_status():
    """Check if the comprehensive database is loaded"""
    return st.session_state.get('database_loaded', False)

def initialize_system_database():
    """Initialize the system with comprehensive database if not already loaded"""
    if not check_database_status():
        return load_comprehensive_database()
    return None