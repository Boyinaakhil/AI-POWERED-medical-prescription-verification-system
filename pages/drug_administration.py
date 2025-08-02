import streamlit as st
import json
from typing import Dict, Any, List
from data.drug_database import DrugDatabase
from models.drug_interaction import DrugInteractionChecker

def show_drug_administration():
    st.title("🔧 Drug Database Administration")
    st.markdown("Add and manage drugs, interactions, and alternatives in the system database")
    
    # Initialize components
    if 'drug_db' not in st.session_state:
        st.session_state.drug_db = DrugDatabase()
    if 'interaction_checker' not in st.session_state:
        st.session_state.interaction_checker = DrugInteractionChecker()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Database Stats", "💊 Add Drugs", "⚠️ Add Interactions", "📋 Bulk Import"])
    
    with tab1:
        show_database_stats()
    
    with tab2:
        show_add_single_drug()
    
    with tab3:
        show_add_interactions()
    
    with tab4:
        show_bulk_import()

def show_database_stats():
    st.subheader("Current Database Statistics")
    
    drug_stats = st.session_state.drug_db.get_database_stats()
    interaction_stats = st.session_state.interaction_checker.get_interaction_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Drugs", drug_stats['total_drugs'])
    
    with col2:
        st.metric("Total Interactions", interaction_stats['total_interactions'])
    
    with col3:
        st.metric("High Severity", interaction_stats['high_severity'])
    
    with col4:
        st.metric("Medical Conditions", drug_stats['total_conditions'])
    
    st.subheader("Current Drugs in Database")
    drugs_list = st.session_state.drug_db.get_all_drugs()
    if drugs_list:
        for i, drug in enumerate(drugs_list, 1):
            drug_info = st.session_state.drug_db.get_drug_info(drug)
            with st.expander(f"{i}. {drug.title()} - {drug_info.get('category', 'Unknown')}"):
                st.write(f"**Generic Name:** {drug_info.get('generic_name', 'N/A')}")
                st.write(f"**Brand Names:** {', '.join(drug_info.get('brand_names', []))}")
                st.write(f"**Indications:** {', '.join(drug_info.get('indications', []))}")
                st.write(f"**Side Effects:** {', '.join(drug_info.get('side_effects', []))}")

def show_add_single_drug():
    st.subheader("Add Single Drug")
    
    with st.form("add_drug_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            drug_name = st.text_input("Drug Name (Generic)", placeholder="e.g., metformin")
            generic_name = st.text_input("Full Generic Name", placeholder="e.g., Metformin Hydrochloride")
            category = st.selectbox("Drug Category", [
                "Antidiabetic", "ACE Inhibitor", "Beta Blocker", "Calcium Channel Blocker",
                "Diuretic", "Statin", "NSAID", "Antibiotic", "Anticoagulant", "Antiplatelet",
                "Bronchodilator", "Corticosteroid", "Antidepressant", "Anticonvulsant", "Other"
            ])
            
        with col2:
            brand_names = st.text_area("Brand Names (one per line)", placeholder="Glucophage\nFortamet\nGlumetza")
            strength_options = st.text_area("Strength Options (one per line)", placeholder="500mg\n850mg\n1000mg")
            dosage_forms = st.text_area("Dosage Forms (one per line)", placeholder="Tablet\nExtended-release tablet")
        
        indications = st.text_area("Indications/Uses (one per line)", placeholder="Type 2 diabetes\nPCOS\nPrediabetes")
        contraindications = st.text_area("Contraindications (one per line)", placeholder="Severe renal impairment\nSevere hepatic impairment")
        side_effects = st.text_area("Side Effects (one per line)", placeholder="GI upset\nLactic acidosis\nB12 deficiency")
        
        st.subheader("Age-Specific Information")
        pediatric_info = st.text_input("Pediatric Information", placeholder="Safety and efficacy established in children ≥10 years")
        adult_info = st.text_input("Adult Information", placeholder="Standard dosing")
        geriatric_info = st.text_input("Geriatric Information", placeholder="Use with caution, monitor renal function")
        
        submitted = st.form_submit_button("Add Drug to Database")
        
        if submitted:
            if drug_name and generic_name:
                drug_data = {
                    'generic_name': generic_name,
                    'brand_names': [name.strip() for name in brand_names.split('\n') if name.strip()],
                    'category': category,
                    'indications': [ind.strip() for ind in indications.split('\n') if ind.strip()],
                    'contraindications': [con.strip() for con in contraindications.split('\n') if con.strip()],
                    'side_effects': [se.strip() for se in side_effects.split('\n') if se.strip()],
                    'dosage_forms': [df.strip() for df in dosage_forms.split('\n') if df.strip()],
                    'strength_options': [so.strip() for so in strength_options.split('\n') if so.strip()],
                    'age_restrictions': {
                        'pediatric': pediatric_info or 'No specific pediatric information available',
                        'adult': adult_info or 'Standard dosing',
                        'geriatric': geriatric_info or 'No specific geriatric considerations'
                    }
                }
                
                success = st.session_state.drug_db.add_drug(drug_name, drug_data)
                if success:
                    st.success(f"✅ Successfully added {drug_name.title()} to the database!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add drug to database")
            else:
                st.error("Please provide at least the drug name and generic name")

def show_add_interactions():
    st.subheader("Add Drug Interactions")
    
    with st.form("add_interaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            drug1 = st.text_input("First Drug", placeholder="e.g., warfarin")
            drug2 = st.text_input("Second Drug", placeholder="e.g., aspirin")
            
        with col2:
            severity = st.selectbox("Interaction Severity", ["Low", "Moderate", "High"])
            
        description = st.text_area("Interaction Description", placeholder="e.g., Increased risk of bleeding")
        recommendation = st.text_area("Clinical Recommendation", placeholder="e.g., Monitor INR closely, consider alternative")
        
        submitted = st.form_submit_button("Add Interaction")
        
        if submitted:
            if drug1 and drug2 and description:
                success = st.session_state.interaction_checker.add_interaction(
                    drug1, drug2, severity, description, recommendation
                )
                if success:
                    st.success(f"✅ Successfully added interaction: {drug1.title()} ↔ {drug2.title()}")
                    st.rerun()
                else:
                    st.error("❌ Failed to add interaction")
            else:
                st.error("Please provide both drugs and interaction description")

def show_bulk_import():
    st.subheader("Bulk Import Data")
    
    st.markdown("""
    **Import Format Instructions:**
    
    For drugs, use this JSON structure:
    ```json
    {
        "drug_name": {
            "generic_name": "Full Generic Name",
            "brand_names": ["Brand1", "Brand2"],
            "category": "Drug Category",
            "indications": ["Use1", "Use2"],
            "contraindications": ["Contra1", "Contra2"],
            "side_effects": ["Effect1", "Effect2"],
            "dosage_forms": ["Form1", "Form2"],
            "strength_options": ["Strength1", "Strength2"],
            "age_restrictions": {
                "pediatric": "Pediatric info",
                "adult": "Adult info", 
                "geriatric": "Geriatric info"
            }
        }
    }
    ```
    """)
    
    import_type = st.selectbox("Import Type", ["Drugs", "Interactions"])
    
    if import_type == "Drugs":
        drug_json = st.text_area("Paste Drug JSON Data", height=300, placeholder="Paste your drug data in JSON format here...")
        
        if st.button("Import Drugs"):
            try:
                drugs_data = json.loads(drug_json)
                results = st.session_state.drug_db.bulk_add_drugs(drugs_data)
                
                success_count = sum(results.values())
                total_count = len(results)
                
                st.success(f"✅ Successfully imported {success_count}/{total_count} drugs!")
                
                if success_count < total_count:
                    st.warning("Some drugs failed to import:")
                    for drug, status in results.items():
                        if not status:
                            st.write(f"❌ {drug}")
                
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please check your data.")
            except Exception as e:
                st.error(f"❌ Import failed: {str(e)}")
    
    else:  # Interactions
        st.markdown("""
        For interactions, use this JSON structure:
        ```json
        [
            {
                "drug1": "drug_name_1",
                "drug2": "drug_name_2", 
                "severity": "High/Moderate/Low",
                "description": "Interaction description",
                "recommendation": "Clinical recommendation"
            }
        ]
        ```
        """)
        
        interaction_json = st.text_area("Paste Interaction JSON Data", height=300)
        
        if st.button("Import Interactions"):
            try:
                interactions_data = json.loads(interaction_json)
                results = st.session_state.interaction_checker.bulk_add_interactions(interactions_data)
                
                success_count = sum(results.values())
                total_count = len(results)
                
                st.success(f"✅ Successfully imported {success_count}/{total_count} interactions!")
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please check your data.")
            except Exception as e:
                st.error(f"❌ Import failed: {str(e)}")

def show():
    """Entry point for the drug administration page"""
    show_drug_administration()

if __name__ == "__main__":
    show_drug_administration()