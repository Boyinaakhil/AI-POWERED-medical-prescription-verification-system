import os
import requests
from typing import List, Dict, Any
import streamlit as st

class DrugInteractionChecker:
    def __init__(self):
        self.huggingface_token = os.getenv("HUGGINGFACE_API_KEY", "")
        self.api_url = "https://api-inference.huggingface.co/models/OpenMed/OpenMed-NER-PharmaDetect-SuperClinical-434M"
        self.headers = {"Authorization": f"Bearer {self.huggingface_token}"}
        
        # Known drug interactions database (expandable)
        self.interaction_database = {
            ("warfarin", "aspirin"): {
                "severity": "High",
                "description": "Increased risk of bleeding",
                "recommendation": "Monitor INR closely, consider alternative"
            },
            ("metformin", "insulin"): {
                "severity": "Moderate",
                "description": "Risk of hypoglycemia",
                "recommendation": "Monitor blood glucose levels"
            },
            ("lisinopril", "spironolactone"): {
                "severity": "High",
                "description": "Risk of hyperkalemia",
                "recommendation": "Monitor potassium levels"
            },
            ("simvastatin", "clarithromycin"): {
                "severity": "High",
                "description": "Increased risk of myopathy",
                "recommendation": "Avoid combination or reduce statin dose"
            },
            ("digoxin", "furosemide"): {
                "severity": "Moderate",
                "description": "Increased digitalis toxicity risk",
                "recommendation": "Monitor digoxin levels and electrolytes"
            }
        }
    
    def extract_drugs_from_text(self, text: str) -> List[str]:
        """Extract drug names using Hugging Face NER model"""
        try:
            payload = {"inputs": text}
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                entities = response.json()
                drugs = []
                
                for entity in entities:
                    if entity.get('entity_group', '').upper() in ['CHEMICAL', 'DRUG', 'PHARMA']:
                        drug_name = entity['word'].lower().strip()
                        if drug_name not in drugs:
                            drugs.append(drug_name)
                
                return drugs
            else:
                st.warning(f"API Error: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error extracting drugs: {str(e)}")
            return []
    
    def check_interactions(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Check for drug interactions"""
        interactions = []
        
        # Check all combinations of drugs
        for i in range(len(drugs)):
            for j in range(i + 1, len(drugs)):
                drug1, drug2 = drugs[i].lower(), drugs[j].lower()
                
                # Check both combinations
                interaction_key = (drug1, drug2)
                reverse_key = (drug2, drug1)
                
                if interaction_key in self.interaction_database:
                    interaction_data = self.interaction_database[interaction_key]
                elif reverse_key in self.interaction_database:
                    interaction_data = self.interaction_database[reverse_key]
                else:
                    continue
                
                interactions.append({
                    'drug1': drug1.title(),
                    'drug2': drug2.title(),
                    'severity': interaction_data['severity'],
                    'description': interaction_data['description'],
                    'recommendation': interaction_data['recommendation']
                })
        
        return interactions
    
    def analyze_individual_drugs(self, drugs: List[str]) -> List[Dict[str, Any]]:
        """Analyze individual drug information"""
        drug_info = []
        
        for drug in drugs:
            # Simplified drug information
            info = {
                'name': drug.title(),
                'category': self._get_drug_category(drug),
                'common_side_effects': self._get_side_effects(drug),
                'contraindications': self._get_contraindications(drug)
            }
            drug_info.append(info)
        
        return drug_info
    
    def _get_drug_category(self, drug: str) -> str:
        """Get drug category"""
        categories = {
            'aspirin': 'NSAID/Antiplatelet',
            'warfarin': 'Anticoagulant',
            'metformin': 'Antidiabetic',
            'insulin': 'Hormone/Antidiabetic',
            'lisinopril': 'ACE Inhibitor',
            'simvastatin': 'Statin',
            'digoxin': 'Cardiac Glycoside',
            'furosemide': 'Loop Diuretic',
            'spironolactone': 'Potassium-sparing Diuretic',
            'clarithromycin': 'Macrolide Antibiotic'
        }
        return categories.get(drug.lower(), 'Unknown')
    
    def add_interaction(self, drug1: str, drug2: str, severity: str, description: str, recommendation: str) -> bool:
        """Add new drug interaction to database"""
        try:
            interaction_key = (drug1.lower().strip(), drug2.lower().strip())
            self.interaction_database[interaction_key] = {
                'severity': severity,
                'description': description,
                'recommendation': recommendation
            }
            return True
        except Exception as e:
            print(f"Error adding interaction {drug1}-{drug2}: {e}")
            return False
    
    def bulk_add_interactions(self, interactions_data: List[Dict[str, str]]) -> Dict[str, bool]:
        """Add multiple interactions at once"""
        results = {}
        for interaction in interactions_data:
            drug1 = interaction.get('drug1', '')
            drug2 = interaction.get('drug2', '')
            success = self.add_interaction(
                drug1, drug2,
                interaction.get('severity', 'Moderate'),
                interaction.get('description', ''),
                interaction.get('recommendation', '')
            )
            results[f"{drug1}-{drug2}"] = success
        return results
    
    def get_interaction_stats(self) -> Dict[str, int]:
        """Get statistics about interactions database"""
        severities = {}
        for interaction in self.interaction_database.values():
            severity = interaction['severity']
            severities[severity] = severities.get(severity, 0) + 1
        
        return {
            'total_interactions': len(self.interaction_database),
            'high_severity': severities.get('High', 0),
            'moderate_severity': severities.get('Moderate', 0),
            'low_severity': severities.get('Low', 0)
        }
    
    def _get_side_effects(self, drug: str) -> List[str]:
        """Get common side effects"""
        side_effects = {
            'aspirin': ['GI upset', 'Bleeding', 'Tinnitus'],
            'warfarin': ['Bleeding', 'Bruising', 'Hair loss'],
            'metformin': ['GI upset', 'Lactic acidosis', 'B12 deficiency'],
            'insulin': ['Hypoglycemia', 'Weight gain', 'Injection site reactions'],
            'lisinopril': ['Dry cough', 'Hyperkalemia', 'Angioedema'],
            'simvastatin': ['Muscle pain', 'Liver enzyme elevation', 'Memory issues'],
            'digoxin': ['Nausea', 'Visual disturbances', 'Arrhythmias'],
            'furosemide': ['Dehydration', 'Electrolyte imbalance', 'Ototoxicity'],
            'spironolactone': ['Hyperkalemia', 'Gynecomastia', 'Menstrual irregularities'],
            'clarithromycin': ['GI upset', 'QT prolongation', 'Drug interactions']
        }
        return side_effects.get(drug.lower(), ['Contact healthcare provider'])
    
    def _get_contraindications(self, drug: str) -> List[str]:
        """Get contraindications"""
        contraindications = {
            'aspirin': ['Active bleeding', 'Severe renal impairment', 'Children with viral illness'],
            'warfarin': ['Pregnancy', 'Active bleeding', 'Severe hepatic impairment'],
            'metformin': ['Severe renal impairment', 'Severe hepatic impairment', 'Heart failure'],
            'insulin': ['Hypoglycemia', 'Allergy to insulin'],
            'lisinopril': ['Pregnancy', 'Bilateral renal artery stenosis', 'Angioedema history'],
            'simvastatin': ['Active liver disease', 'Pregnancy', 'Myopathy'],
            'digoxin': ['Ventricular fibrillation', 'Digitalis toxicity', 'Hypertrophic cardiomyopathy'],
            'furosemide': ['Anuria', 'Severe electrolyte depletion', 'Digitalis toxicity'],
            'spironolactone': ['Hyperkalemia', 'Severe renal impairment', 'Addison disease'],
            'clarithromycin': ['Hypersensitivity', 'Severe hepatic impairment', 'QT prolongation']
        }
        return contraindications.get(drug.lower(), ['Consult healthcare provider'])
