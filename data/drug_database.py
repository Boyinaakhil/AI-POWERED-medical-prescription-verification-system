from typing import Dict, List, Any

class DrugDatabase:
    def __init__(self):
        self.drugs = {
            'aspirin': {
                'generic_name': 'Acetylsalicylic Acid',
                'brand_names': ['Bayer', 'Bufferin', 'Ecotrin'],
                'category': 'NSAID/Antiplatelet',
                'indications': ['Pain relief', 'Fever reduction', 'Cardiovascular protection'],
                'contraindications': ['Active bleeding', 'Severe renal impairment', 'Children with viral illness'],
                'side_effects': ['GI upset', 'Bleeding', 'Tinnitus'],
                'dosage_forms': ['Tablet', 'Chewable tablet', 'Enteric-coated tablet'],
                'strength_options': ['81mg', '325mg', '500mg'],
                'age_restrictions': {
                    'pediatric': 'Contraindicated in children with viral illness (Reye syndrome risk)',
                    'adult': 'Standard dosing',
                    'geriatric': 'Use with caution, increased bleeding risk'
                }
            },
            'metformin': {
                'generic_name': 'Metformin Hydrochloride',
                'brand_names': ['Glucophage', 'Fortamet', 'Glumetza'],
                'category': 'Antidiabetic (Biguanide)',
                'indications': ['Type 2 diabetes', 'PCOS', 'Prediabetes'],
                'contraindications': ['Severe renal impairment', 'Severe hepatic impairment', 'Heart failure'],
                'side_effects': ['GI upset', 'Lactic acidosis', 'B12 deficiency'],
                'dosage_forms': ['Tablet', 'Extended-release tablet'],
                'strength_options': ['500mg', '850mg', '1000mg'],
                'age_restrictions': {
                    'pediatric': 'Safety and efficacy established in children ≥10 years',
                    'adult': 'Standard dosing',
                    'geriatric': 'Use with caution, monitor renal function'
                }
            },
            'lisinopril': {
                'generic_name': 'Lisinopril',
                'brand_names': ['Prinivil', 'Zestril'],
                'category': 'ACE Inhibitor',
                'indications': ['Hypertension', 'Heart failure', 'Post-MI'],
                'contraindications': ['Pregnancy', 'Bilateral renal artery stenosis', 'Angioedema history'],
                'side_effects': ['Dry cough', 'Hyperkalemia', 'Angioedema'],
                'dosage_forms': ['Tablet'],
                'strength_options': ['2.5mg', '5mg', '10mg', '20mg', '40mg'],
                'age_restrictions': {
                    'pediatric': 'Safety not established in children <6 years',
                    'adult': 'Standard dosing',
                    'geriatric': 'Start with lower doses'
                }
            },
            'warfarin': {
                'generic_name': 'Warfarin Sodium',
                'brand_names': ['Coumadin', 'Jantoven'],
                'category': 'Anticoagulant',
                'indications': ['Atrial fibrillation', 'DVT/PE', 'Mechanical heart valves'],
                'contraindications': ['Pregnancy', 'Active bleeding', 'Severe hepatic impairment'],
                'side_effects': ['Bleeding', 'Bruising', 'Hair loss'],
                'dosage_forms': ['Tablet'],
                'strength_options': ['1mg', '2mg', '2.5mg', '3mg', '4mg', '5mg', '6mg', '7.5mg', '10mg'],
                'age_restrictions': {
                    'pediatric': 'Use with extreme caution, limited data',
                    'adult': 'Standard dosing with INR monitoring',
                    'geriatric': 'Increased sensitivity, start with lower doses'
                }
            },
            'simvastatin': {
                'generic_name': 'Simvastatin',
                'brand_names': ['Zocor'],
                'category': 'HMG-CoA Reductase Inhibitor (Statin)',
                'indications': ['Hypercholesterolemia', 'Cardiovascular risk reduction'],
                'contraindications': ['Active liver disease', 'Pregnancy', 'Myopathy'],
                'side_effects': ['Muscle pain', 'Liver enzyme elevation', 'Memory issues'],
                'dosage_forms': ['Tablet'],
                'strength_options': ['5mg', '10mg', '20mg', '40mg', '80mg'],
                'age_restrictions': {
                    'pediatric': 'Safety established in children ≥10 years with familial hypercholesterolemia',
                    'adult': 'Standard dosing',
                    'geriatric': 'Start with lower doses, monitor for drug interactions'
                }
            }
        }
        
        self.alternatives = {
            'aspirin': ['ibuprofen', 'acetaminophen', 'naproxen'],
            'metformin': ['glyburide', 'glipizide', 'sitagliptin'],
            'lisinopril': ['losartan', 'amlodipine', 'metoprolol'],
            'warfarin': ['rivaroxaban', 'apixaban', 'dabigatran'],
            'simvastatin': ['atorvastatin', 'rosuvastatin', 'pravastatin']
        }
        
        self.medical_conditions = [
            'Hypertension',
            'Diabetes Type 2',
            'Hyperlipidemia',
            'Atrial Fibrillation',
            'Coronary Artery Disease',
            'Heart Failure',
            'Chronic Kidney Disease',
            'Osteoarthritis',
            'Depression',
            'Anxiety',
            'COPD',
            'Asthma',
            'Hypothyroidism',
            'GERD',
            'Osteoporosis'
        ]
    
    def get_drug_info(self, drug_name: str) -> Dict[str, Any]:
        """Get comprehensive drug information"""
        drug_key = drug_name.lower().strip()
        return self.drugs.get(drug_key, {})
    
    def get_alternatives(self, drug_name: str) -> List[str]:
        """Get alternative medications"""
        drug_key = drug_name.lower().strip()
        return self.alternatives.get(drug_key, [])
    
    def search_drugs(self, query: str) -> List[str]:
        """Search for drugs by name or indication"""
        query = query.lower()
        matches = []
        
        for drug_name, drug_info in self.drugs.items():
            # Check drug name
            if query in drug_name:
                matches.append(drug_name)
                continue
            
            # Check brand names
            for brand in drug_info.get('brand_names', []):
                if query in brand.lower():
                    matches.append(drug_name)
                    break
            
            # Check indications
            for indication in drug_info.get('indications', []):
                if query in indication.lower():
                    matches.append(drug_name)
                    break
        
        return list(set(matches))  # Remove duplicates
    
    def get_age_specific_info(self, drug_name: str, age_category: str) -> str:
        """Get age-specific prescribing information"""
        drug_info = self.get_drug_info(drug_name)
        age_restrictions = drug_info.get('age_restrictions', {})
        return age_restrictions.get(age_category, 'No specific age-related information available')
    
    def get_medical_conditions(self) -> List[str]:
        """Get list of medical conditions"""
        return self.medical_conditions
    
    def get_all_drugs(self) -> List[str]:
        """Get list of all drugs in database"""
        return list(self.drugs.keys())
    
    def add_drug(self, drug_name: str, drug_data: Dict[str, Any]) -> bool:
        """Add new drug to database"""
        try:
            drug_key = drug_name.lower().strip()
            self.drugs[drug_key] = drug_data
            return True
        except Exception as e:
            print(f"Error adding drug {drug_name}: {e}")
            return False
    
    def add_interaction(self, drug1: str, drug2: str, interaction_data: Dict[str, str]) -> bool:
        """Add new drug interaction"""
        try:
            interaction_key = (drug1.lower().strip(), drug2.lower().strip())
            # Store interaction in drug interaction checker (will implement)
            return True
        except Exception as e:
            print(f"Error adding interaction {drug1}-{drug2}: {e}")
            return False
    
    def bulk_add_drugs(self, drugs_data: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Add multiple drugs at once"""
        results = {}
        for drug_name, drug_data in drugs_data.items():
            results[drug_name] = self.add_drug(drug_name, drug_data)
        return results
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about the drug database"""
        return {
            'total_drugs': len(self.drugs),
            'total_conditions': len(self.medical_conditions),
            'drugs_with_alternatives': len([d for d in self.drugs.keys() if d in self.alternatives])
        }
